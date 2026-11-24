from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.activos.models import Activo
from apps.mantenimientos.models import (
    EstadoMantenimiento,
    Mantenimiento,
    TipoMantenimiento,
)
from apps.usuarios.models import RolChoices, Usuario


class Command(BaseCommand):
    help = (
        "Carga mantenimientos preventivos de prueba para el año actual, "
        "distribuidos entre todos los activos (idempotente)."
    )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Este comando solo se puede ejecutar con DEBUG=True.")

        activos = list(
            Activo.objects.filter(is_active=True).exclude(estado="DADO_DE_BAJA").order_by("id")[:40]
        )
        if not activos:
            raise CommandError(
                "No hay activos activos. Ejecute primero: manage.py seed_inventario_dev"
            )

        tecnico = (
            Usuario.objects.filter(rol=RolChoices.TECNICO, is_active=True).order_by("id").first()
            or Usuario.objects.filter(rol=RolChoices.ADMINISTRADOR, is_active=True)
            .order_by("id")
            .first()
        )
        if tecnico is None:
            raise CommandError("No hay usuarios activos para asignar como técnico.")

        hoy = timezone.localdate()
        anio = hoy.year
        creados = 0
        completados = 0
        reprogramados = 0

        with transaction.atomic():
            for indice, activo in enumerate(activos):
                mes = (indice % 12) + 1
                dia = min(5 + (indice % 20), 28)
                fecha = date(anio, mes, dia)
                es_pasado = fecha < hoy
                completar = es_pasado and indice % 4 != 0

                defaults = {
                    "tipo": TipoMantenimiento.PREVENTIVO,
                    "tecnico": tecnico if completar else None,
                    "costo": Decimal("150000.00") if completar else None,
                    "observacion": "Mantenimiento de prueba (seed).",
                }
                if completar:
                    defaults.update(
                        {
                            "estado": EstadoMantenimiento.COMPLETADO,
                            "fecha_realizacion": min(fecha + timedelta(days=2), hoy),
                        }
                    )
                else:
                    defaults.update(
                        {
                            "estado": EstadoMantenimiento.PROGRAMADO,
                            "fecha_realizacion": None,
                        }
                    )

                _, creado = Mantenimiento.objects.get_or_create(
                    activo=activo,
                    fecha_programada=fecha,
                    tipo=TipoMantenimiento.PREVENTIVO,
                    defaults=defaults,
                )
                if creado:
                    creados += 1
                    completados += 1 if completar else 0

                if es_pasado and not completar and indice % 12 == 0:
                    original = Mantenimiento.objects.get(
                        activo=activo,
                        fecha_programada=fecha,
                        tipo=TipoMantenimiento.PREVENTIVO,
                    )
                    nueva_fecha = date(anio, 12, min(dia, 28))
                    _, creado_reprog = Mantenimiento.objects.get_or_create(
                        activo=activo,
                        fecha_programada=nueva_fecha,
                        tipo=TipoMantenimiento.PREVENTIVO,
                        reprogramacion_de=original,
                        defaults={
                            "estado": EstadoMantenimiento.PROGRAMADO,
                            "tecnico": tecnico,
                            "observacion": "Reprogramación de prueba (seed).",
                        },
                    )
                    if creado_reprog:
                        creados += 1
                        reprogramados += 1

        descripciones = [
            "No enciende; se revisó la fuente de poder.",
            "Pantalla con fallas; se reemplazó el cable.",
            "Sobrecalentamiento; se limpió el ventilador.",
        ]
        correctivos_creados = 0
        for posicion in range(min(3, len(activos))):
            activo = activos[posicion]
            fecha_evento = hoy - timedelta(days=10 + posicion * 5)
            fecha_seguimiento = hoy + timedelta(days=7 + posicion * 3)
            _, creado_correctivo = Mantenimiento.objects.get_or_create(
                activo=activo,
                fecha_programada=fecha_evento,
                tipo=TipoMantenimiento.CORRECTIVO,
                defaults={
                    "estado": EstadoMantenimiento.COMPLETADO,
                    "fecha_realizacion": fecha_evento,
                    "fecha_seguimiento": fecha_seguimiento,
                    "tecnico": tecnico,
                    "observacion": descripciones[posicion],
                },
            )
            correctivos_creados += 1 if creado_correctivo else 0

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed de mantenimientos {anio}: {creados} preventivos creados "
                f"({completados} completados, {reprogramados} reprogramados) y "
                f"{correctivos_creados} correctivos. Activos usados: {len(activos)}."
            )
        )
