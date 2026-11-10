import pyotp
import pytest
from django.conf import settings
from django.urls import reverse

from apps.autenticacion.crypto import cifrar_secreto
from apps.autenticacion.models import DispositivoMFA
from apps.usuarios.models import RolChoices, Usuario


@pytest.fixture
def usuario_prueba(db):
    """Crea un usuario estándar para pruebas de integración."""
    user = Usuario.objects.create_user(
        email="usuario@empresa.com",
        password="Password123!",
        nombre_completo="Usuario de Prueba",
        rol=RolChoices.TECNICO,
    )
    return user


@pytest.fixture
def usuario_admin(db):
    """Crea un usuario administrador."""
    return Usuario.objects.create_user(
        email="admin@empresa.com",
        password="AdminPassword123!",
        nombre_completo="Admin Test",
        rol=RolChoices.ADMINISTRADOR,
    )


def test_login_credenciales_invalidas_mensaje_generico(api_client, usuario_prueba):
    """Prueba que el mensaje sea siempre genérico tanto para correo inexistente como clave incorrecta."""
    url = reverse("autenticacion:login")

    # Contraseña incorrecta
    resp_pass = api_client.post(
        url, {"email": "usuario@empresa.com", "password": "ClaveIncorrecta"}
    )
    assert resp_pass.status_code == 401
    assert resp_pass.data["detail"] == "Credenciales inválidas."

    # Correo inexistente
    resp_email = api_client.post(url, {"email": "noexiste@empresa.com", "password": "Password123!"})
    assert resp_email.status_code == 401
    assert resp_email.data["detail"] == "Credenciales inválidas."


def test_bloqueo_tras_5_fallos_consecutivos(api_client, usuario_prueba):
    """Prueba que 5 fallos consecutivos bloqueen la cuenta durante 15 minutos."""
    url = reverse("autenticacion:login")

    for _ in range(4):
        resp = api_client.post(url, {"email": "usuario@empresa.com", "password": "ClaveIncorrecta"})
        assert resp.status_code == 401

    usuario_prueba.refresh_from_db()
    assert usuario_prueba.intentos_fallidos == 4
    assert usuario_prueba.esta_bloqueado is False

    # El 5to fallo bloquea
    resp_bloqueo = api_client.post(
        url, {"email": "usuario@empresa.com", "password": "ClaveIncorrecta"}
    )
    assert resp_bloqueo.status_code == 403
    assert resp_bloqueo.data["code"] == "cuenta_bloqueada"

    usuario_prueba.refresh_from_db()
    assert usuario_prueba.intentos_fallidos == 5
    assert usuario_prueba.esta_bloqueado is True


def test_login_flujo_mfa_setup_y_confirm(api_client, usuario_prueba):
    """
    Flujo completo para usuario sin segundo factor (MFA_ENFORCED=True):
    1. Login -> mfa_setup_required
    2. mfa/setup -> secret y otpauth_uri
    3. mfa/confirm con código TOTP -> activa MFA, devuelve 10 códigos de recuperación y cookie refresh
    """
    login_url = reverse("autenticacion:login")
    resp_login = api_client.post(
        login_url, {"email": "usuario@empresa.com", "password": "Password123!"}
    )
    assert resp_login.status_code == 200
    assert resp_login.data["status"] == "mfa_setup_required"
    mfa_token = resp_login.data["mfa_token"]
    assert mfa_token is not None

    # 2. Setup
    setup_url = reverse("autenticacion:mfa-setup")
    resp_setup = api_client.post(setup_url, {"mfa_token": mfa_token})
    assert resp_setup.status_code == 200
    secret = resp_setup.data["secret"]
    otpauth_uri = resp_setup.data["otpauth_uri"]
    assert secret is not None
    assert otpauth_uri.startswith("otpauth://")

    # 3. Confirmar con código válido
    confirm_url = reverse("autenticacion:mfa-confirm")
    codigo_totp = pyotp.TOTP(secret).now()
    resp_confirm = api_client.post(confirm_url, {"mfa_token": mfa_token, "code": codigo_totp})
    assert resp_confirm.status_code == 200
    assert resp_confirm.data["status"] == "ok"
    assert "access" in resp_confirm.data
    assert len(resp_confirm.data["recovery_codes"]) == 10
    assert "refresh_token" in resp_confirm.cookies

    # Verificar que el dispositivo quedó confirmado en BD
    usuario_prueba.refresh_from_db()
    assert usuario_prueba.dispositivo_mfa.confirmado is True
    assert usuario_prueba.dispositivo_mfa.codigos_recuperacion.count() == 10


def test_login_con_mfa_required_y_verify_totp(api_client, usuario_prueba):
    """Flujo habitual de usuario que ya tiene segundo factor configurado."""
    secret = pyotp.random_base32()
    DispositivoMFA.objects.create(
        usuario=usuario_prueba,
        secreto_cifrado=cifrar_secreto(secret),
        confirmado=True,
    )

    # Paso 1: credenciales
    login_url = reverse("autenticacion:login")
    resp_login = api_client.post(
        login_url, {"email": "usuario@empresa.com", "password": "Password123!"}
    )
    assert resp_login.status_code == 200
    assert resp_login.data["status"] == "mfa_required"
    mfa_token = resp_login.data["mfa_token"]

    # Paso 2: verificar TOTP
    verify_url = reverse("autenticacion:mfa-verify")
    codigo_totp = pyotp.TOTP(secret).now()
    resp_verify = api_client.post(verify_url, {"mfa_token": mfa_token, "code": codigo_totp})
    assert resp_verify.status_code == 200
    assert resp_verify.data["status"] == "ok"
    assert "access" in resp_verify.data
    assert "refresh_token" in resp_verify.cookies


