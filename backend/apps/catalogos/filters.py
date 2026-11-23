import django_filters

from apps.catalogos.models import Categoria, Marca, ModeloActivo, Sede, Ubicacion


class SedeFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter()
    search = django_filters.CharFilter(field_name="nombre", lookup_expr="icontains")

    class Meta:
        model = Sede
        fields = ["is_active", "search"]


class UbicacionFilter(django_filters.FilterSet):
    sede = django_filters.NumberFilter(field_name="sede_id")
    is_active = django_filters.BooleanFilter()
    search = django_filters.CharFilter(field_name="nombre", lookup_expr="icontains")

    class Meta:
        model = Ubicacion
        fields = ["sede", "is_active", "search"]


class CategoriaFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter()
    search = django_filters.CharFilter(field_name="nombre", lookup_expr="icontains")

    class Meta:
        model = Categoria
        fields = ["is_active", "search"]


class MarcaFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter()
    search = django_filters.CharFilter(field_name="nombre", lookup_expr="icontains")

    class Meta:
        model = Marca
        fields = ["is_active", "search"]


class ModeloActivoFilter(django_filters.FilterSet):
    marca = django_filters.NumberFilter(field_name="marca_id")
    categoria = django_filters.NumberFilter(field_name="categoria_id")
    is_active = django_filters.BooleanFilter()
    search = django_filters.CharFilter(field_name="nombre", lookup_expr="icontains")

    class Meta:
        model = ModeloActivo
        fields = ["marca", "categoria", "is_active", "search"]
