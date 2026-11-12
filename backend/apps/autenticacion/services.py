import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.exceptions import (
    CredencialesInvalidasError,
    CuentaBloqueadaError,
    ReglaDeNegocioError,
)
from apps.common.sessions import revocar_tokens_refresco
from apps.usuarios.models import Usuario
from apps.usuarios.utils import normalizar_email

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
    PURPOSE_PASSWORD_CHANGE,
    PURPOSE_SETUP,
    PURPOSE_VERIFY,
    generar_mfa_token,
    validar_mfa_token,
)
from .types import ResultadoAutenticacion

logger = logging.getLogger(__name__)


def _resolver_estado_post_autenticacion(user: Usuario) -> ResultadoAutenticacion:
    """Determina el siguiente estado tras credenciales válidas (o cambio de contraseña)."""
    dispositivo = getattr(user, "dispositivo_mfa", None)
    if dispositivo and dispositivo.confirmado:
        mfa_token = generar_mfa_token(user.id, purpose=PURPOSE_VERIFY)
        logger.info("MFA requerido para user_id=%s", user.id)
        return ResultadoAutenticacion(estado="mfa_required", usuario=user, mfa_token=mfa_token)

    mfa_enforced = getattr(settings, "MFA_ENFORCED", True)
    if mfa_enforced:
        mfa_token = generar_mfa_token(user.id, purpose=PURPOSE_SETUP)
        logger.info("Configuración obligatoria de MFA para user_id=%s", user.id)
        return ResultadoAutenticacion(
            estado="mfa_setup_required", usuario=user, mfa_token=mfa_token
        )

    user.resetear_intentos_fallidos()
    refresh = RefreshToken.for_user(user)
    logger.info("Autenticación directa exitosa para user_id=%s", user.id)
    return ResultadoAutenticacion(estado="ok", usuario=user, refresh=refresh)


def autenticar_usuario_paso1(email: str, password: str, *, ip=None) -> ResultadoAutenticacion:
    """
    Paso 1 del flujo de autenticación:
    Valida credenciales y evalúa el estado del segundo factor.
    Estados posibles: ok, mfa_required, mfa_setup_required, password_change_required.
    No registra LOGIN_EXITOSO (solo al emitir sesión final).
    """
    email_normalizado = normalizar_email(email)
    user = Usuario.objects.filter(email__iexact=email_normalizado).first()

    if not user:
        logger.warning("Intento de login fallido: usuario no encontrado.")
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

    if user.debe_cambiar_password:
        password_token = generar_mfa_token(user.id, purpose=PURPOSE_PASSWORD_CHANGE)
        logger.info("Cambio de contraseña obligatorio para user_id=%s", user.id)
        return ResultadoAutenticacion(
            estado="password_change_required", usuario=user, password_token=password_token
        )

    return _resolver_estado_post_autenticacion(user)


def cambiar_password_obligatorio(
    password_token: str, new_password: str, *, ip=None
) -> ResultadoAutenticacion:
    """
    Cambia la contraseña cuando debe_cambiar_password es True.
    Token de un solo uso (se invalida al poner debe_cambiar_password=False).
    """
    user_id = validar_mfa_token(password_token, expected_purpose=PURPOSE_PASSWORD_CHANGE)
    user = Usuario.objects.filter(id=user_id).first()
    if not user:
        raise CredencialesInvalidasError("Usuario no encontrado o inactivo.")

    if not user.is_active:
        raise CredencialesInvalidasError("El usuario se encuentra inactivo en el sistema.")

    if user.esta_bloqueado:
        raise CuentaBloqueadaError("La cuenta se encuentra temporalmente bloqueada.")

    if not user.debe_cambiar_password:
        raise ReglaDeNegocioError(
            "El cambio de contraseña obligatorio ya no es válido.",
            code="cambio_password_no_requerido",
        )

    if user.check_password(new_password):
        raise ReglaDeNegocioError(
            "La nueva contraseña no puede ser igual a la contraseña actual.",
            code="password_igual_anterior",
            errors=[
                {
                    "field": "new_password",
                    "message": "La nueva contraseña debe ser diferente a la actual.",
                }
            ],
        )

    validate_password(new_password, user)

    with transaction.atomic():
        user.set_password(new_password)
        user.debe_cambiar_password = False
        user.intentos_fallidos = 0
        user.bloqueado_hasta = None
        user.save(
            update_fields=[
                "password",
                "debe_cambiar_password",
                "intentos_fallidos",
                "bloqueado_hasta",
                "updated_at",
            ]
        )
        revocar_tokens_refresco(user)

    logger.info("Cambio obligatorio de contraseña completado para user_id=%s", user.id)
    return _resolver_estado_post_autenticacion(user)


def iniciar_setup_mfa(mfa_token: str) -> dict[str, str]:
    """Genera el secreto TOTP y la URI para configurar la app autenticadora."""
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
    """Valida el primer código, activa MFA, genera códigos de recuperación y abre sesión."""

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
    logger.info("Dispositivo MFA confirmado y activado para user_id=%s", user.id)

    return refresh, codigos_planos, user


def verificar_mfa_sesion(
    mfa_token: str,
    code: str | None = None,
    recovery_code: str | None = None,
    clock: datetime | None = None,
) -> tuple[RefreshToken, Usuario]:
    """Verifica un código TOTP o de recuperación para abrir sesión."""

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
            "MFA verificado mediante código de recuperación para user_id=%s.",
            user.id,
        )
        return refresh, user

    raise ReglaDeNegocioError("Debe suministrar un código TOTP o de recuperación.")


def rotar_token_refresco(refresh_token_str: str) -> tuple[str, str]:
    """
    Valida el token de refresco, lo rota y añade a lista negra el anterior.
    Comprueba explícitamente is_active y no bloqueado.
    Retorna (nuevo_access_token, nuevo_refresh_token).
    """
    if not refresh_token_str:
        raise CredencialesInvalidasError(
            "Cookie de refresco no presente o inválida.",
            code="refresh_token_faltante",
        )

    try:
        token = RefreshToken(refresh_token_str)
        user_id = token.payload.get("user_id")
        user = Usuario.objects.filter(id=user_id).first()
        if not user or not user.is_active or user.esta_bloqueado:
            raise CredencialesInvalidasError(
                "Usuario inválido, inactivo o bloqueado.",
                code="usuario_invalido",
            )

        token.blacklist()
        nuevo_token = RefreshToken.for_user(user)
        return str(nuevo_token.access_token), str(nuevo_token)
    except CredencialesInvalidasError:
        raise
    except TokenError as exc:
        logger.warning("Fallo en rotación de refresh token: %s", exc)
        raise CredencialesInvalidasError(
            "Token de refresco inválido o expirado.",
            code="token_refresco_invalido",
        ) from exc


def invalidar_sesion(refresh_token_str: str | None) -> None:
    """Añade a lista negra el refresh token para cerrar sesión."""
    if not refresh_token_str:
        return
    try:
        token = RefreshToken(refresh_token_str)
        token.blacklist()
        logger.info("Sesión cerrada y token invalidado en lista negra.")
    except Exception as exc:
        logger.warning("Aviso al cerrar sesión: %s", exc)
