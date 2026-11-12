import pytest
from django.contrib.auth import get_user_model

from apps.autenticacion.services import cambiar_password_obligatorio
from apps.autenticacion.tokens import PURPOSE_PASSWORD_CHANGE, PURPOSE_VERIFY, generar_mfa_token
from apps.common.exceptions import (
    CredencialesInvalidasError,
    CuentaBloqueadaError,
    ReglaDeNegocioError,
)

Usuario = get_user_model()


@pytest.fixture
def usuario_pwd(db):
    u = Usuario.objects.create_user(
        email="cambio@test.com",
        password="Password123!",
        nombre_completo="Cambio",
        rol="TECNICO",
        debe_cambiar_password=True,
    )
    return u


def test_cambiar_password_token_invalido():
    with pytest.raises(CredencialesInvalidasError):
        cambiar_password_obligatorio("token-malo", "NuevaPassword123!")


def test_cambiar_password_proposito_cruzado(usuario_pwd):
    token = generar_mfa_token(usuario_pwd.id, PURPOSE_VERIFY)
    with pytest.raises(CredencialesInvalidasError):
        cambiar_password_obligatorio(token, "NuevaPassword123!")


def test_cambiar_password_usuario_inactivo(usuario_pwd):
    usuario_pwd.is_active = False
    usuario_pwd.save()
    token = generar_mfa_token(usuario_pwd.id, PURPOSE_PASSWORD_CHANGE)
    with pytest.raises(CredencialesInvalidasError):
        cambiar_password_obligatorio(token, "NuevaPassword123!")


def test_cambiar_password_usuario_bloqueado(usuario_pwd):
    from datetime import timedelta

    from django.utils import timezone

    usuario_pwd.bloqueado_hasta = timezone.now() + timedelta(minutes=10)
    usuario_pwd.save()
    token = generar_mfa_token(usuario_pwd.id, PURPOSE_PASSWORD_CHANGE)
    with pytest.raises(CuentaBloqueadaError):
        cambiar_password_obligatorio(token, "NuevaPassword123!")


def test_cambiar_password_flag_false(usuario_pwd):
    usuario_pwd.debe_cambiar_password = False
    usuario_pwd.save()
    token = generar_mfa_token(usuario_pwd.id, PURPOSE_PASSWORD_CHANGE)
    with pytest.raises(ReglaDeNegocioError):
        cambiar_password_obligatorio(token, "NuevaPassword123!")


def test_cambiar_password_igual_anterior(usuario_pwd):
    token = generar_mfa_token(usuario_pwd.id, PURPOSE_PASSWORD_CHANGE)
    with pytest.raises(ReglaDeNegocioError) as exc:
        cambiar_password_obligatorio(token, "Password123!")
    assert exc.value.code == "password_igual_anterior"


def test_cambiar_password_debil(usuario_pwd):
    from django.core.exceptions import ValidationError

    token = generar_mfa_token(usuario_pwd.id, PURPOSE_PASSWORD_CHANGE)
    with pytest.raises(ValidationError):
        cambiar_password_obligatorio(token, "123")
