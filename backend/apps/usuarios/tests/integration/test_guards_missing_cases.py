import pytest
from rest_framework.test import APIClient

from apps.common.exceptions import ReglaDeNegocioError
from apps.usuarios.models import RolChoices, Usuario
from apps.usuarios.services import actualizar_usuario, inactivar_usuario


@pytest.mark.django_db
def test_auto_cambio_rol_api_400():
    client = APIClient()
    admin = Usuario.objects.create_user(
        email="selfrole@test.com",
        password="AdminPass123!",
        nombre_completo="Self",
        rol=RolChoices.ADMINISTRADOR,
    )
    client.force_authenticate(user=admin)
    resp = client.patch(
        f"/api/v1/usuarios/{admin.id}/",
        {"nombre_completo": "Self", "rol": RolChoices.TECNICO},
        format="json",
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_ultimo_admin_no_cambiar_de_rol_servicio():
    # Dos admins activos: cambiar rol de uno es permitido (queda el otro). Para probar guarda
    # de "último admin", simulamos con actor distinto y objetivo siendo el único admin activo.
    admin1 = Usuario.objects.create_user(
        email="la1@test.com", password="x", nombre_completo="A1", rol=RolChoices.ADMINISTRADOR
    )
    admin2 = Usuario.objects.create_user(
        email="la2@test.com", password="x", nombre_completo="A2", rol=RolChoices.ADMINISTRADOR
    )
    # dejar admin2 como único admin activo
    admin1.is_active = False
    admin1.save(update_fields=["is_active"])
    with pytest.raises(ReglaDeNegocioError) as exc:
        actualizar_usuario(
            admin2, nombre_completo="A2", rol=RolChoices.TECNICO, actor=admin1, ip=None
        )
    assert exc.value.code == "ultimo_admin"


@pytest.mark.django_db
def test_ultimo_admin_no_inactivar_servicio():
    admin1 = Usuario.objects.create_user(
        email="li1@test.com", password="x", nombre_completo="A1", rol=RolChoices.ADMINISTRADOR
    )
    admin2 = Usuario.objects.create_user(
        email="li2@test.com", password="x", nombre_completo="A2", rol=RolChoices.ADMINISTRADOR
    )
    admin1.is_active = False
    admin1.save(update_fields=["is_active"])
    with pytest.raises(ReglaDeNegocioError) as exc:
        inactivar_usuario(admin2, actor=admin1, ip=None)
    assert exc.value.code == "ultimo_admin"
