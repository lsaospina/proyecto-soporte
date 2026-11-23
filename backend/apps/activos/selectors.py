from django.db.models import Q

from apps.activos.models import Activo


def listar_activos(
    *,
    categoria=None,
    marca=None,
    modelo=None,
    estado=None,
    fecha_desde=None,
    fecha_hasta=None,
    is_active=None,
    search=None,
):
    qs = Activo.objects.select_related("modelo__marca", "modelo__categoria")
    if categoria is not None:
        qs = qs.filter(modelo__categoria=categoria)
    if marca is not None:
        qs = qs.filter(modelo__marca=marca)
    if modelo is not None:
        qs = qs.filter(modelo=modelo)
    if estado:
        qs = qs.filter(estado=estado)
    if fecha_desde:
        qs = qs.filter(fecha_adquisicion__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha_adquisicion__lte=fecha_hasta)
    qs = qs.filter(is_active=is_active) if is_active is not None else qs.filter(is_active=True)
    if search:
        qs = qs.filter(
            Q(serial__icontains=search)
            | Q(codigo_qr__icontains=search)
            | Q(direccion_mac__icontains=search)
            | Q(modelo__marca__nombre__icontains=search)
            | Q(modelo__nombre__icontains=search)
        )
    return qs
