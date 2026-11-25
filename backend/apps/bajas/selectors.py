from django.db.models import Q

from apps.bajas.models import Baja


def listar_bajas(*, activo=None, search=None):
    qs = Baja.objects.select_related(
        "activo__modelo__marca",
        "activo__modelo__categoria",
        "autorizado_por",
        "documento",
    )
    if activo:
        qs = qs.filter(activo_id=activo)
    if search:
        qs = qs.filter(
            Q(activo__serial__icontains=search)
            | Q(activo__codigo_qr__icontains=search)
            | Q(motivo__icontains=search)
        )
    return qs.order_by("-fecha", "-id")


def obtener_baja(pk):
    return (
        Baja.objects.select_related(
            "activo__modelo__marca", "autorizado_por", "documento"
        )
        .filter(pk=pk)
        .first()
    )
