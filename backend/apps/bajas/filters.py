import django_filters

from apps.bajas.models import Baja


class BajaFilter(django_filters.FilterSet):
    activo = django_filters.NumberFilter(field_name="activo_id")
    fecha_desde = django_filters.DateFilter(field_name="fecha", lookup_expr="gte")
    fecha_hasta = django_filters.DateFilter(field_name="fecha", lookup_expr="lte")

    class Meta:
        model = Baja
        fields = ["activo", "fecha_desde", "fecha_hasta"]
