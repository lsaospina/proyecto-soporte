from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    model = Usuario
    list_display = (
        "email",
        "nombre_completo",
        "rol",
        "is_active",
        "esta_bloqueado",
        "intentos_fallidos",
    )
    list_filter = ("rol", "is_active", "is_staff")
    search_fields = ("email", "nombre_completo")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Información personal", {"fields": ("nombre_completo",)}),
        (
            "Permisos y Roles",
            {
                "fields": (
                    "rol",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Seguridad", {"fields": ("intentos_fallidos", "bloqueado_hasta")}),
        ("Fechas importantes", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "nombre_completo",
                    "rol",
                    "password",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
