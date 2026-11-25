from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords

from apps.activos.models import Activo
from apps.common.models import BaseModel


class TipoDocumento(models.TextChoices):
    FACTURA = "FACTURA", "Factura"
    MANUAL = "MANUAL", "Manual"
    GARANTIA = "GARANTIA", "Garantía"
    CONTRATO = "CONTRATO", "Contrato"
    EVIDENCIA_MANTENIMIENTO = "EVIDENCIA_MANTENIMIENTO", "Evidencia de mantenimiento"
    OTRO = "OTRO", "Otro"


class Documento(BaseModel):
    activo = models.ForeignKey(
        Activo, on_delete=models.PROTECT, related_name="documentos"
    )
    nombre = models.CharField(max_length=150)
    tipo = models.CharField(
        max_length=30, choices=TipoDocumento.choices, default=TipoDocumento.OTRO
    )
    archivo = models.FileField(upload_to="documentos/%Y/%m/")
    descripcion = models.TextField(blank=True, default="")
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="documentos_subidos",
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["activo"], name="documento_activo_idx"),
            models.Index(fields=["tipo"], name="documento_tipo_idx"),
        ]

    def __str__(self):
        return self.nombre
