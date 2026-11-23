from datetime import date, timedelta

from apps.activos.utils import normalizar_mac, normalizar_serial


def test_normalizar_serial():
    assert normalizar_serial("  abc123  ") == "ABC123"


def test_normalizar_mac():
    assert normalizar_mac("aa-bb-cc-dd-ee-ff") == "AA:BB:CC:DD:EE:FF"
    assert normalizar_mac("aabbccddeeff") == "AA:BB:CC:DD:EE:FF"


def test_transiciones_estado():
    from apps.activos.models import EstadoActivo
    from apps.activos.services import TRANSICIONES

    assert EstadoActivo.ASIGNADO in TRANSICIONES[EstadoActivo.DISPONIBLE]
    assert EstadoActivo.DADO_DE_BAJA not in TRANSICIONES[EstadoActivo.DADO_DE_BAJA]


def test_fecha_futura_rechazada():
    import pytest

    from apps.activos.services import crear_activo
    from apps.common.exceptions import ReglaDeNegocioError

    with pytest.raises(ReglaDeNegocioError):
        crear_activo(
            {"serial": "X", "modelo": None, "fecha_adquisicion": date.today() + timedelta(days=1)},
            actor=None,
        )
