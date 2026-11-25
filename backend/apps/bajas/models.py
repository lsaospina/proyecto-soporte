from django.conf import settings
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from apps.activos.models import Activo
from apps.common.models import BaseModel
from apps.documentos.models import Documento


class Baja(BaseModel):
    activo = models.OneToOneField(
        Activo, on_delete=models.PROTECT, related_name="baja"
    )
    fecha = models.DateField(default=timezone.localdate)
    motivo = models.TextField()
    autorizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="bajas_autorizadas",
    )
    documento = models.ForeignKey(
        Documento,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="bajas",
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Baja"
        verbose_name_plural = "Bajas"
        ordering = ["-fecha", "-id"]
        indexes = [
            models.Index(fields=["fecha"], name="baja_fecha_idx"),
        ]

    def __str__(self):
        return f"Baja {self.activo.serial} ({self.fecha})"
