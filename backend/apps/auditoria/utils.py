from django.conf import settings


def get_client_ip(request) -> str | None:
    """Obtiene la IP del cliente. Solo confía en X-Forwarded-For si TRUST_X_FORWARDED_FOR=True."""
    trust_forwarded = getattr(settings, "TRUST_X_FORWARDED_FOR", False)
    if trust_forwarded:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip() or None
    return request.META.get("REMOTE_ADDR") or None


def sanitizar_entidad_id(valor) -> str:
    """Devuelve el valor solo si contiene '@' y longitud <= 64; en caso contrario, cadena vacía."""
    if valor is None:
        return ""
    text = str(valor)
    if "@" in text and len(text) <= 64:
        return text
    return ""
