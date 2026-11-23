from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.activos.filters import ActivoFilter
from apps.activos.models import Activo
from apps.activos.permissions import IsActivoAccess
from apps.activos.selectors import listar_activos
from apps.activos.serializers import ActivoCreateUpdateSerializer, ActivoSerializer
from apps.activos.services import (
    actualizar_activo,
    crear_activo,
    inactivar_activo,
    reactivar_activo,
)
from apps.common.pagination import StandardResultsSetPagination


class ActivoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsActivoAccess]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ActivoFilter
    search_fields = [
        "serial",
        "codigo_qr",
        "direccion_mac",
        "modelo__marca__nombre",
        "modelo__nombre",
    ]
    ordering_fields = ["serial", "fecha_adquisicion", "created_at"]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        if self.action in (
            "retrieve",
            "inactivar",
            "reactivar",
            "historial",
            "partial_update",
            "update",
            "destroy",
        ):
            return Activo.objects.select_related("modelo__marca", "modelo__categoria")
        return listar_activos()

    def get_serializer_class(self):
        if self.action in ("create", "partial_update", "update"):
            return ActivoCreateUpdateSerializer
        return ActivoSerializer

    def perform_create(self, serializer):
        obj = crear_activo(serializer.validated_data, self.request.user, ip=self._ip())
        serializer.instance = obj

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        out = ActivoSerializer(serializer.instance)
        headers = self.get_success_headers(out.data)
        return Response(out.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        instancia = self.get_object()
        actualizar_activo(instancia, serializer.validated_data, self.request.user, ip=self._ip())
        serializer.instance = instancia

    def _ip(self):
        from apps.auditoria.utils import get_client_ip

        return get_client_ip(self.request)

    @action(detail=True, methods=["post"])
    def inactivar(self, request, pk=None):
        obj = self.get_object()
        if request.user.rol != "ADMINISTRADOR":
            return Response(status=status.HTTP_403_FORBIDDEN)
        inactivar_activo(obj, request.user, ip=self._ip())
        return Response(ActivoSerializer(obj).data)

    @action(detail=True, methods=["post"])
    def reactivar(self, request, pk=None):
        obj = self.get_object()
        if request.user.rol != "ADMINISTRADOR":
            return Response(status=status.HTTP_403_FORBIDDEN)
        reactivar_activo(obj, request.user, ip=self._ip())
        return Response(ActivoSerializer(obj).data)

    @action(detail=True, methods=["get"])
    def historial(self, request, pk=None):
        obj = self.get_object()
        hist = obj.history.all().order_by("-history_date")
        data = [
            {
                "fecha": h.history_date,
                "usuario": getattr(h.history_user, "email", None),
                "tipo": h.history_type,
                "campos": [f for f in h.diff_against(h.prev_record).changed_fields]
                if h.prev_record
                else [],
            }
            for h in hist
        ]
        return Response(data)
