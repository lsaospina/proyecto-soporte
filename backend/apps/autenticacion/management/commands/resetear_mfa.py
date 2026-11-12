from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.auditoria.models import AccionAuditoria
from apps.auditoria.services import registrar_evento
from apps.common.sessions import revocar_tokens_refresco
from apps.usuarios.models import Usuario
from apps.usuarios.utils import normalizar_email


class Command(BaseCommand):
    help = "Resetea el MFA de un usuario (borra dispositivo, revoca refresh y audita)."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Correo del usuario a resetear MFA.")

    def handle(self, *args, **options):
        email = normalizar_email(options["email"])
        usuario = Usuario.objects.filter(email__iexact=email).first()
        if not usuario:
            raise CommandError(f"Usuario no encontrado: {email}")

        with transaction.atomic():
            dispositivo = getattr(usuario, "dispositivo_mfa", None)
            if dispositivo:
                dispositivo.delete()
            revocar_tokens_refresco(usuario)
            registrar_evento(
                usuario=None,
                accion=AccionAuditoria.MFA_RESETEADO,
                entidad="Usuario",
                entidad_id=str(usuario.pk),
                ip=None,
            )

        self.stdout.write(self.style.SUCCESS(f"MFA reseteado correctamente para {usuario.email}."))
