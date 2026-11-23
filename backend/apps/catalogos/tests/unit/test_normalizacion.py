from apps.catalogos.utils import normalizar_nombre


def test_normalizar_nombre_strip_y_colapsa_espacios():
    assert normalizar_nombre("  Hola   Mundo  ") == "Hola Mundo"
    assert normalizar_nombre("") == ""
    assert normalizar_nombre(None) == ""
