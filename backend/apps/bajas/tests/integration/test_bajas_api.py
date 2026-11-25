from datetime import date

import pytest

from apps.activos.models import Activo, AsignacionActivo, EstadoActivo
from apps.bajas.models import Baja
from apps.catalogos.models import Categoria, Marca, ModeloActivo
from apps.usuarios.models import RolChoices, Usuario


def _usuario(email, rol):
    return Usuario.objects.create_user(
        email=email, password="Pass12345!", nombre_completo=email, rol=rol
    )


@pytest.fixture
def admin_user(db):
    return _usuario("admin.baja@test.com", RolChoices.ADMINISTRADOR)


@pytest.fixture
def tecnico_user(db):
    return _usuario("tec.baja@test.com", RolChoices.TECNICO)


@pytest.fixture
def responsable_user(db):
    return _usuario("resp.baja@test.com", RolChoices.USUARIO_RESPONSABLE)


@pytest.fixture
def activo(db):
    marca = Marca.objects.create(nombre="Dell")
    categoria = Categoria.objects.create(nombre="HW")
    modelo = ModeloActivo.objects.create(marca=marca, categoria=categoria, nombre="Latitude")
    return Activo.objects.create(
        serial="SN-BAJA-1",
        modelo=modelo,
        fecha_adquisicion=date(2024, 1, 1),
        codigo_qr="AST-2024-950001",
    )


def auth(client, user):
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestBajasPermisos:
    def test_list_unauth_401(self, api_client):
        assert api_client.get("/api/v1/bajas/").status_code == 401

    def test_list_tecnico_403(self, api_client, tecnico_user):
        assert auth(api_client, tecnico_user).get("/api/v1/bajas/").status_code == 403

    def test_crear_responsable_403(self, api_client, responsable_user, activo):
        auth(api_client, responsable_user)
        resp = api_client.post("/api/v1/bajas/", {"activo": activo.id, "motivo": "X"})
        assert resp.status_code == 403


@pytest.mark.django_db
class TestBajasCRUD:
    def test_registrar_baja_cambia_estado(self, api_client, admin_user, activo):
        auth(api_client, admin_user)
        resp = api_client.post(
            "/api/v1/bajas/", {"activo": activo.id, "motivo": "Equipo obsoleto"}
        )
        assert resp.status_code == 201
        activo.refresh_from_db()
        assert activo.estado == EstadoActivo.DADO_DE_BAJA
        assert Baja.objects.filter(activo=activo).count() == 1

    def test_baja_duplicada(self, api_client, admin_user, activo):
        Baja.objects.create(activo=activo, motivo="Obsoleto", autorizado_por=admin_user)
        auth(api_client, admin_user)
        resp = api_client.post(
            "/api/v1/bajas/", {"activo": activo.id, "motivo": "Otra"}
        )
        assert resp.status_code == 400

    def test_baja_con_asignacion_abierta(self, api_client, admin_user, responsable_user, activo):
        AsignacionActivo.objects.create(
            activo=activo,
            usuario=responsable_user,
            asignado_por=admin_user,
            fecha_inicio=date(2024, 1, 1),
        )
        auth(api_client, admin_user)
        resp = api_client.post(
            "/api/v1/bajas/", {"activo": activo.id, "motivo": "Obsoleto"}
        )
        assert resp.status_code == 400

    def test_list_filtra_por_activo(self, api_client, admin_user, activo):
        Baja.objects.create(activo=activo, motivo="Obsoleto", autorizado_por=admin_user)
        auth(api_client, admin_user)
        resp = api_client.get("/api/v1/bajas/", {"activo": activo.id})
        assert resp.status_code == 200
        assert resp.data["count"] == 1
