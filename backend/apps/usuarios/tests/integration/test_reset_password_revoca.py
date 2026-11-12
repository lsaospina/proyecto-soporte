from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.usuarios.models import RolChoices, Usuario


@pytest.mark.django_db
def test_reset_password_limpia_bloqueo_y_refresh_viejo_falla(api_client, settings):
    settings.MFA_ENFORCED = False
    admin = Usuario.objects.create_user(
        email="admreset@test.com",
        password="AdminPass123!",
        nombre_completo="Admin",
        rol=RolChoices.ADMINISTRADOR,
    )
    u = Usuario.objects.create_user(
        email="blk@test.com",
        password="UserPass123!",
        nombre_completo="Blk",
        rol=RolChoices.TECNICO,
    )
    # Login para obtener refresh válido
    resp = api_client.post(
        reverse("autenticacion:login"),
        {"email": "blk@test.com", "password": "UserPass123!"},
        format="json",
    )
    assert resp.status_code == 200
    old_refresh = resp.cookies["refresh_token"].value

    # Simular bloqueo por intentos
    u.intentos_fallidos = 5
    u.bloqueado_hasta = timezone.now() + timedelta(minutes=15)
    u.save(update_fields=["intentos_fallidos", "bloqueado_hasta"])

    api_client.force_authenticate(user=admin)
    resp_reset = api_client.post(f"/api/v1/usuarios/{u.id}/reset_password/")
    assert resp_reset.status_code == 200

    u.refresh_from_db()
    assert u.intentos_fallidos == 0
    assert u.bloqueado_hasta is None
    assert u.debe_cambiar_password is True

    # Refresh viejo debe fallar (revocado)
    client2 = api_client.__class__()
    client2.cookies["refresh_token"] = old_refresh
    resp_refresh = client2.post(reverse("autenticacion:refresh"))
    assert resp_refresh.status_code == 401
