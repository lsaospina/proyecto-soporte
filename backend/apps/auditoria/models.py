from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class AccionAuditoria(models.TextChoices):
    LOGIN_EXITOSO = "LOGIN_EXITOSO", "Inicio de sesión exitoso"
    LOGIN_FALLIDO = "LOGIN_FALLIDO", "Inicio de sesión fallido"
    LOGOUT = "LOGOUT", "Cierre de sesión"
    MFA_ACTIVADO = "MFA_ACTIVADO", "MFA activado"
    MFA_VERIFICADO = "MFA_VERIFICADO", "MFA verificado"
    MFA_RECHAZADO = "MFA_RECHAZADO", "MFA rechazado"
    PASSWORD_CAMBIADA = "PASSWORD_CAMBIADA", "Contraseña cambiada"
    USUARIO_CREADO = "USUARIO_CREADO", "Usuario creado"
    USUARIO_ACTUALIZADO = "USUARIO_ACTUALIZADO", "Usuario actualizado"
    USUARIO_INACTIVADO = "USUARIO_INACTIVADO", "Usuario inactivado"
    USUARIO_REACTIVADO = "USUARIO_REACTIVADO", "Usuario reactivado"
    PASSWORD_RESETEADA = "PASSWORD_RESETEADA", "Contraseña reseteada"
    MFA_RESETEADO = "MFA_RESETEADO", "MFA reseteado"


class RegistroAuditoria(BaseModel):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registros_auditoria",
        verbose_name="Usuario",
    )
    accion = models.CharField(
        max_length=40,
        choices=AccionAuditoria.choices,
        verbose_name="Acción",
    )
    entidad = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Entidad",
    )
    entidad_id = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name="ID de entidad",
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha",
    )
    ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP",
    )

    class Meta:
        verbose_name = "Registro de auditoría"
        verbose_name_plural = "Registros de auditoría"
        ordering = ["-fecha"]
        indexes = [
            models.Index(fields=["fecha"], name="auditoria_fecha_idx"),
            models.Index(fields=["accion"], name="auditoria_accion_idx"),
            models.Index(fields=["usuario"], name="auditoria_usuario_idx"),
        ]

    def __str__(self):
        return f"{self.accion} - {self.fecha}"
