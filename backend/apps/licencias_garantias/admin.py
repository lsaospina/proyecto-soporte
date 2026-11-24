from django.contrib import admin

from apps.licencias_garantias.models import Licencia, Proveedor


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "contacto", "is_active")
    list_filter = ("is_active",)
    search_fields = ("nombre", "contacto")


@admin.register(Licencia)
class LicenciaAdmin(admin.ModelAdmin):
    list_display = (
        "servicio",
        "proveedor",
        "periodicidad",
        "fecha_renovacion",
        "valor",
        "renovacion_automatica",
        "is_active",
    )
    list_filter = ("periodicidad", "renovacion_automatica", "is_active", "proveedor")
    search_fields = ("servicio", "proveedor__nombre", "responsable_uso")
    date_hierarchy = "fecha_renovacion"
