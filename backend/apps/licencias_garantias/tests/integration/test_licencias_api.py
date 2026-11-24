from datetime import date

import pytest
from freezegun import freeze_time
from rest_framework.test import APIClient

from apps.auditoria.models import RegistroAuditoria
from apps.licencias_garantias.models import (
    EstadoRenovacion,
    Licencia,
    PeriodicidadRenovacion,
    Proveedor,
)
from apps.usuarios.models import RolChoices, Usuario

URL = "/api/v1/licencias/"


def _usuario(email, rol):
    return Usuario.objects.create_user(
        email=email, password="Pass12345!", nombre_completo=email, rol=rol
    )


@pytest.fixture
def admin_user(db):
    return _usuario("lic-admin@test.com", RolChoices.ADMINISTRADOR)


@pytest.fixture
def tecnico_user(db):
    return _usuario("lic-tec@test.com", RolChoices.TECNICO)


@pytest.fixture
def responsable_user(db):
    return _usuario("lic-resp@test.com", RolChoices.USUARIO_RESPONSABLE)


@pytest.fixture
def proveedor(db):
    return Proveedor.objects.create(nombre="Microsoft")


def auth(client, user):
    client.force_authenticate(user=user)
    return client


def crear_licencia(proveedor, **kwargs):
    datos = {
        "servicio": "Servicio base",
        "fecha_renovacion": date(2026, 12, 1),
        "periodicidad": PeriodicidadRenovacion.ANUAL,
        "valor": "100.00",
    }
    datos.update(kwargs)
    return Licencia.objects.create(proveedor=proveedor, **datos)


@pytest.mark.django_db
@freeze_time("2026-11-15 12:00:00")
class TestLicenciasPermisos:
    def test_anonimo_401(self):
        assert APIClient().get(URL).status_code == 401

    def test_tecnico_y_responsable_403(self, api_client, tecnico_user, responsable_user):
        assert auth(api_client, tecnico_user).get(URL).status_code == 403
        assert auth(api_client, responsable_user).get(URL).status_code == 403


