from datetime import date

import pytest
from freezegun import freeze_time
from rest_framework.test import APIClient

from apps.activos.models import Activo
from apps.auditoria.models import RegistroAuditoria
from apps.catalogos.models import Categoria, Marca, ModeloActivo
from apps.mantenimientos.models import Mantenimiento
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
    return _usuario("admin2@test.com", RolChoices.ADMINISTRADOR)


@pytest.fixture
def tecnico_user(db):
    return _usuario("tec2@test.com", RolChoices.TECNICO)


@pytest.fixture
def responsable_user(db):
    return _usuario("resp2@test.com", RolChoices.USUARIO_RESPONSABLE)


@pytest.fixture
def activo(db):
    marca = Marca.objects.create(nombre="HP")
    categoria = Categoria.objects.create(nombre="HW2")
    modelo = ModeloActivo.objects.create(marca=marca, categoria=categoria, nombre="EliteBook")
    return Activo.objects.create(
        serial="COR1",
        modelo=modelo,
        fecha_adquisicion=date(2024, 1, 1),
        codigo_qr="AST-2024-000201",
    )


def auth(client, user):
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
@freeze_time("2026-11-15 12:00:00")
class TestCorrectivos:
    def test_create_tecnico_201(self, api_client, tecnico_user, activo):
        resp = auth(api_client, tecnico_user).post(
            "/api/v1/mantenimientos/correctivos/",
            {
                "activo": activo.pk,
                "fecha_programada": "2026-11-10",
                "fecha_seguimiento": "2026-12-01",
                "observacion": "No enciende; se cambió la fuente.",
            },
            format="json",
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["tipo"] == "CORRECTIVO"
        assert body["estado"] == "COMPLETADO"
        assert body["fecha_seguimiento"] == "2026-12-01"
        assert body["observacion"].startswith("No enciende")

    def test_create_responsable_403(self, api_client, responsable_user, activo):
        resp = auth(api_client, responsable_user).post(
            "/api/v1/mantenimientos/correctivos/",
            {
                "activo": activo.pk,
                "fecha_programada": "2026-11-10",
                "fecha_seguimiento": "2026-12-01",
                "observacion": "Falla",
            },
            format="json",
        )
        assert resp.status_code == 403

    def test_fecha_evento_futura_400(self, api_client, tecnico_user, activo):
        resp = auth(api_client, tecnico_user).post(
            "/api/v1/mantenimientos/correctivos/",
            {
                "activo": activo.pk,
                "fecha_programada": "2026-11-20",
                "fecha_seguimiento": "2026-12-01",
                "observacion": "Falla",
            },
            format="json",
        )
        assert resp.status_code == 400

    def test_seguimiento_anterior_400(self, api_client, tecnico_user, activo):
        resp = auth(api_client, tecnico_user).post(
            "/api/v1/mantenimientos/correctivos/",
            {
                "activo": activo.pk,
                "fecha_programada": "2026-11-10",
                "fecha_seguimiento": "2026-11-01",
                "observacion": "Falla",
            },
            format="json",
        )
        assert resp.status_code == 400

    def test_list_filtra_por_tipo(self, api_client, tecnico_user, activo):
        Mantenimiento.objects.create(
            activo=activo,
            fecha_programada=date(2026, 11, 10),
            tipo="CORRECTIVO",
            observacion="Falla",
            fecha_seguimiento=date(2026, 12, 1),
            estado="COMPLETADO",
        )
        Mantenimiento.objects.create(
            activo=activo,
            fecha_programada=date(2026, 11, 20),
            tipo="PREVENTIVO",
        )
        resp = auth(api_client, tecnico_user).get(
            "/api/v1/mantenimientos/?tipo=CORRECTIVO&anio=2026&mes=11"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["tipo"] == "CORRECTIVO"

    def test_resumen_no_cuenta_correctivos(self, api_client, tecnico_user, activo):
        Mantenimiento.objects.create(
            activo=activo,
            fecha_programada=date(2026, 11, 10),
            tipo="CORRECTIVO",
            observacion="Falla",
            fecha_seguimiento=date(2026, 12, 1),
            estado="COMPLETADO",
        )
        resp = auth(api_client, tecnico_user).get("/api/v1/mantenimientos/resumen/?anio=2026")
        assert resp.status_code == 200
        assert resp.json()["meses"][10]["agendados"] == 0

    def test_auditoria_correctivo(self, api_client, tecnico_user, activo):
        resp = auth(api_client, tecnico_user).post(
            "/api/v1/mantenimientos/correctivos/",
            {
                "activo": activo.pk,
                "fecha_programada": "2026-11-10",
                "fecha_seguimiento": "2026-12-01",
                "observacion": "Falla",
            },
            format="json",
        )
        assert resp.status_code == 201
        assert RegistroAuditoria.objects.filter(
            accion="MANTENIMIENTO_CORRECTIVO_REGISTRADO",
            entidad_id=str(resp.json()["id"]),
        ).exists()
