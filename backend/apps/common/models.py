from django.db import models


class BaseModel(models.Model):
    """
    Modelo base abstracto que provee estampas de tiempo automáticas
    para todos los modelos de negocio.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
        help_text="Momento exacto en que se creó el registro.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización",
        help_text="Momento exacto de la última modificación.",
    )

    class Meta:
        abstract = True
