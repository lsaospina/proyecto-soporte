from django.contrib import admin

from apps.activos.models import Activo, AsignacionActivo


@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):
    list_display = ("serial", "codigo_qr", "modelo", "estado", "is_active")
    list_filter = ("estado", "is_active")
    search_fields = ("serial", "codigo_qr", "direccion_mac")
    readonly_fields = ("estado", "codigo_qr", "created_at", "updated_at")


@admin.register(AsignacionActivo)
class AsignacionActivoAdmin(admin.ModelAdmin):
    list_display = ("activo", "usuario", "fecha_inicio", "fecha_fin", "asignado_por")
    list_filter = ("fecha_fin",)
    search_fields = ("activo__serial", "usuario__nombre_completo")
    readonly_fields = [field.name for field in AsignacionActivo._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
