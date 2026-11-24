from datetime import date

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.activos.models import Activo, AsignacionActivo, EstadoActivo
from apps.catalogos.models import Categoria, Marca, ModeloActivo
from apps.usuarios.models import RolChoices, Usuario


@pytest.fixture
def datos(db):
    marca = Marca.objects.create(nombre="Dell")
    categoria = Categoria.objects.create(nombre="HW")
    modelo = ModeloActivo.objects.create(marca=marca, categoria=categoria, nombre="Latitude")
    for indice in range(1, 4):
        Activo.objects.create(
            serial=f"SEEDASIG{indice}",
            modelo=modelo,
            fecha_adquisicion=date(2024, 1, 1),
            codigo_qr=f"AST-2024-SEEDASIG{indice}",
            estado=EstadoActivo.ASIGNADO,
        )
        Activo.objects.create(
            serial=f"SEEDLIBRE{indice}",
            modelo=modelo,
            fecha_adquisicion=date(2024, 1, 1),
            codigo_qr=f"AST-2024-SEEDLIBRE{indice}",
            estado=EstadoActivo.DISPONIBLE,
        )
    Usuario.objects.create_user(
        email="seed-admin@test.com",
        password="Pass12345!",
        nombre_completo="Admin Seed",
        rol=RolChoices.ADMINISTRADOR,
    )
    Usuario.objects.create_user(
        email="seed-trab@test.com",
        password="Pass12345!",
        nombre_completo="Trabajador Seed",
        rol=RolChoices.USUARIO_RESPONSABLE,
    )


@pytest.mark.django_db
def test_seed_rechaza_debug_false(settings, datos):
    settings.DEBUG = False
    with pytest.raises(CommandError):
        call_command("seed_asignaciones_dev")


@pytest.mark.django_db
def test_seed_regulariza_estados_y_es_idempotente(settings, datos):
    settings.DEBUG = True
    call_command("seed_asignaciones_dev")

    abiertas = AsignacionActivo.objects.filter(fecha_fin__isnull=True)
    assert abiertas.count() == Activo.objects.filter(estado=EstadoActivo.ASIGNADO).count()
    assert AsignacionActivo.objects.filter(fecha_fin__isnull=False).exists()
    total = AsignacionActivo.objects.count()
    assert total >= 9

    call_command("seed_asignaciones_dev")
    assert AsignacionActivo.objects.count() == total
