from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class DispositivoMFA(BaseModel):
    """
    Almacena la configuración del segundo factor (TOTP) de un usuario.
    El secreto nunca se guarda en texto claro; se almacena cifrado con Fernet.
    """

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dispositivo_mfa",
        verbose_name="Usuario",
    )
    secreto_cifrado = models.CharField(
        max_length=255,
        verbose_name="Secreto TOTP cifrado",
        help_text="Clave secreta TOTP cifrada con clave simétrica Fernet.",
    )
    confirmado = models.BooleanField(
        default=False,
        verbose_name="Dispositivo confirmado",
        help_text="Indica si el usuario completó satisfactoriamente el primer enrolamiento.",
    )
    ultimo_paso_usado = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Último paso TOTP usado",
        help_text="Paso temporal del último código TOTP verificado con éxito (evita repetición).",
    )

    class Meta:
        verbose_name = "Dispositivo MFA"
        verbose_name_plural = "Dispositivos MFA"

    def __str__(self):
        estado = "confirmado" if self.confirmado else "pendiente"
        return f"MFA ({estado}) - {self.usuario.email}"


class CodigoRecuperacion(BaseModel):
    """
    Códigos de un solo uso para acceder a la cuenta si se pierde el autenticador TOTP.
    Se almacenan hasheados con el hasher de contraseñas de Django.
    """

    dispositivo = models.ForeignKey(
        DispositivoMFA,
        on_delete=models.CASCADE,
        related_name="codigos_recuperacion",
        verbose_name="Dispositivo MFA",
    )
    codigo_hash = models.CharField(
        max_length=255,
        verbose_name="Hash del código de recuperación",
        help_text="Hash criptográfico del código de recuperación.",
    )
    usado_en = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de uso",
        help_text="Estampa de tiempo en la que este código fue consumido (un solo uso).",
    )

    class Meta:
        verbose_name = "Código de Recuperación"
        verbose_name_plural = "Códigos de Recuperación"

    @property
    def esta_usado(self) -> bool:
        return self.usado_en is not None

    def __str__(self):
        estado = "USADO" if self.esta_usado else "DISPONIBLE"
        return f"Código [{estado}] - {self.dispositivo.usuario.email}"
