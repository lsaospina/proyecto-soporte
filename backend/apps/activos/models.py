from django.core.validators import MinValueValidator
from django.db import models
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
