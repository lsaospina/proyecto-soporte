from datetime import date
from decimal import Decimal

import pytest
from freezegun import freeze_time
from rest_framework.test import APIClient

from apps.activos.models import Activo
from apps.catalogos.models import Categoria, Marca, ModeloActivo
from apps.mantenimientos.models import (
    EstadoMantenimiento,
    Mantenimiento,
    SituacionMantenimiento,
)
from apps.usuarios.models import RolChoices, Usuario


@pytest.fixture
def api_client():
    return APIClient()


def _usuario(email, rol):
    return Usuario.objects.create_user(
        email=email, password="Pass12345!", nombre_completo=email, rol=rol
    )


@pytest.fixture
def admin_user(db):
    return _usuario("admin@test.com", RolChoices.ADMINISTRADOR)


@pytest.fixture
def tecnico_user(db):
    return _usuario("tec@test.com", RolChoices.TECNICO)


@pytest.fixture
def responsable_user(db):
    return _usuario("resp@test.com", RolChoices.USUARIO_RESPONSABLE)


@pytest.fixture
def activo(db):
    marca = Marca.objects.create(nombre="Dell")
    categoria = Categoria.objects.create(nombre="HW")
    modelo = ModeloActivo.objects.create(marca=marca, categoria=categoria, nombre="Latitude")
    return Activo.objects.create(
        serial="SN1", modelo=modelo, fecha_adquisicion=date(2024, 1, 1), codigo_qr="AST-2024-000001"
    )


def auth(client, user):
    client.force_authenticate(user=user)
    return client


def crear(activo, fecha, **kwargs):
    kwargs.setdefault("estado", EstadoMantenimiento.PROGRAMADO)
    return Mantenimiento.objects.create(activo=activo, fecha_programada=fecha, **kwargs)


@pytest.mark.django_db
@freeze_time("2026-11-15 12:00:00")
class TestMantenimientosPermisos:
    def test_list_unauth_401(self, api_client):
        assert api_client.get("/api/v1/mantenimientos/").status_code == 401

    def test_list_responsable_403(self, api_client, responsable_user):
        assert auth(api_client, responsable_user).get("/api/v1/mantenimientos/").status_code == 403

    def test_list_tecnico_200(self, api_client, tecnico_user):
        assert auth(api_client, tecnico_user).get("/api/v1/mantenimientos/").status_code == 200

    def test_create_tecnico_201(self, api_client, tecnico_user, activo):
        resp = auth(api_client, tecnico_user).post(
            "/api/v1/mantenimientos/",
            {"activo": activo.pk, "fecha_programada": "2026-11-20"},
            format="json",
        )
        assert resp.status_code == 201
        assert resp.json()["tipo"] == "PREVENTIVO"

    def test_create_fecha_pasada_400(self, api_client, tecnico_user, activo):
        resp = auth(api_client, tecnico_user).post(
            "/api/v1/mantenimientos/",
            {"activo": activo.pk, "fecha_programada": "2026-11-14"},
            format="json",
        )
        assert resp.status_code == 400

    def test_cancelar_tecnico_403(self, api_client, tecnico_user, activo):
        m = crear(activo, date(2026, 11, 20))
        resp = auth(api_client, tecnico_user).post(
            f"/api/v1/mantenimientos/{m.pk}/cancelar/", {"motivo": "x"}, format="json"
        )
        assert resp.status_code == 403

    def test_cancelar_admin_200(self, api_client, admin_user, activo):
        m = crear(activo, date(2026, 11, 20))
        resp = auth(api_client, admin_user).post(
            f"/api/v1/mantenimientos/{m.pk}/cancelar/", {"motivo": "Equipo retirado"}, format="json"
        )
        assert resp.status_code == 200
        assert resp.json()["estado"] == "CANCELADO"

    def test_cancelar_sin_motivo_400(self, api_client, admin_user, activo):
        m = crear(activo, date(2026, 11, 20))
        resp = auth(api_client, admin_user).post(
            f"/api/v1/mantenimientos/{m.pk}/cancelar/", {"motivo": " "}, format="json"
        )
        assert resp.status_code == 400


