from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from apps.activos.models import Activo
from apps.mantenimientos.models import Mantenimiento
from apps.usuarios.models import Usuario


class MantenimientoSerializer(serializers.ModelSerializer):
    activo_serial = serializers.CharField(source="activo.serial", read_only=True)
    activo_codigo = serializers.CharField(source="activo.codigo_qr", read_only=True)
    marca_nombre = serializers.CharField(source="activo.modelo.marca.nombre", read_only=True)
    modelo_nombre = serializers.CharField(source="activo.modelo.nombre", read_only=True)
    categoria_nombre = serializers.CharField(
        source="activo.modelo.categoria.nombre", read_only=True
    )
    tecnico_nombre = serializers.CharField(
        source="tecnico.nombre_completo", read_only=True, default=None
    )
    situacion = serializers.SerializerMethodField()
    es_evidencia = serializers.SerializerMethodField()
    reprogramado_como = serializers.SerializerMethodField()

    class Meta:
        model = Mantenimiento
        fields = [
            "id",
            "activo",
            "activo_serial",
            "activo_codigo",
            "marca_nombre",
            "modelo_nombre",
            "categoria_nombre",
            "tipo",
            "fecha_programada",
            "fecha_realizacion",
            "tecnico",
            "tecnico_nombre",
            "costo",
            "observacion",
            "motivo_cancelacion",
            "estado",
            "situacion",
            "es_evidencia",
            "reprogramado_como",
            "reprogramacion_de",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_situacion(self, obj):
        return obj.situacion

    def get_es_evidencia(self, obj):
        return obj.es_evidencia

    def get_reprogramado_como(self, obj):
        anotado = getattr(obj, "reprogramado_como_id_anotado", None)
        if anotado is not None:
            return anotado
        try:
            return obj.reprogramado_como.pk
        except ObjectDoesNotExist:
            return None


class MantenimientoCreateSerializer(serializers.Serializer):
    activo = serializers.PrimaryKeyRelatedField(queryset=Activo.objects.all())
    fecha_programada = serializers.DateField()
    tecnico = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.filter(is_active=True), required=False, allow_null=True
    )
    observacion = serializers.CharField(required=False, allow_blank=True, default="")


class CompletarMantenimientoSerializer(serializers.Serializer):
    fecha_realizacion = serializers.DateField()
    tecnico = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.filter(is_active=True))
    costo = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0"))
    observacion = serializers.CharField(required=False, allow_blank=True)


class ReprogramarMantenimientoSerializer(serializers.Serializer):
    fecha_programada = serializers.DateField()


class CancelarMantenimientoSerializer(serializers.Serializer):
    motivo = serializers.CharField()
