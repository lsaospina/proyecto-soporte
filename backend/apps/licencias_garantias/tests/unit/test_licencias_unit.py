from datetime import date

from freezegun import freeze_time

from apps.licencias_garantias.models import EstadoRenovacion, Licencia
from apps.licencias_garantias.serializers import LicenciaWriteSerializer


@freeze_time("2026-11-15 12:00:00")
class TestEstadoRenovacion:
    def test_vigente(self):
        licencia = Licencia(fecha_renovacion=date(2026, 12, 20))
        assert licencia.dias_para_renovacion == 35
        assert licencia.estado_renovacion == EstadoRenovacion.VIGENTE
        assert licencia.estado_renovacion_etiqueta == "Vigente"

    def test_por_vencer_incluye_el_limite(self):
        assert (
            Licencia(fecha_renovacion=date(2026, 11, 15)).estado_renovacion
            == EstadoRenovacion.POR_VENCER
        )
        assert (
            Licencia(fecha_renovacion=date(2026, 12, 15)).estado_renovacion
            == EstadoRenovacion.POR_VENCER
        )

    def test_vencida(self):
        licencia = Licencia(fecha_renovacion=date(2026, 11, 14))
        assert licencia.dias_para_renovacion == -1
        assert licencia.estado_renovacion == EstadoRenovacion.VENCIDA

    def test_inactiva_tiene_prioridad(self):
        licencia = Licencia(fecha_renovacion=date(2027, 1, 1), is_active=False)
        assert licencia.estado_renovacion == EstadoRenovacion.INACTIVA


class TestLicenciaWriteSerializer:
    def test_normaliza_proveedor_y_servicio(self):
        serializer = LicenciaWriteSerializer(
            data={
                "proveedor": "  Oracle   Cloud  ",
                "servicio": "  Base de datos   autonoma ",
                "fecha_renovacion": "2026-12-01",
            }
        )
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["proveedor"] == "Oracle Cloud"
        assert serializer.validated_data["servicio"] == "Base de datos autonoma"
        assert serializer.validated_data["periodicidad"] == "ANUAL"
        assert serializer.validated_data["cantidad"] == 1
        assert serializer.validated_data["renovacion_automatica"] is False

    def test_rechaza_cantidad_cero(self):
        serializer = LicenciaWriteSerializer(
            data={
                "proveedor": "Oracle",
                "servicio": "Cloud",
                "fecha_renovacion": "2026-12-01",
                "cantidad": 0,
            }
        )
        assert not serializer.is_valid()
        assert "cantidad" in serializer.errors

    def test_rechaza_valor_negativo_y_proveedor_vacio(self):
        serializer = LicenciaWriteSerializer(
            data={
                "proveedor": "   ",
                "servicio": "Cloud",
                "fecha_renovacion": "2026-12-01",
                "valor": "-1",
            }
        )
        assert not serializer.is_valid()
        assert "proveedor" in serializer.errors
        assert "valor" in serializer.errors
