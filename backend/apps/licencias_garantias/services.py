from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.auditoria.services import registrar_evento
from apps.catalogos.utils import normalizar_nombre
from apps.common.exceptions import ReglaDeNegocioError
from apps.licencias_garantias.models import Licencia, Proveedor


def resolver_proveedor(nombre, actor=None):
    """Devuelve el proveedor existente (comparación sin mayúsculas) o lo crea."""
    nombre = normalizar_nombre(nombre)
    existente = Proveedor.objects.filter(nombre__iexact=nombre).first()
    if existente:
        if not existente.is_active:
            existente.is_active = True
            existente._history_user = actor
            existente.save(update_fields=["is_active", "updated_at"])
        return existente
    try:
        proveedor = Proveedor(nombre=nombre)
        proveedor._history_user = actor
        proveedor.save()
        return proveedor
    except IntegrityError:
        return Proveedor.objects.get(nombre__iexact=nombre)


def crear_licencia(datos, actor, ip=None):
    datos = dict(datos)
    nombre_proveedor = datos.pop("proveedor")
    with transaction.atomic():
        proveedor = resolver_proveedor(nombre_proveedor, actor)
        licencia = Licencia(proveedor=proveedor, **datos)
        licencia._history_user = actor
        licencia.save()
        registrar_evento(
            usuario=actor,
            accion="LICENCIA_CREADA",
            entidad="Licencia",
            entidad_id=licencia.pk,
            ip=ip,
        )
    return licencia


def actualizar_licencia(instancia, datos, actor, ip=None):
    datos = dict(datos)
    nombre_proveedor = datos.pop("proveedor", None)
    with transaction.atomic():
        if nombre_proveedor is not None:
            instancia.proveedor = resolver_proveedor(nombre_proveedor, actor)
        for campo, valor in datos.items():
            setattr(instancia, campo, valor)
        instancia._history_user = actor
        instancia.save()
        registrar_evento(
            usuario=actor,
            accion="LICENCIA_ACTUALIZADA",
            entidad="Licencia",
            entidad_id=instancia.pk,
            ip=ip,
        )
    return instancia


def inactivar_licencia(instancia, actor, ip=None):
    if instancia.is_active:
        with transaction.atomic():
            instancia.is_active = False
            instancia._history_user = actor
            instancia.save(update_fields=["is_active", "updated_at"])
            registrar_evento(
                usuario=actor,
                accion="LICENCIA_INACTIVADA",
                entidad="Licencia",
                entidad_id=instancia.pk,
                ip=ip,
            )
    return instancia


def reactivar_licencia(instancia, actor, ip=None):
    if not instancia.is_active:
        with transaction.atomic():
            instancia.is_active = True
            instancia._history_user = actor
            instancia.save(update_fields=["is_active", "updated_at"])
            registrar_evento(
                usuario=actor,
                accion="LICENCIA_REACTIVADA",
                entidad="Licencia",
                entidad_id=instancia.pk,
                ip=ip,
            )
    return instancia


def renovar_licencia(instancia, fecha_renovacion, valor, actor, ip=None):
    if not instancia.is_active:
        raise ReglaDeNegocioError(
            "No se puede renovar una licencia inactiva. Reactívela primero.",
            code="licencia_inactiva",
        )
    if fecha_renovacion < timezone.localdate():
        raise ReglaDeNegocioError(
            "La nueva fecha de renovación debe ser hoy o posterior.",
            code="fecha_pasada",
            errors=[
                {
                    "field": "fecha_renovacion",
                    "message": "La fecha debe ser hoy o posterior.",
                }
            ],
        )
    with transaction.atomic():
        instancia.fecha_renovacion = fecha_renovacion
        if valor is not None:
            instancia.valor = valor
        instancia._history_user = actor
        instancia.save(update_fields=["fecha_renovacion", "valor", "updated_at"])
        registrar_evento(
            usuario=actor,
            accion="LICENCIA_RENOVADA",
            entidad="Licencia",
            entidad_id=instancia.pk,
            ip=ip,
        )
    return instancia
