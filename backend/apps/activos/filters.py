import django_filters

from apps.activos.models import Activo, AsignacionActivo, EstadoActivo


class ActivoFilter(django_filters.FilterSet):
    categoria = django_filters.NumberFilter(field_name="modelo__categoria_id")
    marca = django_filters.NumberFilter(field_name="modelo__marca_id")
    modelo = django_filters.NumberFilter(field_name="modelo_id")
    estado = django_filters.ChoiceFilter(choices=EstadoActivo.choices)
    estado_no = django_filters.ChoiceFilter(
        field_name="estado", choices=EstadoActivo.choices, exclude=True
    )
    fecha_desde = django_filters.DateFilter(field_name="fecha_adquisicion", lookup_expr="gte")
    fecha_hasta = django_filters.DateFilter(field_name="fecha_adquisicion", lookup_expr="lte")
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Activo
        fields = [
            "categoria",
            "marca",
            "modelo",
            "estado",
            "estado_no",
            "fecha_desde",
            "fecha_hasta",
            "is_active",
        ]


class AsignacionFilter(django_filters.FilterSet):
    activo = django_filters.NumberFilter(field_name="activo_id")
    usuario = django_filters.NumberFilter(field_name="usuario_id")
    abierta = django_filters.BooleanFilter(method="filtrar_abierta")
    fecha_desde = django_filters.DateFilter(field_name="fecha_inicio", lookup_expr="gte")
    fecha_hasta = django_filters.DateFilter(field_name="fecha_inicio", lookup_expr="lte")

    class Meta:
        model = AsignacionActivo
        fields = ["activo", "usuario", "abierta", "fecha_desde", "fecha_hasta"]

    def filtrar_abierta(self, queryset, name, value):
        return queryset.filter(fecha_fin__isnull=value)
