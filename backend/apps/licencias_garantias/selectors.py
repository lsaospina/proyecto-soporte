from datetime import timedelta
from decimal import Decimal

from django.db.models import Case, Count, DecimalField, ExpressionWrapper, F, Sum, Value, When
from django.utils import timezone

from apps.licencias_garantias.models import (
    DIAS_POR_VENCER,
    EstadoRenovacion,
    Licencia,
    PeriodicidadRenovacion,
    Proveedor,
)

FACTORES_ANUALES = {
    PeriodicidadRenovacion.MENSUAL: Decimal("12"),
    PeriodicidadRenovacion.TRIMESTRAL: Decimal("4"),
    PeriodicidadRenovacion.SEMESTRAL: Decimal("2"),
    PeriodicidadRenovacion.ANUAL: Decimal("1"),
    PeriodicidadRenovacion.BIENAL: Decimal("0.5"),
}


def _monto(valor) -> str:
    return str(Decimal(valor or 0).quantize(Decimal("0.01")))


def _expresion_costo_anual():
    factor = Case(
        *[
            When(periodicidad=periodicidad, then=Value(factor))
            for periodicidad, factor in FACTORES_ANUALES.items()
        ],
        default=Value(Decimal("1")),
        output_field=DecimalField(max_digits=6, decimal_places=2),
    )
    return ExpressionWrapper(
        F("valor") * factor, output_field=DecimalField(max_digits=16, decimal_places=2)
    )


def listar_licencias():
    return Licencia.objects.select_related("proveedor")


def listar_proveedores():
    return Proveedor.objects.filter(is_active=True).order_by("nombre")


def filtrar_por_estado_renovacion(qs, estado):
    hoy = timezone.localdate()
    limite = hoy + timedelta(days=DIAS_POR_VENCER)
    if estado == EstadoRenovacion.INACTIVA:
        return qs.filter(is_active=False)
    if estado == EstadoRenovacion.VENCIDA:
        return qs.filter(is_active=True, fecha_renovacion__lt=hoy)
    if estado == EstadoRenovacion.POR_VENCER:
        return qs.filter(is_active=True, fecha_renovacion__gte=hoy, fecha_renovacion__lte=limite)
    return qs.filter(is_active=True, fecha_renovacion__gt=limite)


def resumen_licencias(hoy=None):
    hoy = hoy or timezone.localdate()
    limite = hoy + timedelta(days=DIAS_POR_VENCER)

    licencias = Licencia.objects.all()
    activas = licencias.filter(is_active=True)
    por_vencer = activas.filter(fecha_renovacion__gte=hoy, fecha_renovacion__lte=limite)
    vencidas = activas.filter(fecha_renovacion__lt=hoy)

    costo_anual = activas.aggregate(total=Sum(_expresion_costo_anual()))["total"]
    costo_por_vencer = por_vencer.aggregate(total=Sum("valor"))["total"]

    por_periodicidad = list(
        activas.values("periodicidad").annotate(total=Count("id")).order_by("periodicidad")
    )
    por_proveedor = list(
        activas.values(nombre=F("proveedor__nombre"))
        .annotate(total=Count("id"))
        .order_by("-total", "nombre")[:5]
    )

    return {
        "hoy": hoy,
        "total": licencias.count(),
        "activas": activas.count(),
        "inactivas": licencias.filter(is_active=False).count(),
        "por_vencer": por_vencer.count(),
        "vencidas": vencidas.count(),
        "renovacion_automatica": activas.filter(renovacion_automatica=True).count(),
        "costo_anual_estimado": _monto(costo_anual),
        "costo_por_vencer": _monto(costo_por_vencer),
        "por_periodicidad": por_periodicidad,
        "por_proveedor": por_proveedor,
    }
