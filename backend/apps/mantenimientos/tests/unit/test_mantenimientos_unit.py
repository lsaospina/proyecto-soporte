from datetime import date, timedelta

import pytest
from freezegun import freeze_time

from apps.common.exceptions import ReglaDeNegocioError
from apps.mantenimientos.models import (
    EstadoMantenimiento,
    Mantenimiento,
    SituacionMantenimiento,
)
from apps.mantenimientos.services import (
    _validar_fecha_no_pasada,
    cancelar_mantenimiento,
    completar_mantenimiento,
)


def _mantenimiento(fecha, estado=EstadoMantenimiento.PROGRAMADO, reprogramado=False):
    obj = Mantenimiento(fecha_programada=fecha, estado=estado)
    obj.tiene_reprogramacion = reprogramado
    return obj


@freeze_time("2026-11-15 12:00:00")
def test_situacion_pendiente():
    assert _mantenimiento(date(2026, 11, 20)).situacion == SituacionMantenimiento.PENDIENTE


@freeze_time("2026-11-15 12:00:00")
def test_situacion_vencido():
    obj = _mantenimiento(date(2026, 11, 10))
    assert obj.situacion == SituacionMantenimiento.VENCIDO
    assert obj.es_evidencia is False


@freeze_time("2026-11-15 12:00:00")
def test_situacion_incumplido_es_evidencia():
    obj = _mantenimiento(date(2026, 11, 10), reprogramado=True)
    assert obj.situacion == SituacionMantenimiento.INCUMPLIDO
    assert obj.es_evidencia is True


@freeze_time("2026-11-15 12:00:00")
def test_situacion_completado_y_cancelado():
    assert (
        _mantenimiento(date(2026, 11, 10), estado=EstadoMantenimiento.COMPLETADO).situacion
        == SituacionMantenimiento.COMPLETADO
    )
    assert (
        _mantenimiento(date(2026, 11, 10), estado=EstadoMantenimiento.CANCELADO).situacion
        == SituacionMantenimiento.CANCELADO
    )


@freeze_time("2026-11-15 12:00:00")
def test_fecha_pasada_rechazada():
    with pytest.raises(ReglaDeNegocioError):
        _validar_fecha_no_pasada(date(2026, 11, 14))


@freeze_time("2026-11-15 12:00:00")
def test_completar_rechaza_incumplido():
    obj = _mantenimiento(date(2026, 11, 10), reprogramado=True)
    with pytest.raises(ReglaDeNegocioError):
        completar_mantenimiento(
            obj,
            {"fecha_realizacion": date(2026, 11, 15), "tecnico": object(), "costo": 1},
            actor=None,
        )


@freeze_time("2026-11-15 12:00:00")
def test_cancelar_exige_motivo():
    obj = _mantenimiento(date(2026, 11, 20))
    with pytest.raises(ReglaDeNegocioError):
        cancelar_mantenimiento(obj, "   ", actor=None)


@freeze_time("2026-11-15 12:00:00")
def test_fecha_manana_es_valida():
    _validar_fecha_no_pasada(date(2026, 11, 16))
    _validar_fecha_no_pasada(date.today() + timedelta(days=0))
