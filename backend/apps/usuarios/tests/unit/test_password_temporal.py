import pytest

from apps.usuarios.services import generar_password_temporal


@pytest.mark.unit
def test_generar_password_temporal_politica():
    for _ in range(20):
        pwd = generar_password_temporal()
        assert len(pwd) >= 12
        assert any(c.isupper() for c in pwd)
        assert any(c.islower() for c in pwd)
        assert any(c.isdigit() for c in pwd)
        assert any(not c.isalnum() for c in pwd)
