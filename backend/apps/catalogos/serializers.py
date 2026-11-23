from rest_framework import serializers

from apps.catalogos.models import Categoria, Marca, ModeloActivo, Sede, Ubicacion


class SedeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sede
        fields = ["id", "nombre", "direccion", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class UbicacionSerializer(serializers.ModelSerializer):
    sede_nombre = serializers.CharField(source="sede.nombre", read_only=True)

    class Meta:
        model = Ubicacion
        fields = ["id", "sede", "sede_nombre", "nombre", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "sede_nombre", "created_at", "updated_at"]


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ["id", "nombre", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ModeloActivoSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(source="marca.nombre", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)

    class Meta:
        model = ModeloActivo
        fields = [
            "id",
            "marca",
            "marca_nombre",
            "categoria",
            "categoria_nombre",
            "nombre",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "marca_nombre", "categoria_nombre", "created_at", "updated_at"]
