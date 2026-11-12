# Generated for T-002
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RegistroAuditoria",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Momento exacto en que se creó el registro.",
                        verbose_name="Fecha de creación",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Momento exacto de la última modificación.",
                        verbose_name="Fecha de actualización",
                    ),
                ),
                (
                    "accion",
                    models.CharField(
                        choices=[
                            ("LOGIN_EXITOSO", "Inicio de sesión exitoso"),
                            ("LOGIN_FALLIDO", "Inicio de sesión fallido"),
                            ("LOGOUT", "Cierre de sesión"),
                            ("MFA_ACTIVADO", "MFA activado"),
                            ("MFA_VERIFICADO", "MFA verificado"),
                            ("MFA_RECHAZADO", "MFA rechazado"),
                            ("PASSWORD_CAMBIADA", "Contraseña cambiada"),
                            ("USUARIO_CREADO", "Usuario creado"),
                            ("USUARIO_ACTUALIZADO", "Usuario actualizado"),
                            ("USUARIO_INACTIVADO", "Usuario inactivado"),
                            ("USUARIO_REACTIVADO", "Usuario reactivado"),
                            ("PASSWORD_RESETEADA", "Contraseña reseteada"),
                            ("MFA_RESETEADO", "MFA reseteado"),
                        ],
                        max_length=40,
                        verbose_name="Acción",
                    ),
                ),
                (
                    "entidad",
                    models.CharField(blank=True, default="", max_length=50, verbose_name="Entidad"),
                ),
                (
                    "entidad_id",
                    models.CharField(
                        blank=True, default="", max_length=64, verbose_name="ID de entidad"
                    ),
                ),
                ("fecha", models.DateTimeField(auto_now_add=True, verbose_name="Fecha")),
                (
                    "ip",
                    models.GenericIPAddressField(
                        blank=True, null=True, verbose_name="Dirección IP"
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="registros_auditoria",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Registro de auditoría",
                "verbose_name_plural": "Registros de auditoría",
                "ordering": ["-fecha"],
            },
        ),
        migrations.AddIndex(
            model_name="registroauditoria",
            index=models.Index(fields=["fecha"], name="auditoria_fecha_idx"),
        ),
        migrations.AddIndex(
            model_name="registroauditoria",
            index=models.Index(fields=["accion"], name="auditoria_accion_idx"),
        ),
        migrations.AddIndex(
            model_name="registroauditoria",
            index=models.Index(fields=["usuario"], name="auditoria_usuario_idx"),
        ),
    ]
