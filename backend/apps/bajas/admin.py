from django.contrib import admin

from apps.bajas.models import Baja


@admin.register(Baja)
class BajaAdmin(admin.ModelAdmin):
    list_display = ("activo", "fecha", "autorizado_por", "documento")
    search_fields = ("activo__serial", "activo__codigo_qr", "motivo")
    readonly_fields = [field.name for field in Baja._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
