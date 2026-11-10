import logging
from datetime import datetime

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.exceptions import (
    CredencialesInvalidasError,
    CuentaBloqueadaError,
    ReglaDeNegocioError,
)
from apps.usuarios.models import Usuario

from .crypto import (
    cifrar_secreto,
    descifrar_secreto,
    generar_codigos_recuperacion,
    generar_secreto_totp,
    obtener_uri_totp,
    verificar_codigo_recuperacion,
    verificar_totp,
)
from .models import CodigoRecuperacion, DispositivoMFA
from .tokens import (
    PURPOSE_SETUP,
    PURPOSE_VERIFY,
    generar_mfa_token,
    validar_mfa_token,
)

logger = logging.getLogger(__name__)


def autenticar_usuario_paso1(
    email: str,
    password: str,
) -> tuple[str, str | None, RefreshToken | None, Usuario]:
    """
    Paso 1 del flujo de autenticación:
    Valida credenciales y evalúa el estado del segundo factor.
    Retorna (estado, mfa_token, refresh_token, usuario)
    Estados posibles:
      - 'ok': Acceso directo concedido (solo si MFA no es forzado y usuario no tiene MFA).
      - 'mfa_required': Requiere ingresar código de segundo factor.
      - 'mfa_setup_required': Requiere enrolamiento inicial de segundo factor.
    """
    email_normalizado = email.strip().lower()
    user = Usuario.objects.filter(email__iexact=email_normalizado).first()

    if not user:
        logger.warning("Intento de login fallido: usuario no encontrado para email proporcionado.")
        raise CredencialesInvalidasError("Credenciales inválidas.")

    if user.esta_bloqueado:
        logger.warning("Intento de acceso a cuenta bloqueada: user_id=%s", user.id)
        raise CuentaBloqueadaError(
            "La cuenta se encuentra temporalmente bloqueada por exceso de intentos fallidos. Intente más tarde.",
            code="cuenta_bloqueada",
        )

    if not user.check_password(password):
        fallos = user.registrar_intento_fallido()
        logger.warning(
            "Contraseña inválida para user_id=%s. Total intentos fallidos: %s",
            user.id,
            fallos,
        )
        if user.esta_bloqueado:
            raise CuentaBloqueadaError(
                "La cuenta ha sido bloqueada durante 15 minutos debido a 5 intentos fallidos consecutivos.",
                code="cuenta_bloqueada",
            )
        raise CredencialesInvalidasError("Credenciales inválidas.")

    if not user.is_active:
        logger.warning("Intento de acceso de usuario inactivo: user_id=%s", user.id)
        raise CredencialesInvalidasError("El usuario se encuentra inactivo en el sistema.")

    # Verificar configuración de MFA
    dispositivo = getattr(user, "dispositivo_mfa", None)
    if dispositivo and dispositivo.confirmado:
        mfa_token = generar_mfa_token(user.id, purpose=PURPOSE_VERIFY)
        logger.info("Credenciales válidas. MFA requerido para user_id=%s", user.id)
        return "mfa_required", mfa_token, None, user

    mfa_enforced = getattr(settings, "MFA_ENFORCED", True)
    if mfa_enforced:
        mfa_token = generar_mfa_token(user.id, purpose=PURPOSE_SETUP)
        logger.info(
            "Credenciales válidas. Configuración obligatoria de MFA para user_id=%s",
            user.id,
        )
        return "mfa_setup_required", mfa_token, None, user

    # Si MFA no es forzado y no tiene dispositivo
    user.resetear_intentos_fallidos()
    refresh = RefreshToken.for_user(user)
    logger.info("Autenticación directa exitosa para user_id=%s", user.id)
    return "ok", None, refresh, user


