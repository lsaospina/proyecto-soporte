import pytest
from django.test.utils import override_settings
from rest_framework.test import APIClient

from apps.catalogos.models import Categoria, Marca, ModeloActivo, Sede, Ubicacion
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
        nombre_completo="Responsable",
        rol=RolChoices.USUARIO_RESPONSABLE,
    )


def auth(client, user):
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestCatalogosPermisos:
    @pytest.mark.parametrize(
        "path",
        [
            "/api/v1/sedes/",
            "/api/v1/ubicaciones/",
            "/api/v1/categorias/",
            "/api/v1/marcas/",
            "/api/v1/modelos/",
        ],
    )
    def test_list_unauthenticated_401(self, api_client, path):
        assert api_client.get(path).status_code == 401

    @pytest.mark.parametrize(
        "path",
        [
            "/api/v1/sedes/",
            "/api/v1/ubicaciones/",
            "/api/v1/categorias/",
            "/api/v1/marcas/",
            "/api/v1/modelos/",
        ],
    )
    def test_list_responsable_403(self, api_client, responsable_user, path):
        auth(api_client, responsable_user)
        assert api_client.get(path).status_code == 403

    @pytest.mark.parametrize(
        "path",
        [
            "/api/v1/sedes/",
            "/api/v1/ubicaciones/",
            "/api/v1/categorias/",
            "/api/v1/marcas/",
            "/api/v1/modelos/",
        ],
    )
    def test_list_tecnico_200(self, api_client, tecnico_user, path):
        auth(api_client, tecnico_user)
        assert api_client.get(path).status_code == 200

    @pytest.mark.parametrize(
        "path",
        [
            "/api/v1/sedes/",
            "/api/v1/ubicaciones/",
            "/api/v1/categorias/",
            "/api/v1/marcas/",
            "/api/v1/modelos/",
        ],
    )
    def test_list_admin_200(self, api_client, admin_user, path):
        auth(api_client, admin_user)
        assert api_client.get(path).status_code == 200

    def test_create_tecnico_403(self, api_client, tecnico_user):
        auth(api_client, tecnico_user)
        assert api_client.post("/api/v1/sedes/", {"nombre": "S1"}, format="json").status_code == 403

    def test_create_admin_201(self, api_client, admin_user):
        auth(api_client, admin_user)
        resp = api_client.post(
            "/api/v1/sedes/", {"nombre": "Sede1", "direccion": "dir"}, format="json"
        )
        assert resp.status_code == 201


@pytest.mark.django_db
class TestUnicidadCI:
    def test_sede_nombre_ci_unico(self, api_client, admin_user):
        auth(api_client, admin_user)
        api_client.post("/api/v1/sedes/", {"nombre": "Central"}, format="json")
        resp = api_client.post("/api/v1/sedes/", {"nombre": "CENTRAL"}, format="json")
        assert resp.status_code == 400

    def test_ubicacion_nombre_por_sede_ci_unico(self, db, api_client, admin_user):
        auth(api_client, admin_user)
        sede = Sede.objects.create(nombre="Sede")
        api_client.post("/api/v1/ubicaciones/", {"sede": sede.pk, "nombre": "Piso1"}, format="json")
        resp = api_client.post(
            "/api/v1/ubicaciones/", {"sede": sede.pk, "nombre": "PISO1"}, format="json"
        )
        assert resp.status_code == 400

    def test_categoria_nombre_ci_unico(self, api_client, admin_user):
        auth(api_client, admin_user)
        api_client.post("/api/v1/categorias/", {"nombre": "Hardware"}, format="json")
        resp = api_client.post("/api/v1/categorias/", {"nombre": "hardware"}, format="json")
        assert resp.status_code == 400

    def test_marca_nombre_ci_unico(self, api_client, admin_user):
        auth(api_client, admin_user)
        api_client.post("/api/v1/marcas/", {"nombre": "Dell"}, format="json")
        resp = api_client.post("/api/v1/marcas/", {"nombre": "DELL"}, format="json")
        assert resp.status_code == 400

    def test_modelo_nombre_por_marca_ci_unico(self, db, api_client, admin_user):
        auth(api_client, admin_user)
        marca = Marca.objects.create(nombre="Dell")
        cat = Categoria.objects.create(nombre="HW")
        api_client.post(
            "/api/v1/modelos/",
            {"marca": marca.pk, "categoria": cat.pk, "nombre": "Latitude"},
            format="json",
        )
        resp = api_client.post(
            "/api/v1/modelos/",
            {"marca": marca.pk, "categoria": cat.pk, "nombre": "LATITUDE"},
            format="json",
        )
        assert resp.status_code == 400


