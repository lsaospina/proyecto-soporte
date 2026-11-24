from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.activos.models import Activo, AsignacionActivo, EstadoActivo
from apps.usuarios.models import RolChoices, Usuario


class Command(BaseCommand):
    help = "Seed de asignaciones de activos para desarrollo (idempotente)."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Este comando solo se ejecuta con DEBUG=True.")
        if AsignacionActivo.objects.exists():
            self.stdout.write("Ya existen asignaciones; no se crean duplicados.")
            return

        usuarios = list(Usuario.objects.filter(is_active=True).order_by("id"))
        if not usuarios:
            self.stdout.write(
                self.style.WARNING("No hay usuarios activos; ejecute seed_usuarios_dev.")
            )
            return
        admin = next(
            (usuario for usuario in usuarios if usuario.rol == RolChoices.ADMINISTRADOR),
            usuarios[0],
        )
        hoy = timezone.localdate()
        creadas = 0

        # 1) Regulariza los activos que el seed de inventario dejó en ASIGNADO.
        marcados = Activo.objects.filter(estado=EstadoActivo.ASIGNADO, is_active=True).order_by(
            "id"
        )
        for indice, activo in enumerate(marcados):
            inicio = max(activo.fecha_adquisicion, hoy - timedelta(days=90 + indice * 5))
            creadas += self._crear_asignacion(
                activo,
                usuarios[indice % len(usuarios)],
                admin,
                min(inicio, hoy),
                "Asignación inicial de ejemplo.",
            )

        # 2) Genera historial para algunos activos disponibles: anterior + actual.
        disponibles = list(
            Activo.objects.filter(estado=EstadoActivo.DISPONIBLE, is_active=True).order_by("id")[:4]
        )
        for indice, activo in enumerate(disponibles):
            inicio_previo = max(activo.fecha_adquisicion, hoy - timedelta(days=300))
            fin_previo = max(inicio_previo, hoy - timedelta(days=120))
            anterior = AsignacionActivo(
                activo=activo,
                usuario=usuarios[(indice + 1) % len(usuarios)],
                asignado_por=admin,
                fecha_inicio=inicio_previo,
                fecha_fin=fin_previo,
                observacion="Asignación anterior de ejemplo.",
            )
            anterior._history_user = admin
            anterior.save()
            creadas += 1

            inicio_actual = max(activo.fecha_adquisicion, fin_previo, hoy - timedelta(days=60))
            creadas += self._crear_asignacion(
                activo,
                usuarios[(indice + 2) % len(usuarios)],
                admin,
                min(inicio_actual, hoy),
                "Asignación vigente de ejemplo.",
            )

        self.stdout.write(self.style.SUCCESS(f"Seed aplicado: {creadas} asignaciones."))
        if creadas == 0:
            self.stdout.write(
                self.style.WARNING("No había activos disponibles para generar asignaciones.")
            )

    def _crear_asignacion(self, activo, usuario, admin, fecha_inicio, observacion):
        asignacion = AsignacionActivo(
            activo=activo,
            usuario=usuario,
            asignado_por=admin,
            fecha_inicio=fecha_inicio,
            observacion=observacion,
        )
        asignacion._history_user = admin
        asignacion.save()
        if activo.estado != EstadoActivo.ASIGNADO:
            activo.estado = EstadoActivo.ASIGNADO
            activo._history_user = admin
            activo.save(update_fields=["estado", "updated_at"])
        return 1