def iniciar_setup_mfa(mfa_token: str) -> dict[str, str]:
    """
    Genera el secreto TOTP y la URI para que el usuario configure su app autenticadora.
    """
    user_id = validar_mfa_token(mfa_token, expected_purpose=PURPOSE_SETUP)
    user = Usuario.objects.filter(id=user_id, is_active=True).first()
    if not user:
        raise CredencialesInvalidasError("Usuario no encontrado o inactivo.")

    if user.esta_bloqueado:
        raise CuentaBloqueadaError("La cuenta se encuentra temporalmente bloqueada.")

    secreto_plano = generar_secreto_totp()
    secreto_cifrado = cifrar_secreto(secreto_plano)

    DispositivoMFA.objects.update_or_create(
        usuario=user,
        defaults={
            "secreto_cifrado": secreto_cifrado,
            "confirmado": False,
            "ultimo_paso_usado": None,
        },
    )

    otpauth_uri = obtener_uri_totp(secreto_plano, user.email)
    logger.info("Nuevo secreto TOTP generado para enrolamiento: user_id=%s", user.id)

    return {
        "secret": secreto_plano,
        "otpauth_uri": otpauth_uri,
    }


def confirmar_setup_mfa(
    mfa_token: str,
    code: str,
    clock: datetime | None = None,
) -> tuple[RefreshToken, list[str], Usuario]:
    """
    Valida el primer código del usuario para activar el dispositivo MFA,
    genera los códigos de recuperación de emergencia y abre sesión.
    """
    user_id = validar_mfa_token(mfa_token, expected_purpose=PURPOSE_SETUP)
    user = Usuario.objects.filter(id=user_id, is_active=True).first()
    if not user:
        raise CredencialesInvalidasError("Usuario no encontrado o inactivo.")

    if user.esta_bloqueado:
        raise CuentaBloqueadaError("La cuenta se encuentra temporalmente bloqueada.")

    dispositivo = getattr(user, "dispositivo_mfa", None)
    if not dispositivo:
        raise ReglaDeNegocioError(
            "No se ha iniciado la configuración de MFA. Ejecute setup primero.",
            code="mfa_no_iniciado",
        )

    secreto_plano = descifrar_secreto(dispositivo.secreto_cifrado)
    valido, matched_step = verificar_totp(
        secreto=secreto_plano,
        codigo=code,
        ultimo_paso_usado=None,
        at_time=clock,
    )

    if not valido:
        fallos = user.registrar_intento_fallido()
        logger.warning(
            "Fallo al confirmar código MFA para user_id=%s. Intentos fallidos: %s",
            user.id,
            fallos,
        )
        if user.esta_bloqueado:
            raise CuentaBloqueadaError(
                "La cuenta ha sido bloqueada durante 15 minutos debido a 5 intentos fallidos.",
                code="cuenta_bloqueada",
            )
        raise CredencialesInvalidasError("Código de verificación incorrecto o expirado.")

    with transaction.atomic():
        dispositivo.confirmado = True
        dispositivo.ultimo_paso_usado = matched_step
        dispositivo.save(update_fields=["confirmado", "ultimo_paso_usado", "updated_at"])

        # Generar 10 códigos de recuperación
        dispositivo.codigos_recuperacion.all().delete()
        pares_codigos = generar_codigos_recuperacion(cantidad=10)
        codigos_planos = []
        for codigo_plano, codigo_hash in pares_codigos:
            CodigoRecuperacion.objects.create(
                dispositivo=dispositivo,
                codigo_hash=codigo_hash,
            )
            codigos_planos.append(codigo_plano)

    user.resetear_intentos_fallidos()
    refresh = RefreshToken.for_user(user)
    logger.info("Dispositivo MFA confirmado y activado exitosamente para user_id=%s", user.id)

    return refresh, codigos_planos, user


