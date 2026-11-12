import pytest
from django.urls import reverse

from apps.usuarios.models import RolChoices, Usuario


@pytest.mark.django_db
def test_refresh_rechaza_usuario_inactivo(api_client, settings):
    settings.MFA_ENFORCED = False
    u = Usuario.objects.create_user(
        email="ref@test.com", password="Password123!", nombre_completo="Ref", rol=RolChoices.TECNICO
    )
    resp = api_client.post(
        reverse("autenticacion:login"),
        {"email": "ref@test.com", "password": "Password123!"},
        format="json",
    )
    assert resp.status_code == 200
    refresh = resp.cookies["refresh_token"].value
    u.is_active = False
    u.save(update_fields=["is_active"])
    api_client.cookies["refresh_token"] = refresh
    resp2 = api_client.post(reverse("autenticacion:refresh"))
    assert resp2.status_code == 401


@pytest.mark.django_db
def test_me_rechaza_usuario_inactivo(api_client, settings):
    settings.MFA_ENFORCED = False
    u = Usuario.objects.create_user(
        email="meina@test.com",
        password="Password123!",
        nombre_completo="Me",
        rol=RolChoices.TECNICO,
    )
    resp = api_client.post(
        reverse("autenticacion:login"),
        {"email": "meina@test.com", "password": "Password123!"},
        format="json",
    )
    access = resp.data["access"]
    u.is_active = False
    u.save(update_fields=["is_active"])
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    resp2 = api_client.get(reverse("autenticacion:me"))
    assert resp2.status_code == 401
