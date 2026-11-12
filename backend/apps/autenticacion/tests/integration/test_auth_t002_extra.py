import pytest
from django.urls import reverse

from apps.auditoria.models import AccionAuditoria, RegistroAuditoria
from apps.autenticacion.models import DispositivoMFA
from apps.usuarios.models import RolChoices, Usuario


@pytest.mark.django_db
def test_mfa_rechazado_registra_auditoria(api_client, settings):
    settings.MFA_ENFORCED = False
    u = Usuario.objects.create_user(
        email="mfar@test.com", password="Password123!", nombre_completo="M", rol=RolChoices.TECNICO
    )
    from apps.autenticacion.crypto import cifrar_secreto, generar_secreto_totp

    secret = generar_secreto_totp()
    DispositivoMFA.objects.create(
        usuario=u, secreto_cifrado=cifrar_secreto(secret), confirmado=True
    )
    resp = api_client.post(
        reverse("autenticacion:login"),
        {"email": "mfar@test.com", "password": "Password123!"},
        format="json",
    )
    assert resp.data["status"] == "mfa_required"
    token = resp.data["mfa_token"]
    resp2 = api_client.post(
        reverse("autenticacion:mfa-verify"), {"mfa_token": token, "code": "000000"}, format="json"
    )
    assert resp2.status_code == 401
    assert RegistroAuditoria.objects.filter(accion=AccionAuditoria.MFA_RECHAZADO).exists()


@pytest.mark.django_db
def test_reset_mfa_lleva_a_setup_en_login(api_client, settings):
    settings.MFA_ENFORCED = True
    admin = Usuario.objects.create_user(
        email="adm@t.com",
        password="AdminPass123!",
        nombre_completo="A",
        rol=RolChoices.ADMINISTRADOR,
    )
    u = Usuario.objects.create_user(
        email="usr@t.com", password="UserPass123!", nombre_completo="U", rol=RolChoices.TECNICO
    )
    from apps.autenticacion.crypto import cifrar_secreto, generar_secreto_totp

    DispositivoMFA.objects.create(
        usuario=u, secreto_cifrado=cifrar_secreto(generar_secreto_totp()), confirmado=True
    )
    api_client.force_authenticate(user=admin)
    resp = api_client.post(f"/api/v1/usuarios/{u.id}/reset_mfa/")
    assert resp.status_code == 204
    api_client.force_authenticate(user=None)
    resp2 = api_client.post(
        reverse("autenticacion:login"),
        {"email": "usr@t.com", "password": "UserPass123!"},
        format="json",
    )
    assert resp2.status_code == 200
    assert resp2.data["status"] == "mfa_setup_required"


@pytest.mark.django_db
def test_login_email_muy_largo_no_500(api_client):
    largo = ("a" * 300) + "@test.com"
    resp = api_client.post(
        reverse("autenticacion:login"), {"email": largo, "password": "x"}, format="json"
    )
    assert resp.status_code in {400, 401}
    assert resp.status_code != 500


@pytest.mark.django_db
def test_login_email_con_arroba_65_a_254_no_500_y_entidad_id_vacio(api_client):
    # 65 chars before @ + @ + domain => length 65+1+8=74 (>=65 chars with @, <=254)
    local = "a" * 65
    email = f"{local}@test.com"
    assert 65 <= len(email) <= 254
    resp = api_client.post(
        reverse("autenticacion:login"), {"email": email, "password": "x"}, format="json"
    )
    assert resp.status_code in {400, 401}
    assert resp.status_code != 500
    evento = RegistroAuditoria.objects.filter(accion=AccionAuditoria.LOGIN_FALLIDO).latest("id")
    # sanitizar_entidad_id: solo si contiene '@' y len <= 64 -> vacío si >64
    assert evento.entidad_id == ""
