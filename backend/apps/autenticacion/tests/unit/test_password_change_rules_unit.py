from unittest.mock import patch

import pytest
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from apps.autenticacion.services import cambiar_password_obligatorio
from apps.common.exceptions import (
    CredencialesInvalidasError,
    CuentaBloqueadaError,
    ReglaDeNegocioError,
)
from apps.usuarios.models import RolChoices, Usuario


def make_user(**overrides):
    defaults = dict(
        email="u@test.com",
        nombre_completo="U",
        rol=RolChoices.ADMINISTRADOR,
        is_active=True,
        debe_cambiar_password=True,
        id=42,
    )
    defaults.update(overrides)
    user = Usuario(**{k: v for k, v in defaults.items() if k != "id"})
    user.id = defaults["id"]
    user.set_password("TempPass123!")
    return user


# --- Reglas puras (sin DB) ---


def test_password_debil_rechazada():
    # Invoca: django.contrib.auth.password_validation.validate_password
    # Fake: Usuario en memoria (no guardado)
    user = make_user()
    with pytest.raises(ValidationError):
        validate_password("123", user)


def test_password_igual_a_la_temporal_regla():
    # Invoca: cambiar_password_obligatorio (código real)
    # Fake: Usuario.objects.filter parcheado para devolver un usuario con debe_cambiar_password=True;
    #       validar_mfa_token parcheado para devolver el id.
    user = make_user(debe_cambiar_password=True)
    with (
        patch("apps.autenticacion.services.validar_mfa_token", return_value=user.id),
        patch("apps.autenticacion.services.Usuario.objects") as mock_mgr,
        patch("apps.autenticacion.services.revocar_tokens_refresco"),
        patch("apps.autenticacion.services.transaction.atomic"),
    ):
        mock_mgr.filter.return_value.first.return_value = user
        with pytest.raises(ReglaDeNegocioError):
            cambiar_password_obligatorio("tok", "TempPass123!", ip=None)


def test_token_un_solo_uso_rechaza_si_ya_cambiado():
    # Invoca: cambiar_password_obligatorio (código real)
    # Fake: Usuario con debe_cambiar_password=False
    user = make_user(debe_cambiar_password=False)
    with (
        patch("apps.autenticacion.services.validar_mfa_token", return_value=user.id),
        patch("apps.autenticacion.services.Usuario.objects") as mock_mgr,
        patch("apps.autenticacion.services.revocar_tokens_refresco"),
        patch("apps.autenticacion.services.transaction.atomic"),
    ):
        mock_mgr.filter.return_value.first.return_value = user
        with pytest.raises(ReglaDeNegocioError):
            cambiar_password_obligatorio("tok", "NuevaPass123!", ip=None)


def test_usuario_inactivo_rechazado():
    # Invoca: cambiar_password_obligatorio (código real)
    user = make_user(is_active=False)
    with (
        patch("apps.autenticacion.services.validar_mfa_token", return_value=user.id),
        patch("apps.autenticacion.services.Usuario.objects") as mock_mgr,
    ):
        mock_mgr.filter.return_value.first.return_value = user
        with pytest.raises(CredencialesInvalidasError):
            cambiar_password_obligatorio("tok", "NuevaPass123!", ip=None)


def test_usuario_bloqueado_rechazado():
    # Invoca: cambiar_password_obligatorio (código real)
    from datetime import timedelta

    from django.utils import timezone

    user = make_user(bloqueado_hasta=timezone.now() + timedelta(minutes=10))
    with (
        patch("apps.autenticacion.services.validar_mfa_token", return_value=user.id),
        patch("apps.autenticacion.services.Usuario.objects") as mock_mgr,
    ):
        mock_mgr.filter.return_value.first.return_value = user
        with pytest.raises(CuentaBloqueadaError):
            cambiar_password_obligatorio("tok", "NuevaPass123!", ip=None)
