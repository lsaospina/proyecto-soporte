import django_filters

from apps.licencias_garantias.models import EstadoRenovacion, Licencia, PeriodicidadRenovacion
from apps.licencias_garantias.selectors import filtrar_por_estado_renovacion


class LicenciaFilter(django_filters.FilterSet):
    proveedor = django_filters.NumberFilter(field_name="proveedor_id")
    periodicidad = django_filters.ChoiceFilter(choices=PeriodicidadRenovacion.choices)
    estado_renovacion = django_filters.ChoiceFilter(
        choices=EstadoRenovacion.choices, method="filtrar_estado_renovacion"
    )
    is_active = django_filters.BooleanFilter()
    fecha_desde = django_filters.DateFilter(field_name="fecha_renovacion", lookup_expr="gte")
    fecha_hasta = django_filters.DateFilter(field_name="fecha_renovacion", lookup_expr="lte")

    class Meta:
        model = Licencia
        fields = [
            "proveedor",
            "periodicidad",
            "estado_renovacion",
            "is_active",
            "fecha_desde",
            "fecha_hasta",
        ]

    def filtrar_estado_renovacion(self, queryset, name, value):
        return filtrar_por_estado_renovacion(queryset, value)
