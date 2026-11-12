def normalizar_email(email: str) -> str:
    """Normaliza correo: strip + lower para comparaciones y unicidad case-insensitive."""
    if email is None:
        return ""
    return email.strip().lower()
