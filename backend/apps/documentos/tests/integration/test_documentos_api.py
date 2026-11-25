from datetime import date

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.activos.models import Activo
from apps.catalogos.models import Categoria, Marca, ModeloActivo
from apps.documentos.models import Documento
from apps.usuarios.models import RolChoices, Usuario


@pytest.fixture(autouse=True)
def media_root(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    yield


def _usuario(email, rol):
    return Usuario.objects.create_user(
        email=email, password="Pass12345!", nombre_completo=email, rol=rol
    )


@pytest.fixture
def admin_user(db):
    return _usuario("admin.doc@test.com", RolChoices.ADMINISTRADOR)


@pytest.fixture
def tecnico_user(db):
    return _usuario("tec.doc@test.com", RolChoices.TECNICO)


@pytest.fixture
def responsable_user(db):
    return _usuario("resp.doc@test.com", RolChoices.USUARIO_RESPONSABLE)


@pytest.fixture
def activo(db):
    marca = Marca.objects.create(nombre="Dell")
    categoria = Categoria.objects.create(nombre="HW")
    modelo = ModeloActivo.objects.create(marca=marca, categoria=categoria, nombre="Latitude")
    return Activo.objects.create(
        serial="SN-DOC-1",
        modelo=modelo,
        fecha_adquisicion=date(2024, 1, 1),
        codigo_qr="AST-2024-900001",
    )


def auth(client, user):
    client.force_authenticate(user=user)
    return client


def _archivo(nombre="manual.pdf"):
    return SimpleUploadedFile(nombre, b"%PDF-1.4 contenido de prueba", content_type="application/pdf")


def _crear_documento(activo, usuario, **kwargs):
    return Documento.objects.create(
        activo=activo,
        subido_por=usuario,
        nombre=kwargs.get("nombre", "Manual"),
        tipo=kwargs.get("tipo", "MANUAL"),
        archivo=_archivo(kwargs.get("archivo_nombre", "manual.pdf")),
    )


@pytest.mark.django_db
class TestDocumentosPermisos:
    def test_list_unauth_401(self, api_client):
        assert api_client.get("/api/v1/documentos/").status_code == 401

    def test_list_responsable_403(self, api_client, responsable_user):
        assert auth(api_client, responsable_user).get("/api/v1/documentos/").status_code == 403

    def test_list_tecnico_200(self, api_client, tecnico_user):
        assert auth(api_client, tecnico_user).get("/api/v1/documentos/").status_code == 200

    def test_subir_responsable_403(self, api_client, responsable_user, activo):
        auth(api_client, responsable_user)
        data = {"activo": activo.id, "nombre": "X", "tipo": "OTRO", "archivo": _archivo()}
        assert api_client.post("/api/v1/documentos/", data, format="multipart").status_code == 403


@pytest.mark.django_db
class TestDocumentosCRUD:
    def test_subir_documento(self, api_client, admin_user, activo):
        auth(api_client, admin_user)
        data = {"activo": activo.id, "nombre": "Manual", "tipo": "MANUAL", "archivo": _archivo()}
        resp = api_client.post("/api/v1/documentos/", data, format="multipart")
        assert resp.status_code == 201
        assert resp.data["nombre"] == "Manual"
        assert Documento.objects.filter(activo=activo).count() == 1

    def test_subir_extension_invalida(self, api_client, admin_user, activo):
        auth(api_client, admin_user)
        data = {
            "activo": activo.id,
            "nombre": "Malware",
            "tipo": "OTRO",
            "archivo": SimpleUploadedFile("malware.exe", b"x"),
        }
        resp = api_client.post("/api/v1/documentos/", data, format="multipart")
        assert resp.status_code == 400

    def test_list_filtra_por_activo(self, api_client, admin_user, activo):
        _crear_documento(activo, admin_user)
        auth(api_client, admin_user)
        resp = api_client.get("/api/v1/documentos/", {"activo": activo.id})
        assert resp.status_code == 200
        assert resp.data["count"] == 1

    def test_descargar(self, api_client, admin_user, activo):
        documento = _crear_documento(activo, admin_user)
        auth(api_client, admin_user)
        resp = api_client.get(f"/api/v1/documentos/{documento.id}/descargar/")
        assert resp.status_code == 200
        assert "attachment" in resp["Content-Disposition"]

    def test_eliminar(self, api_client, admin_user, activo):
        documento = _crear_documento(activo, admin_user)
        auth(api_client, admin_user)
        resp = api_client.delete(f"/api/v1/documentos/{documento.id}/")
        assert resp.status_code == 204
        assert Documento.objects.filter(pk=documento.pk).count() == 0