@pytest.mark.django_db
@freeze_time("2026-11-15 12:00:00")
class TestCompletar:
    def test_completar_ok(self, api_client, tecnico_user, activo):
        m = crear(activo, date(2026, 11, 10))
        resp = auth(api_client, tecnico_user).post(
            f"/api/v1/mantenimientos/{m.pk}/completar/",
            {
                "fecha_realizacion": "2026-11-14",
                "tecnico": tecnico_user.pk,
                "costo": "1500.00",
                "observacion": "Limpieza",
            },
            format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["situacion"] == SituacionMantenimiento.COMPLETADO
        m.refresh_from_db()
        assert m.estado == EstadoMantenimiento.COMPLETADO
        assert m.costo == Decimal("1500.00")

    def test_completar_fecha_futura_400(self, api_client, tecnico_user, activo):
        m = crear(activo, date(2026, 11, 10))
        resp = auth(api_client, tecnico_user).post(
            f"/api/v1/mantenimientos/{m.pk}/completar/",
            {"fecha_realizacion": "2026-11-16", "tecnico": tecnico_user.pk, "costo": "1"},
            format="json",
        )
        assert resp.status_code == 400

    def test_completar_incumplido_400(self, api_client, tecnico_user, activo):
        original = crear(activo, date(2026, 10, 10))
        crear(activo, date(2026, 11, 20), reprogramacion_de=original)
        resp = auth(api_client, tecnico_user).post(
            f"/api/v1/mantenimientos/{original.pk}/completar/",
            {"fecha_realizacion": "2026-11-15", "tecnico": tecnico_user.pk, "costo": "1"},
            format="json",
        )
        assert resp.status_code == 400


@pytest.mark.django_db
@freeze_time("2026-11-15 12:00:00")
class TestReprogramar:
    def test_reprogramar_pendiente_mueve_200(self, api_client, tecnico_user, activo):
        m = crear(activo, date(2026, 11, 20))
        resp = auth(api_client, tecnico_user).post(
            f"/api/v1/mantenimientos/{m.pk}/reprogramar/",
            {"fecha_programada": "2026-11-25"},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == m.pk
        m.refresh_from_db()
        assert m.fecha_programada == date(2026, 11, 25)

    def test_reprogramar_vencido_crea_201(self, api_client, tecnico_user, activo):
        original = crear(activo, date(2026, 11, 10))
        resp = auth(api_client, tecnico_user).post(
            f"/api/v1/mantenimientos/{original.pk}/reprogramar/",
            {"fecha_programada": "2026-12-10"},
            format="json",
        )
        assert resp.status_code == 201
        nuevo_id = resp.json()["id"]
        assert nuevo_id != original.pk

        original.refresh_from_db()
        assert original.situacion == SituacionMantenimiento.INCUMPLIDO
        assert original.es_evidencia is True
        nuevo = Mantenimiento.objects.get(pk=nuevo_id)
        assert nuevo.reprogramacion_de_id == original.pk
        assert nuevo.situacion == SituacionMantenimiento.PENDIENTE

    def test_reprogramar_incumplido_400(self, api_client, tecnico_user, activo):
        original = crear(activo, date(2026, 10, 10))
        crear(activo, date(2026, 11, 20), reprogramacion_de=original)
        resp = auth(api_client, tecnico_user).post(
            f"/api/v1/mantenimientos/{original.pk}/reprogramar/",
            {"fecha_programada": "2026-12-10"},
            format="json",
        )
        assert resp.status_code == 400


@pytest.mark.django_db
@freeze_time("2026-11-15 12:00:00")
class TestResumenYCalendario:
    def test_resumen_anual(self, api_client, tecnico_user, activo):
        crear(activo, date(2026, 11, 10), estado=EstadoMantenimiento.COMPLETADO)
        crear(activo, date(2026, 11, 20))
        crear(activo, date(2026, 12, 5))
        resp = auth(api_client, tecnico_user).get("/api/v1/mantenimientos/resumen/?anio=2026")
        assert resp.status_code == 200
        data = resp.json()
        assert data["hoy"] == "2026-11-15"
        noviembre = data["meses"][10]
        assert noviembre["agendados"] == 2
        assert noviembre["completados"] == 1
        assert noviembre["porcentaje_cumplimiento"] == 50
        diciembre = data["meses"][11]
        assert diciembre["agendados"] == 1

    def test_calendario_mensual(self, api_client, tecnico_user, activo):
        crear(activo, date(2026, 11, 20))
        resp = auth(api_client, tecnico_user).get(
            "/api/v1/mantenimientos/calendario/?anio=2026&mes=11"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["hoy"] == "2026-11-15"
        assert len(data["mantenimientos"]) == 1
        assert data["mantenimientos"][0]["situacion"] == "PENDIENTE"

    def test_calendario_mes_invalido_400(self, api_client, tecnico_user):
        resp = auth(api_client, tecnico_user).get(
            "/api/v1/mantenimientos/calendario/?anio=2026&mes=13"
        )
        assert resp.status_code == 400

    def test_list_filtros(self, api_client, tecnico_user, activo):
        crear(activo, date(2026, 11, 10))
        crear(activo, date(2026, 12, 10))
        resp = auth(api_client, tecnico_user).get(
            "/api/v1/mantenimientos/?anio=2026&mes=11&situacion=VENCIDO&search=SN1"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert data["hoy"] == "2026-11-15"

    def test_auditoria_eventos(self, api_client, tecnico_user, activo):
        from apps.auditoria.models import RegistroAuditoria

        m = crear(activo, date(2026, 11, 10))
        auth(api_client, tecnico_user).post(
            f"/api/v1/mantenimientos/{m.pk}/completar/",
            {"fecha_realizacion": "2026-11-15", "tecnico": tecnico_user.pk, "costo": "1"},
            format="json",
        )
        assert RegistroAuditoria.objects.filter(
            accion="MANTENIMIENTO_COMPLETADO", entidad_id=str(m.pk)
        ).exists()
