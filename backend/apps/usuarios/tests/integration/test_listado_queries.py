import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from apps.usuarios.models import RolChoices, Usuario


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return Usuario.objects.create_user(
        email="adminq@test.com",
        password="AdminPass123!",
        nombre_completo="Admin Q",
        rol=RolChoices.ADMINISTRADOR,
    )


@pytest.mark.django_db
def test_listado_usuarios_assert_num_queries(api_client, admin_user):
    # Crear algunos usuarios para que el listado no sea trivial
    for i in range(5):
        Usuario.objects.create_user(
            email=f"u{i}@test.com", password="x", nombre_completo=f"U{i}", rol=RolChoices.TECNICO
        )
    api_client.force_authenticate(user=admin_user)
    with CaptureQueriesContext(connection) as ctx:
        resp = api_client.get("/api/v1/usuarios/")
    assert resp.status_code == 200
    # listado + count/paginación + posibles auth/session lookups deben ser acotados (sin N+1)
    assert len(ctx.captured_queries) <= 12