def verificar_mfa_sesion(
    mfa_token: str,
    code: str | None = None,
    recovery_code: str | None = None,
    clock: datetime | None = None,
) -> tuple[RefreshToken, Usuario]:
    """
    Verifica un código TOTP o un código de recuperación para abrir sesión.
    """
    user_id = validar_mfa_token(mfa_token, expected_purpose=PURPOSE_VERIFY)
    user = Usuario.objects.filter(id=user_id, is_active=True).first()
    if not user:
        raise CredencialesInvalidasError("Usuario no encontrado o inactivo.")

    if user.esta_bloqueado:
        raise CuentaBloqueadaError("La cuenta se encuentra temporalmente bloqueada.")

    dispositivo = getattr(user, "dispositivo_mfa", None)
    if not dispositivo or not dispositivo.confirmado:
        raise ReglaDeNegocioError(
            "El usuario no tiene un dispositivo MFA confirmado.",
            code="mfa_no_configurado",
        )

    # 1. Verificación mediante código TOTP
    if code:
        secreto_plano = descifrar_secreto(dispositivo.secreto_cifrado)
        valido, matched_step = verificar_totp(
            secreto=secreto_plano,
            codigo=code,
            ultimo_paso_usado=dispositivo.ultimo_paso_usado,
            at_time=clock,
        )
        if not valido:
            fallos = user.registrar_intento_fallido()
            logger.warning(
                "Fallo de código TOTP en login para user_id=%s. Intentos fallidos: %s",
                user.id,
                fallos,
            )
            if user.esta_bloqueado:
                raise CuentaBloqueadaError(
                    "La cuenta ha sido bloqueada por 15 minutos debido a 5 intentos fallidos.",
                    code="cuenta_bloqueada",
                )
            raise CredencialesInvalidasError(
                "Código de verificación TOTP inválido, expirado o ya utilizado."
            )

        dispositivo.ultimo_paso_usado = matched_step
        dispositivo.save(update_fields=["ultimo_paso_usado", "updated_at"])
        user.resetear_intentos_fallidos()
        refresh = RefreshToken.for_user(user)
        logger.info("MFA verificado correctamente por TOTP para user_id=%s", user.id)
        return refresh, user

    # 2. Verificación mediante código de recuperación de emergencia
    if recovery_code:
        codigos_disponibles = dispositivo.codigos_recuperacion.filter(usado_en__isnull=True)
        codigo_encontrado = None
        for obj in codigos_disponibles:
            if verificar_codigo_recuperacion(recovery_code, obj.codigo_hash):
                codigo_encontrado = obj
                break

        if not codigo_encontrado:
            fallos = user.registrar_intento_fallido()
            logger.warning(
                "Fallo de código de recuperación para user_id=%s. Intentos fallidos: %s",
                user.id,
                fallos,
            )
            if user.esta_bloqueado:
                raise CuentaBloqueadaError(
                    "La cuenta ha sido bloqueada por 15 minutos debido a 5 intentos fallidos.",
                    code="cuenta_bloqueada",
                )
            raise CredencialesInvalidasError("Código de recuperación inválido o ya utilizado.")

        codigo_encontrado.usado_en = timezone.now()
        codigo_encontrado.save(update_fields=["usado_en", "updated_at"])
        user.resetear_intentos_fallidos()
        refresh = RefreshToken.for_user(user)
        logger.info(
            "MFA verificado mediante código de recuperación para user_id=%s. Código consumido id=%s",
            user.id,
            codigo_encontrado.id,
        )
        return refresh, user

    raise ReglaDeNegocioError("Debe suministrar un código TOTP o de recuperación.")


def rotar_token_refresco(refresh_token_str: str) -> tuple[str, str]:
    """
    Valida el token de refresco, lo rota y añade a lista negra el anterior.
    Retorna (nuevo_access_token, nuevo_refresh_token).
    """
    if not refresh_token_str:
        raise CredencialesInvalidasError(
            "Cookie de refresco no presente o inválida.",
            code="refresh_token_faltante",
        )

    try:
        token = RefreshToken(refresh_token_str)
        # Rotación manual segura para persistir en lista negra
        user_id = token.payload.get("user_id")
        user = Usuario.objects.filter(id=user_id, is_active=True).first()
        if not user or user.esta_bloqueado:
            raise CredencialesInvalidasError("Usuario inválido o bloqueado.")

        token.blacklist()
        nuevo_token = RefreshToken.for_user(user)
        return str(nuevo_token.access_token), str(nuevo_token)
    except TokenError as exc:
        logger.warning("Fallo en rotación de refresh token: %s", exc)
        raise CredencialesInvalidasError(
            "Token de refresco inválido o expirado.",
            code="token_refresco_invalido",
        ) from exc


def invalidar_sesion(refresh_token_str: str | None) -> None:
    """
    Añade a lista negra el refresh token para cerrar sesión.
    """
    if not refresh_token_str:
        return
    try:
        token = RefreshToken(refresh_token_str)
        token.blacklist()
        logger.info("Sesión cerrada y token invalidado en lista negra.")
    except Exception as exc:
        logger.warning("Aviso al cerrar sesión: %s", exc)
