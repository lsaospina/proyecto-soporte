from datetime import date

import pytest
from django.db import IntegrityError, transaction
from freezegun import freeze_time
from rest_framework.test import APIClient

from apps.activos.models import Activo, AsignacionActivo, EstadoActivo
from apps.catalogos.models import Categoria, Marca, ModeloActivo
from apps.usuarios.models import RolChoices, Usuario

URL = "/api/v1/asignaciones/"


def _usuario(email, rol, is_active=True):
    return Usuario.objects.create_user(
        email=email,
        password="Pass12345!",
        nombre_completo=email,
        rol=rol,
        is_active=is_active,
    )


@pytest.fixture
def admin_user(db):
    return _usuario("asig-admin@test.com", RolChoices.ADMINISTRADOR)


@pytest.fixture
def tecnico_user(db):
    return _usuario("asig-tec@test.com", RolChoices.TECNICO)


@pytest.fixture
def responsable_user(db):
    return _usuario("asig-resp@test.com", RolChoices.USUARIO_RESPONSABLE)


@pytest.fixture
def trabajador(db):
    return _usuario("asig-trabajador@test.com", RolChoices.USUARIO_RESPONSABLE)


@pytest.fixture
def trabajador2(db):
    return _usuario("asig-trabajador2@test.com", RolChoices.USUARIO_RESPONSABLE)


@pytest.fixture
def modelo(db):
    marca = Marca.objects.create(nombre="Dell")
    categoria = Categoria.objects.create(nombre="HW")
    return ModeloActivo.objects.create(marca=marca, categoria=categoria, nombre="Latitude")


def crear_activo(modelo, serial="ASIG1", estado=EstadoActivo.DISPONIBLE, **kwargs):
    datos = {
        "serial": serial,
        "modelo": modelo,
        "fecha_adquisicion": date(2024, 1, 1),
        "codigo_qr": f"AST-2024-{serial}",
        "estado": estado,
    }
    datos.update(kwargs)
    return Activo.objects.create(**datos)


def auth(client, user):
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
@freeze_time("2026-11-15 12:00:00")
class TestAsignacionesPermisos:
    def test_anonimo_401(self):
        assert APIClient().get(URL).status_code == 401

    def test_responsable_403(self, api_client, responsable_user):
        assert auth(api_client, responsable_user).get(URL).status_code == 403

    def test_tecnico_lee_pero_no_escribe(self, api_client, tecnico_user, trabajador, modelo):
        activo = crear_activo(modelo)
        client = auth(api_client, tecnico_user)
        assert client.get(URL).status_code == 200
        resp = client.post(URL, {"activo": activo.pk, "usuario": trabajador.pk}, format="json")
        assert resp.status_code == 403


