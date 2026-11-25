from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.activos.models import Activo, AsignacionActivo, EstadoActivo
from apps.bajas.models import Baja
from apps.bajas.services import registrar_baja
from apps.usuarios.models import RolChoices, Usuario

PREFIJO_DEMO = "[DEMO]"

MOTIVOS = [
    ("Equipo obsoleto; fin de vida útil.", 120),
    ("Daño irreparable en la placa base.", 60),
    ("Pérdida total por accidente.", 30),
    ("Donación a institución educativa.", 200),
    ("Falla eléctrica no reparable.", 15),
]


class Command(BaseCommand):
    help = (
        "Registra bajas de demostración para activos elegibles (sin asignación "
        "abierta ni baja previa). Idempotente; solo DEBUG."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--cantidad",
            type=int,
            default=3,
            help="Cuántas bajas de ejemplo crear (por defecto 3).",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Este comando solo se ejecuta con DEBUG=True.")

        admin = (
            Usuario.objects.filter(rol=RolChoices.ADMINISTRADOR, is_active=True)
            .order_by("id")
            .first()
        )
        if admin is None:
            raise CommandError(
                "No hay administrador activo. Ejecuta primero: manage.py seed_usuarios_dev"
            )

        if Baja.objects.filter(motivo__startswith=PREFIJO_DEMO).exists():
            self.stdout.write(
                self.style.WARNING("Ya existen bajas de demostración; no se duplican.")
            )
            return

        cantidad = max(1, options["cantidad"])
        abiertos = AsignacionActivo.objects.filter(fecha_fin__isnull=True).values_list(
            "activo_id", flat=True
        )
        con_baja = Baja.objects.values_list("activo_id", flat=True)
        candidatos = list(
            Activo.objects.filter(is_active=True)
            .exclude(estado=EstadoActivo.DADO_DE_BAJA)
            .exclude(id__in=abiertos)
            .exclude(id__in=con_baja)
            .order_by("id")[:cantidad]
        )
        if not candidatos:
            raise CommandError(
                "No hay activos elegibles (requieren no tener asignación abierta ni baja). "
                "Revisa seed_inventario_dev / seed_asignaciones_dev."
            )

        hoy = timezone.localdate()
        creadas = 0
        for indice, activo in enumerate(candidatos):
            motivo, dias = MOTIVOS[indice % len(MOTIVOS)]
            try:
                registrar_baja(
                    {
                        "activo": activo,
                        "fecha": hoy - timedelta(days=dias),
                        "motivo": f"{PREFIJO_DEMO} {motivo}",
                    },
                    admin,
                )
                creadas += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Baja creada: {activo.codigo_qr} ({activo.serial})")
                )
            except Exception as exc:  # noqa: BLE001 - se reporta y continúa
                self.stdout.write(
                    self.style.WARNING(f"Omitido {activo.serial}: {exc}")
                )

        if creadas == 0:
            self.stdout.write(
                self.style.WARNING("No se creó ninguna baja (activos no elegibles).")
            )
            return
        self.stdout.write(
            self.style.SUCCESS(f"Bajas de demostración creadas: {creadas}.")
        )
