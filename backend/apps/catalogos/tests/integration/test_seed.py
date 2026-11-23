import pytest
from django.core.management import call_command
from django.test.utils import override_settings

from apps.catalogos.models import Categoria, Marca, ModeloActivo, Sede, Ubicacion


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_seed_inventario_dev_idempotente():
    call_command("seed_inventario_dev")
    call_command("seed_inventario_dev")
    assert Sede.objects.count() == 2
    assert Ubicacion.objects.count() == 6
    assert Categoria.objects.count() == 5
    assert Marca.objects.count() == 5
    assert ModeloActivo.objects.count() == 10


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_seed_se_niega_si_debug_false():
    from django.core.management.base import CommandError

    with pytest.raises(CommandError):
        call_command("seed_inventario_dev")
