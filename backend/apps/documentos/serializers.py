import os

from rest_framework import serializers

from apps.activos.models import Activo
from apps.documentos.models import Documento, TipoDocumento

MAX_BYTES = 10 * 1024 * 1024
EXTENSIONES_PERMITIDAS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".txt",
}


class DocumentoSerializer(serializers.ModelSerializer):
    activo_serial = serializers.CharField(source="activo.serial", read_only=True)
    tipo_etiqueta = serializers.CharField(source="get_tipo_display", read_only=True)
    subido_por_nombre = serializers.CharField(
        source="subido_por.nombre_completo", read_only=True
    )
    archivo_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Documento
        fields = [
            "id",
            "activo",
            "activo_serial",
            "nombre",
            "tipo",
            "tipo_etiqueta",
            "descripcion",
            "subido_por",
            "subido_por_nombre",
            "archivo_nombre",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_archivo_nombre(self, obj):
        return os.path.basename(obj.archivo.name) if obj.archivo else None


class DocumentoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = ["activo", "nombre", "tipo", "archivo", "descripcion"]

    def validate_archivo(self, archivo):
        if archivo.size > MAX_BYTES:
            raise serializers.ValidationError("El archivo supera el tamaño máximo de 10 MB.")
        extension = os.path.splitext(archivo.name)[1].lower()
        if extension not in EXTENSIONES_PERMITIDAS:
            raise serializers.ValidationError(
                "Tipo de archivo no permitido. Usa PDF, imágenes, Word, Excel o TXT."
            )
        return archivo

    def validate_nombre(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre es obligatorio.")
        return value.strip()
