from django.db import IntegrityError, transaction

from apps.auditoria.services import registrar_evento
from apps.catalogos.models import Categoria, Marca, ModeloActivo, Sede, Ubicacion
from apps.catalogos.utils import normalizar_nombre
from apps.common.exceptions import ReglaDeNegocioError

MODELO_MAP = {
    "Sede": Sede,
    "Ubicacion": Ubicacion,
    "Categoria": Categoria,
    "Marca": Marca,
    "ModeloActivo": ModeloActivo,
}

HIJOS_ACTIVOS = {
    Sede: lambda i: i.ubicaciones.filter(is_active=True).exists(),
    Marca: lambda i: i.modelos.filter(is_active=True).exists(),
    Categoria: lambda i: i.modelos.filter(is_active=True).exists(),
}


def crear_catalogo(entidad, datos, actor, ip=None):
    model = MODELO_MAP[entidad]
    datos = dict(datos)
    if "nombre" in datos and datos["nombre"] is not None:
        datos["nombre"] = normalizar_nombre(datos["nombre"])
    with transaction.atomic():
        try:
            obj = model(**datos)
            obj._history_user = actor
            obj.save()
        except IntegrityError:
            raise ReglaDeNegocioError("Ya existe un registro con ese nombre.") from None
        registrar_evento(
            usuario=actor,
            accion="CATALOGO_CREADO",
            entidad=entidad,
            entidad_id=obj.pk,
            ip=ip,
        )
    return obj


def actualizar_catalogo(entidad, instancia, datos, actor, ip=None):
    datos = dict(datos)
    if "nombre" in datos and datos["nombre"] is not None:
        datos["nombre"] = normalizar_nombre(datos["nombre"])
    with transaction.atomic():
        for k, v in datos.items():
            setattr(instancia, k, v)
        instancia._history_user = actor
        try:
            instancia.save()
        except IntegrityError:
            raise ReglaDeNegocioError("Ya existe un registro con ese nombre.") from None
        registrar_evento(
            usuario=actor,
            accion="CATALOGO_ACTUALIZADO",
            entidad=entidad,
            entidad_id=instancia.pk,
            ip=ip,
        )
    return instancia


def inactivar_catalogo(entidad, instancia, actor, ip=None):
    model = MODELO_MAP[entidad]
    checker = HIJOS_ACTIVOS.get(model)
    if checker is not None and checker(instancia):
        raise ReglaDeNegocioError("No se puede inactivar: tiene elementos activos asociados.")
    with transaction.atomic():
        instancia.is_active = False
        instancia._history_user = actor
        instancia.save(update_fields=["is_active", "updated_at"])
        registrar_evento(
            usuario=actor,
            accion="CATALOGO_INACTIVADO",
            entidad=entidad,
            entidad_id=instancia.pk,
            ip=ip,
        )
    return instancia


def reactivar_catalogo(entidad, instancia, actor, ip=None):
    with transaction.atomic():
        instancia.is_active = True
        instancia._history_user = actor
        instancia.save(update_fields=["is_active", "updated_at"])
        registrar_evento(
            usuario=actor,
            accion="CATALOGO_REACTIVADO",
            entidad=entidad,
            entidad_id=instancia.pk,
            ip=ip,
        )
    return instancia
