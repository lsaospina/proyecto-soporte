import re
from datetime import date

from django.db import IntegrityError, transaction

from apps.activos.models import Activo, EstadoActivo
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
