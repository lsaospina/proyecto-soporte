from rest_framework import serializers

from apps.activos.models import Activo
from apps.bajas.models import Baja
from apps.documentos.models import Documento


class BajaSerializer(serializers.ModelSerializer):
    activo_serial = serializers.CharField(source="activo.serial", read_only=True)
    activo_codigo = serializers.CharField(source="activo.codigo_qr", read_only=True)
    marca_nombre = serializers.CharField(source="activo.modelo.marca.nombre", read_only=True)
    modelo_nombre = serializers.CharField(source="activo.modelo.nombre", read_only=True)
    autorizado_por_nombre = serializers.CharField(
        source="autorizado_por.nombre_completo", read_only=True
    )
    documento_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Baja
        fields = [
            "id",
            "activo",
            "activo_serial",
            "activo_codigo",
            "marca_nombre",
            "modelo_nombre",
            "fecha",
            "motivo",
            "autorizado_por",
            "autorizado_por_nombre",
            "documento",
            "documento_nombre",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_documento_nombre(self, obj):
        return obj.documento.nombre if obj.documento else None


class BajaCreateSerializer(serializers.Serializer):
    activo = serializers.PrimaryKeyRelatedField(queryset=Activo.objects.all())
    fecha = serializers.DateField(required=False)
    motivo = serializers.CharField()
    documento = serializers.PrimaryKeyRelatedField(
        queryset=Documento.objects.all(), required=False, allow_null=True
    )

    def validate_motivo(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El motivo es obligatorio.")
        return value.strip()
