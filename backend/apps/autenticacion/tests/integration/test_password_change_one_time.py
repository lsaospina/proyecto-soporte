import pytest
from django.urls import reverse

from apps.usuarios.models import RolChoices, Usuario


@pytest.mark.django_db
def test_password_change_token_un_solo_uso(api_client, settings):
    settings.MFA_ENFORCED = False
    Usuario.objects.create_user(
        email="once@test.com",
        password="TempPass123!",
        nombre_completo="Once",
        rol=RolChoices.TECNICO,
        debe_cambiar_password=True,
    )
    resp = api_client.post(
        reverse("autenticacion:login"),
        {"email": "once@test.com", "password": "TempPass123!"},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data["status"] == "password_change_required"
    token = resp.data["password_token"]

    payload = {
        "password_token": token,
        "new_password": "NuevaPass123!x",
        "confirm_password": "NuevaPass123!x",
    }
    resp2 = api_client.post(reverse("autenticacion:password-change"), payload, format="json")
    assert resp2.status_code == 200

    # Reutilizar el mismo token debe fallar (debe_cambiar_password ya es False / un solo uso)
    resp3 = api_client.post(reverse("autenticacion:password-change"), payload, format="json")
    assert resp3.status_code == 400
