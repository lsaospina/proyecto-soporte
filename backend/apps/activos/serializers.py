from rest_framework import serializers

from apps.activos.models import Activo


class ActivoSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(source="modelo.marca.nombre", read_only=True)
    categoria_nombre = serializers.CharField(source="modelo.categoria.nombre", read_only=True)
    modelo_nombre = serializers.CharField(source="modelo.nombre", read_only=True)

    class Meta:
        model = Activo
        fields = [
            "id",
            "serial",
            "modelo",
            "modelo_nombre",
            "marca_nombre",
            "categoria_nombre",
            "fecha_adquisicion",
            "valor_adquisicion",
            "estado",
            "codigo_qr",
            "procesador",
            "ram_gb",
            "almacenamiento_gb",
            "direccion_mac",
            "observaciones",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "estado",
            "codigo_qr",
            "marca_nombre",
            "categoria_nombre",
            "modelo_nombre",
            "created_at",
            "updated_at",
        ]


class ActivoCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activo
        fields = [
            "serial",
            "modelo",
            "fecha_adquisicion",
            "valor_adquisicion",
            "procesador",
            "ram_gb",
            "almacenamiento_gb",
            "direccion_mac",
            "observaciones",
        ]
