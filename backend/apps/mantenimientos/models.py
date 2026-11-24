from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from apps.activos.models import Activo
from apps.common.models import BaseModel


class TipoMantenimiento(models.TextChoices):
    PREVENTIVO = "PREVENTIVO", "Preventivo"
    CORRECTIVO = "CORRECTIVO", "Correctivo"


class EstadoMantenimiento(models.TextChoices):
    PROGRAMADO = "PROGRAMADO", "Programado"
    COMPLETADO = "COMPLETADO", "Completado"
    CANCELADO = "CANCELADO", "Cancelado"


class SituacionMantenimiento(models.TextChoices):
    PENDIENTE = "PENDIENTE", "Pendiente"
    COMPLETADO = "COMPLETADO", "Completado"
    VENCIDO = "VENCIDO", "Vencido"
    INCUMPLIDO = "INCUMPLIDO", "Incumplido"
    CANCELADO = "CANCELADO", "Cancelado"


class Mantenimiento(BaseModel):
    activo = models.ForeignKey(Activo, on_delete=models.PROTECT, related_name="mantenimientos")
    tipo = models.CharField(
        max_length=20, choices=TipoMantenimiento.choices, default=TipoMantenimiento.PREVENTIVO
    )
    fecha_programada = models.DateField()
    fecha_realizacion = models.DateField(null=True, blank=True)
    fecha_seguimiento = models.DateField(null=True, blank=True)
    tecnico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="mantenimientos_asignados",
    )
    costo = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    observacion = models.TextField(blank=True, default="")
    motivo_cancelacion = models.TextField(blank=True, default="")
    estado = models.CharField(
        max_length=20, choices=EstadoMantenimiento.choices, default=EstadoMantenimiento.PROGRAMADO
    )
    reprogramacion_de = models.OneToOneField(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reprogramado_como",
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"
        ordering = ["-fecha_programada", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(costo__isnull=True) | models.Q(costo__gte=0),
                name="mantenimiento_costo_no_negativo",
            ),
        ]
        indexes = [
            models.Index(fields=["fecha_programada"], name="mantenimiento_fecha_idx"),
            models.Index(fields=["estado"], name="mantenimiento_estado_idx"),
        ]

    def __str__(self):
        return f"{self.activo.serial} - {self.fecha_programada}"

    @property
    def situacion(self) -> str:
        if self.estado == EstadoMantenimiento.COMPLETADO:
            return SituacionMantenimiento.COMPLETADO
        if self.estado == EstadoMantenimiento.CANCELADO:
            return SituacionMantenimiento.CANCELADO
        tiene_reprogramacion = getattr(self, "tiene_reprogramacion", None)
        if tiene_reprogramacion is None:
            tiene_reprogramacion = Mantenimiento.objects.filter(
                reprogramacion_de_id=self.pk
            ).exists()
        if tiene_reprogramacion:
            return SituacionMantenimiento.INCUMPLIDO
        if self.fecha_programada < timezone.localdate():
            return SituacionMantenimiento.VENCIDO
        return SituacionMantenimiento.PENDIENTE

    @property
    def es_evidencia(self) -> bool:
        return self.situacion == SituacionMantenimiento.INCUMPLIDO
