import pytest
from rest_framework import serializers

from apps.bajas.serializers import BajaCreateSerializer


def test_motivo_obligatorio():
    serializer = BajaCreateSerializer()
    with pytest.raises(serializers.ValidationError):
        serializer.validate_motivo("   ")


def test_motivo_trim():
    serializer = BajaCreateSerializer()
    assert serializer.validate_motivo("  Equipo obsoleto  ") == "Equipo obsoleto"
