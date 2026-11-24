from django.db.models import (
    Case,
    CharField,
    Exists,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)
from django.utils import timezone

from apps.mantenimientos.models import (
    EstadoMantenimiento,
    Mantenimiento,
    SituacionMantenimiento,
    TipoMantenimiento,
)

CAMPOS_RELACIONADOS = ("activo__modelo__marca", "activo__modelo__categoria", "tecnico")


def anotar_situacion(qs):
    hoy = timezone.localdate()
    hijos = Mantenimiento.objects.filter(reprogramacion_de=OuterRef("pk"))
    return qs.annotate(
        tiene_reprogramacion=Exists(hijos),
        reprogramado_como_id_anotado=Subquery(hijos.values("id")[:1]),
    ).annotate(
        situacion_calc=Case(
            When(
                estado=EstadoMantenimiento.COMPLETADO, then=Value(SituacionMantenimiento.COMPLETADO)
            ),
            When(
                estado=EstadoMantenimiento.CANCELADO, then=Value(SituacionMantenimiento.CANCELADO)
            ),
            When(tiene_reprogramacion=True, then=Value(SituacionMantenimiento.INCUMPLIDO)),
            When(fecha_programada__lt=hoy, then=Value(SituacionMantenimiento.VENCIDO)),
            default=Value(SituacionMantenimiento.PENDIENTE),
            output_field=CharField(),
        )
    )


def listar_mantenimientos(
    *, anio=None, mes=None, situacion=None, tecnico=None, tipo=None, search=None
):
    qs = anotar_situacion(Mantenimiento.objects.select_related(*CAMPOS_RELACIONADOS))
    if tipo:
        qs = qs.filter(tipo=tipo)
    if anio:
        qs = qs.filter(fecha_programada__year=anio)
    if mes:
        qs = qs.filter(fecha_programada__month=mes)
    if tecnico:
        qs = qs.filter(tecnico_id=tecnico)
    if situacion:
        qs = qs.filter(situacion_calc=situacion)
    if search:
        qs = qs.filter(
            Q(activo__serial__icontains=search)
            | Q(activo__codigo_qr__icontains=search)
            | Q(activo__modelo__nombre__icontains=search)
            | Q(activo__modelo__marca__nombre__icontains=search)
        )
    return qs


def obtener_mantenimiento(pk):
    return (
        anotar_situacion(Mantenimiento.objects.select_related(*CAMPOS_RELACIONADOS))
        .filter(pk=pk)
        .first()
    )


def resumen_anual(anio):
    hoy = timezone.localdate()
    registros = list(
        anotar_situacion(
            Mantenimiento.objects.filter(
                fecha_programada__year=anio, tipo=TipoMantenimiento.PREVENTIVO
            ).select_related(*CAMPOS_RELACIONADOS)
        )
    )
    meses = []
    for mes in range(1, 13):
        items = [m for m in registros if m.fecha_programada.month == mes]
        agendados = [m for m in items if m.estado != EstadoMantenimiento.CANCELADO]
        completados = [m for m in items if m.situacion_calc == SituacionMantenimiento.COMPLETADO]
        vencidos = [m for m in items if m.situacion_calc == SituacionMantenimiento.VENCIDO]
        incumplidos = [m for m in items if m.situacion_calc == SituacionMantenimiento.INCUMPLIDO]
        total = len(agendados)
        porcentaje = round(len(completados) * 100 / total) if total else 0
        meses.append(
            {
                "mes": mes,
                "agendados": total,
                "completados": len(completados),
                "vencidos": len(vencidos),
                "incumplidos": len(incumplidos),
                "porcentaje_cumplimiento": porcentaje,
            }
        )
    return {"anio": anio, "hoy": hoy, "meses": meses}


def calendario_mensual(anio, mes):
    hoy = timezone.localdate()
    qs = anotar_situacion(
        Mantenimiento.objects.filter(
            fecha_programada__year=anio,
            fecha_programada__month=mes,
            tipo=TipoMantenimiento.PREVENTIVO,
        ).select_related(*CAMPOS_RELACIONADOS)
    ).order_by("fecha_programada", "id")
    return {"anio": anio, "mes": mes, "hoy": hoy, "mantenimientos": qs}
