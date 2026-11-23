def normalizar_nombre(valor: str) -> str:
    return " ".join((valor or "").strip().split())
