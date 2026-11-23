import pytest
from rest_framework.test import APIClient

from apps.activos.models import Activo, EstadoActivo
from apps.catalogos.models import Categoria, Marca, ModeloActivo
from apps.usuarios.models import RolChoices, Usuario


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return Usuario.objects.create_user(
        email="admin@test.com",
        password="AdminPass123!",
        nombre_completo="Admin",
        rol=RolChoices.ADMINISTRADOR,
    )


@pytest.fixture
def tecnico_user(db):
    return Usuario.objects.create_user(
        email="tec@test.com",
        password="TecPass123!",
        nombre_completo="Tecnico",
        rol=RolChoices.TECNICO,
    )


@pytest.fixture
def responsable_user(db):
    return Usuario.objects.create_user(
        email="resp@test.com",
        password="RespPass123!",
        nombre_completo="Resp",
        rol=RolChoices.USUARIO_RESPONSABLE,
    )


def auth(client, user):
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def modelo(db):
    marca = Marca.objects.create(nombre="Dell")
    cat = Categoria.objects.create(nombre="HW")
    return ModeloActivo.objects.create(marca=marca, categoria=cat, nombre="Latitude")


@pytest.mark.django_db
class TestActivosPermisos:
    def test_list_unauth_401(self, api_client):
        assert api_client.get("/api/v1/activos/").status_code == 401

    def test_list_responsable_403(self, api_client, responsable_user):
        auth(api_client, responsable_user)
        assert api_client.get("/api/v1/activos/").status_code == 403

    def test_list_tecnico_200(self, api_client, tecnico_user):
        auth(api_client, tecnico_user)
        assert api_client.get("/api/v1/activos/").status_code == 200

    def test_list_admin_200(self, api_client, admin_user):
        auth(api_client, admin_user)
        assert api_client.get("/api/v1/activos/").status_code == 200

    def test_create_tecnico_201(self, api_client, tecnico_user, modelo):
        auth(api_client, tecnico_user)
        resp = api_client.post(
            "/api/v1/activos/",
            {"serial": "S1", "modelo": modelo.pk, "fecha_adquisicion": "2024-01-01"},
            format="json",
        )
        assert resp.status_code == 201

    def test_create_admin_201(self, api_client, admin_user, modelo):
        auth(api_client, admin_user)
        resp = api_client.post(
            "/api/v1/activos/",
            {"serial": "S2", "modelo": modelo.pk, "fecha_adquisicion": "2024-01-01"},
            format="json",
        )
        assert resp.status_code == 201

    def test_inactivar_tecnico_403(self, api_client, tecnico_user, modelo):
        auth(api_client, tecnico_user)
        a = Activo.objects.create(
            serial="S3", modelo=modelo, fecha_adquisicion="2024-01-01", codigo_qr="AST-2024-000003"
        )
        resp = api_client.post(f"/api/v1/activos/{a.pk}/inactivar/")
        assert resp.status_code == 403

    def test_inactivar_admin_ok(self, api_client, admin_user, modelo):
        auth(api_client, admin_user)
        a = Activo.objects.create(
            serial="S4", modelo=modelo, fecha_adquisicion="2024-01-01", codigo_qr="AST-2024-000004"
        )
        resp = api_client.post(f"/api/v1/activos/{a.pk}/inactivar/")
        assert resp.status_code == 200


@pytest.mark.django_db
class TestActivosUnicidad:
    def test_serial_duplicado_400(self, api_client, admin_user, modelo):
        auth(api_client, admin_user)
        api_client.post(
            "/api/v1/activos/",
            {"serial": "DUP", "modelo": modelo.pk, "fecha_adquisicion": "2024-01-01"},
            format="json",
        )
        resp = api_client.post(
            "/api/v1/activos/",
            {"serial": "dup", "modelo": modelo.pk, "fecha_adquisicion": "2024-01-01"},
            format="json",
        )
        assert resp.status_code == 400

    def test_mac_duplicado_400(self, api_client, admin_user, modelo):
        auth(api_client, admin_user)
        api_client.post(
            "/api/v1/activos/",
            {
                "serial": "M1",
                "modelo": modelo.pk,
                "fecha_adquisicion": "2024-01-01",
                "direccion_mac": "AA:BB:CC:DD:EE:FF",
            },
            format="json",
        )
        resp = api_client.post(
            "/api/v1/activos/",
            {
                "serial": "M2",
                "modelo": modelo.pk,
                "fecha_adquisicion": "2024-01-01",
                "direccion_mac": "aa:bb:cc:dd:ee:ff",
            },
            format="json",
        )
        assert resp.status_code == 400


