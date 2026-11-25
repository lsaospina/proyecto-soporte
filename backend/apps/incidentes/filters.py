import django_filters

from apps.incidentes.models import Incidente, EstadoIncidente


class IncidenteFilter(django_filters.FilterSet):
    estado = django_filters.ChoiceFilter(choices=EstadoIncidente.choices)
    activo = django_filters.NumberFilter(field_name="activo_id")
    reportado_por = django_filters.NumberFilter(field_name="reportado_por_id")

    class Meta:
        model = Incidente
        fields = ["estado", "activo", "reportado_por"]
