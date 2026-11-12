from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="debe_cambiar_password",
            field=models.BooleanField(
                default=False,
                help_text="Indica si el usuario debe cambiar su contraseña en el próximo inicio de sesión.",
                verbose_name="Debe cambiar contraseña",
            ),
        ),
    ]
