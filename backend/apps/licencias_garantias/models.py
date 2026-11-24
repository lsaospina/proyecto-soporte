from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from apps.common.models import BaseModel

DIAS_POR_VENCER = 30


class PeriodicidadRenovacion(models.TextChoices):
    MENSUAL = "MENSUAL", "Mensual"
    TRIMESTRAL = "TRIMESTRAL", "Trimestral"
    SEMESTRAL = "SEMESTRAL", "Semestral"
    ANUAL = "ANUAL", "Anual"
    BIENAL = "BIENAL", "Bienal"


class EstadoRenovacion(models.TextChoices):
    VIGENTE = "VIGENTE", "Vigente"
    POR_VENCER = "POR_VENCER", "Por vencer"
    VENCIDA = "VENCIDA", "Vencida"
    INACTIVA = "INACTIVA", "Inactiva"


class Proveedor(BaseModel):
    nombre = models.CharField(max_length=120)
    contacto = models.CharField(max_length=160, blank=True, default="")
    is_active = models.BooleanField(default=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        constraints = [
            models.UniqueConstraint(
                models.functions.Lower("nombre"),
                name="proveedor_nombre_ci_unico",
            ),
        ]
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Licencia(BaseModel):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name="licencias")
    servicio = models.CharField(max_length=160)
    periodicidad = models.CharField(
        max_length=20,
        choices=PeriodicidadRenovacion.choices,
        default=PeriodicidadRenovacion.ANUAL,
    )
    fecha_renovacion = models.DateField()
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Valor total a pagar en la renovación (COP).",
    )
    renovacion_automatica = models.BooleanField(default=False)
    medio_pago = models.CharField(max_length=160, blank=True, default="")
    cuenta_vinculada = models.CharField(max_length=160, blank=True, default="")
    responsable_uso = models.CharField(max_length=200, blank=True, default="")
    observacion = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Licencia"
        verbose_name_plural = "Licencias"
        ordering = ["fecha_renovacion", "servicio"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(cantidad__gte=1),
                name="licencia_cantidad_positiva",
            ),
            models.CheckConstraint(
                condition=models.Q(valor__isnull=True) | models.Q(valor__gte=0),
                name="licencia_valor_no_negativo",
            ),
        ]
        indexes = [
            models.Index(fields=["fecha_renovacion"], name="licencia_renovacion_idx"),
            models.Index(fields=["proveedor"], name="licencia_proveedor_idx"),
        ]

    def __str__(self):
        return f"{self.servicio} - {self.fecha_renovacion}"

    @property
    def dias_para_renovacion(self) -> int:
        return (self.fecha_renovacion - timezone.localdate()).days

    @property
    def estado_renovacion(self) -> str:
        if not self.is_active:
            return EstadoRenovacion.INACTIVA
        dias = self.dias_para_renovacion
        if dias < 0:
            return EstadoRenovacion.VENCIDA
        if dias <= DIAS_POR_VENCER:
            return EstadoRenovacion.POR_VENCER
        return EstadoRenovacion.VIGENTE

    @property
    def estado_renovacion_etiqueta(self) -> str:
        return EstadoRenovacion(self.estado_renovacion).label
