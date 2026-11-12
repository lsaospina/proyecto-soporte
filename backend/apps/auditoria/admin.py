from django.contrib import admin

from .models import RegistroAuditoria


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "accion", "usuario", "entidad", "entidad_id", "ip")
    list_filter = ("accion", "fecha")
    search_fields = ("entidad", "entidad_id", "ip", "usuario__email")
    readonly_fields = (
        "usuario",
        "accion",
        "entidad",
        "entidad_id",
        "fecha",
        "ip",
        "created_at",
        "updated_at",
    )
    ordering = ("-fecha",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
