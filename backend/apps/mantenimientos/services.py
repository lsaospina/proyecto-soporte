from django.db import transaction
from django.utils import timezone

from apps.activos.models import EstadoActivo
from apps.auditoria.services import registrar_evento
from apps.common.exceptions import ReglaDeNegocioError
from apps.mantenimientos.models import (
    EstadoMantenimiento,
    Mantenimiento,
    SituacionMantenimiento,
    TipoMantenimiento,
)

SITUACIONES_COMPLETABLES = (SituacionMantenimiento.PENDIENTE, SituacionMantenimiento.VENCIDO)
SITUACIONES_CANCELABLES = (SituacionMantenimiento.PENDIENTE, SituacionMantenimiento.VENCIDO)


def _validar_fecha_no_pasada(fecha, campo="fecha_programada"):
    if fecha < timezone.localdate():
        raise ReglaDeNegocioError(
            "La fecha no puede ser anterior a hoy.",
            code="fecha_pasada",
            errors=[{"field": campo, "message": "La fecha no puede ser anterior a hoy."}],
        )


def programar_mantenimiento(datos, actor, ip=None):
    fecha = datos["fecha_programada"]
    _validar_fecha_no_pasada(fecha)
    activo = datos["activo"]
    if not activo.is_active:
        raise ReglaDeNegocioError("El activo está inactivo.", code="activo_inactivo")
    if activo.estado == EstadoActivo.DADO_DE_BAJA:
        raise ReglaDeNegocioError("El activo está dado de baja.", code="activo_dado_de_baja")

    with transaction.atomic():
        obj = Mantenimiento.objects.create(
            activo=activo,
            tipo=TipoMantenimiento.PREVENTIVO,
            fecha_programada=fecha,
            tecnico=datos.get("tecnico"),
            observacion=datos.get("observacion", ""),
            estado=EstadoMantenimiento.PROGRAMADO,
        )
        obj._history_user = actor
        obj.save(update_fields=["updated_at"])
        registrar_evento(
            usuario=actor,
            accion="MANTENIMIENTO_PROGRAMADO",
            entidad="Mantenimiento",
            entidad_id=obj.pk,
            ip=ip,
        )
    return obj


def completar_mantenimiento(instancia, datos, actor, ip=None):
    if instancia.situacion not in SITUACIONES_COMPLETABLES:
        raise ReglaDeNegocioError(
            "Solo se puede completar un mantenimiento pendiente o vencido.",
            code="completar_no_permitido",
        )
    fecha_realizacion = datos["fecha_realizacion"]
    if fecha_realizacion > timezone.localdate():
        raise ReglaDeNegocioError(
            "La fecha de realización no puede ser futura.",
            code="fecha_futura",
            errors=[{"field": "fecha_realizacion", "message": "La fecha no puede ser futura."}],
        )
    tecnico = datos["tecnico"]
    if tecnico is None or not tecnico.is_active:
        raise ReglaDeNegocioError(
            "Debe indicar un técnico activo.",
            code="tecnico_invalido",
            errors=[{"field": "tecnico", "message": "Seleccione un técnico activo."}],
        )
    costo = datos.get("costo")
    if costo is None or costo < 0:
        raise ReglaDeNegocioError(
            "El costo debe ser mayor o igual a cero.",
            code="costo_invalido",
            errors=[{"field": "costo", "message": "El costo debe ser mayor o igual a cero."}],
        )

    with transaction.atomic():
        instancia.estado = EstadoMantenimiento.COMPLETADO
        instancia.fecha_realizacion = fecha_realizacion
        instancia.tecnico = tecnico
        instancia.costo = costo
        instancia.observacion = datos.get("observacion", instancia.observacion)
        instancia._history_user = actor
        instancia.save()
        registrar_evento(
            usuario=actor,
            accion="MANTENIMIENTO_COMPLETADO",
            entidad="Mantenimiento",
            entidad_id=instancia.pk,
            ip=ip,
        )
    return instancia


def reprogramar_mantenimiento(instancia, nueva_fecha, actor, ip=None):
    if instancia.estado != EstadoMantenimiento.PROGRAMADO:
        raise ReglaDeNegocioError(
            "Solo se puede reprogramar un mantenimiento programado.",
            code="reprogramar_no_permitido",
        )
    if Mantenimiento.objects.filter(reprogramacion_de_id=instancia.pk).exists():
        raise ReglaDeNegocioError(
            "Este mantenimiento ya fue reprogramado.",
            code="ya_reprogramado",
        )
    _validar_fecha_no_pasada(nueva_fecha)

    situacion = instancia.situacion
    with transaction.atomic():
        if situacion == SituacionMantenimiento.PENDIENTE:
            instancia.fecha_programada = nueva_fecha
            instancia._history_user = actor
            instancia.save(update_fields=["fecha_programada", "updated_at"])
            registrar_evento(
                usuario=actor,
                accion="MANTENIMIENTO_REPROGRAMADO",
                entidad="Mantenimiento",
                entidad_id=instancia.pk,
                ip=ip,
            )
            return instancia, False

        if situacion == SituacionMantenimiento.VENCIDO:
            nuevo = Mantenimiento.objects.create(
                activo=instancia.activo,
                tipo=instancia.tipo,
                fecha_programada=nueva_fecha,
                tecnico=instancia.tecnico,
                observacion=instancia.observacion,
                estado=EstadoMantenimiento.PROGRAMADO,
                reprogramacion_de=instancia,
            )
            nuevo._history_user = actor
            nuevo.save(update_fields=["updated_at"])
            registrar_evento(
                usuario=actor,
                accion="MANTENIMIENTO_REPROGRAMADO",
                entidad="Mantenimiento",
                entidad_id=instancia.pk,
                ip=ip,
            )
            registrar_evento(
                usuario=actor,
                accion="MANTENIMIENTO_PROGRAMADO",
                entidad="Mantenimiento",
                entidad_id=nuevo.pk,
                ip=ip,
            )
            return nuevo, True

        raise ReglaDeNegocioError(
            "El mantenimiento no se puede reprogramar en su situación actual.",
            code="reprogramar_no_permitido",
        )


def cancelar_mantenimiento(instancia, motivo, actor, ip=None):
    if not motivo or not motivo.strip():
        raise ReglaDeNegocioError(
            "El motivo de cancelación es obligatorio.",
            code="motivo_requerido",
            errors=[{"field": "motivo", "message": "Indique el motivo de cancelación."}],
        )
    if instancia.situacion not in SITUACIONES_CANCELABLES:
        raise ReglaDeNegocioError(
            "El mantenimiento no se puede cancelar en su situación actual.",
            code="cancelar_no_permitido",
        )
    with transaction.atomic():
        instancia.estado = EstadoMantenimiento.CANCELADO
        instancia.motivo_cancelacion = motivo.strip()
        instancia._history_user = actor
        instancia.save(update_fields=["estado", "motivo_cancelacion", "updated_at"])
        registrar_evento(
            usuario=actor,
            accion="MANTENIMIENTO_CANCELADO",
            entidad="Mantenimiento",
            entidad_id=instancia.pk,
            ip=ip,
        )
    return instancia
