# RF013: gestión documental (modelo Documento)

import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("activos", "0004_historicalactivo_plazo_garantia_meses"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Documento",
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
                ("nombre", models.CharField(max_length=150)),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("FACTURA", "Factura"),
                            ("MANUAL", "Manual"),
                            ("GARANTIA", "Garantía"),
                            ("CONTRATO", "Contrato"),
                            ("EVIDENCIA_MANTENIMIENTO", "Evidencia de mantenimiento"),
                            ("OTRO", "Otro"),
                        ],
                        default="OTRO",
                        max_length=30,
                    ),
                ),
                ("archivo", models.FileField(upload_to="documentos/%Y/%m/")),
                ("descripcion", models.TextField(blank=True, default="")),
                (
                    "activo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="documentos",
                        to="activos.activo",
                    ),
                ),
                (
                    "subido_por",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="documentos_subidos",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Documento",
                "verbose_name_plural": "Documentos",
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="HistoricalDocumento",
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
                ("nombre", models.CharField(max_length=150)),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("FACTURA", "Factura"),
                            ("MANUAL", "Manual"),
                            ("GARANTIA", "Garantía"),
                            ("CONTRATO", "Contrato"),
                            ("EVIDENCIA_MANTENIMIENTO", "Evidencia de mantenimiento"),
                            ("OTRO", "Otro"),
                        ],
                        default="OTRO",
                        max_length=30,
                    ),
                ),
                ("archivo", models.FileField(upload_to="documentos/%Y/%m/")),
                ("descripcion", models.TextField(blank=True, default="")),
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
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "subido_por",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Documento",
                "verbose_name_plural": "historical Documentos",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AddIndex(
            model_name="documento",
            index=models.Index(fields=["activo"], name="documento_activo_idx"),
        ),
        migrations.AddIndex(
            model_name="documento",
            index=models.Index(fields=["tipo"], name="documento_tipo_idx"),
        ),
    ]
