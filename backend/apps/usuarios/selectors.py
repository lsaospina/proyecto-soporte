from django.db.models import Q

from .models import Usuario
from .utils import normalizar_email


def listar_usuarios(*, rol=None, is_active=None, search=None):
    queryset = Usuario.objects.all().select_related("dispositivo_mfa")
    if rol:
        queryset = queryset.filter(rol=rol)
    if is_active is not None:
        if isinstance(is_active, str):
            is_active = is_active.lower() in {"true", "1", "yes"}
        queryset = queryset.filter(is_active=is_active)
    if search:
        search = search.strip()
        if "@" in search:
            queryset = queryset.filter(
                Q(email__iexact=normalizar_email(search)) | Q(nombre_completo__icontains=search)
            )
        else:
            queryset = queryset.filter(
                Q(email__icontains=search) | Q(nombre_completo__icontains=search)
            )
    return queryset.order_by("email")
