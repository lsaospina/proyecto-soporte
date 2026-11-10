import secrets
from datetime import datetime

import pyotp
from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone

from apps.common.exceptions import ReglaDeNegocioError


def get_fernet(key: str | None = None) -> Fernet:
    """Retorna una instancia de Fernet utilizando la clave configurada."""
    fernet_key = key or getattr(settings, "MFA_ENCRYPTION_KEY", "")
    if not fernet_key:
        raise ReglaDeNegocioError(
            "MFA_ENCRYPTION_KEY no está configurada en las variables de entorno.",
            code="mfa_key_missing",
        )
    try:
        return Fernet(fernet_key.encode() if isinstance(fernet_key, str) else fernet_key)
    except Exception as exc:
        raise ReglaDeNegocioError(
            "MFA_ENCRYPTION_KEY no es una clave Fernet válida (debe ser base64 url-safe de 32 bytes).",
            code="mfa_key_invalid",
        ) from exc


def cifrar_secreto(secreto: str, key: str | None = None) -> str:
    """Cifra un secreto TOTP en texto plano usando Fernet."""
    f = get_fernet(key)
    return f.encrypt(secreto.encode("utf-8")).decode("utf-8")


def descifrar_secreto(secreto_cifrado: str, key: str | None = None) -> str:
    """Descifra un secreto TOTP cifrado con Fernet."""
    f = get_fernet(key)
    return f.decrypt(secreto_cifrado.encode("utf-8")).decode("utf-8")


def generar_secreto_totp() -> str:
    """Genera un nuevo secreto TOTP aleatorio en base32 (160 bits / 32 caracteres)."""
    return pyotp.random_base32()


def obtener_uri_totp(secreto: str, email: str, issuer: str | None = None) -> str:
    """
    Retorna la URI otpauth:// estándar compatible con Google Authenticator,
    Microsoft Authenticator, etc. El frontend se encarga de renderizar el QR.
    """
    issuer_name = issuer or getattr(settings, "MFA_ISSUER", "InventarioSoporte")
    totp = pyotp.TOTP(secreto, interval=30, digits=6)
    return totp.provisioning_uri(name=email, issuer_name=issuer_name)


def verificar_totp(
    secreto: str,
    codigo: str,
    ultimo_paso_usado: int | None = None,
    at_time: datetime | None = None,
) -> tuple[bool, int | None]:
    """
    Verifica un código TOTP de 6 dígitos con ventana de tolerancia ±1 paso (±30s).
    Guarda y retorna el paso del código que COINCIDIÓ (no el paso actual).
    Rechaza reutilización de un paso ya usado (matched_step <= ultimo_paso_usado).
    """
    if at_time is None:
        at_time = timezone.now()

    totp = pyotp.TOTP(secreto, interval=30, digits=6)
    current_step = totp.timecode(at_time)

    cleaned_code = str(codigo).strip().replace(" ", "").replace("-", "")
    if len(cleaned_code) != 6 or not cleaned_code.isdigit():
        return False, None

    matched_step = None
    # Evalúa paso actual (0), anterior (-1) y siguiente (+1)
    for delta in [0, -1, 1]:
        step = current_step + delta
        expected_otp = totp.generate_otp(step)
        if secrets.compare_digest(cleaned_code, expected_otp):
            matched_step = step
            break

    if matched_step is None:
        return False, None

    # Anti-reúso: si el paso ya fue usado o es anterior al último registrado, se rechaza
    if ultimo_paso_usado is not None and matched_step <= ultimo_paso_usado:
        return False, None

    return True, matched_step


def generar_codigos_recuperacion(cantidad: int = 10) -> list[tuple[str, str]]:
    """
    Genera pares de (codigo_plano, codigo_hash) para recuperación de emergencia.
    Formato amigable: 8 caracteres alfanuméricos agrupados (ej: A1B2-C3D4).
    """
    codigos = []
    caracteres = (
        "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"  # Base 32 amigable sin ambigüedades (sin 0, 1, I, O)
    )
    for _ in range(cantidad):
        parte1 = "".join(secrets.choice(caracteres) for _ in range(4))
        parte2 = "".join(secrets.choice(caracteres) for _ in range(4))
        codigo_plano = f"{parte1}-{parte2}"
        codigo_hash = make_password(codigo_plano)
        codigos.append((codigo_plano, codigo_hash))
    return codigos


def verificar_codigo_recuperacion(codigo_plano: str, codigo_hash: str) -> bool:
    """Verifica si un código plano coincide con el hash almacenado."""
    cleaned = codigo_plano.strip().upper()
    return check_password(cleaned, codigo_hash)
