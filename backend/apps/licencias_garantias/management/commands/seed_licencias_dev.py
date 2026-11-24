from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.licencias_garantias.models import Licencia, PeriodicidadRenovacion, Proveedor


class Command(BaseCommand):
    help = "Seed de licencias y proveedores para desarrollo (idempotente)."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Este comando solo se ejecuta con DEBUG=True.")
        if Licencia.objects.exists():
            self.stdout.write("Ya existen licencias; no se crean duplicados.")
            return

        hoy = timezone.localdate()
        registros = [
            {
                "proveedor": "Microsoft",
                "servicio": "Microsoft 365 Familia",
                "periodicidad": PeriodicidadRenovacion.ANUAL,
                "dias": 29,
                "cantidad": 6,
                "valor": "459999.00",
                "renovacion_automatica": True,
                "medio_pago": "Facturación electrónica",
                "cuenta_vinculada": "admin@empresa.com",
                "responsable_uso": "Equipo administrativo",
                "observacion": "Renovación anual del paquete ofimático.",
            },
            {
                "proveedor": "Microsoft",
                "servicio": "Microsoft 365 Personal",
                "periodicidad": PeriodicidadRenovacion.ANUAL,
                "dias": 260,
                "cantidad": 1,
                "valor": "369999.00",
                "renovacion_automatica": True,
                "medio_pago": "Visa **3569",
                "cuenta_vinculada": "contabilidad@empresa.com",
                "responsable_uso": "Equipo de Contabilidad",
            },
            {
                "proveedor": "Kaspersky",
                "servicio": "Small Office Security",
                "periodicidad": PeriodicidadRenovacion.BIENAL,
                "dias": 254,
                "cantidad": 25,
                "valor": "2342017.00",
                "renovacion_automatica": True,
                "medio_pago": "Facturación electrónica",
                "cuenta_vinculada": "coordinacion@empresa.com",
                "responsable_uso": "Equipo operativo",
            },
            {
                "proveedor": "Google",
                "servicio": "Google Workspace Business Standard",
                "periodicidad": PeriodicidadRenovacion.ANUAL,
                "dias": 18,
                "cantidad": 110,
                "valor": "5288300.00",
                "renovacion_automatica": False,
                "medio_pago": "Facturación electrónica",
                "cuenta_vinculada": "ti@empresa.com",
                "responsable_uso": "Toda la empresa",
                "observacion": "Confirmar cantidad de licencias antes de renovar.",
            },
            {
                "proveedor": "Google",
                "servicio": "Google Cloud Platform",
                "periodicidad": PeriodicidadRenovacion.MENSUAL,
                "dias": 8,
                "cantidad": 1,
                "valor": None,
                "renovacion_automatica": True,
                "medio_pago": "Facturación electrónica",
                "cuenta_vinculada": "ti@empresa.com",
                "responsable_uso": "Equipo de Sistemas",
                "observacion": "El valor cambia según el consumo mensual.",
            },
            {
                "proveedor": "Hostingred",
                "servicio": "VPS Miami - servidor web",
                "periodicidad": PeriodicidadRenovacion.MENSUAL,
                "dias": 9,
                "cantidad": 1,
                "valor": "307258.00",
                "renovacion_automatica": True,
                "medio_pago": "Facturación electrónica",
                "responsable_uso": "Equipo de Sistemas",
            },
            {
                "proveedor": "Hostingred",
                "servicio": "Certificado SSL corporativo",
                "periodicidad": PeriodicidadRenovacion.ANUAL,
                "dias": 19,
                "cantidad": 1,
                "valor": "295558.00",
                "renovacion_automatica": True,
                "medio_pago": "Facturación electrónica",
                "cuenta_vinculada": "ti@empresa.com",
                "responsable_uso": "Equipo de Sistemas",
            },
            {
                "proveedor": "GoDaddy",
                "servicio": "Dominio sfacebar.com",
                "periodicidad": PeriodicidadRenovacion.ANUAL,
                "dias": 84,
                "cantidad": 1,
                "valor": "175029.00",
                "renovacion_automatica": True,
                "medio_pago": "Visa **9777",
                "cuenta_vinculada": "ti@empresa.com",
                "responsable_uso": "Equipo de Sistemas",
            },
            {
                "proveedor": "GoDaddy",
                "servicio": "SSL administrado sfacebar.com",
                "periodicidad": PeriodicidadRenovacion.ANUAL,
                "dias": 25,
                "cantidad": 1,
                "valor": "456499.00",
                "renovacion_automatica": True,
                "medio_pago": "Visa **0297",
                "cuenta_vinculada": "ti@empresa.com",
                "responsable_uso": "Equipo de Sistemas",
            },
            {
                "proveedor": "ETB",
                "servicio": "Internet dedicado 200 Mbps",
                "periodicidad": PeriodicidadRenovacion.ANUAL,
                "dias": -89,
                "cantidad": 1,
                "valor": "1199000.00",
                "renovacion_automatica": False,
                "medio_pago": "Facturación electrónica",
                "responsable_uso": "Oficina Bogotá",
                "observacion": "Renovación pendiente de gestión.",
            },
            {
                "proveedor": "Movistar Empresas",
                "servicio": "Banda ancha 900 Mbps",
                "periodicidad": PeriodicidadRenovacion.ANUAL,
                "dias": -75,
                "cantidad": 1,
                "valor": "89592.00",
                "renovacion_automatica": False,
                "medio_pago": "Facturación electrónica",
                "responsable_uso": "Oficina Bogotá",
            },
            {
                "proveedor": "Crowdstrike",
                "servicio": "Falcon Go",
                "periodicidad": PeriodicidadRenovacion.ANUAL,
                "dias": -197,
                "cantidad": 1,
                "valor": "240509.00",
                "renovacion_automatica": False,
                "medio_pago": "Visa **0297",
                "cuenta_vinculada": "coordinacion@empresa.com",
                "responsable_uso": "Analista de seguridad",
                "observacion": "Licencia exigida por el banco para acceso a aplicativos.",
            },
            {
                "proveedor": "Fortinet",
                "servicio": "Fortigate 60E Bogotá",
                "periodicidad": PeriodicidadRenovacion.ANUAL,
                "dias": -83,
                "cantidad": 1,
                "valor": "3008755.00",
                "renovacion_automatica": False,
                "medio_pago": "Facturación electrónica",
                "cuenta_vinculada": "ti@empresa.com",
                "responsable_uso": "Equipo de Sistemas",
            },
            {
                "proveedor": "TMSOFT",
                "servicio": "Nebula Call 3 agentes",
                "periodicidad": PeriodicidadRenovacion.MENSUAL,
                "dias": 8,
                "cantidad": 3,
                "valor": "399000.00",
                "renovacion_automatica": True,
                "medio_pago": "Facturación electrónica",
                "cuenta_vinculada": "soporte@empresa.com",
                "responsable_uso": "Mesa de ayuda",
            },
            {
                "proveedor": "Amazon Web Services",
                "servicio": "Almacenamiento S3",
                "periodicidad": PeriodicidadRenovacion.MENSUAL,
                "dias": 12,
                "cantidad": 1,
                "valor": None,
                "renovacion_automatica": True,
                "medio_pago": "Facturación electrónica",
                "cuenta_vinculada": "ti@empresa.com",
                "responsable_uso": "Equipo de Sistemas",
                "is_active": False,
            },
        ]

        for registro in registros:
            datos = dict(registro)
            nombre = datos.pop("proveedor")
            proveedor, _ = Proveedor.objects.get_or_create(nombre=nombre)
            Licencia.objects.create(
                proveedor=proveedor,
                fecha_renovacion=hoy + timedelta(days=datos.pop("dias")),
                **datos,
            )

        self.stdout.write(
            self.style.SUCCESS(f"Seed aplicado: {len(registros)} licencias de ejemplo.")
        )
