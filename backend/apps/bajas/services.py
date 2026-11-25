from django.db import transaction
from django.utils import timezone

from apps.activos.models import AsignacionActivo, EstadoActivo
from apps.auditoria.services import registrar_evento
from apps.bajas.models import Baja
from apps.common.exceptions import ReglaDeNegocioError


def registrar_baja(datos, actor, ip=None):
    activo = datos["activo"]
    if not activo.is_active:
        raise ReglaDeNegocioError("El activo está inactivo.", code="activo_inactivo")
    if Baja.objects.filter(activo=activo).exists() or activo.estado == EstadoActivo.DADO_DE_BAJA:
        raise ReglaDeNegocioError(
            "El activo ya tiene una baja registrada.",
            code="baja_duplicada",
        )
    if AsignacionActivo.objects.filter(activo=activo, fecha_fin__isnull=True).exists():
        raise ReglaDeNegocioError(
            "El activo tiene una asignación vigente; regístrala como devolución antes de darlo de baja.",
            code="activo_asignado",
        )

    motivo = (datos.get("motivo") or "").strip()
    if not motivo:
        raise ReglaDeNegocioError(
            "El motivo es obligatorio.",
            code="motivo_requerido",
            errors=[{"field": "motivo", "message": "Indique el motivo de la baja."}],
        )
    fecha = datos.get("fecha") or timezone.localdate()
    if fecha > timezone.localdate():
        raise ReglaDeNegocioError(
            "La fecha de baja no puede ser futura.",
            code="fecha_futura",
            errors=[{"field": "fecha", "message": "La fecha no puede ser futura."}],
        )

    with transaction.atomic():
        activo.estado = EstadoActivo.DADO_DE_BAJA
        activo._history_user = actor
        activo.save(update_fields=["estado", "updated_at"])

        obj = Baja(
            activo=activo,
            fecha=fecha,
            motivo=motivo,
            autorizado_por=actor,
            documento=datos.get("documento"),
        )
        obj._history_user = actor
        obj.save()

        registrar_evento(
            usuario=actor,
            accion="BAJA_REGISTRADA",
            entidad="Baja",
            entidad_id=obj.pk,
            ip=ip,
        )
    return obj
