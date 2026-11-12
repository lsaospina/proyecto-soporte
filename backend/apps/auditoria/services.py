from .models import RegistroAuditoria


def registrar_evento(*, usuario=None, accion, entidad="", entidad_id="", ip=None):
    """Registra un evento de auditoría con una sola escritura."""
    return RegistroAuditoria.objects.create(
        usuario=usuario,
        accion=accion,
        entidad=entidad or "",
        entidad_id=entidad_id or "",
        ip=ip,
    )
