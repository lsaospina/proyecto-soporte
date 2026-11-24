from django.db.models import OuterRef, Q, Subquery
from django.utils import timezone

from apps.activos.models import Activo, AsignacionActivo, EstadoActivo
from apps.usuarios.models import Usuario


def _anotar_responsable(qs):
    abierta = AsignacionActivo.objects.filter(activo=OuterRef("pk"), fecha_fin__isnull=True)
    return qs.annotate(responsable_actual=Subquery(abierta.values("usuario__nombre_completo")[:1]))


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
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if search:
        qs = qs.filter(
            Q(serial__icontains=search)
            | Q(codigo_qr__icontains=search)
            | Q(direccion_mac__icontains=search)
            | Q(modelo__marca__nombre__icontains=search)
            | Q(modelo__nombre__icontains=search)
        )
    return _anotar_responsable(qs)


def listar_asignaciones(*, activo=None, usuario=None, abierta=None, search=None):
    qs = AsignacionActivo.objects.select_related(
        "activo__modelo__marca",
        "activo__modelo__categoria",
        "usuario",
        "asignado_por",
    )
    if activo is not None:
        qs = qs.filter(activo_id=activo)
    if usuario is not None:
        qs = qs.filter(usuario_id=usuario)
    if abierta is not None:
        qs = qs.filter(fecha_fin__isnull=abierta)
    if search:
        qs = qs.filter(
            Q(activo__serial__icontains=search)
            | Q(activo__codigo_qr__icontains=search)
            | Q(usuario__nombre_completo__icontains=search)
            | Q(usuario__email__icontains=search)
            | Q(activo__modelo__marca__nombre__icontains=search)
            | Q(activo__modelo__nombre__icontains=search)
        )
    return qs


def asignacion_abierta(activo_id):
    return listar_asignaciones(activo=activo_id, abierta=True).first()


def usuarios_asignables():
    return Usuario.objects.filter(is_active=True).order_by("nombre_completo", "email")


def resumen_asignaciones():
    operativos = Activo.objects.filter(is_active=True).exclude(estado=EstadoActivo.DADO_DE_BAJA)
    abiertas = AsignacionActivo.objects.filter(fecha_fin__isnull=True)
    return {
        "hoy": timezone.localdate(),
        "activos_operativos": operativos.count(),
        "asignados": abiertas.count(),
        "disponibles": operativos.filter(estado=EstadoActivo.DISPONIBLE).count(),
        "en_mantenimiento": operativos.filter(estado=EstadoActivo.EN_MANTENIMIENTO).count(),
        "colaboradores": abiertas.values("usuario_id").distinct().count(),
        "asignaciones_historicas": AsignacionActivo.objects.count(),
    }
