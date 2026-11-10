from datetime import UTC, datetime, timedelta

import pyotp
from cryptography.fernet import Fernet

from apps.autenticacion.crypto import (
    cifrar_secreto,
    descifrar_secreto,
    generar_codigos_recuperacion,
    generar_secreto_totp,
    obtener_uri_totp,
    verificar_codigo_recuperacion,
    verificar_totp,
)


def test_cifrado_y_descifrado_secreto():
    """Prueba que el cifrado Fernet sea simétrico y no almacene texto claro."""
    key = Fernet.generate_key().decode()
    secreto_original = generar_secreto_totp()

    secreto_cifrado = cifrar_secreto(secreto_original, key=key)
    assert secreto_cifrado != secreto_original
    assert isinstance(secreto_cifrado, str)

    secreto_recuperado = descifrar_secreto(secreto_cifrado, key=key)
    assert secreto_recuperado == secreto_original


def test_totp_verificacion_con_ventana_y_reloj_inyectado():
    """Prueba la tolerancia de ±1 paso (±30s) con reloj inyectable."""
    secreto = pyotp.random_base32()
    totp = pyotp.TOTP(secreto, interval=30, digits=6)
    tiempo_base = datetime(2026, 11, 10, 12, 0, 15, tzinfo=UTC)
    paso_actual = totp.timecode(tiempo_base)

    # 1. Código del paso actual (delta 0)
    codigo_actual = totp.at(tiempo_base)
    valido, matched_step = verificar_totp(secreto, codigo_actual, at_time=tiempo_base)
    assert valido is True
    assert matched_step == paso_actual

    # 2. Código del paso anterior (-30s) debe ser aceptado por la ventana de tolerancia
    tiempo_anterior = tiempo_base - timedelta(seconds=30)
    codigo_anterior = totp.at(tiempo_anterior)
    valido_ant, matched_step_ant = verificar_totp(secreto, codigo_anterior, at_time=tiempo_base)
    assert valido_ant is True
    assert matched_step_ant == paso_actual - 1

    # 3. Código del paso siguiente (+30s) debe ser aceptado
    tiempo_siguiente = tiempo_base + timedelta(seconds=30)
    codigo_siguiente = totp.at(tiempo_siguiente)
    valido_sig, matched_step_sig = verificar_totp(secreto, codigo_siguiente, at_time=tiempo_base)
    assert valido_sig is True
    assert matched_step_sig == paso_actual + 1

    # 4. Código fuera de ventana (delta -2 pasos / -60s) debe ser rechazado
    tiempo_lejano = tiempo_base - timedelta(seconds=65)
    codigo_lejano = totp.at(tiempo_lejano)
    valido_lejano, step_lejano = verificar_totp(secreto, codigo_lejano, at_time=tiempo_base)
    assert valido_lejano is False
    assert step_lejano is None


def test_totp_rechazo_de_reutilizacion():
    """
    Prueba que el paso del código que COINCIDIÓ quede guardado y
    no se permita reutilizar el mismo código ni uno anterior dentro de la ventana.
    """
    secreto = pyotp.random_base32()
    totp = pyotp.TOTP(secreto, interval=30, digits=6)
    tiempo_actual = datetime(2026, 11, 10, 14, 0, 10, tzinfo=UTC)
    paso_actual = totp.timecode(tiempo_actual)
    codigo = totp.at(tiempo_actual)

    # Primer uso: válido
    valido, step = verificar_totp(secreto, codigo, ultimo_paso_usado=None, at_time=tiempo_actual)
    assert valido is True
    assert step == paso_actual

    # Segundo intento con el mismo código e igual paso: RECHAZADO por anti-reúso
    valido_reuso, step_reuso = verificar_totp(
        secreto, codigo, ultimo_paso_usado=step, at_time=tiempo_actual
    )
    assert valido_reuso is False
    assert step_reuso is None

    # Intento 15 segundos después dentro del mismo paso (paso_actual): RECHAZADO
    tiempo_mas_tarde = tiempo_actual + timedelta(seconds=15)
    valido_reuso2, _ = verificar_totp(
        secreto, codigo, ultimo_paso_usado=step, at_time=tiempo_mas_tarde
    )
    assert valido_reuso2 is False

    # Intento con el código del paso anterior habiendo usado ya el paso actual: RECHAZADO
    codigo_anterior = totp.generate_otp(paso_actual - 1)
    valido_ant, _ = verificar_totp(
        secreto, codigo_anterior, ultimo_paso_usado=step, at_time=tiempo_actual
    )
    assert valido_ant is False

    # Nuevo paso en el futuro: ACEPTADO
    tiempo_futuro = tiempo_actual + timedelta(seconds=35)
    codigo_futuro = totp.at(tiempo_futuro)
    valido_futuro, step_futuro = verificar_totp(
        secreto, codigo_futuro, ultimo_paso_usado=step, at_time=tiempo_futuro
    )
    assert valido_futuro is True
    assert step_futuro == paso_actual + 1


def test_generacion_y_hash_codigos_recuperacion():
    """Prueba que los 10 códigos de recuperación se generen con formato y hashes válidos."""
    pares = generar_codigos_recuperacion(cantidad=10)
    assert len(pares) == 10

    # Todos deben ser únicos
    planos = [p[0] for p in pares]
    assert len(set(planos)) == 10

    for codigo_plano, codigo_hash in pares:
        assert "-" in codigo_plano
        assert len(codigo_plano) == 9  # Formato XXXX-XXXX
        assert verificar_codigo_recuperacion(codigo_plano, codigo_hash) is True
        assert verificar_codigo_recuperacion("CODIGO-INCORRECTO", codigo_hash) is False


def test_obtener_uri_totp():
    """Prueba que la URI de aprovisionamiento contenga el esquema otpauth y el emisor."""
    secreto = "JBSWY3DPEHPK3PXP"
    uri = obtener_uri_totp(secreto, email="usuario@empresa.com", issuer="MiEmpresa")
    assert uri.startswith("otpauth://totp/")
    assert "usuario%40empresa.com" in uri or "usuario@empresa.com" in uri
    assert "secret=JBSWY3DPEHPK3PXP" in uri
    assert "issuer=MiEmpresa" in uri
