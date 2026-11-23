from django.db import models
from simple_history.models import HistoricalRecords

from apps.common.models import BaseModel


class Sede(BaseModel):
    nombre = models.CharField(max_length=120)
    direccion = models.CharField(max_length=255, blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                models.functions.Lower("nombre"),
                name="sede_nombre_ci_unico",
            ),
        ]
        ordering = ["nombre"]

    history = HistoricalRecords()

    def __str__(self):
        return self.nombre


class Ubicacion(BaseModel):
    sede = models.ForeignKey("catalogos.Sede", on_delete=models.PROTECT, related_name="ubicaciones")
    nombre = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                models.functions.Lower("nombre"),
                "sede",
                name="ubicacion_nombre_sede_ci_unico",
            ),
        ]
        ordering = ["sede__nombre", "nombre"]

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.sede.nombre} - {self.nombre}"


class Categoria(BaseModel):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                models.functions.Lower("nombre"),
                name="categoria_nombre_ci_unico",
            ),
        ]
        ordering = ["nombre"]

    history = HistoricalRecords()

    def __str__(self):
        return self.nombre


class Marca(BaseModel):
    nombre = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                models.functions.Lower("nombre"),
                name="marca_nombre_ci_unico",
            ),
        ]
        ordering = ["nombre"]

    history = HistoricalRecords()

    def __str__(self):
        return self.nombre


class ModeloActivo(BaseModel):
    marca = models.ForeignKey("catalogos.Marca", on_delete=models.PROTECT, related_name="modelos")
    categoria = models.ForeignKey(
        "catalogos.Categoria", on_delete=models.PROTECT, related_name="modelos"
    )
    nombre = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                "marca",
                models.functions.Lower("nombre"),
                name="modelo_nombre_marca_ci_unico",
            ),
        ]
        ordering = ["marca__nombre", "nombre"]

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.marca.nombre} {self.nombre}"
