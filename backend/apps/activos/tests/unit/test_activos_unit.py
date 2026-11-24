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


def test_asignacion_activa_y_dias():
    from freezegun import freeze_time

    from apps.activos.models import AsignacionActivo

    with freeze_time("2026-11-15 12:00:00"):
        abierta = AsignacionActivo(fecha_inicio=date(2026, 11, 1))
        cerrada = AsignacionActivo(fecha_inicio=date(2026, 10, 1), fecha_fin=date(2026, 10, 21))
        assert abierta.activa is True
        assert abierta.dias_asignado == 14
        assert cerrada.activa is False
        assert cerrada.dias_asignado == 20
