import contextlib

import pytest
from django.core.management import CommandError, call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.auditoria.models import AccionAuditoria, RegistroAuditoria
from apps.autenticacion.models import DispositivoMFA
from apps.usuarios.models import RolChoices, Usuario
from apps.usuarios.services import inactivar_usuario


@pytest.mark.django_db
def test_resetear_mfa_command_exitoso():
    u = Usuario.objects.create_user(
        email="cmd@test.com", password="x", nombre_completo="CMD", rol=RolChoices.TECNICO
    )
    DispositivoMFA.objects.create(usuario=u, secreto_cifrado="x", confirmado=True)
    call_command("resetear_mfa", email="CMD@test.com")
    assert not DispositivoMFA.objects.filter(usuario=u).exists()
    assert RegistroAuditoria.objects.filter(
        accion=AccionAuditoria.MFA_RESETEADO,
        usuario__isnull=True,
        entidad="Usuario",
        entidad_id=str(u.pk),
    ).exists()


@pytest.mark.django_db
def test_resetear_mfa_command_usuario_inexistente():
    with pytest.raises(CommandError):
        call_command("resetear_mfa", email="noexiste@test.com")


@pytest.mark.django_db
def test_guarda_ultimo_admin_usa_for_update_y_order_by_pk():
    admin = Usuario.objects.create_user(
        email="a1@test.com", password="x", nombre_completo="A1", rol=RolChoices.ADMINISTRADOR
    )
    # Ensure only this admin is active
    Usuario.objects.exclude(pk=admin.pk).update(is_active=False)
    Usuario.objects.create_user(
        email="actor@test.com", password="x", nombre_completo="Actor", rol=RolChoices.ADMINISTRADOR
    )
    # make actor also admin but we want admin to be target in a scenario? easier: call service guard path via inactivar_usuario on another admin when two exist - capture queries during call
    admin2 = Usuario.objects.create_user(
        email="a2@test.com", password="x", nombre_completo="A2", rol=RolChoices.ADMINISTRADOR
    )
    # inactivar admin2 by actor=admin should run guarda query
    with CaptureQueriesContext(connection) as ctx, contextlib.suppress(Exception):
        inactivar_usuario(admin2, actor=admin, ip=None)
    sqls = " ".join(q["sql"] for q in ctx.captured_queries).upper()
    assert "FOR UPDATE" in sqls
    assert "ORDER BY" in sqls
