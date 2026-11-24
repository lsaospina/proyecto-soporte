from rest_framework import serializers


class EstadoActivoResumenSerializer(serializers.Serializer):
    estado = serializers.CharField()
    etiqueta = serializers.CharField()
    total = serializers.IntegerField()


class GrupoActivoResumenSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    total = serializers.IntegerField()


class ActivoBreveSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    serial = serializers.CharField()
    codigo_qr = serializers.CharField()
    marca = serializers.CharField()
    modelo = serializers.CharField()
    categoria = serializers.CharField()
    estado = serializers.CharField()
    fecha_adquisicion = serializers.DateField()


class ActivosResumenSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    operativos = serializers.IntegerField()
    en_mantenimiento = serializers.IntegerField()
    dados_de_baja = serializers.IntegerField()
    inactivos = serializers.IntegerField()
    valor_total = serializers.DecimalField(
        max_digits=14, decimal_places=2, allow_null=True, required=False
    )
    por_estado = EstadoActivoResumenSerializer(many=True)
    por_categoria = GrupoActivoResumenSerializer(many=True)
    por_marca = GrupoActivoResumenSerializer(many=True)
    ultimas_adquisiciones = ActivoBreveSerializer(many=True)


class MantenimientoBreveSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    activo_serial = serializers.CharField()
    activo_codigo = serializers.CharField()
    marca = serializers.CharField()
    modelo = serializers.CharField()
    tipo = serializers.CharField()
    fecha_programada = serializers.DateField()
    tecnico = serializers.CharField(allow_null=True)
    observacion = serializers.CharField()
    dias_restantes = serializers.IntegerField(required=False)
    dias_atraso = serializers.IntegerField(required=False)


class PreventivosAnioSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    agendados = serializers.IntegerField()
    cancelados = serializers.IntegerField()
    completados = serializers.IntegerField()
    vencidos = serializers.IntegerField()
    incumplidos = serializers.IntegerField()
    pendientes = serializers.IntegerField()
    porcentaje_cumplimiento = serializers.IntegerField()


class MesResumenSerializer(serializers.Serializer):
    mes = serializers.IntegerField()
    agendados = serializers.IntegerField()
    completados = serializers.IntegerField()
    vencidos = serializers.IntegerField()
    incumplidos = serializers.IntegerField()
    porcentaje_cumplimiento = serializers.IntegerField()


class CorrectivosResumenSerializer(serializers.Serializer):
    registrados_30_dias = serializers.IntegerField()
    costo_30_dias = serializers.DecimalField(max_digits=14, decimal_places=2)
    recientes = MantenimientoBreveSerializer(many=True)


class ActivosSinPreventivoSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    activos = ActivoBreveSerializer(many=True)


class MantenimientosResumenSerializer(serializers.Serializer):
    preventivos_anio = PreventivosAnioSerializer()
    mensual = MesResumenSerializer(many=True)
    proximos = MantenimientoBreveSerializer(many=True)
    vencidos = MantenimientoBreveSerializer(many=True)
    correctivos = CorrectivosResumenSerializer()
    activos_sin_preventivo = ActivosSinPreventivoSerializer()
    costo_anio = serializers.DecimalField(max_digits=14, decimal_places=2)


class DashboardResumenSerializer(serializers.Serializer):
    hoy = serializers.DateField()
    anio = serializers.IntegerField()
    activos = ActivosResumenSerializer()
    mantenimientos = MantenimientosResumenSerializer(allow_null=True)
