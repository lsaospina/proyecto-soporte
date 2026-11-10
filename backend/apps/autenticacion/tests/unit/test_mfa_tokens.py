import pytest

from apps.autenticacion.tokens import (
    PURPOSE_SETUP,
    PURPOSE_VERIFY,
    generar_mfa_token,
    validar_mfa_token,
)
from apps.common.exceptions import CredencialesInvalidasError


def test_mfa_token_flujo_valido():
    """Generación y validación correcta para un usuario y propósito determinado."""
    user_id = 42
    token = generar_mfa_token(user_id=user_id, purpose=PURPOSE_SETUP)
    assert isinstance(token, str)

    recuperado_id = validar_mfa_token(token, expected_purpose=PURPOSE_SETUP)
    assert recuperado_id == user_id


def test_mfa_token_proposito_cruzado_rechazado():
    """
    El token de setup NO debe servir para verify, ni el de verify para setup.
    """
    user_id = 99
    token_setup = generar_mfa_token(user_id=user_id, purpose=PURPOSE_SETUP)

    with pytest.raises(CredencialesInvalidasError) as exc_info:
        validar_mfa_token(token_setup, expected_purpose=PURPOSE_VERIFY)
    assert exc_info.value.code == "mfa_proposito_invalido"

    token_verify = generar_mfa_token(user_id=user_id, purpose=PURPOSE_VERIFY)
    with pytest.raises(CredencialesInvalidasError) as exc_info2:
        validar_mfa_token(token_verify, expected_purpose=PURPOSE_SETUP)
    assert exc_info2.value.code == "mfa_proposito_invalido"


def test_mfa_token_expiracion():
    """Prueba que el token firmado expire según max_age."""
    user_id = 10
    token = generar_mfa_token(user_id=user_id, purpose=PURPOSE_VERIFY)

    # Validando con max_age menor a 1s tras una pausa o max_age=0
    with pytest.raises(CredencialesInvalidasError) as exc_info:
        validar_mfa_token(token, expected_purpose=PURPOSE_VERIFY, max_age=-1)
    assert exc_info.value.code == "mfa_token_expirado"


def test_mfa_token_invalido_o_manipulado():
    """Prueba que tokens alterados o malformados sean rechazados."""
    with pytest.raises(CredencialesInvalidasError) as exc_info:
        validar_mfa_token("token.completamente.falso", expected_purpose=PURPOSE_VERIFY)
    assert exc_info.value.code == "mfa_token_invalido"

    with pytest.raises(CredencialesInvalidasError) as exc_info2:
        validar_mfa_token("", expected_purpose=PURPOSE_VERIFY)
    assert exc_info2.value.code == "mfa_token_faltante"
