from django.db import migrations, models
from django.db.models.functions import Lower


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0003_normalizar_emails"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="usuario",
            constraint=models.UniqueConstraint(
                Lower("email"),
                name="usuario_email_ci_unico",
            ),
        ),
    ]
