from django.contrib import admin

from apps.mantenimientos.models import Mantenimiento


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "activo",
        "tipo",
        "fecha_programada",
        "estado",
        "tecnico",
        "costo",
    )
    list_filter = ("tipo", "estado", "fecha_programada")
    search_fields = ("activo__serial", "activo__codigo_qr")
    readonly_fields = ("reprogramacion_de", "created_at", "updated_at")
