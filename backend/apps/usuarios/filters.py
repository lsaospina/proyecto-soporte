import django_filters

from .models import RolChoices, Usuario


class UsuarioFilter(django_filters.FilterSet):
    rol = django_filters.ChoiceFilter(choices=RolChoices.choices)
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Usuario
        fields = ["rol", "is_active"]
