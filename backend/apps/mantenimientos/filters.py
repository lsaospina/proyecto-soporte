import django_filters

from apps.mantenimientos.models import Mantenimiento, SituacionMantenimiento


class MantenimientoFilter(django_filters.FilterSet):
    anio = django_filters.NumberFilter(field_name="fecha_programada", lookup_expr="year")
    mes = django_filters.NumberFilter(field_name="fecha_programada", lookup_expr="month")
    situacion = django_filters.ChoiceFilter(
        choices=SituacionMantenimiento.choices, method="filtrar_situacion"
    )
    tecnico = django_filters.NumberFilter(field_name="tecnico_id")

    class Meta:
        model = Mantenimiento
        fields = ["anio", "mes", "situacion", "tecnico"]

    def filtrar_situacion(self, queryset, name, value):
        return queryset.filter(situacion_calc=value)
