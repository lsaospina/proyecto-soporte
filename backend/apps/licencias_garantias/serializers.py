from decimal import Decimal

from rest_framework import serializers

from apps.catalogos.utils import normalizar_nombre
from apps.licencias_garantias.models import Licencia, PeriodicidadRenovacion


class ProveedorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()


class LicenciaSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source="proveedor.nombre", read_only=True)
    dias_para_renovacion = serializers.IntegerField(read_only=True)
    estado_renovacion = serializers.CharField(read_only=True)
    estado_renovacion_etiqueta = serializers.CharField(read_only=True)

    class Meta:
        model = Licencia
        fields = [
            "id",
            "proveedor",
            "proveedor_nombre",
            "servicio",
            "periodicidad",
            "fecha_renovacion",
            "cantidad",
            "valor",
            "renovacion_automatica",
            "medio_pago",
            "cuenta_vinculada",
            "responsable_uso",
            "observacion",
            "is_active",
            "dias_para_renovacion",
            "estado_renovacion",
            "estado_renovacion_etiqueta",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class LicenciaWriteSerializer(serializers.Serializer):
    proveedor = serializers.CharField(max_length=120)
    servicio = serializers.CharField(max_length=160)
    periodicidad = serializers.ChoiceField(
        choices=PeriodicidadRenovacion.choices,
        required=False,
        default=PeriodicidadRenovacion.ANUAL,
    )
    fecha_renovacion = serializers.DateField()
    cantidad = serializers.IntegerField(min_value=1, required=False, default=1)
    valor = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0"),
        required=False,
        allow_null=True,
    )
    renovacion_automatica = serializers.BooleanField(required=False, default=False)
    medio_pago = serializers.CharField(max_length=160, required=False, allow_blank=True, default="")
    cuenta_vinculada = serializers.CharField(
        max_length=160, required=False, allow_blank=True, default=""
    )
    responsable_uso = serializers.CharField(
        max_length=200, required=False, allow_blank=True, default=""
    )
    observacion = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_proveedor(self, value):
        nombre = normalizar_nombre(value)
        if not nombre:
            raise serializers.ValidationError("Ingrese el proveedor.")
        return nombre

    def validate_servicio(self, value):
        servicio = normalizar_nombre(value)
        if not servicio:
            raise serializers.ValidationError("Ingrese el servicio.")
        return servicio


class RenovarLicenciaSerializer(serializers.Serializer):
    fecha_renovacion = serializers.DateField()
    valor = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0"),
        required=False,
        allow_null=True,
    )


class PeriodicidadResumenSerializer(serializers.Serializer):
    periodicidad = serializers.CharField()
    total = serializers.IntegerField()


class ProveedorResumenSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    total = serializers.IntegerField()


class ResumenLicenciasSerializer(serializers.Serializer):
    hoy = serializers.DateField()
    total = serializers.IntegerField()
    activas = serializers.IntegerField()
    inactivas = serializers.IntegerField()
    por_vencer = serializers.IntegerField()
    vencidas = serializers.IntegerField()
    renovacion_automatica = serializers.IntegerField()
    costo_anual_estimado = serializers.DecimalField(max_digits=16, decimal_places=2)
    costo_por_vencer = serializers.DecimalField(max_digits=16, decimal_places=2)
    por_periodicidad = PeriodicidadResumenSerializer(many=True)
    por_proveedor = ProveedorResumenSerializer(many=True)
