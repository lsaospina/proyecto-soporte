from django.db.models import Q

from apps.documentos.models import Documento


def listar_documentos(*, activo=None, tipo=None, search=None):
    qs = Documento.objects.select_related(
        "activo__modelo__marca", "subido_por"
    )
    if activo:
        qs = qs.filter(activo_id=activo)
    if tipo:
        qs = qs.filter(tipo=tipo)
    if search:
        qs = qs.filter(
            Q(nombre__icontains=search)
            | Q(descripcion__icontains=search)
            | Q(activo__serial__icontains=search)
            | Q(activo__codigo_qr__icontains=search)
        )
    return qs.order_by("-created_at", "-id")


def obtener_documento(pk):
    return (
        Documento.objects.select_related("activo", "subido_por").filter(pk=pk).first()
    )
