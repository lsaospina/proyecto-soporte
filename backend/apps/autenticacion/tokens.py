from typing import Literal

from django.core import signing

from apps.common.exceptions import CredencialesInvalidasError

MFA_PURPOSE = Literal["setup", "verify"]
PURPOSE_SETUP = "setup"
PURPOSE_VERIFY = "verify"

_MFA_SALT = "apps.autenticacion.mfa_token.v1"


def generar_mfa_token(user_id: int, purpose: str) -> str:
    """
    Genera un token firmado de corta vida (5 minutos) con un propósito específico.
    No es un token JWT y no es aceptado como access token de sesión.
    """
    signer = signing.TimestampSigner(salt=_MFA_SALT)
    payload = {
        "user_id": user_id,
        "purpose": purpose,
    }
    return signer.sign_object(payload)


def validar_mfa_token(token: str, expected_purpose: str, max_age: int = 300) -> int:
    """
    Valida la firma, expiración (máximo 5 minutos) y propósito del mfa_token.
    Retorna el user_id autenticado.
    Lanza CredencialesInvalidasError si la firma es inválida, expiró o el propósito no coincide.
    """
    if not token or not isinstance(token, str):
        raise CredencialesInvalidasError(
            "El token MFA es obligatorio.",
            code="mfa_token_faltante",
        )

    signer = signing.TimestampSigner(salt=_MFA_SALT)
    try:
        data = signer.unsign_object(token, max_age=max_age)
    except signing.SignatureExpired as exc:
        raise CredencialesInvalidasError(
            "El token de segundo factor ha expirado. Inicie sesión nuevamente.",
            code="mfa_token_expirado",
        ) from exc
    except signing.BadSignature as exc:
        raise CredencialesInvalidasError(
            "El token de segundo factor es inválido.",
            code="mfa_token_invalido",
        ) from exc

    if not isinstance(data, dict):
        raise CredencialesInvalidasError(
            "Estructura del token MFA inválida.",
            code="mfa_token_invalido",
        )

    token_purpose = data.get("purpose")
    if token_purpose != expected_purpose:
        raise CredencialesInvalidasError(
            "El token MFA no es válido para esta operación (propósito no coincide).",
            code="mfa_proposito_invalido",
        )

    user_id = data.get("user_id")
    if not user_id:
        raise CredencialesInvalidasError(
            "Token MFA no contiene identificador de usuario.",
            code="mfa_token_invalido",
        )

    return int(user_id)
