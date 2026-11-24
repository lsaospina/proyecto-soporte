import re
from datetime import date

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.activos.models import Activo, AsignacionActivo, EstadoActivo
from apps.activos.utils import normalizar_mac, normalizar_serial
from apps.auditoria.services import registrar_evento
from apps.common.exceptions import ReglaDeNegocioError

TRANSICIONES = {
    EstadoActivo.DISPONIBLE: {
        EstadoActivo.ASIGNADO,
        EstadoActivo.EN_MANTENIMIENTO,
        EstadoActivo.DADO_DE_BAJA,
    },
    EstadoActivo.ASIGNADO: {
        EstadoActivo.DISPONIBLE,
        EstadoActivo.EN_MANTENIMIENTO,
        EstadoActivo.DADO_DE_BAJA,
    },
    EstadoActivo.EN_MANTENIMIENTO: {EstadoActivo.DISPONIBLE, EstadoActivo.DADO_DE_BAJA},
    EstadoActivo.DADO_DE_BAJA: set(),
}


def _validar_mac(valor: str) -> str:
    v = normalizar_mac(valor)
    if v == "":
        return ""
    if not re.fullmatch(r"(?:[0-9A-F]{2}:){5}[0-9A-F]{2}", v):
        raise ReglaDeNegocioError(
            "Formato de MAC inválido. Use AA:BB:CC:DD:EE:FF.", code="mac_invalida"
        )
    return v


def generar_codigo_qr(activo_id: int) -> str:
    return f"AST-{date.today().year}-{activo_id:06d}"


def crear_activo(datos, actor, ip=None):
    datos = dict(datos)
    datos["serial"] = normalizar_serial(datos.get("serial", ""))
    if "direccion_mac" in datos and datos["direccion_mac"]:
        datos["direccion_mac"] = _validar_mac(datos["direccion_mac"])
    datos.pop("estado", None)
    datos.pop("codigo_qr", None)
    if isinstance(datos.get("fecha_adquisicion"), str):
        from datetime import datetime

        datos["fecha_adquisicion"] = datetime.strptime(
            datos["fecha_adquisicion"], "%Y-%m-%d"
        ).date()
    if datos.get("fecha_adquisicion") and datos["fecha_adquisicion"] > date.today():
        raise ReglaDeNegocioError(
            "La fecha de adquisición no puede ser futura.", code="fecha_futura"
        )
    with transaction.atomic():
        try:
            obj = Activo.objects.create(**datos, estado=EstadoActivo.DISPONIBLE)
        except IntegrityError:
            raise ReglaDeNegocioError("Serial o MAC duplicado.", code="duplicado") from None
        obj.codigo_qr = generar_codigo_qr(obj.pk)
        obj._history_user = actor
        obj.save(update_fields=["codigo_qr", "updated_at"])
        registrar_evento(
            usuario=actor, accion="ACTIVO_CREADO", entidad="Activo", entidad_id=obj.pk, ip=ip
        )
    return obj


def actualizar_activo(instancia, datos, actor, ip=None):
    datos = dict(datos)
    datos.pop("estado", None)
    datos.pop("codigo_qr", None)
    if "serial" in datos:
        datos["serial"] = normalizar_serial(datos["serial"])
    if "direccion_mac" in datos and datos["direccion_mac"]:
        datos["direccion_mac"] = _validar_mac(datos["direccion_mac"])
    if (
        "fecha_adquisicion" in datos
        and datos["fecha_adquisicion"]
        and datos["fecha_adquisicion"] > date.today()
    ):
        raise ReglaDeNegocioError(
            "La fecha de adquisición no puede ser futura.", code="fecha_futura"
        )
    with transaction.atomic():
        for k, v in datos.items():
            setattr(instancia, k, v)
        instancia._history_user = actor
        try:
            instancia.save()
        except IntegrityError:
            raise ReglaDeNegocioError("Serial o MAC duplicado.", code="duplicado") from None
        registrar_evento(
            usuario=actor,
            accion="ACTIVO_ACTUALIZADO",
            entidad="Activo",
            entidad_id=instancia.pk,
            ip=ip,
        )
    return instancia


def cambiar_estado(activo, nuevo_estado, actor, ip=None):
    if nuevo_estado not in EstadoActivo.values:
        raise ReglaDeNegocioError("Estado inválido.", code="estado_invalido")
    if nuevo_estado == EstadoActivo.ASIGNADO:
        raise ReglaDeNegocioError(
            "El estado ASIGNADO se gestiona con una asignación de responsable.",
            code="usar_asignacion",
        )
    if nuevo_estado not in TRANSICIONES.get(activo.estado, set()):
        raise ReglaDeNegocioError("Transición de estado no permitida.", code="transicion_invalida")
    with transaction.atomic():
        activo.estado = nuevo_estado
        activo._history_user = actor
        activo.save(update_fields=["estado", "updated_at"])
        registrar_evento(
            usuario=actor,
            accion="ACTIVO_ACTUALIZADO",
            entidad="Activo",
            entidad_id=activo.pk,
            ip=ip,
        )
    return activo


def inactivar_activo(instancia, actor, ip=None):
    if instancia.estado != EstadoActivo.DISPONIBLE:
        raise ReglaDeNegocioError(
            "Solo se puede inactivar un activo DISPONIBLE.", code="inactivacion_no_permitida"
        )
    with transaction.atomic():
        instancia.is_active = False
        instancia._history_user = actor
        instancia.save(update_fields=["is_active", "updated_at"])
        registrar_evento(
            usuario=actor,
            accion="ACTIVO_INACTIVADO",
            entidad="Activo",
            entidad_id=instancia.pk,
            ip=ip,
        )
    return instancia


