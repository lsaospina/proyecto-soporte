import pytest
from django.urls import reverse

from apps.auditoria.models import AccionAuditoria, RegistroAuditoria
from apps.usuarios.models import RolChoices, Usuario


@pytest.mark.django_db
def test_login_email_case_insensitive(api_client, settings):
    settings.MFA_ENFORCED = False
    Usuario.objects.create_user(
        email="ana@x.com",
        password="Password123!",
        nombre_completo="Ana",
        rol=RolChoices.TECNICO,
    )
    resp = api_client.post(
        reverse("autenticacion:login"),
        {"email": "Ana@X.com", "password": "Password123!"},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data["status"] == "ok"


@pytest.mark.django_db
def test_login_fallido_registra_auditoria(api_client):
    resp = api_client.post(
        reverse("autenticacion:login"),
        {"email": "noexiste@test.com", "password": "bad"},
        format="json",
    )
    assert resp.status_code == 401
    assert RegistroAuditoria.objects.filter(accion=AccionAuditoria.LOGIN_FALLIDO).exists()


@pytest.mark.django_db
def test_login_exitoso_registra_auditoria(api_client, settings):
    settings.MFA_ENFORCED = False
    u = Usuario.objects.create_user(
        email="ok@test.com",
        password="Password123!",
        nombre_completo="OK",
        rol=RolChoices.TECNICO,
    )
    resp = api_client.post(
        reverse("autenticacion:login"),
        {"email": "ok@test.com", "password": "Password123!"},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data["status"] == "ok"
    assert RegistroAuditoria.objects.filter(
        accion=AccionAuditoria.LOGIN_EXITOSO, usuario=u
    ).exists()


@pytest.mark.django_db
def test_login_mfa_required_no_registra_login_exitoso(api_client, settings):
    settings.MFA_ENFORCED = True
    u = Usuario.objects.create_user(
        email="mfa@test.com",
        password="Password123!",
        nombre_completo="MFA",
        rol=RolChoices.TECNICO,
    )
    resp = api_client.post(
        reverse("autenticacion:login"),
        {"email": "mfa@test.com", "password": "Password123!"},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data["status"] in {"mfa_required", "mfa_setup_required"}
    assert not RegistroAuditoria.objects.filter(
        accion=AccionAuditoria.LOGIN_EXITOSO, usuario=u
    ).exists()


@pytest.mark.django_db
def test_password_change_required_flow(api_client, settings):
    settings.MFA_ENFORCED = False
    u = Usuario.objects.create_user(
        email="must@test.com",
        password="TempPass123!",
        nombre_completo="Must",
        rol=RolChoices.TECNICO,
        debe_cambiar_password=True,
    )
    resp = api_client.post(
        reverse("autenticacion:login"),
        {"email": "must@test.com", "password": "TempPass123!"},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data["status"] == "password_change_required"
    token = resp.data["password_token"]

    resp2 = api_client.post(
        reverse("autenticacion:password-change"),
        {
            "password_token": token,
            "new_password": "NuevaPass123!x",
            "confirm_password": "NuevaPass123!x",
        },
        format="json",
    )
    assert resp2.status_code == 200
    assert resp2.data["status"] == "ok"
    assert resp2["Cache-Control"] == "no-store"
    u.refresh_from_db()
    assert u.debe_cambiar_password is False
    assert RegistroAuditoria.objects.filter(
        accion=AccionAuditoria.PASSWORD_CAMBIADA, usuario=u
    ).exists()
    assert RegistroAuditoria.objects.filter(
        accion=AccionAuditoria.LOGIN_EXITOSO, usuario=u
    ).exists()
