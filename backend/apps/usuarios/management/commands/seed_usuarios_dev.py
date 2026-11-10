from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.usuarios.models import RolChoices, Usuario


class Command(BaseCommand):
    help = (
        "Siembra 3 usuarios de prueba (uno por rol) con la clave configurada en SEED_DEV_PASSWORD."
    )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "Este comando solo puede ejecutarse en entornos de desarrollo (DEBUG=True)."
            )

        password = getattr(settings, "SEED_DEV_PASSWORD", "DevPassword123!")
        if not password:
            raise CommandError("SEED_DEV_PASSWORD no está definida.")

        usuarios_datos = [
            {
                "email": "admin@inventario.local",
                "nombre_completo": "Administrador del Sistema",
                "rol": RolChoices.ADMINISTRADOR,
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "email": "tecnico@inventario.local",
                "nombre_completo": "Técnico de Soporte",
                "rol": RolChoices.TECNICO,
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "email": "responsable@inventario.local",
                "nombre_completo": "Usuario Responsable de Activos",
                "rol": RolChoices.USUARIO_RESPONSABLE,
                "is_staff": False,
                "is_superuser": False,
            },
        ]

        creados = 0
        actualizados = 0

        for datos in usuarios_datos:
            email = datos["email"]
            user, created = Usuario.objects.get_or_create(
                email=email,
                defaults={
                    "nombre_completo": datos["nombre_completo"],
                    "rol": datos["rol"],
                    "is_staff": datos["is_staff"],
                    "is_superuser": datos["is_superuser"],
                    "is_active": True,
                },
            )
            user.set_password(password)
            user.nombre_completo = datos["nombre_completo"]
            user.rol = datos["rol"]
            user.is_staff = datos["is_staff"]
            user.is_superuser = datos["is_superuser"]
            user.is_active = True
            user.intentos_fallidos = 0
            user.bloqueado_hasta = None
            user.save()

            if created:
                creados += 1
                self.stdout.write(self.style.SUCCESS(f"Usuario creado: {email} ({datos['rol']})"))
            else:
                actualizados += 1
                self.stdout.write(
                    self.style.WARNING(f"Usuario actualizado/reseteado: {email} ({datos['rol']})")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Proceso finalizado. {creados} creados, {actualizados} actualizados. "
                f"Contraseña asignada: '{password}'."
            )
        )
