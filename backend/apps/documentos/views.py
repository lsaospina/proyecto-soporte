import os

from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.auditoria.services import registrar_evento
from apps.auditoria.utils import get_client_ip
from apps.common.pagination import StandardResultsSetPagination
from apps.documentos.filters import DocumentoFilter
from apps.documentos.permissions import IsDocumentoAccess
from apps.documentos.selectors import listar_documentos, obtener_documento
from apps.documentos.serializers import (
    DocumentoCreateSerializer,
    DocumentoSerializer,
)
from apps.documentos.services import eliminar_documento, subir_documento


class DocumentoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsDocumentoAccess]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DocumentoFilter
    search_fields = ["nombre", "descripcion", "activo__serial", "activo__codigo_qr"]
    ordering_fields = ["created_at", "nombre", "tipo"]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        return listar_documentos()

    def get_serializer_class(self):
        if self.action == "create":
            return DocumentoCreateSerializer
        return DocumentoSerializer

    def _ip(self):
        return get_client_ip(self.request)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = subir_documento(serializer.validated_data, request.user, ip=self._ip())
        out = DocumentoSerializer(obtener_documento(obj.pk), context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instancia = self.get_object()
        eliminar_documento(instancia, request.user, ip=self._ip())
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(responses={(200, "application/octet-stream"): bytes})
    @action(detail=True, methods=["get"])
    def descargar(self, request, pk=None):
        obj = self.get_object()
        registrar_evento(
            usuario=request.user,
            accion="DOCUMENTO_DESCARGADO",
            entidad="Documento",
            entidad_id=obj.pk,
            ip=self._ip(),
        )
        archivo = obj.archivo.open("rb")
        return FileResponse(
            archivo,
            as_attachment=True,
            filename=os.path.basename(obj.archivo.name),
        )
