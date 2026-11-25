from django.conf import settings
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from apps.activos.models import Activo
from apps.common.models import BaseModel


class EstadoIncidente(models.TextChoices):
    REPORTADO = "REPORTADO", "Reportado"
    EN_PROCESO = "EN_PROCESO", "En proceso"
    RESUELTO = "RESUELTO", "Resuelto"
    CERRADO = "CERRADO", "Cerrado"
    CANCELADO = "CANCELADO", "Cancelado"


class Incidente(BaseModel):
    activo = models.ForeignKey(
        Activo, on_delete=models.PROTECT, related_name="incidentes"
    )
    reportado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="incidentes_reportados",
    )
    fecha = models.DateField(default=timezone.localdate)
    descripcion = models.TextField()
    estado = models.CharField(
        max_length=20, choices=EstadoIncidente.choices, default=EstadoIncidente.REPORTADO
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Incidente"
        verbose_name_plural = "Incidentes"
        ordering = ["-fecha", "-id"]
        indexes = [
            models.Index(fields=["fecha"], name="incidente_fecha_idx"),
            models.Index(fields=["estado"], name="incidente_estado_idx"),
            models.Index(fields=["activo"], name="incidente_activo_idx"),
        ]

    def __str__(self):
        return f"{self.activo.serial} - {self.fecha} - {self.get_estado_display()}"
