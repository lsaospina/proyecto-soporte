from django.contrib import admin

from apps.documentos.models import Documento


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo", "tipo", "subido_por", "created_at")
    list_filter = ("tipo",)
    search_fields = ("nombre", "activo__serial", "activo__codigo_qr")
    readonly_fields = [field.name for field in Documento._meta.fields]
