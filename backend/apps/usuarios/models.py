from datetime import timedelta

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel


class RolChoices(models.TextChoices):
    ADMINISTRADOR = "ADMINISTRADOR", "Administrador"
    TECNICO = "TECNICO", "Técnico"
    USUARIO_RESPONSABLE = "USUARIO_RESPONSABLE", "Usuario Responsable"


class UsuarioManager(BaseUserManager):
    """Administrador personalizado de usuarios donde el email es el identificador único."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("rol", RolChoices.ADMINISTRADOR)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser, BaseModel):
    """
    Modelo de usuario del sistema.
    Autenticación por email único, roles explícitos y control de bloqueos por seguridad.
    """

    username = None
    email = models.EmailField(
        unique=True,
        verbose_name="Correo electrónico",
        help_text="Correo electrónico institucional único para el inicio de sesión.",
    )
    nombre_completo = models.CharField(
        max_length=255,
        verbose_name="Nombre completo",
        help_text="Nombre y apellidos del usuario.",
    )
    rol = models.CharField(
        max_length=30,
        choices=RolChoices.choices,
        default=RolChoices.USUARIO_RESPONSABLE,
        verbose_name="Rol en el sistema",
        help_text="Determina los permisos y nivel de acceso en la plataforma.",
    )
    intentos_fallidos = models.PositiveIntegerField(
        default=0,
        verbose_name="Intentos fallidos",
        help_text="Contador consecutivo de intentos fallidos de autenticación o MFA.",
    )
    bloqueado_hasta = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Bloqueado hasta",
        help_text="Estampa de tiempo hasta la cual la cuenta no puede autenticarse.",
    )

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre_completo"]

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["email"]

    def __str__(self):
        return f"{self.email} ({self.get_rol_display()})"

    @property
    def esta_bloqueado(self) -> bool:
        """Indica si la cuenta está temporalmente bloqueada por exceso de intentos fallidos."""
        if not self.bloqueado_hasta:
            return False
        return timezone.now() < self.bloqueado_hasta

    def registrar_intento_fallido(self) -> int:
        """
        Incrementa el contador de intentos fallidos.
        Si alcanza 5 fallos, bloquea la cuenta durante 15 minutos.
        Persiste los cambios de inmediato.
        """
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= 5:
            self.bloqueado_hasta = timezone.now() + timedelta(minutes=15)
        self.save(update_fields=["intentos_fallidos", "bloqueado_hasta"])
        return self.intentos_fallidos

    def resetear_intentos_fallidos(self) -> None:
        """Restablece los contadores de fallos y desbloquea la cuenta."""
        if self.intentos_fallidos > 0 or self.bloqueado_hasta is not None:
            self.intentos_fallidos = 0
            self.bloqueado_hasta = None
            self.save(update_fields=["intentos_fallidos", "bloqueado_hasta"])
