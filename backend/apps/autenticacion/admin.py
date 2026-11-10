from django.contrib import admin

from .models import CodigoRecuperacion, DispositivoMFA


class CodigoRecuperacionInline(admin.TabularInline):
    model = CodigoRecuperacion
    extra = 0
    readonly_fields = ("codigo_hash", "usado_en", "created_at")
    can_delete = False


@admin.register(DispositivoMFA)
class DispositivoMFAAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "confirmado",
        "ultimo_paso_usado",
        "created_at",
        "updated_at",
    )
    list_filter = ("confirmado",)
    search_fields = ("usuario__email", "usuario__nombre_completo")
    readonly_fields = (
        "secreto_cifrado",
        "ultimo_paso_usado",
        "created_at",
        "updated_at",
    )
    inlines = [CodigoRecuperacionInline]
