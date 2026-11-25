import os

from django.db import transaction

from apps.auditoria.services import registrar_evento
from apps.documentos.models import Documento, TipoDocumento


def subir_documento(datos, actor, ip=None):
    archivo = datos["archivo"]
    nombre = (datos.get("nombre") or os.path.basename(archivo.name)).strip()
    with transaction.atomic():
        obj = Documento(
            activo=datos["activo"],
            nombre=nombre,
            tipo=datos.get("tipo") or TipoDocumento.OTRO,
            archivo=archivo,
            descripcion=(datos.get("descripcion") or "").strip(),
            subido_por=actor,
        )
        obj._history_user = actor
        obj.save()
        registrar_evento(
            usuario=actor,
            accion="DOCUMENTO_SUBIDO",
            entidad="Documento",
            entidad_id=obj.pk,
            ip=ip,
        )
    return obj


def eliminar_documento(instancia, actor, ip=None):
    entidad_id = instancia.pk
    archivo = instancia.archivo
    with transaction.atomic():
        instancia.delete()
        registrar_evento(
            usuario=actor,
            accion="DOCUMENTO_ELIMINADO",
            entidad="Documento",
            entidad_id=entidad_id,
            ip=ip,
        )
    if archivo:
        archivo.delete(save=False)
