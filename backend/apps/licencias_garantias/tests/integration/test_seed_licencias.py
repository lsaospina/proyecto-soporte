import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.licencias_garantias.models import EstadoRenovacion, Licencia, Proveedor


@pytest.mark.django_db
def test_seed_rechaza_debug_false(settings):
    settings.DEBUG = False
    with pytest.raises(CommandError):
        call_command("seed_licencias_dev")


@pytest.mark.django_db
def test_seed_idempotente_y_genera_estados(settings):
    settings.DEBUG = True
    call_command("seed_licencias_dev")
    total = Licencia.objects.count()
    assert total >= 10
    assert Proveedor.objects.exists()

    estados = {
        Licencia(
            proveedor=licencia.proveedor,
            fecha_renovacion=licencia.fecha_renovacion,
            is_active=licencia.is_active,
        ).estado_renovacion
        for licencia in Licencia.objects.all()
    }
    assert EstadoRenovacion.VENCIDA in estados
    assert EstadoRenovacion.POR_VENCER in estados
    assert EstadoRenovacion.VIGENTE in estados
    assert Licencia.objects.filter(is_active=False).exists()

    call_command("seed_licencias_dev")
    assert Licencia.objects.count() == total
