# Corrección RF010: campo de plazo de garantía en Activo

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("activos", "0002_historicalasignacionactivo_asignacionactivo"),
    ]

    operations = [
        migrations.AddField(
            model_name="activo",
            name="plazo_garantia_meses",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Plazo de garantía en meses (ej. 12, 6).",
                null=True,
            ),
        ),
    ]
