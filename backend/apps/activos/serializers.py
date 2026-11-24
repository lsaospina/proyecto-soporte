from rest_framework import serializers

from apps.activos.models import Activo, AsignacionActivo
from apps.usuarios.models import Usuario


class ActivoSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(source="modelo.marca.nombre", read_only=True)
    categoria_nombre = serializers.CharField(source="modelo.categoria.nombre", read_only=True)
    modelo_nombre = serializers.CharField(source="modelo.nombre", read_only=True)
    responsable_actual = serializers.SerializerMethodField()

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
            "responsable_actual",
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
            "responsable_actual",
            "created_at",
            "updated_at",
        ]

    def get_responsable_actual(self, obj):
        if hasattr(obj, "responsable_actual"):
            return obj.responsable_actual
        abierta = obj.asignaciones.filter(fecha_fin__isnull=True).select_related("usuario").first()
        return abierta.usuario.nombre_completo if abierta else None


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


class AsignacionSerializer(serializers.ModelSerializer):
    activo_serial = serializers.CharField(source="activo.serial", read_only=True)
    activo_codigo = serializers.CharField(source="activo.codigo_qr", read_only=True)
    marca_nombre = serializers.CharField(source="activo.modelo.marca.nombre", read_only=True)
    modelo_nombre = serializers.CharField(source="activo.modelo.nombre", read_only=True)
    categoria_nombre = serializers.CharField(
        source="activo.modelo.categoria.nombre", read_only=True
    )
    usuario_nombre = serializers.CharField(source="usuario.nombre_completo", read_only=True)
    usuario_email = serializers.CharField(source="usuario.email", read_only=True)
    asignado_por_nombre = serializers.CharField(
        source="asignado_por.nombre_completo", read_only=True
    )
    activa = serializers.BooleanField(read_only=True)
    dias_asignado = serializers.IntegerField(read_only=True)

    class Meta:
        model = AsignacionActivo
        fields = [
            "id",
            "activo",
            "activo_serial",
            "activo_codigo",
            "marca_nombre",
            "modelo_nombre",
            "categoria_nombre",
            "usuario",
            "usuario_nombre",
            "usuario_email",
            "asignado_por",
            "asignado_por_nombre",
            "fecha_inicio",
            "fecha_fin",
            "activa",
            "dias_asignado",
            "observacion",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class AsignarActivoSerializer(serializers.Serializer):
    activo = serializers.PrimaryKeyRelatedField(queryset=Activo.objects.all())
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.filter(is_active=True))
    fecha_inicio = serializers.DateField(required=False, allow_null=True)
    observacion = serializers.CharField(required=False, allow_blank=True, default="")


class CerrarAsignacionSerializer(serializers.Serializer):
    fecha_fin = serializers.DateField(required=False, allow_null=True)


class UsuarioAsignableSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre_completo = serializers.CharField()
    email = serializers.EmailField()
    rol = serializers.CharField()


class ResumenAsignacionesSerializer(serializers.Serializer):
    hoy = serializers.DateField()
    activos_operativos = serializers.IntegerField()
    asignados = serializers.IntegerField()
    disponibles = serializers.IntegerField()
    en_mantenimiento = serializers.IntegerField()
    colaboradores = serializers.IntegerField()
    asignaciones_historicas = serializers.IntegerField()
