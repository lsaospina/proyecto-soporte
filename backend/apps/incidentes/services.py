from django.db import transaction
from django.utils import timezone

from apps.auditoria.services import registrar_evento
from apps.common.exceptions import ReglaDeNegocioError
from apps.incidentes.models import EstadoIncidente, Incidente


ESTADOS_EDITABLES = (
    EstadoIncidente.REPORTADO,
    EstadoIncidente.EN_PROCESO,
    EstadoIncidente.RESUELTO,
    EstadoIncidente.CERRADO,
    EstadoIncidente.CANCELADO,
)


def registrar_incidente(datos, actor, ip=None):
    activo = datos["activo"]
    if not activo.is_active:
        raise ReglaDeNegocioError("El activo está inactivo.", code="activo_inactivo")
    if activo.estado == "DADO_DE_BAJA":
        raise ReglaDeNegocioError(
            "El activo está dado de baja.", code="activo_dado_de_baja"
        )
    descripcion = (datos.get("descripcion") or "").strip()
    if not descripcion:
        raise ReglaDeNegocioError(
            "La descripción es obligatoria.",
            code="descripcion_requerida",
            errors=[{"field": "descripcion", "message": "La descripción es obligatoria."}],
        )
    fecha = datos.get("fecha") or timezone.localdate()

    with transaction.atomic():
        obj = Incidente(
            activo=activo,
            reportado_por=actor,
            fecha=fecha,
            descripcion=descripcion,
            estado=EstadoIncidente.REPORTADO,
        )
        obj._history_user = actor
        obj.save()
        registrar_evento(
            usuario=actor,
            accion="INCIDENTE_REPORTADO",
            entidad="Incidente",
            entidad_id=obj.pk,
            ip=ip,
        )
    return obj


def cambiar_estado_incidente(instancia, nuevo_estado, actor, ip=None):
    if nuevo_estado not in ESTADOS_EDITABLES:
        raise ReglaDeNegocioError(
            "Estado no válido.", code="estado_invalido"
        )
    if instancia.estado == nuevo_estado:
        raise ReglaDeNegocioError(
            "El incidente ya tiene ese estado.",
            code="estado_duplicado",
        )
    if instancia.estado in (EstadoIncidente.CERRADO, EstadoIncidente.CANCELADO):
        raise ReglaDeNegocioError(
            "No se puede cambiar el estado de un incidente cerrado o cancelado.",
            code="incidente_cerrado",
        )

    with transaction.atomic():
        instancia.estado = nuevo_estado
        instancia._history_user = actor
        instancia.save(update_fields=["estado", "updated_at"])
        registrar_evento(
            usuario=actor,
            accion=f"INCIDENTE_ESTADO_CAMBIADO_{nuevo_estado}",
            entidad="Incidente",
            entidad_id=instancia.pk,
            ip=ip,
        )
    return instancia
