from datetime import timedelta

from django.utils import timezone

from apps.usuarios.models import RolChoices, Usuario


def test_usuario_esta_bloqueado_propiedad():
    """Prueba unitaria de la propiedad esta_bloqueado sin requerir base de datos."""
    usuario = Usuario(
        email="test@empresa.com",
        nombre_completo="Usuario Prueba",
        rol=RolChoices.TECNICO,
    )

    # 1. Sin bloqueo
    assert usuario.esta_bloqueado is False

    # 2. Bloqueado hacia el futuro
    usuario.bloqueado_hasta = timezone.now() + timedelta(minutes=15)
    assert usuario.esta_bloqueado is True

    # 3. Bloqueo expirado en el pasado
    usuario.bloqueado_hasta = timezone.now() - timedelta(seconds=1)
    assert usuario.esta_bloqueado is False


def test_usuario_roles_choices():
    """Valida los valores definidos para los roles del sistema."""
    assert RolChoices.ADMINISTRADOR == "ADMINISTRADOR"
    assert RolChoices.TECNICO == "TECNICO"
    assert RolChoices.USUARIO_RESPONSABLE == "USUARIO_RESPONSABLE"