def reactivar_activo(instancia, actor, ip=None):
    with transaction.atomic():
        instancia.is_active = True
        instancia._history_user = actor
        instancia.save(update_fields=["is_active", "updated_at"])
        registrar_evento(
            usuario=actor,
            accion="ACTIVO_REACTIVADO",
            entidad="Activo",
            entidad_id=instancia.pk,
            ip=ip,
        )
    return instancia


def _marcar_estado(activo, estado, actor):
    if activo.estado != estado:
        activo.estado = estado
        activo._history_user = actor
        activo.save(update_fields=["estado", "updated_at"])


def _validar_asignacion(activo, usuario, fecha_inicio):
    if not activo.is_active or activo.estado == EstadoActivo.DADO_DE_BAJA:
        raise ReglaDeNegocioError(
            "El activo no está disponible para asignación.", code="activo_no_asignable"
        )
    if activo.estado == EstadoActivo.EN_MANTENIMIENTO:
        raise ReglaDeNegocioError(
            "El activo está en mantenimiento y no se puede asignar.",
            code="activo_en_mantenimiento",
        )
    if usuario is None or not usuario.is_active:
        raise ReglaDeNegocioError(
            "Seleccione un colaborador activo.",
            code="usuario_invalido",
            errors=[{"field": "usuario", "message": "Seleccione un colaborador activo."}],
        )
    hoy = timezone.localdate()
    fecha = fecha_inicio or hoy
    if fecha > hoy:
        raise ReglaDeNegocioError(
            "La fecha de inicio no puede ser futura.",
            code="fecha_futura",
            errors=[{"field": "fecha_inicio", "message": "La fecha no puede ser futura."}],
        )
    if fecha < activo.fecha_adquisicion:
        raise ReglaDeNegocioError(
            "La fecha de inicio no puede ser anterior a la adquisición del activo.",
            code="fecha_anterior_adquisicion",
            errors=[
                {
                    "field": "fecha_inicio",
                    "message": "Debe ser igual o posterior a la fecha de adquisición.",
                }
            ],
        )
    return fecha


def asignar_activo(activo, usuario, fecha_inicio=None, observacion="", actor=None, ip=None):
    fecha = _validar_asignacion(activo, usuario, fecha_inicio)
    if AsignacionActivo.objects.filter(activo=activo, fecha_fin__isnull=True).exists():
        raise ReglaDeNegocioError(
            "El activo ya tiene un responsable asignado.", code="activo_ya_asignado"
        )
    with transaction.atomic():
        asignacion = AsignacionActivo(
            activo=activo,
            usuario=usuario,
            asignado_por=actor,
            fecha_inicio=fecha,
            observacion=observacion or "",
        )
        asignacion._history_user = actor
        asignacion.save()
        _marcar_estado(activo, EstadoActivo.ASIGNADO, actor)
        registrar_evento(
            usuario=actor,
            accion="ASIGNACION_CREADA",
            entidad="Asignacion",
            entidad_id=asignacion.pk,
            ip=ip,
        )
    return asignacion


def cerrar_asignacion(asignacion, fecha_fin=None, actor=None, ip=None):
    if asignacion.fecha_fin is not None:
        raise ReglaDeNegocioError("La asignación ya está cerrada.", code="asignacion_cerrada")
    hoy = timezone.localdate()
    fecha = fecha_fin or hoy
    if fecha > hoy:
        raise ReglaDeNegocioError(
            "La fecha de devolución no puede ser futura.",
            code="fecha_futura",
            errors=[{"field": "fecha_fin", "message": "La fecha no puede ser futura."}],
        )
    if fecha < asignacion.fecha_inicio:
        raise ReglaDeNegocioError(
            "La fecha de devolución no puede ser anterior al inicio de la asignación.",
            code="fecha_invalida",
            errors=[{"field": "fecha_fin", "message": "Debe ser igual o posterior al inicio."}],
        )
    with transaction.atomic():
        asignacion.fecha_fin = fecha
        asignacion._history_user = actor
        asignacion.save(update_fields=["fecha_fin", "updated_at"])
        if asignacion.activo.estado == EstadoActivo.ASIGNADO:
            _marcar_estado(asignacion.activo, EstadoActivo.DISPONIBLE, actor)
        registrar_evento(
            usuario=actor,
            accion="ASIGNACION_CERRADA",
            entidad="Asignacion",
            entidad_id=asignacion.pk,
            ip=ip,
        )
    return asignacion


def reasignar_activo(activo, usuario, fecha_inicio=None, observacion="", actor=None, ip=None):
    abierta = (
        AsignacionActivo.objects.select_related("activo")
        .filter(activo=activo, fecha_fin__isnull=True)
        .first()
    )
    if abierta is None:
        raise ReglaDeNegocioError(
            "El activo no tiene una asignación abierta para reasignar.",
            code="sin_asignacion_abierta",
        )
    fecha = fecha_inicio or timezone.localdate()
    with transaction.atomic():
        cerrar_asignacion(abierta, fecha_fin=fecha, actor=actor, ip=ip)
        return asignar_activo(
            abierta.activo,
            usuario,
            fecha_inicio=fecha,
            observacion=observacion,
            actor=actor,
            ip=ip,
        )
