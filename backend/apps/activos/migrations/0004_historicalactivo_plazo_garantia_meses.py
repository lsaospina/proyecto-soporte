# Agrega plazo_garantia_meses también a la tabla histórica de Activo (simple-history)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("activos", "0003_activo_plazo_garantia_meses"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalactivo",
            name="plazo_garantia_meses",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Plazo de garantía en meses (ej. 12, 6).",
                null=True,
            ),
        ),
    ]
