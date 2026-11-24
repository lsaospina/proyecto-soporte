from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, F, Q, Sum
from django.utils import timezone

from apps.activos.models import Activo, EstadoActivo
from apps.mantenimientos.models import (
    EstadoMantenimiento,
    Mantenimiento,
    SituacionMantenimiento,
    TipoMantenimiento,
)
from apps.mantenimientos.selectors import anotar_situacion, resumen_anual

DIAS_PROXIMOS = 14
DIAS_CORRECTIVOS = 30
LIMITE_LISTAS = 5

ESTADOS_VIGENTES = [
    (EstadoActivo.DISPONIBLE, "Disponible"),
    (EstadoActivo.ASIGNADO, "Asignado"),
    (EstadoActivo.EN_MANTENIMIENTO, "En mantenimiento"),
    (EstadoActivo.DADO_DE_BAJA, "Dado de baja"),
]

CAMPOS_MANTENIMIENTO = ("activo__modelo__marca", "activo__modelo__categoria", "tecnico")


def _monto(valor) -> str | None:
    if valor is None:
        return None
    return str(Decimal(valor).quantize(Decimal("0.01")))


def _activos_gestionables():
    return Activo.objects.filter(is_active=True).exclude(estado=EstadoActivo.DADO_DE_BAJA)


def _serializar_activo(activo: Activo) -> dict:
    return {
        "id": activo.id,
        "serial": activo.serial,
        "codigo_qr": activo.codigo_qr,
        "marca": activo.modelo.marca.nombre,
        "modelo": activo.modelo.nombre,
        "categoria": activo.modelo.categoria.nombre,
        "estado": activo.estado,
        "fecha_adquisicion": activo.fecha_adquisicion,
    }


def _serializar_mantenimiento(mantenimiento: Mantenimiento) -> dict:
    return {
        "id": mantenimiento.id,
        "activo_serial": mantenimiento.activo.serial,
        "activo_codigo": mantenimiento.activo.codigo_qr,
        "marca": mantenimiento.activo.modelo.marca.nombre,
        "modelo": mantenimiento.activo.modelo.nombre,
        "tipo": mantenimiento.tipo,
        "fecha_programada": mantenimiento.fecha_programada,
        "tecnico": mantenimiento.tecnico.nombre_completo if mantenimiento.tecnico else None,
        "observacion": mantenimiento.observacion,
    }


def _resumen_activos(*, incluir_valor: bool) -> dict:
    vigentes = Activo.objects.filter(is_active=True)
    gestionables = _activos_gestionables()

    conteo_estados = {
        row["estado"]: row["total"] for row in vigentes.values("estado").annotate(total=Count("id"))
    }
    total = sum(conteo_estados.values())
    operativos = conteo_estados.get(EstadoActivo.DISPONIBLE, 0) + conteo_estados.get(
        EstadoActivo.ASIGNADO, 0
    )

    por_categoria = list(
        gestionables.values(nombre=F("modelo__categoria__nombre"))
        .annotate(total=Count("id"))
        .order_by("-total", "nombre")
        .values("nombre", "total")[:8]
    )
    por_marca = list(
        gestionables.values(nombre=F("modelo__marca__nombre"))
        .annotate(total=Count("id"))
        .order_by("-total", "nombre")
        .values("nombre", "total")[:6]
    )

    ultimas = gestionables.select_related("modelo__marca", "modelo__categoria").order_by(
        "-fecha_adquisicion", "-id"
    )[:LIMITE_LISTAS]

    valor_total = None
    if incluir_valor:
        suma = gestionables.aggregate(total=Sum("valor_adquisicion"))["total"]
        valor_total = _monto(suma or Decimal("0"))

    return {
        "total": total,
        "operativos": operativos,
        "en_mantenimiento": conteo_estados.get(EstadoActivo.EN_MANTENIMIENTO, 0),
        "dados_de_baja": conteo_estados.get(EstadoActivo.DADO_DE_BAJA, 0),
        "inactivos": Activo.objects.filter(is_active=False).count(),
        "valor_total": valor_total,
        "por_estado": [
            {"estado": estado, "etiqueta": etiqueta, "total": conteo_estados.get(estado, 0)}
            for estado, etiqueta in ESTADOS_VIGENTES
        ],
        "por_categoria": por_categoria,
        "por_marca": por_marca,
        "ultimas_adquisiciones": [_serializar_activo(a) for a in ultimas],
    }


def _preventivos_del_anio(anio: int) -> dict:
    qs = anotar_situacion(
        Mantenimiento.objects.filter(tipo=TipoMantenimiento.PREVENTIVO, fecha_programada__year=anio)
    )
    totales = qs.aggregate(
        total=Count("id"),
        cancelados=Count("id", filter=Q(estado=EstadoMantenimiento.CANCELADO)),
        completados=Count("id", filter=Q(situacion_calc=SituacionMantenimiento.COMPLETADO)),
        vencidos=Count("id", filter=Q(situacion_calc=SituacionMantenimiento.VENCIDO)),
        incumplidos=Count("id", filter=Q(situacion_calc=SituacionMantenimiento.INCUMPLIDO)),
        pendientes=Count("id", filter=Q(situacion_calc=SituacionMantenimiento.PENDIENTE)),
    )
    agendados = totales["total"] - totales["cancelados"]
    porcentaje = round(totales["completados"] * 100 / agendados) if agendados else 0
    return {
        "total": totales["total"],
        "agendados": agendados,
        "cancelados": totales["cancelados"],
        "completados": totales["completados"],
        "vencidos": totales["vencidos"],
        "incumplidos": totales["incumplidos"],
        "pendientes": totales["pendientes"],
        "porcentaje_cumplimiento": porcentaje,
    }


