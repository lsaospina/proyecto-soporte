# RF014: gestión de bajas (modelo Baja)

import django.db.models.deletion
import django.utils.timezone
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("activos", "0004_historicalactivo_plazo_garantia_meses"),
        ("documentos", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Baja",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
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
                ("fecha", models.DateField(default=django.utils.timezone.localdate)),
                ("motivo", models.TextField()),
                (
                    "activo",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="baja",
                        to="activos.activo",
                    ),
                ),
                (
                    "autorizado_por",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="bajas_autorizadas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "documento",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="bajas",
                        to="documentos.documento",
                    ),
                ),
            ],
            options={
                "verbose_name": "Baja",
                "verbose_name_plural": "Bajas",
                "ordering": ["-fecha", "-id"],
            },
        ),
        migrations.CreateModel(
            name="HistoricalBaja",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        blank=True,
                        editable=False,
                        help_text="Momento exacto en que se creó el registro.",
                        verbose_name="Fecha de creación",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        blank=True,
                        editable=False,
                        help_text="Momento exacto de la última modificación.",
                        verbose_name="Fecha de actualización",
                    ),
                ),
                ("fecha", models.DateField(default=django.utils.timezone.localdate)),
                ("motivo", models.TextField()),
                (
                    "history_id",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("history_date", models.DateTimeField(db_index=True)),
                (
                    "history_change_reason",
                    models.CharField(max_length=100, null=True),
                ),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "activo",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="activos.activo",
                    ),
                ),
                (
                    "autorizado_por",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "documento",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="documentos.documento",
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Baja",
                "verbose_name_plural": "historical Bajas",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AddIndex(
            model_name="baja",
            index=models.Index(fields=["fecha"], name="baja_fecha_idx"),
        ),
    ]
