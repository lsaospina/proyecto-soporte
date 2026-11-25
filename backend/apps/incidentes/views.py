from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from apps.common.pagination import StandardResultsSetPagination
from apps.incidentes.filters import IncidenteFilter
from apps.incidentes.models import Incidente
from apps.incidentes.permissions import IsIncidenteAccess
from apps.incidentes.selectors import listar_incidentes, obtener_incidente
from apps.incidentes.serializers import (
    CambiarEstadoIncidenteSerializer,
    IncidenteCreateSerializer,
    IncidenteSerializer,
)
from apps.incidentes.services import cambiar_estado_incidente, registrar_incidente
from apps.auditoria.utils import get_client_ip


class IncidenteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsIncidenteAccess]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = IncidenteFilter
    search_fields = ["activo__serial", "descripcion"]
    ordering_fields = ["fecha", "created_at", "estado"]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        return listar_incidentes(usuario=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return IncidenteCreateSerializer
        if self.action == "cambiar_estado":
            return CambiarEstadoIncidenteSerializer
        return IncidenteSerializer

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed(
            "PATCH",
            detail="Use la acción cambiar_estado para modificar un incidente.",
        )

    def _ip(self):
        return get_client_ip(self.request)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if isinstance(response.data, dict):
            response.data["hoy"] = timezone.localdate()
        return response

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = registrar_incidente(serializer.validated_data, request.user, ip=self._ip())
        out = IncidenteSerializer(obtener_incidente(obj.pk), context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"])
    def cambiar_estado(self, request, pk=None):
        instancia = self.get_object()
        serializer = CambiarEstadoIncidenteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = cambiar_estado_incidente(
            instancia, serializer.validated_data["estado"], request.user, ip=self._ip()
        )
        return Response(IncidenteSerializer(obtener_incidente(obj.pk)).data)