def _proximos_mantenimientos(hoy: date) -> list[dict]:
    limite = hoy + timedelta(days=DIAS_PROXIMOS)
    qs = (
        anotar_situacion(
            Mantenimiento.objects.filter(
                tipo=TipoMantenimiento.PREVENTIVO,
                fecha_programada__gte=hoy,
                fecha_programada__lte=limite,
            ).select_related(*CAMPOS_MANTENIMIENTO)
        )
        .filter(situacion_calc=SituacionMantenimiento.PENDIENTE)
        .order_by("fecha_programada", "id")[:LIMITE_LISTAS]
    )
    return [
        {**_serializar_mantenimiento(m), "dias_restantes": (m.fecha_programada - hoy).days}
        for m in qs
    ]


def _mantenimientos_vencidos(hoy: date) -> list[dict]:
    qs = (
        anotar_situacion(
            Mantenimiento.objects.filter(
                tipo=TipoMantenimiento.PREVENTIVO,
                fecha_programada__lt=hoy,
            ).select_related(*CAMPOS_MANTENIMIENTO)
        )
        .filter(situacion_calc=SituacionMantenimiento.VENCIDO)
        .order_by("fecha_programada", "id")[:LIMITE_LISTAS]
    )
    return [
        {**_serializar_mantenimiento(m), "dias_atraso": (hoy - m.fecha_programada).days} for m in qs
    ]


def _correctivos_recientes(hoy: date) -> dict:
    desde = hoy - timedelta(days=DIAS_CORRECTIVOS)
    recientes = (
        Mantenimiento.objects.filter(tipo=TipoMantenimiento.CORRECTIVO)
        .select_related(*CAMPOS_MANTENIMIENTO)
        .order_by("-fecha_programada", "-id")[:LIMITE_LISTAS]
    )
    en_periodo = Mantenimiento.objects.filter(
        tipo=TipoMantenimiento.CORRECTIVO,
        fecha_programada__gte=desde,
        fecha_programada__lte=hoy,
    ).exclude(estado=EstadoMantenimiento.CANCELADO)
    costo_periodo = en_periodo.aggregate(total=Sum("costo"))["total"]
    return {
        "registrados_30_dias": en_periodo.count(),
        "costo_30_dias": _monto(costo_periodo or Decimal("0")),
        "recientes": [_serializar_mantenimiento(m) for m in recientes],
    }


def _activos_sin_preventivo(anio: int) -> dict:
    inicio = date(anio, 1, 1)
    fin = date(anio, 12, 31)
    con_preventivo = Mantenimiento.objects.filter(
        tipo=TipoMantenimiento.PREVENTIVO,
        fecha_programada__gte=inicio,
        fecha_programada__lte=fin,
    ).exclude(estado=EstadoMantenimiento.CANCELADO)
    sin_preventivo = (
        _activos_gestionables()
        .exclude(id__in=con_preventivo.values("activo_id"))
        .select_related("modelo__marca", "modelo__categoria")
        .order_by("serial")
    )
    return {
        "total": sin_preventivo.count(),
        "activos": [_serializar_activo(a) for a in sin_preventivo[:LIMITE_LISTAS]],
    }


def _resumen_mantenimientos(hoy: date, anio: int) -> dict:
    preventivos = _preventivos_del_anio(anio)
    correctivos = _correctivos_recientes(hoy)
    costo_anio = Mantenimiento.objects.filter(
        fecha_programada__year=anio, estado=EstadoMantenimiento.COMPLETADO
    ).aggregate(total=Sum("costo"))["total"]

    return {
        "preventivos_anio": preventivos,
        "mensual": resumen_anual(anio)["meses"],
        "proximos": _proximos_mantenimientos(hoy),
        "vencidos": _mantenimientos_vencidos(hoy),
        "correctivos": correctivos,
        "activos_sin_preventivo": _activos_sin_preventivo(anio),
        "costo_anio": _monto(costo_anio or Decimal("0")),
    }


def resumen_dashboard(*, hoy: date | None = None, incluir_mantenimientos: bool = True) -> dict:
    hoy = hoy or timezone.localdate()
    anio = hoy.year
    data = {
        "hoy": hoy,
        "anio": anio,
        "activos": _resumen_activos(incluir_valor=incluir_mantenimientos),
        "mantenimientos": None,
    }
    if incluir_mantenimientos:
        data["mantenimientos"] = _resumen_mantenimientos(hoy, anio)
    return data
