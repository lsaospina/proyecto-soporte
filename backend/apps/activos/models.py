from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from apps.catalogos.models import ModeloActivo
from apps.common.models import BaseModel


class EstadoActivo(models.TextChoices):
    DISPONIBLE = "DISPONIBLE", "Disponible"
    ASIGNADO = "ASIGNADO", "Asignado"
    EN_MANTENIMIENTO = "EN_MANTENIMIENTO", "En mantenimiento"
    DADO_DE_BAJA = "DADO_DE_BAJA", "Dado de baja"


class Activo(BaseModel):
    serial = models.CharField(max_length=120, unique=True)
    modelo = models.ForeignKey(ModeloActivo, on_delete=models.PROTECT, related_name="activos")
    fecha_adquisicion = models.DateField()
    valor_adquisicion = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    estado = models.CharField(
        max_length=20, choices=EstadoActivo.choices, default=EstadoActivo.DISPONIBLE
    )
    codigo_qr = models.CharField(max_length=20, unique=True, editable=False)
    procesador = models.CharField(max_length=120, blank=True, default="")
    ram_gb = models.PositiveIntegerField(null=True, blank=True)
    almacenamiento_gb = models.PositiveIntegerField(null=True, blank=True)
    direccion_mac = models.CharField(max_length=17, blank=True, default="")
    observaciones = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                models.functions.Lower("serial"),
                name="activo_serial_ci_unico",
            ),
            models.UniqueConstraint(
                models.functions.Lower("direccion_mac"),
                condition=models.Q(direccion_mac__gt=""),
                name="activo_mac_ci_unico_no_vacio",
            ),
        ]
        ordering = ["serial"]

    def __str__(self):
        return self.serial


class AsignacionActivo(BaseModel):
    activo = models.ForeignKey(Activo, on_delete=models.PROTECT, related_name="asignaciones")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="asignaciones_recibidas",
    )
    asignado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="asignaciones_realizadas",
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    observacion = models.TextField(blank=True, default="")

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Asignación de activo"
        verbose_name_plural = "Asignaciones de activos"
        ordering = ["-fecha_inicio", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["activo"],
                condition=models.Q(fecha_fin__isnull=True),
                name="asignacion_activo_abierta_unica",
            ),
            models.CheckConstraint(
                condition=models.Q(fecha_fin__isnull=True)
                | models.Q(fecha_fin__gte=models.F("fecha_inicio")),
                name="asignacion_fechas_validas",
            ),
        ]
        indexes = [
            models.Index(fields=["activo"], name="asignacion_activo_idx"),
            models.Index(fields=["usuario"], name="asignacion_usuario_idx"),
            models.Index(fields=["fecha_inicio"], name="asignacion_inicio_idx"),
        ]

    def __str__(self):
        return f"{self.activo.serial} - {self.usuario.nombre_completo}"

    @property
    def activa(self) -> bool:
        return self.fecha_fin is None

    @property
    def dias_asignado(self) -> int:
        fin = self.fecha_fin or timezone.localdate()
        return max((fin - self.fecha_inicio).days, 0)
