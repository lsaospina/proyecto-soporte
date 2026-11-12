import secrets
import string

from django.db import IntegrityError, transaction

from apps.auditoria.models import AccionAuditoria
from apps.auditoria.services import registrar_evento
from apps.common.exceptions import ReglaDeNegocioError
from apps.common.sessions import revocar_tokens_refresco

from .models import RolChoices, Usuario
from .utils import normalizar_email


def generar_password_temporal() -> str:
    """Genera contraseña temporal >=12 chars con mayúscula, minúscula, dígito y símbolo."""
    alphabet_upper = string.ascii_uppercase
    alphabet_lower = string.ascii_lowercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+[]{}"
    all_chars = alphabet_upper + alphabet_lower + digits + symbols
    while True:
        password = [
            secrets.choice(alphabet_upper),
            secrets.choice(alphabet_lower),
            secrets.choice(digits),
            secrets.choice(symbols),
        ]
        password += [secrets.choice(all_chars) for _ in range(8)]
        secrets.SystemRandom().shuffle(password)
        candidate = "".join(password)
        # Garantiza política mínima ya satisfecha
        if (
            any(c.isupper() for c in candidate)
            and any(c.islower() for c in candidate)
            and any(c.isdigit() for c in candidate)
            and any(c in symbols for c in candidate)
        ):
            return candidate


def _email_duplicado_error():
    return ReglaDeNegocioError(
        "Ya existe un usuario con ese correo.",
        code="email_duplicado",
        errors=[{"field": "email", "message": "Ya existe un usuario con ese correo."}],
    )


def _guardar_usuario_con_email(usuario, *, email=None):
    try:
        if email is not None:
            usuario.email = email
        usuario.save()
    except IntegrityError as exc:
        raise _email_duplicado_error() from exc


def crear_usuario(*, email, nombre_completo, rol, actor, ip=None):
    email_norm = normalizar_email(email)
    password_temporal = generar_password_temporal()
    with transaction.atomic():
        try:
            usuario = Usuario.objects.create_user(
                email=email_norm,
                password=password_temporal,
                nombre_completo=nombre_completo,
                rol=rol,
                debe_cambiar_password=True,
                is_active=True,
            )
        except IntegrityError as exc:
            raise _email_duplicado_error() from exc
        registrar_evento(
            usuario=actor,
            accion=AccionAuditoria.USUARIO_CREADO,
            entidad="Usuario",
            entidad_id=str(usuario.pk),
            ip=ip,
        )
    return usuario, password_temporal


def actualizar_usuario(usuario, *, nombre_completo, rol, actor, ip=None):
    # Email no se edita por ahora (A4). Si cambiara, normalizar y capturar IntegrityError.
    with transaction.atomic():
        if actor.pk == usuario.pk and rol != usuario.rol:
            raise ReglaDeNegocioError(
                "No puede cambiar su propio rol desde este módulo.",
                code="auto_cambio_rol_no_permitido",
                errors=[{"field": "rol", "message": "No puede cambiar su propio rol."}],
            )
        # Guardia último admin si se le quita rol admin
        if usuario.rol == RolChoices.ADMINISTRADOR and rol != RolChoices.ADMINISTRADOR:
            _asegurar_no_ultimo_admin(usuario)
        usuario.nombre_completo = nombre_completo
        usuario.rol = rol
        try:
            usuario.save(update_fields=["nombre_completo", "rol", "updated_at"])
        except IntegrityError as exc:
            raise _email_duplicado_error() from exc
        registrar_evento(
            usuario=actor,
            accion=AccionAuditoria.USUARIO_ACTUALIZADO,
            entidad="Usuario",
            entidad_id=str(usuario.pk),
            ip=ip,
        )
    return usuario


def _asegurar_no_ultimo_admin(usuario_objetivo):
    admins = list(
        Usuario.objects.select_for_update()
        .filter(rol=RolChoices.ADMINISTRADOR, is_active=True)
        .order_by("pk")
    )
    if len(admins) == 1 and admins[0].pk == usuario_objetivo.pk:
        raise ReglaDeNegocioError(
            "No es posible dejar el sistema sin al menos un administrador activo.",
            code="ultimo_admin",
            errors=[
                {"field": "is_active", "message": "Debe existir al menos un administrador activo."}
            ],
        )


def inactivar_usuario(usuario, *, actor, ip=None):
    if actor.pk == usuario.pk:
        raise ReglaDeNegocioError(
            "No puede inactivar su propia cuenta.",
            code="auto_inactivacion_no_permitida",
        )
    with transaction.atomic():
        usuario_locked = Usuario.objects.select_for_update().get(pk=usuario.pk)
        if usuario_locked.rol == RolChoices.ADMINISTRADOR and usuario_locked.is_active:
            _asegurar_no_ultimo_admin(usuario_locked)
        usuario_locked.is_active = False
        usuario_locked.save(update_fields=["is_active", "updated_at"])
        revocar_tokens_refresco(usuario_locked)
        registrar_evento(
            usuario=actor,
            accion=AccionAuditoria.USUARIO_INACTIVADO,
            entidad="Usuario",
            entidad_id=str(usuario_locked.pk),
            ip=ip,
        )
    usuario.refresh_from_db()
    return usuario


def reactivar_usuario(usuario, *, actor, ip=None):
    with transaction.atomic():
        usuario.is_active = True
        usuario.save(update_fields=["is_active", "updated_at"])
        registrar_evento(
            usuario=actor,
            accion=AccionAuditoria.USUARIO_REACTIVADO,
            entidad="Usuario",
            entidad_id=str(usuario.pk),
            ip=ip,
        )
    return usuario


def resetear_password(usuario, *, actor, ip=None):
    if actor.pk == usuario.pk:
        raise ReglaDeNegocioError(
            "No puede resetear su propia contraseña desde este módulo.",
            code="auto_reset_password_no_permitido",
        )
    password_temporal = generar_password_temporal()
    with transaction.atomic():
        usuario.set_password(password_temporal)
        usuario.debe_cambiar_password = True
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        usuario.save(
            update_fields=[
                "password",
                "debe_cambiar_password",
                "intentos_fallidos",
                "bloqueado_hasta",
                "updated_at",
            ]
        )
        revocar_tokens_refresco(usuario)
        registrar_evento(
            usuario=actor,
            accion=AccionAuditoria.PASSWORD_RESETEADA,
            entidad="Usuario",
            entidad_id=str(usuario.pk),
            ip=ip,
        )
    return password_temporal


def resetear_mfa(usuario, *, actor, ip=None):
    if actor.pk == usuario.pk:
        raise ReglaDeNegocioError(
            "No puede resetear su propio MFA desde este módulo.",
            code="auto_reset_mfa_no_permitido",
        )
    with transaction.atomic():
        dispositivo = getattr(usuario, "dispositivo_mfa", None)
        if dispositivo:
            dispositivo.delete()
        revocar_tokens_refresco(usuario)
        registrar_evento(
            usuario=actor,
            accion=AccionAuditoria.MFA_RESETEADO,
            entidad="Usuario",
            entidad_id=str(usuario.pk),
            ip=ip,
        )
    return usuario
