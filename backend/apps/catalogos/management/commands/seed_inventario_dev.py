from datetime import date
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.activos.models import Activo, EstadoActivo
from apps.catalogos.models import Categoria, Marca, ModeloActivo, Sede, Ubicacion
from apps.catalogos.utils import normalizar_nombre


class Command(BaseCommand):
    help = "Seed de catálogos de inventario para desarrollo (idempotente)."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Este comando solo se ejecuta con DEBUG=True.")

        sedes_data = [
            ("Sede Central", "Calle 1 # 2-3"),
            ("Sede Norte", "Carrera 4 # 5-6"),
        ]
        sedes = {}
        for nombre, direccion in sedes_data:
            sede, _ = Sede.objects.get_or_create(
                nombre=normalizar_nombre(nombre),
                defaults={"direccion": direccion, "is_active": True},
            )
            sedes[nombre] = sede

        ubicaciones_por_sede = {
            "Sede Central": ["Piso 1", "Piso 2", "Bodega"],
            "Sede Norte": ["Recepción", "Oficina", "Almacén"],
        }
        for sede_nombre, ubis in ubicaciones_por_sede.items():
            sede = sedes[sede_nombre]
            for u in ubis:
                Ubicacion.objects.get_or_create(
                    sede=sede,
                    nombre=normalizar_nombre(u),
                    defaults={"is_active": True},
                )

        categorias_nombres = ["Computo", "Redes", "Perifericos", "Mobiliario", "Software"]
        categorias = {}
        for n in categorias_nombres:
            cat, _ = Categoria.objects.get_or_create(
                nombre=normalizar_nombre(n), defaults={"is_active": True}
            )
            categorias[n] = cat

        marcas_nombres = ["Dell", "HP", "Lenovo", "Cisco", "Logitech"]
        marcas = {}
        for n in marcas_nombres:
            m, _ = Marca.objects.get_or_create(
                nombre=normalizar_nombre(n), defaults={"is_active": True}
            )
            marcas[n] = m

        modelos = [
            ("Dell", "Computo", "Latitude 5420"),
            ("Dell", "Computo", "OptiPlex 7090"),
            ("HP", "Computo", "EliteBook 840"),
            ("HP", "Perifericos", "LaserJet Pro"),
            ("Lenovo", "Computo", "ThinkPad T14"),
            ("Lenovo", "Mobiliario", "Escritorio Ergo"),
            ("Cisco", "Redes", "Switch 2960"),
            ("Cisco", "Redes", "Router ISR 1100"),
            ("Logitech", "Perifericos", "Mouse MX Master"),
            ("Logitech", "Perifericos", "Teclado MX Keys"),
        ]
        for marca_n, cat_n, nombre in modelos:
            ModeloActivo.objects.get_or_create(
                marca=marcas[marca_n],
                nombre=normalizar_nombre(nombre),
                defaults={"categoria": categorias[cat_n], "is_active": True},
            )

        # 40 activos variados
        modelos_list = list(ModeloActivo.objects.all())
        estados = [
            EstadoActivo.DISPONIBLE,
            EstadoActivo.ASIGNADO,
            EstadoActivo.EN_MANTENIMIENTO,
            EstadoActivo.DADO_DE_BAJA,
        ]
        for i in range(40):
            modelo = modelos_list[i % len(modelos_list)]
            serial = f"SN-{i + 1:05d}"
            Activo.objects.get_or_create(
                serial=serial,
                defaults={
                    "modelo": modelo,
                    "fecha_adquisicion": date(2024, (i % 12) + 1, (i % 28) + 1),
                    "valor_adquisicion": Decimal("1000.00") + i,
                    "estado": estados[i % len(estados)],
                    "codigo_qr": f"AST-2024-{i + 1:06d}",
                    "procesador": "Intel i5" if i % 2 == 0 else "AMD Ryzen 5",
                    "ram_gb": 8 if i % 3 == 0 else 16,
                    "almacenamiento_gb": 256 if i % 2 == 0 else 512,
                    "direccion_mac": f"AA:BB:CC:DD:EE:{i:02X}",
                    "observaciones": f"Activo de prueba {i + 1}",
                    "is_active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("Seed de inventario aplicado."))
