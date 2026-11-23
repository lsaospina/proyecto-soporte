import re


def normalizar_serial(valor: str) -> str:
    return (valor or "").strip().upper()


def normalizar_mac(valor: str) -> str:
    v = (valor or "").strip().upper().replace("-", ":").replace(".", ":")
    # collapse any non-hex separators
    hex_chars = re.sub(r"[^0-9A-F]", "", v)
    if len(hex_chars) == 12:
        return ":".join(hex_chars[i : i + 2] for i in range(0, 12, 2))
    return v
