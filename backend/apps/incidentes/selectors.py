from django.db.models import Q
from django.utils import timezone

from apps.incidentes.models import Incidente


def listar_incidentes(*, usuario=None, activo=None, estado=None, search=None):
    qs = Incidente.objects.select_related("activo__modelo__marca", "activo__modelo__categoria", "reportado_por")
    if usuario and usuario.rol == "USUARIO_RESPONSABLE":
        qs = qs.filter(reportado_por_id=usuario.id)
    if activo:
        qs = qs.filter(activo_id=activo)
    if estado:
        qs = qs.filter(estado=estado)
    if search:
        qs = qs.filter(
            Q(activo__serial__icontains=search)
            | Q(activo__codigo_qr__icontains=search)
            | Q(descripcion__icontains=search)
        )
    return qs.order_by("-fecha", "-id")


def obtener_incidente(pk):
    return (
        Incidente.objects.select_related(
            "activo__modelo__marca", "activo__modelo__categoria", "reportado_por"
        )
        .filter(pk=pk)
        .first()
    )