@pytest.mark.django_db
@freeze_time("2026-11-15 12:00:00")
class TestLicenciasCRUD:
    def test_crear_con_proveedor_nuevo(self, api_client, admin_user):
        resp = auth(api_client, admin_user).post(
            URL,
            {
                "proveedor": "  Oracle   Cloud ",
                "servicio": "  Base de datos autónoma ",
                "periodicidad": "MENSUAL",
                "fecha_renovacion": "2026-12-01",
                "cantidad": 2,
                "valor": "100.50",
                "renovacion_automatica": True,
                "medio_pago": "Facturación electrónica",
                "cuenta_vinculada": "ti@test.com",
                "responsable_uso": "Equipo de Sistemas",
                "observacion": "Nota",
            },
            format="json",
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["proveedor_nombre"] == "Oracle Cloud"
        assert body["servicio"] == "Base de datos autónoma"
        assert body["estado_renovacion"] == EstadoRenovacion.POR_VENCER
        assert body["dias_para_renovacion"] == 16
        assert body["valor"] == "100.50"

        proveedor = Proveedor.objects.get(nombre="Oracle Cloud")
        assert proveedor.licencias.count() == 1
        assert RegistroAuditoria.objects.filter(
            accion="LICENCIA_CREADA", entidad_id=str(body["id"])
        ).exists()
        assert Licencia.objects.get(pk=body["id"]).history.first().history_user == admin_user

    def test_crear_reutiliza_proveedor_sin_mayusculas(self, api_client, admin_user, proveedor):
        resp = auth(api_client, admin_user).post(
            URL,
            {
                "proveedor": "microsoft",
                "servicio": "Azure DevOps",
                "fecha_renovacion": "2026-12-01",
            },
            format="json",
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["proveedor"] == proveedor.pk
        assert Proveedor.objects.count() == 1
        assert body["cantidad"] == 1
        assert body["renovacion_automatica"] is False

    def test_crear_reactiva_proveedor_inactivo(self, api_client, admin_user):
        Proveedor.objects.create(nombre="Google", is_active=False)
        resp = auth(api_client, admin_user).post(
            URL,
            {
                "proveedor": "google",
                "servicio": "Workspace",
                "fecha_renovacion": "2027-01-01",
            },
            format="json",
        )
        assert resp.status_code == 201
        assert Proveedor.objects.get(nombre="Google").is_active is True

    def test_actualizar_licencia_y_proveedor(self, api_client, admin_user, proveedor):
        licencia = crear_licencia(proveedor)
        resp = auth(api_client, admin_user).patch(
            f"{URL}{licencia.pk}/",
            {"proveedor": "Google", "servicio": "Workspace", "valor": "250.00"},
            format="json",
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["proveedor_nombre"] == "Google"
        assert body["servicio"] == "Workspace"
        assert body["valor"] == "250.00"
        assert RegistroAuditoria.objects.filter(
            accion="LICENCIA_ACTUALIZADA", entidad_id=str(licencia.pk)
        ).exists()

    def test_renovar_actualiza_fecha_y_valor(self, api_client, admin_user, proveedor):
        licencia = crear_licencia(proveedor)
        resp = auth(api_client, admin_user).post(
            f"{URL}{licencia.pk}/renovar/",
            {"fecha_renovacion": "2027-12-01", "valor": "120.00"},
            format="json",
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["fecha_renovacion"] == "2027-12-01"
        assert body["valor"] == "120.00"
        assert body["estado_renovacion"] == EstadoRenovacion.VIGENTE
        assert body["dias_para_renovacion"] == 381
        assert RegistroAuditoria.objects.filter(
            accion="LICENCIA_RENOVADA", entidad_id=str(licencia.pk)
        ).exists()
        licencia.refresh_from_db()
        assert licencia.history.count() == 2

    def test_renovar_fecha_pasada_400(self, api_client, admin_user, proveedor):
        licencia = crear_licencia(proveedor)
        resp = auth(api_client, admin_user).post(
            f"{URL}{licencia.pk}/renovar/",
            {"fecha_renovacion": "2026-11-14"},
            format="json",
        )
        assert resp.status_code == 400
        assert resp.json()["errors"][0]["field"] == "fecha_renovacion"

    def test_renovar_inactiva_400(self, api_client, admin_user, proveedor):
        licencia = crear_licencia(proveedor, is_active=False)
        resp = auth(api_client, admin_user).post(
            f"{URL}{licencia.pk}/renovar/",
            {"fecha_renovacion": "2027-12-01"},
            format="json",
        )
        assert resp.status_code == 400
        assert resp.json()["code"] == "licencia_inactiva"

    def test_inactivar_y_reactivar(self, api_client, admin_user, proveedor):
        licencia = crear_licencia(proveedor)
        client = auth(api_client, admin_user)

        resp = client.post(f"{URL}{licencia.pk}/inactivar/")
        assert resp.status_code == 200
        assert resp.json()["estado_renovacion"] == EstadoRenovacion.INACTIVA

        resp = client.post(f"{URL}{licencia.pk}/reactivar/")
        assert resp.status_code == 200
        assert resp.json()["is_active"] is True

        acciones = set(
            RegistroAuditoria.objects.filter(entidad_id=str(licencia.pk)).values_list(
                "accion", flat=True
            )
        )
        assert {"LICENCIA_INACTIVADA", "LICENCIA_REACTIVADA"} <= acciones


@pytest.mark.django_db
@freeze_time("2026-11-15 12:00:00")
class TestLicenciasListadoYResumen:
    @pytest.fixture
    def escenario(self, proveedor):
        return {
            "vencida": crear_licencia(proveedor, fecha_renovacion=date(2026, 10, 1)),
            "por_vencer": crear_licencia(
                proveedor,
                servicio="Mensual",
                periodicidad=PeriodicidadRenovacion.MENSUAL,
                fecha_renovacion=date(2026, 11, 20),
                valor="10.00",
                renovacion_automatica=True,
            ),
            "vigente": crear_licencia(
                proveedor,
                servicio="Bienal",
                periodicidad=PeriodicidadRenovacion.BIENAL,
                fecha_renovacion=date(2027, 6, 1),
            ),
            "inactiva": crear_licencia(
                proveedor,
                servicio="Inactiva",
                fecha_renovacion=date(2027, 6, 1),
                valor="1000.00",
                is_active=False,
            ),
        }

    def test_filtro_por_estado_renovacion(self, api_client, admin_user, escenario):
        client = auth(api_client, admin_user)
        casos = {
            EstadoRenovacion.VENCIDA: 1,
            EstadoRenovacion.POR_VENCER: 1,
            EstadoRenovacion.VIGENTE: 1,
            EstadoRenovacion.INACTIVA: 1,
        }
        for estado, esperado in casos.items():
            resp = client.get(URL, {"estado_renovacion": estado})
            assert resp.status_code == 200
            assert resp.json()["count"] == esperado

    def test_filtro_por_proveedor_busqueda_y_activas(self, api_client, admin_user, escenario):
        otro = Proveedor.objects.create(nombre="Google")
        crear_licencia(otro, servicio="Workspace")
        client = auth(api_client, admin_user)

        resp = client.get(URL, {"proveedor": otro.pk})
        assert resp.json()["count"] == 1

        resp = client.get(URL, {"search": "Workspace"})
        assert resp.json()["count"] == 1

        resp = client.get(URL, {"is_active": "false"})
        assert resp.json()["count"] == 1

    def test_resumen_calcula_costos_anualizados(self, api_client, admin_user, escenario):
        resp = auth(api_client, admin_user).get(f"{URL}resumen/")
        assert resp.status_code == 200
        body = resp.json()

        assert body["total"] == 4
        assert body["activas"] == 3
        assert body["inactivas"] == 1
        assert body["vencidas"] == 1
        assert body["por_vencer"] == 1
        assert body["renovacion_automatica"] == 1
        assert body["costo_anual_estimado"] == "270.00"
        assert body["costo_por_vencer"] == "10.00"
        assert {"periodicidad": "MENSUAL", "total": 1} in body["por_periodicidad"]

    def test_proveedores_solo_activos(self, api_client, admin_user, proveedor):
        Proveedor.objects.create(nombre="Antiguo", is_active=False)
        resp = auth(api_client, admin_user).get(f"{URL}proveedores/")
        assert resp.status_code == 200
        assert resp.json() == [{"id": proveedor.pk, "nombre": "Microsoft"}]
