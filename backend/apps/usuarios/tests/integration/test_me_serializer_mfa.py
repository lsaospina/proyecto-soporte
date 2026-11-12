import pytest
from django.contrib.auth import get_user_model

from apps.autenticacion.serializers import UsuarioMeSerializer

Usuario = get_user_model()


@pytest.mark.django_db
def test_mfa_activo_sin_dispositivo():
    user = Usuario(email="nodisp@test.com", nombre_completo="No Disp", rol="TECNICO")
    user.set_password("x")
    user.save()
    # sin dispositivo_mfa relacionado
    data = UsuarioMeSerializer(user).data
    assert data["mfa_activo"] is False
