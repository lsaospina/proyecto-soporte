from datetime import date

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.activos.models import Activo
from apps.catalogos.models import Categoria, Marca, ModeloActivo
from apps.mantenimientos.models import EstadoMantenimiento, Mantenimiento
from apps.usuarios.models import RolChoices, Usuario


@pytest.fixture
def datos(db):
    marca = Marca.objects.create(nombre="Dell")
    categoria = Categoria.objects.create(nombre="HW")
    modelo = ModeloActivo.objects.create(marca=marca, categoria=categoria, nombre="Latitude")
    for i in (1, 2):
        Activo.objects.create(
            serial=f"SEED{i}",
            modelo=modelo,
            fecha_adquisicion=date(2024, 1, 1),
            codigo_qr=f"AST-2024-00010{i}",
        )
    Usuario.objects.create_user(
        email="tecseed@test.com",
        password="Pass12345!",
        nombre_completo="Técnico Seed",
        rol=RolChoices.TECNICO,
    )


@pytest.mark.django_db
def test_seed_rechaza_debug_false(settings, datos):
    settings.DEBUG = False
    with pytest.raises(CommandError):
        call_command("seed_mantenimientos_dev")


@pytest.mark.django_db
def test_seed_idempotente_y_genera_situaciones(settings, datos):
    settings.DEBUG = True
    call_command("seed_mantenimientos_dev")
    total = Mantenimiento.objects.count()
    assert total >= 3
    assert Mantenimiento.objects.filter(estado=EstadoMantenimiento.COMPLETADO).exists()
    assert Mantenimiento.objects.filter(reprogramacion_de__isnull=False).exists()
    assert (
        Mantenimiento.objects.filter(reprogramacion_de__isnull=True)
        .exclude(estado=EstadoMantenimiento.COMPLETADO)
        .exists()
    )

    call_command("seed_mantenimientos_dev")
    assert Mantenimiento.objects.count() == total