@pytest.mark.django_db
class TestActivosReglas:
    def test_create_ignora_estado(self, api_client, admin_user, modelo):
        auth(api_client, admin_user)
        resp = api_client.post(
            "/api/v1/activos/",
            {
                "serial": "E1",
                "modelo": modelo.pk,
                "fecha_adquisicion": "2024-01-01",
                "estado": "ASIGNADO",
            },
            format="json",
        )
        assert resp.status_code == 201
        assert resp.data["estado"] == "DISPONIBLE"

    def test_inactivar_solo_disponible(self, api_client, admin_user, modelo):
        auth(api_client, admin_user)
        a = Activo.objects.create(
            serial="I1",
            modelo=modelo,
            fecha_adquisicion="2024-01-01",
            codigo_qr="AST-2024-000010",
            estado=EstadoActivo.ASIGNADO,
        )
        resp = api_client.post(f"/api/v1/activos/{a.pk}/inactivar/")
        assert resp.status_code == 400

    def test_reactivar_ok(self, api_client, admin_user, modelo):
        auth(api_client, admin_user)
        a = Activo.objects.create(
            serial="R1",
            modelo=modelo,
            fecha_adquisicion="2024-01-01",
            codigo_qr="AST-2024-000011",
            is_active=False,
        )
        resp = api_client.post(f"/api/v1/activos/{a.pk}/reactivar/")
        assert resp.status_code == 200


@pytest.mark.django_db
class TestActivosHistorialAuditoria:
    def test_historial_usuario(self, db, admin_user, modelo):
        from apps.activos.services import crear_activo

        a = crear_activo(
            {"serial": "H1", "modelo": modelo, "fecha_adquisicion": "2024-01-01"}, actor=admin_user
        )
        hist = a.history.first()
        assert hist.history_user == admin_user

    def test_evento_auditoria(self, db, admin_user, modelo):
        from apps.activos.services import crear_activo
        from apps.auditoria.models import AccionAuditoria, RegistroAuditoria

        crear_activo(
            {"serial": "H2", "modelo": modelo, "fecha_adquisicion": "2024-01-01"}, actor=admin_user
        )
        ev = RegistroAuditoria.objects.filter(accion=AccionAuditoria.ACTIVO_CREADO).first()
        assert ev is not None


@pytest.mark.django_db
class TestActivosNumQueries:
    def test_list_num_queries(self, db, api_client, admin_user, modelo):
        Activo.objects.bulk_create(
            [
                Activo(
                    serial=f"Q{i}",
                    modelo=modelo,
                    fecha_adquisicion="2024-01-01",
                    codigo_qr=f"AST-2024-{i:06d}",
                )
                for i in range(5)
            ]
        )
        auth(api_client, admin_user)
        from django.db import connection, reset_queries

        reset_queries()
        resp = api_client.get("/api/v1/activos/")
        assert resp.status_code == 200
        assert len(connection.queries) <= 5


@pytest.mark.django_db
class TestActivosFiltros:
    def test_filtro_estado(self, api_client, admin_user, modelo):
        auth(api_client, admin_user)
        Activo.objects.create(
            serial="F1",
            modelo=modelo,
            fecha_adquisicion="2024-01-01",
            codigo_qr="AST-2024-000020",
            estado=EstadoActivo.DISPONIBLE,
        )
        Activo.objects.create(
            serial="F2",
            modelo=modelo,
            fecha_adquisicion="2024-01-01",
            codigo_qr="AST-2024-000021",
            estado=EstadoActivo.ASIGNADO,
        )
        resp = api_client.get("/api/v1/activos/?estado=ASIGNADO")
        assert resp.status_code == 200
        assert resp.data["count"] == 1

    def test_search_serial(self, api_client, admin_user, modelo):
        auth(api_client, admin_user)
        Activo.objects.create(
            serial="SEARCHME",
            modelo=modelo,
            fecha_adquisicion="2024-01-01",
            codigo_qr="AST-2024-000022",
        )
        resp = api_client.get("/api/v1/activos/?search=SEARCHME")
        assert resp.status_code == 200
        assert resp.data["count"] == 1


@pytest.mark.django_db
class TestActivosInactivosVisible:
    def test_por_defecto_solo_activos(self, api_client, admin_user, modelo):
        auth(api_client, admin_user)
        Activo.objects.create(
            serial="ACT",
            modelo=modelo,
            fecha_adquisicion="2024-01-01",
            codigo_qr="AST-2024-000030",
            is_active=True,
        )
        Activo.objects.create(
            serial="INA",
            modelo=modelo,
            fecha_adquisicion="2024-01-01",
            codigo_qr="AST-2024-000031",
            is_active=False,
        )
        resp = api_client.get("/api/v1/activos/")
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["serial"] == "ACT"

    def test_is_active_false_devuelve_inactivos(self, api_client, admin_user, modelo):
        auth(api_client, admin_user)
        Activo.objects.create(
            serial="ACT2",
            modelo=modelo,
            fecha_adquisicion="2024-01-01",
            codigo_qr="AST-2024-000032",
            is_active=True,
        )
        Activo.objects.create(
            serial="INA2",
            modelo=modelo,
            fecha_adquisicion="2024-01-01",
            codigo_qr="AST-2024-000033",
            is_active=False,
        )
        resp = api_client.get("/api/v1/activos/?is_active=false")
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["serial"] == "INA2"

    def test_todos_devuelve_ambos(self, api_client, admin_user, modelo):
        auth(api_client, admin_user)
        Activo.objects.create(
            serial="ACT3",
            modelo=modelo,
            fecha_adquisicion="2024-01-01",
            codigo_qr="AST-2024-000034",
            is_active=True,
        )
        Activo.objects.create(
            serial="INA3",
            modelo=modelo,
            fecha_adquisicion="2024-01-01",
            codigo_qr="AST-2024-000035",
            is_active=False,
        )
        resp = api_client.get("/api/v1/activos/?todos=1")
        assert resp.data["count"] == 2