def test_verify_codigo_reutilizado_rechazado(api_client, usuario_prueba):
    """Rechazo del mismo código TOTP usado dos veces consecutivas."""
    secret = pyotp.random_base32()
    DispositivoMFA.objects.create(
        usuario=usuario_prueba,
        secreto_cifrado=cifrar_secreto(secret),
        confirmado=True,
    )

    login_url = reverse("autenticacion:login")
    resp_login1 = api_client.post(
        login_url, {"email": "usuario@empresa.com", "password": "Password123!"}
    )
    mfa_token1 = resp_login1.data["mfa_token"]

    verify_url = reverse("autenticacion:mfa-verify")
    codigo = pyotp.TOTP(secret).now()

    # Primer uso: OK
    resp_ok = api_client.post(verify_url, {"mfa_token": mfa_token1, "code": codigo})
    assert resp_ok.status_code == 200

    # Segundo uso del mismo código (nuevo mfa_token emitido)
    resp_login2 = api_client.post(
        login_url, {"email": "usuario@empresa.com", "password": "Password123!"}
    )
    mfa_token2 = resp_login2.data["mfa_token"]

    resp_reuso = api_client.post(verify_url, {"mfa_token": mfa_token2, "code": codigo})
    assert resp_reuso.status_code == 401


def test_verify_codigo_recuperacion_de_un_solo_uso(api_client, usuario_prueba):
    """Prueba que el código de recuperación funcione y no pueda volver a usarse."""
    login_url = reverse("autenticacion:login")
    resp_login = api_client.post(
        login_url, {"email": "usuario@empresa.com", "password": "Password123!"}
    )
    mfa_token = resp_login.data["mfa_token"]

    resp_setup = api_client.post(reverse("autenticacion:mfa-setup"), {"mfa_token": mfa_token})
    codigo_totp = pyotp.TOTP(resp_setup.data["secret"]).now()

    resp_confirm = api_client.post(
        reverse("autenticacion:mfa-confirm"),
        {"mfa_token": mfa_token, "code": codigo_totp},
    )
    codigos_recuperacion = resp_confirm.data["recovery_codes"]
    primer_codigo = codigos_recuperacion[0]

    # Ahora iniciar nueva sesión con ese código de recuperación
    resp_l2 = api_client.post(
        login_url, {"email": "usuario@empresa.com", "password": "Password123!"}
    )
    mfa_token_l2 = resp_l2.data["mfa_token"]

    verify_url = reverse("autenticacion:mfa-verify")
    resp_rec = api_client.post(
        verify_url,
        {"mfa_token": mfa_token_l2, "recovery_code": primer_codigo},
    )
    assert resp_rec.status_code == 200
    assert "access" in resp_rec.data

    # Segundo intento con el MISMO código de recuperación: debe fallar
    resp_l3 = api_client.post(
        login_url, {"email": "usuario@empresa.com", "password": "Password123!"}
    )
    mfa_token_l3 = resp_l3.data["mfa_token"]

    resp_rec_reuso = api_client.post(
        verify_url,
        {"mfa_token": mfa_token_l3, "recovery_code": primer_codigo},
    )
    assert resp_rec_reuso.status_code == 401


def test_rotacion_refresh_y_logout(api_client, usuario_prueba):
    """Prueba la rotación de cookie refresh y el cierre de sesión con lista negra."""
    # Login directo con MFA_ENFORCED=False
    settings.MFA_ENFORCED = False
    login_url = reverse("autenticacion:login")
    resp_login = api_client.post(
        login_url, {"email": "usuario@empresa.com", "password": "Password123!"}
    )
    assert resp_login.status_code == 200
    refresh_cookie = resp_login.cookies["refresh_token"].value

    # Refresh
    refresh_url = reverse("autenticacion:refresh")
    api_client.cookies["refresh_token"] = refresh_cookie
    resp_refresh = api_client.post(refresh_url)
    assert resp_refresh.status_code == 200
    assert "access" in resp_refresh.data
    nuevo_refresh_cookie = resp_refresh.cookies["refresh_token"].value
    assert nuevo_refresh_cookie != refresh_cookie

    # Reusar el refresh viejo debe fallar
    api_client.cookies["refresh_token"] = refresh_cookie
    resp_reuso = api_client.post(refresh_url)
    assert resp_reuso.status_code == 401

    # Logout con el nuevo refresh
    logout_url = reverse("autenticacion:logout")
    api_client.cookies["refresh_token"] = nuevo_refresh_cookie
    resp_logout = api_client.post(logout_url)
    assert resp_logout.status_code == 200

    # Tras logout, intentar refresh con ese token debe fallar
    api_client.cookies["refresh_token"] = nuevo_refresh_cookie
    resp_tras_logout = api_client.post(refresh_url)
    assert resp_tras_logout.status_code == 401


def test_endpoint_me_por_rol(api_client, usuario_admin):
    """Prueba que el endpoint /me retorne los datos y rol del usuario autenticado."""
    settings.MFA_ENFORCED = False
    login_url = reverse("autenticacion:login")
    resp_login = api_client.post(
        login_url, {"email": "admin@empresa.com", "password": "AdminPassword123!"}
    )
    access_token = resp_login.data["access"]

    me_url = reverse("autenticacion:me")
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    resp_me = api_client.get(me_url)
    assert resp_me.status_code == 200
    assert resp_me.data["email"] == "admin@empresa.com"
    assert resp_me.data["rol"] == RolChoices.ADMINISTRADOR
    assert resp_me.data["mfa_activo"] is False
