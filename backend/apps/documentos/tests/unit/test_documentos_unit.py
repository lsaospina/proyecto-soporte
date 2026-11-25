import pytest
from rest_framework import serializers

from apps.documentos.serializers import MAX_BYTES, DocumentoCreateSerializer


class FakeFile:
    def __init__(self, name, size):
        self.name = name
        self.size = size


def test_extension_permitida_pdf():
    serializer = DocumentoCreateSerializer()
    archivo = FakeFile("manual.pdf", 1024)
    assert serializer.validate_archivo(archivo) is archivo


def test_extension_no_permitida():
    serializer = DocumentoCreateSerializer()
    with pytest.raises(serializers.ValidationError):
        serializer.validate_archivo(FakeFile("malware.exe", 1024))


def test_tamano_excedido():
    serializer = DocumentoCreateSerializer()
    with pytest.raises(serializers.ValidationError):
        serializer.validate_archivo(FakeFile("grande.pdf", MAX_BYTES + 1))


def test_nombre_obligatorio():
    serializer = DocumentoCreateSerializer()
    with pytest.raises(serializers.ValidationError):
        serializer.validate_nombre("   ")
