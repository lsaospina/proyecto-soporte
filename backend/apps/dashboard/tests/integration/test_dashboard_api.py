from datetime import date
from decimal import Decimal

import pytest
from freezegun import freeze_time
from rest_framework.test import APIClient

from apps.activos.models import Activo, EstadoActivo
from apps.catalogos.models import Categoria, Marca, ModeloActivo
from apps.mantenimientos.models import (
    EstadoMantenimiento,
    Mantenimiento,
    TipoMantenimiento,
)
from apps.usuarios.models import RolChoices, Usuario

URL = "/api/v1/dashboard/resumen/"


def _usuario(email, rol):
    return Usuario.objects.create_user(
        email=email, password="Pass12345!", nombre_completo=email, rol=rol
    )


@pytest.fixture
def admin_user(db):
    return _usuario("dash-admin@test.com", RolChoices.ADMINISTRADOR)


@pytest.fixture
def tecnico_user(db):
    return _usuario("dash-tec@test.com", RolChoices.TECNICO)


@pytest.fixture
def responsable_user(db):
    return _usuario("dash-resp@test.com", RolChoices.USUARIO_RESPONSABLE)


@pytest.fixture
def datos(db):
    marca = Marca.objects.create(nombre="Dell")
    categoria = Categoria.objects.create(nombre="Computo")
    modelo = ModeloActivo.objects.create(marca=marca, categoria=categoria, nombre="Latitude")

    def activo(serial, estado, valor, is_active=True):
        return Activo.objects.create(
            serial=serial,
            modelo=modelo,
            fecha_adquisicion=date(2024, 1, 1),
            valor_adquisicion=Decimal(valor),
            estado=estado,
            codigo_qr=f"QR-{serial}",
            is_active=is_active,
        )

    disponible = activo("A-DISP", EstadoActivo.DISPONIBLE, "100.00")
    en_mant = activo("A-MANT", EstadoActivo.EN_MANTENIMIENTO, "200.00")
    baja = activo("A-BAJA", EstadoActivo.DADO_DE_BAJA, "300.00")
    inactivo = activo("A-INAC", EstadoActivo.ASIGNADO, "400.00", is_active=False)

    def mantenimiento(activo_obj, fecha, **kwargs):
        return Mantenimiento.objects.create(activo=activo_obj, fecha_programada=fecha, **kwargs)

    mantenimiento(
        disponible,
        date(2026, 2, 10),
        estado=EstadoMantenimiento.COMPLETADO,
        fecha_realizacion=date(2026, 2, 10),
        costo=Decimal("50.00"),
    )
    mantenimiento(disponible, date(2026, 10, 1))
    mantenimiento(disponible, date(2026, 11, 20))
    incumplido = mantenimiento(disponible, date(2026, 9, 1))
    mantenimiento(
        disponible,
        date(2026, 12, 1),
        reprogramacion_de=incumplido,
    )
    mantenimiento(
        en_mant,
        date(2026, 6, 1),
        estado=EstadoMantenimiento.CANCELADO,
        motivo_cancelacion="Equipo retirado",
    )
    mantenimiento(
        baja,
        date(2026, 11, 10),
        tipo=TipoMantenimiento.CORRECTIVO,
        estado=EstadoMantenimiento.COMPLETADO,
        fecha_realizacion=date(2026, 11, 10),
        costo=Decimal("30.00"),
        observacion="Falla de pantalla",
    )
    return {
        "disponible": disponible,
        "en_mant": en_mant,
        "baja": baja,
        "inactivo": inactivo,
    }


def auth(client, user):
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
@freeze_time("2026-11-15 12:00:00")
class TestDashboardResumen:
    def test_requiere_autenticacion(self):
        resp = APIClient().get(URL)
        assert resp.status_code == 401

    def test_admin_recibe_inventario_y_mantenimientos(self, api_client, admin_user, datos):
        resp = auth(api_client, admin_user).get(URL)
        assert resp.status_code == 200
        body = resp.json()

        assert body["hoy"] == "2026-11-15"
        assert body["anio"] == 2026

        activos = body["activos"]
        assert activos["total"] == 3
        assert activos["operativos"] == 1
        assert activos["en_mantenimiento"] == 1
        assert activos["dados_de_baja"] == 1
        assert activos["inactivos"] == 1
        assert activos["valor_total"] == "300.00"
        assert {e["estado"]: e["total"] for e in activos["por_estado"]} == {
            "DISPONIBLE": 1,
            "ASIGNADO": 0,
            "EN_MANTENIMIENTO": 1,
            "DADO_DE_BAJA": 1,
        }
        assert activos["por_categoria"] == [{"nombre": "Computo", "total": 2}]
        assert activos["por_marca"] == [{"nombre": "Dell", "total": 2}]
        assert len(activos["ultimas_adquisiciones"]) == 2

        mantenimientos = body["mantenimientos"]
        preventivos = mantenimientos["preventivos_anio"]
        assert preventivos["total"] == 6
        assert preventivos["cancelados"] == 1
        assert preventivos["agendados"] == 5
        assert preventivos["completados"] == 1
        assert preventivos["vencidos"] == 1
        assert preventivos["incumplidos"] == 1
        assert preventivos["pendientes"] == 2
        assert preventivos["porcentaje_cumplimiento"] == 20

        assert len(mantenimientos["mensual"]) == 12
        assert mantenimientos["proximos"][0]["fecha_programada"] == "2026-11-20"
        assert mantenimientos["proximos"][0]["dias_restantes"] == 5
        assert mantenimientos["vencidos"][0]["fecha_programada"] == "2026-10-01"
        assert mantenimientos["vencidos"][0]["dias_atraso"] == 45

        correctivos = mantenimientos["correctivos"]
        assert correctivos["registrados_30_dias"] == 1
        assert correctivos["costo_30_dias"] == "30.00"
        assert correctivos["recientes"][0]["activo_serial"] == datos["baja"].serial

        assert mantenimientos["activos_sin_preventivo"]["total"] == 1
        assert mantenimientos["costo_anio"] == "80.00"

    def test_tecnico_recibe_el_mismo_alcance(self, api_client, tecnico_user, datos):
        resp = auth(api_client, tecnico_user).get(URL)
        assert resp.status_code == 200
        body = resp.json()
        assert body["activos"]["valor_total"] == "300.00"
        assert body["mantenimientos"] is not None

    def test_responsable_solo_ve_inventario(self, api_client, responsable_user, datos):
        resp = auth(api_client, responsable_user).get(URL)
        assert resp.status_code == 200
        body = resp.json()
        assert body["mantenimientos"] is None
        assert body["activos"]["valor_total"] is None
        assert body["activos"]["total"] == 3
        assert body["activos"]["por_categoria"] == [{"nombre": "Computo", "total": 2}]

    def test_sin_datos_devuelve_ceros(self, api_client, admin_user):
        resp = auth(api_client, admin_user).get(URL)
        assert resp.status_code == 200
        body = resp.json()
        assert body["activos"]["total"] == 0
        assert body["activos"]["valor_total"] == "0.00"
        assert body["mantenimientos"]["preventivos_anio"]["porcentaje_cumplimiento"] == 0
        assert body["mantenimientos"]["proximos"] == []
        assert body["mantenimientos"]["vencidos"] == []
