from django.db import migrations


def normalizar_emails(apps, schema_editor):
    Usuario = apps.get_model("usuarios", "Usuario")
    # Normalizar a minúsculas
    rows = list(Usuario.objects.values("id", "email"))
    normalized = {}
    collisions = []
    for row in rows:
        email = (row["email"] or "").strip().lower()
        if email in normalized and normalized[email] != row["id"]:
            collisions.append(email)
        else:
            normalized[email] = row["id"]
    if collisions:
        raise RuntimeError(
            "Colisión al normalizar emails a minúsculas. Correos en conflicto: "
            + ", ".join(sorted(set(collisions)))
        )
    for row in rows:
        email_norm = (row["email"] or "").strip().lower()
        if row["email"] != email_norm:
            Usuario.objects.filter(id=row["id"]).update(email=email_norm)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0002_usuario_debe_cambiar_password"),
    ]

    operations = [
        migrations.RunPython(normalizar_emails, noop),
    ]