@pytest.mark.django_db
@freeze_time("2026-11-15 12:00:00")
class TestAsignar:
    def test_asignar_activo_disponible(self, api_client, admin_user, trabajador, modelo):
        activo = crear_activo(modelo)
        resp = auth(api_client, admin_user).post(
            URL,
            {
                "activo": activo.pk,
                "usuario": trabajador.pk,
                "fecha_inicio": "2026-11-01",
                "observacion": "Entrega inicial",
            },
            format="json",
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["activo_serial"] == "ASIG1"
        assert body["usuario_nombre"] == trabajador.nombre_completo
        assert body["asignado_por_nombre"] == admin_user.nombre_completo
        assert body["activa"] is True
        assert body["dias_asignado"] == 14
        assert body["fecha_fin"] is None

        activo.refresh_from_db()
        assert activo.estado == EstadoActivo.ASIGNADO
        asignacion = AsignacionActivo.objects.get(pk=body["id"])
        assert asignacion.history.first().history_user == admin_user
        assert asignacion.activo.history.first().history_user == admin_user

    def test_auditoria_de_asignacion(self, api_client, admin_user, trabajador, modelo):
        activo = crear_activo(modelo)
        resp = auth(api_client, admin_user).post(
            URL, {"activo": activo.pk, "usuario": trabajador.pk}, format="json"
        )
        from apps.auditoria.models import RegistroAuditoria

        assert resp.status_code == 201
        evento = RegistroAuditoria.objects.get(accion="ASIGNACION_CREADA")
        assert evento.entidad == "Asignacion"
        assert evento.entidad_id == str(resp.json()["id"])

    def test_no_permite_dos_asignaciones_abiertas(
        self, api_client, admin_user, trabajador, trabajador2, modelo
    ):
        activo = crear_activo(modelo)
        client = auth(api_client, admin_user)
        assert (
            client.post(
                URL, {"activo": activo.pk, "usuario": trabajador.pk}, format="json"
            ).status_code
            == 201
        )
        resp = client.post(URL, {"activo": activo.pk, "usuario": trabajador2.pk}, format="json")
        assert resp.status_code == 400
        assert resp.json()["code"] == "activo_ya_asignado"
        assert AsignacionActivo.objects.filter(activo=activo).count() == 1

    def test_constraint_unica_de_asignacion_abierta(self, trabajador, trabajador2, modelo):
        activo = crear_activo(modelo)
        AsignacionActivo.objects.create(
            activo=activo,
            usuario=trabajador,
            asignado_por=trabajador,
            fecha_inicio=date(2026, 11, 1),
        )
        with pytest.raises(IntegrityError), transaction.atomic():
            AsignacionActivo.objects.create(
                activo=activo,
                usuario=trabajador2,
                asignado_por=trabajador,
                fecha_inicio=date(2026, 11, 2),
            )

    def test_bloquea_activo_en_mantenimiento(self, api_client, admin_user, trabajador, modelo):
        activo = crear_activo(modelo, estado=EstadoActivo.EN_MANTENIMIENTO)
        resp = auth(api_client, admin_user).post(
            URL, {"activo": activo.pk, "usuario": trabajador.pk}, format="json"
        )
        assert resp.status_code == 400
        assert resp.json()["code"] == "activo_en_mantenimiento"

    def test_bloquea_activo_inactivo_o_de_baja(self, api_client, admin_user, trabajador, modelo):
        inactivo = crear_activo(modelo, serial="ASIG2", is_active=False)
        baja = crear_activo(modelo, serial="ASIG3", estado=EstadoActivo.DADO_DE_BAJA)
        client = auth(api_client, admin_user)
        for activo in (inactivo, baja):
            resp = client.post(URL, {"activo": activo.pk, "usuario": trabajador.pk}, format="json")
            assert resp.status_code == 400
            assert resp.json()["code"] == "activo_no_asignable"

    def test_rechaza_usuario_inactivo(self, api_client, admin_user, modelo):
        inactivo = _usuario("inactivo@test.com", RolChoices.USUARIO_RESPONSABLE, is_active=False)
        activo = crear_activo(modelo)
        resp = auth(api_client, admin_user).post(
            URL, {"activo": activo.pk, "usuario": inactivo.pk}, format="json"
        )
        assert resp.status_code == 400
        assert any(error["field"] == "usuario" for error in resp.json()["errors"])

    def test_rechaza_fecha_futura_y_anterior_a_adquisicion(
        self, api_client, admin_user, trabajador, modelo
    ):
        activo = crear_activo(modelo)
        client = auth(api_client, admin_user)
        resp = client.post(
            URL,
            {"activo": activo.pk, "usuario": trabajador.pk, "fecha_inicio": "2026-11-16"},
            format="json",
        )
        assert resp.status_code == 400
        assert resp.json()["code"] == "fecha_futura"

        resp = client.post(
            URL,
            {"activo": activo.pk, "usuario": trabajador.pk, "fecha_inicio": "2023-12-31"},
            format="json",
        )
        assert resp.status_code == 400
        assert resp.json()["code"] == "fecha_anterior_adquisicion"


@pytest.mark.django_db
@freeze_time("2026-11-15 12:00:00")
class TestCerrarYReasignar:
    def _asignar(self, client, activo, usuario, fecha="2026-11-01"):
        return client.post(
            URL,
            {"activo": activo.pk, "usuario": usuario.pk, "fecha_inicio": fecha},
            format="json",
        )

    def test_cerrar_devuelve_activo_a_disponible(self, api_client, admin_user, trabajador, modelo):
        activo = crear_activo(modelo)
        client = auth(api_client, admin_user)
        creada = self._asignar(client, activo, trabajador).json()

        resp = client.post(
            f"{URL}{creada['id']}/cerrar/", {"fecha_fin": "2026-11-10"}, format="json"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["activa"] is False
        assert body["fecha_fin"] == "2026-11-10"
        assert body["dias_asignado"] == 9
        activo.refresh_from_db()
        assert activo.estado == EstadoActivo.DISPONIBLE

        from apps.auditoria.models import RegistroAuditoria

        assert RegistroAuditoria.objects.filter(accion="ASIGNACION_CERRADA").exists()

    def test_no_se_puede_cerrar_dos_veces(self, api_client, admin_user, trabajador, modelo):
        activo = crear_activo(modelo)
        client = auth(api_client, admin_user)
        creada = self._asignar(client, activo, trabajador).json()
        assert client.post(f"{URL}{creada['id']}/cerrar/", {}, format="json").status_code == 200
        resp = client.post(f"{URL}{creada['id']}/cerrar/", {}, format="json")
        assert resp.status_code == 400
        assert resp.json()["code"] == "asignacion_cerrada"

    def test_cerrar_con_fecha_invalida(self, api_client, admin_user, trabajador, modelo):
        activo = crear_activo(modelo)
        client = auth(api_client, admin_user)
        creada = self._asignar(client, activo, trabajador, "2026-11-10").json()
        for fecha in ("2026-11-09", "2026-11-16"):
            resp = client.post(f"{URL}{creada['id']}/cerrar/", {"fecha_fin": fecha}, format="json")
            assert resp.status_code == 400

    def test_reasignar_cierra_y_abre_nueva(
        self, api_client, admin_user, trabajador, trabajador2, modelo
    ):
        activo = crear_activo(modelo)
        client = auth(api_client, admin_user)
        creada = self._asignar(client, activo, trabajador).json()

        resp = client.post(
            f"{URL}reasignar/",
            {
                "activo": activo.pk,
                "usuario": trabajador2.pk,
                "fecha_inicio": "2026-11-10",
                "observacion": "Cambio de responsable",
            },
            format="json",
        )
        assert resp.status_code == 201
        nueva = resp.json()
        assert nueva["usuario"] == trabajador2.pk
        assert nueva["activa"] is True

        anterior = AsignacionActivo.objects.get(pk=creada["id"])
        assert anterior.fecha_fin == date(2026, 11, 10)
        activo.refresh_from_db()
        assert activo.estado == EstadoActivo.ASIGNADO
        assert AsignacionActivo.objects.filter(activo=activo).count() == 2
        assert AsignacionActivo.objects.filter(activo=activo, fecha_fin__isnull=True).count() == 1

    def test_reasignar_sin_asignacion_abierta_400(self, api_client, admin_user, trabajador, modelo):
        activo = crear_activo(modelo)
        resp = auth(api_client, admin_user).post(
            f"{URL}reasignar/", {"activo": activo.pk, "usuario": trabajador.pk}, format="json"
        )
        assert resp.status_code == 400
        assert resp.json()["code"] == "sin_asignacion_abierta"


@pytest.mark.django_db
@freeze_time("2026-11-15 12:00:00")
class TestListadoYResumen:
    @pytest.fixture
    def escenario(self, admin_user, trabajador, trabajador2, modelo):
        primera = crear_activo(modelo, serial="HIST1")
        segunda = crear_activo(modelo, serial="HIST2")
        client = auth(APIClient(), admin_user)
        abierta = client.post(
            URL, {"activo": primera.pk, "usuario": trabajador.pk}, format="json"
        ).json()
        cerrada = client.post(
            URL, {"activo": segunda.pk, "usuario": trabajador2.pk}, format="json"
        ).json()
        client.post(f"{URL}{cerrada['id']}/cerrar/", {}, format="json")
        return {"abierta": abierta, "cerrada": cerrada, "primera": primera}

    def test_filtros_y_busqueda(self, api_client, admin_user, escenario):
        client = auth(api_client, admin_user)
        resp = client.get(URL, {"abierta": "true"})
        assert resp.json()["count"] == 1
        resp = client.get(URL, {"abierta": "false"})
        assert resp.json()["count"] == 1
        resp = client.get(URL, {"activo": escenario["primera"].pk})
        assert resp.json()["count"] == 1
        resp = client.get(URL, {"search": "HIST1"})
        assert resp.json()["count"] == 1
        resp = client.get(URL, {"search": "trabajador2"})
        assert resp.json()["count"] == 1

    def test_resumen_y_usuarios(self, api_client, admin_user, escenario, trabajador, modelo):
        client = auth(api_client, admin_user)
        resp = client.get(f"{URL}resumen/")
        assert resp.status_code == 200
        body = resp.json()
        assert body["asignados"] == 1
        assert body["asignaciones_historicas"] == 2
        assert body["colaboradores"] == 1
        assert body["disponibles"] == 1

        inactivo = _usuario("inactivo2@test.com", RolChoices.TECNICO, is_active=False)
        resp = client.get(f"{URL}usuarios/")
        assert resp.status_code == 200
        ids = [usuario["id"] for usuario in resp.json()]
        assert trabajador.pk in ids
        assert inactivo.pk not in ids

    def test_responsable_actual_en_activos(self, api_client, admin_user, escenario, trabajador):
        client = auth(api_client, admin_user)
        resp = client.get(f"/api/v1/activos/{escenario['primera'].pk}/")
        assert resp.json()["responsable_actual"] == trabajador.nombre_completo
        resp = client.get("/api/v1/activos/", {"search": "HIST1"})
        assert resp.json()["results"][0]["responsable_actual"] == trabajador.nombre_completo
