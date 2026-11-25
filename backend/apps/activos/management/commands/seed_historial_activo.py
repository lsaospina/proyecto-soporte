from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.activos.models import Activo, AsignacionActivo, EstadoActivo
from apps.incidentes.models import EstadoIncidente, Incidente
from apps.mantenimientos.models import (
    EstadoMantenimiento,
    Mantenimiento,
    TipoMantenimiento,
)
from apps.usuarios.models import RolChoices, Usuario

PREFIJO_DEMO = "[DEMO]"


class Command(BaseCommand):
    help = (
        "Puebla un historial de demostración (asignaciones, mantenimientos, incidentes y "
        "auditoría) para un activo, pensado para mostrar en clase. Idempotente."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--codigo",
            default="AST-2024-000002",
            help="Código QR del activo a poblar (por defecto AST-2024-000002).",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Este comando solo se ejecuta con DEBUG=True.")

        codigo = options["codigo"]
        try:
            activo = Activo.objects.get(codigo_qr=codigo)
        except Activo.DoesNotExist:
            raise CommandError(
                f"No existe un activo con código '{codigo}'. "
                "Ejecuta primero: manage.py seed_inventario_dev"
            )

        if AsignacionActivo.objects.filter(
            activo=activo, observacion__startswith=PREFIJO_DEMO
        ).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"El historial de demostración ya existe para {codigo}; no se duplica."
                )
            )
            return

        admin = Usuario.objects.filter(
            rol=RolChoices.ADMINISTRADOR, is_active=True
        ).order_by("id").first()
        if admin is None:
            raise CommandError("No hay administrador activo. Ejecuta seed_usuarios_dev.")

        tecnico = (
            Usuario.objects.filter(rol=RolChoices.TECNICO, is_active=True).order_by("id").first()
            or admin
        )
        responsables = self._responsables()

        hoy = timezone.localdate()
        fa = activo.fecha_adquisicion

        with transaction.atomic():
            # 1) Garantía (calculada por plazo) + observaciones -> genera auditoría.
            meses_hasta_hoy = (hoy.year - fa.year) * 12 + (hoy.month - fa.month)
            activo.plazo_garantia_meses = max(meses_hasta_hoy + 1, 12)
            activo.observaciones = (
                f"{PREFIJO_DEMO} Equipo de demostración con historial completo: "
                "revisiones, reasignaciones e incidentes."
            )
            activo._history_user = admin
            activo.save()

            # 2) Asignaciones: dos cerradas + una vigente, con cambios de estado auditados.
            # Cierra cualquier asignación abierta previa (p. ej. del seed de asignaciones)
            # para respetar la restricción de una sola asignación abierta por activo.
            for abierta in AsignacionActivo.objects.filter(activo=activo, fecha_fin__isnull=True):
                abierta.fecha_fin = max(abierta.fecha_inicio, hoy - timedelta(days=421))
                abierta._history_user = admin
                abierta.save(update_fields=["fecha_fin", "updated_at"])

            cierres = [
                (responsables[0], hoy - timedelta(days=420), hoy - timedelta(days=300)),
                (responsables[1], hoy - timedelta(days=300), hoy - timedelta(days=90)),
            ]
            for usuario, inicio, fin in cierres:
                self._asignar(activo, usuario, admin, inicio, fin, "Entrega y devolución registrada.")
                activo.estado = EstadoActivo.DISPONIBLE
                activo._history_user = admin
                activo.save(update_fields=["estado", "updated_at"])

            self._asignar(
                activo,
                responsables[2],
                admin,
                hoy - timedelta(days=90),
                None,
                "Asignación vigente del equipo.",
            )
            activo.estado = EstadoActivo.ASIGNADO
            activo._history_user = admin
            activo.save(update_fields=["estado", "updated_at"])

            # 3) Mantenimientos preventivos: completados, vencido, programado y reprogramado.
            self._preventivo(activo, tecnico, hoy - timedelta(days=180), {
                "estado": EstadoMantenimiento.COMPLETADO,
                "fecha_realizacion": hoy - timedelta(days=178),
                "costo": 180000,
                "observacion": f"{PREFIJO_DEMO} Limpieza general y revisión de hardware.",
            })
            self._preventivo(activo, tecnico, hoy - timedelta(days=90), {
                "estado": EstadoMantenimiento.COMPLETADO,
                "fecha_realizacion": hoy - timedelta(days=88),
                "costo": 200000,
                "observacion": f"{PREFIJO_DEMO} Actualización de sistema y antivirus.",
            })
            self._preventivo(activo, None, hoy - timedelta(days=20), {
                "estado": EstadoMantenimiento.PROGRAMADO,
                "observacion": f"{PREFIJO_DEMO} Revisión trimestral vencida (no realizada).",
            })
            self._preventivo(activo, tecnico, hoy + timedelta(days=30), {
                "estado": EstadoMantenimiento.PROGRAMADO,
                "observacion": f"{PREFIJO_DEMO} Próxima revisión programada.",
            })

            original, _ = self._preventivo(activo, None, hoy - timedelta(days=45), {
                "estado": EstadoMantenimiento.PROGRAMADO,
                "observacion": f"{PREFIJO_DEMO} Revisión no atendida (queda como evidencia).",
            })
            if not Mantenimiento.objects.filter(reprogramacion_de=original).exists():
                Mantenimiento.objects.get_or_create(
                    activo=activo,
                    tipo=TipoMantenimiento.PREVENTIVO,
                    fecha_programada=hoy + timedelta(days=15),
                    reprogramacion_de=original,
                    defaults={
                        "estado": EstadoMantenimiento.PROGRAMADO,
                        "tecnico": tecnico,
                        "observacion": f"{PREFIJO_DEMO} Reprogramación de la revisión incumplida.",
                    },
                )

            # 4) Correctivos.
            self._correctivo(
                activo, tecnico, hoy - timedelta(days=30), hoy + timedelta(days=10), 350000,
                f"{PREFIJO_DEMO} No enciende; se reemplazó la fuente de poder.",
            )
            self._correctivo(
                activo, tecnico, hoy - timedelta(days=10), hoy + timedelta(days=20), 120000,
                f"{PREFIJO_DEMO} Pantalla parpadea; se reemplazó el cable de video.",
            )

            # 5) Incidentes en distintos estados.
            self._incidente(activo, responsables[2], hoy - timedelta(days=2),
                            "El equipo no enciende desde la mañana.", EstadoIncidente.REPORTADO)
            self._incidente(activo, responsables[1], hoy - timedelta(days=7),
                            "Se escucha un ruido fuerte en el ventilador.", EstadoIncidente.EN_PROCESO)
            self._incidente(activo, tecnico, hoy - timedelta(days=15),
                            "El puerto USB no reconoce dispositivos.", EstadoIncidente.RESUELTO)
            self._incidente(activo, responsables[0], hoy - timedelta(days=40),
                            "Teclado con varias teclas pegadas.", EstadoIncidente.CERRADO)

        self.stdout.write(
            self.style.SUCCESS(
                f"Historial de demostración creado para {codigo} ({activo.serial}): "
                "3 asignaciones, 5 preventivos, 2 correctivos y 4 incidentes."
            )
        )

    # --- helpers ---
    def _responsables(self):
        demos = [
            ("carlos.ramirez@inventario.local", "Carlos Ramírez"),
            ("laura.gomez@inventario.local", "Laura Gómez"),
            ("andres.torres@inventario.local", "Andrés Torres"),
        ]
        usuarios = []
        for email, nombre in demos:
            usuario, _ = Usuario.objects.get_or_create(
                email=email,
                defaults={
                    "nombre_completo": nombre,
                    "rol": RolChoices.USUARIO_RESPONSABLE,
                    "is_active": True,
                },
            )
            usuarios.append(usuario)
        return usuarios

    def _asignar(self, activo, usuario, admin, inicio, fin, observacion):
        asignacion = AsignacionActivo(
            activo=activo,
            usuario=usuario,
            asignado_por=admin,
            fecha_inicio=inicio,
            fecha_fin=fin,
            observacion=f"{PREFIJO_DEMO} {observacion}",
        )
        asignacion._history_user = admin
        asignacion.save()
        return asignacion

    def _preventivo(self, activo, tecnico, fecha, defaults):
        return Mantenimiento.objects.get_or_create(
            activo=activo,
            tipo=TipoMantenimiento.PREVENTIVO,
            fecha_programada=fecha,
            defaults={**defaults, "tecnico": tecnico},
        )

    def _correctivo(self, activo, tecnico, fecha_evento, fecha_seguimiento, costo, observacion):
        return Mantenimiento.objects.get_or_create(
            activo=activo,
            tipo=TipoMantenimiento.CORRECTIVO,
            fecha_programada=fecha_evento,
            defaults={
                "estado": EstadoMantenimiento.COMPLETADO,
                "fecha_realizacion": fecha_evento,
                "fecha_seguimiento": fecha_seguimiento,
                "tecnico": tecnico,
                "costo": costo,
                "observacion": observacion,
            },
        )

    def _incidente(self, activo, reportado_por, fecha, descripcion, estado):
        return Incidente.objects.get_or_create(
            activo=activo,
            fecha=fecha,
            descripcion=descripcion,
            defaults={"reportado_por": reportado_por, "estado": estado},
        )
