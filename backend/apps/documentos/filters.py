import django_filters

from apps.documentos.models import Documento, TipoDocumento


class DocumentoFilter(django_filters.FilterSet):
    activo = django_filters.NumberFilter(field_name="activo_id")
    tipo = django_filters.ChoiceFilter(choices=TipoDocumento.choices)

    class Meta:
        model = Documento
        fields = ["activo", "tipo"]
