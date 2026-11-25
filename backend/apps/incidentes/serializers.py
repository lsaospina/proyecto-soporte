from rest_framework import serializers

from apps.activos.models import Activo
from apps.incidentes.models import Incidente, EstadoIncidente
from apps.usuarios.models import Usuario


class IncidenteSerializer(serializers.ModelSerializer):
    activo_serial = serializers.CharField(source="activo.serial", read_only=True)
    activo_codigo = serializers.CharField(source="activo.codigo_qr", read_only=True)
    modelo_nombre = serializers.CharField(source="activo.modelo.nombre", read_only=True)
    marca_nombre = serializers.CharField(source="activo.modelo.marca.nombre", read_only=True)
    reportado_por_nombre = serializers.CharField(
        source="reportado_por.nombre_completo", read_only=True
    )

    class Meta:
        model = Incidente
        fields = [
            "id",
            "activo",
            "activo_serial",
            "activo_codigo",
            "modelo_nombre",
            "marca_nombre",
            "reportado_por",
            "reportado_por_nombre",
            "fecha",
            "descripcion",
            "estado",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class IncidenteCreateSerializer(serializers.Serializer):
    activo = serializers.PrimaryKeyRelatedField(queryset=Activo.objects.all())
    descripcion = serializers.CharField()
    fecha = serializers.DateField(required=False)

    def validate_descripcion(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("La descripción es obligatoria.")
        return value.strip()


class CambiarEstadoIncidenteSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=EstadoIncidente.choices)
