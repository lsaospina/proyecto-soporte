from django.contrib import admin

from apps.catalogos.models import Categoria, Marca, ModeloActivo, Sede, Ubicacion


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ("nombre", "is_active", "created_at")
    search_fields = ("nombre",)


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "sede", "is_active", "created_at")
    search_fields = ("nombre", "sede__nombre")
    list_filter = ("sede", "is_active")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "is_active", "created_at")
    search_fields = ("nombre",)


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "is_active", "created_at")
    search_fields = ("nombre",)


@admin.register(ModeloActivo)
class ModeloActivoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "marca", "categoria", "is_active", "created_at")
    search_fields = ("nombre", "marca__nombre", "categoria__nombre")
    list_filter = ("marca", "categoria", "is_active")