@pytest.mark.django_db
class TestGuardasPadreHijo:
    def test_inactivar_sede_con_ubicaciones_activas_bloqueado(self, db, api_client, admin_user):
        auth(api_client, admin_user)
        sede = Sede.objects.create(nombre="Sede")
        Ubicacion.objects.create(sede=sede, nombre="U1", is_active=True)
        resp = api_client.patch(f"/api/v1/sedes/{sede.pk}/", {"is_active": False}, format="json")
        assert resp.status_code == 400

    def test_inactivar_marca_con_modelos_activos_bloqueado(self, db, api_client, admin_user):
        auth(api_client, admin_user)
        marca = Marca.objects.create(nombre="Dell")
        cat = Categoria.objects.create(nombre="HW")
        ModeloActivo.objects.create(marca=marca, categoria=cat, nombre="M1", is_active=True)
        resp = api_client.patch(f"/api/v1/marcas/{marca.pk}/", {"is_active": False}, format="json")
        assert resp.status_code == 400

    def test_inactivar_categoria_con_modelos_activos_bloqueado(self, db, api_client, admin_user):
        auth(api_client, admin_user)
        marca = Marca.objects.create(nombre="Dell")
        cat = Categoria.objects.create(nombre="HW")
        ModeloActivo.objects.create(marca=marca, categoria=cat, nombre="M1", is_active=True)
        resp = api_client.patch(
            f"/api/v1/categorias/{cat.pk}/", {"is_active": False}, format="json"
        )
        assert resp.status_code == 400

    def test_inactivar_sin_hijos_activos_ok(self, db, api_client, admin_user):
        auth(api_client, admin_user)
        sede = Sede.objects.create(nombre="Sede")
        resp = api_client.patch(f"/api/v1/sedes/{sede.pk}/", {"is_active": False}, format="json")
        assert resp.status_code == 200
        sede.refresh_from_db()
        assert sede.is_active is False


@pytest.mark.django_db
class TestProtect:
    def test_borrar_ubicacion_referenciada_protect(self, db):
        sede = Sede.objects.create(nombre="Sede")
        Ubicacion.objects.create(sede=sede, nombre="U1")
        from django.db.models import ProtectedError

        with pytest.raises(ProtectedError):
            sede.delete()

    def test_borrar_modelo_referenciado_protect(self, db):
        marca = Marca.objects.create(nombre="Dell")
        cat = Categoria.objects.create(nombre="HW")
        ModeloActivo.objects.create(marca=marca, categoria=cat, nombre="M1")
        from django.db.models import ProtectedError

        with pytest.raises(ProtectedError):
            marca.delete()


@pytest.mark.django_db
class TestHistorialUsuario:
    def test_history_user_guardado(self, db, admin_user):
        from apps.catalogos.services import crear_catalogo

        sede = crear_catalogo("Sede", {"nombre": "SedeH"}, actor=admin_user)
        hist = sede.history.first()
        assert hist.history_user == admin_user


@pytest.mark.django_db
class TestAuditoriaCatalogo:
    def test_evento_creado(self, db, admin_user):
        from apps.auditoria.models import AccionAuditoria, RegistroAuditoria
        from apps.catalogos.services import crear_catalogo

        crear_catalogo("Sede", {"nombre": "SedeA"}, actor=admin_user)
        ev = RegistroAuditoria.objects.filter(accion=AccionAuditoria.CATALOGO_CREADO).first()
        assert ev is not None
        assert ev.entidad == "Sede"


@pytest.mark.django_db
class TestNumQueries:
    def test_list_sedes_num_queries(self, db, api_client, admin_user):
        Sede.objects.bulk_create([Sede(nombre=f"S{i}") for i in range(5)])
        auth(api_client, admin_user)
        with override_settings(DEBUG=True):
            from django.db import connection, reset_queries

            reset_queries()
            resp = api_client.get("/api/v1/sedes/")
            assert resp.status_code == 200
            # <= 3 queries (select + count)
            assert len(connection.queries) <= 4


@pytest.mark.django_db
class TestIntegrityError400:
    def test_duplicado_retorna_400(self, db, api_client, admin_user):
        auth(api_client, admin_user)
        api_client.post("/api/v1/sedes/", {"nombre": "Dup"}, format="json")
        resp = api_client.post("/api/v1/sedes/", {"nombre": "Dup"}, format="json")
        assert resp.status_code == 400
