from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.common.pagination import StandardResultsSetPagination
from apps.common.permissions import IsAdministrador
from apps.licencias_garantias.filters import LicenciaFilter
from apps.licencias_garantias.selectors import (
    listar_licencias,
    listar_proveedores,
    resumen_licencias,
)
from apps.licencias_garantias.serializers import (
    LicenciaSerializer,
    LicenciaWriteSerializer,
    ProveedorSerializer,
    RenovarLicenciaSerializer,
    ResumenLicenciasSerializer,
)
from apps.licencias_garantias.services import (
    actualizar_licencia,
    crear_licencia,
    inactivar_licencia,
    reactivar_licencia,
    renovar_licencia,
)


def _ip(request):
    from apps.auditoria.utils import get_client_ip

    return get_client_ip(request)


class LicenciaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdministrador]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LicenciaFilter
    search_fields = [
        "servicio",
        "proveedor__nombre",
        "responsable_uso",
        "cuenta_vinculada",
        "medio_pago",
    ]
    ordering_fields = ["fecha_renovacion", "servicio", "valor", "proveedor__nombre", "created_at"]
    ordering = ["fecha_renovacion", "servicio"]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        return listar_licencias()

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return LicenciaWriteSerializer
        if self.action == "renovar":
            return RenovarLicenciaSerializer
        return LicenciaSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if isinstance(response.data, dict):
            response.data["hoy"] = timezone.localdate()
        return response

    def create(self, request, *args, **kwargs):
        serializer = LicenciaWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instancia = crear_licencia(serializer.validated_data, request.user, ip=_ip(request))
        return Response(LicenciaSerializer(instancia).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instancia = self.get_object()
        serializer = LicenciaWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instancia = actualizar_licencia(
            instancia, serializer.validated_data, request.user, ip=_ip(request)
        )
        return Response(LicenciaSerializer(instancia).data)

    @extend_schema(responses={200: ResumenLicenciasSerializer})
    @action(detail=False, methods=["get"])
    def resumen(self, request):
        return Response(ResumenLicenciasSerializer(resumen_licencias()).data)

    @extend_schema(responses={200: ProveedorSerializer(many=True)})
    @action(detail=False, methods=["get"])
    def proveedores(self, request):
        return Response(ProveedorSerializer(listar_proveedores(), many=True).data)

    @extend_schema(request=RenovarLicenciaSerializer, responses={200: LicenciaSerializer})
    @action(detail=True, methods=["post"])
    def renovar(self, request, pk=None):
        instancia = self.get_object()
        serializer = RenovarLicenciaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instancia = renovar_licencia(
            instancia,
            serializer.validated_data["fecha_renovacion"],
            serializer.validated_data.get("valor"),
            request.user,
            ip=_ip(request),
        )
        return Response(LicenciaSerializer(instancia).data)

    @extend_schema(responses={200: LicenciaSerializer})
    @action(detail=True, methods=["post"])
    def inactivar(self, request, pk=None):
        instancia = inactivar_licencia(self.get_object(), request.user, ip=_ip(request))
        return Response(LicenciaSerializer(instancia).data)

    @extend_schema(responses={200: LicenciaSerializer})
    @action(detail=True, methods=["post"])
    def reactivar(self, request, pk=None):
        instancia = reactivar_licencia(self.get_object(), request.user, ip=_ip(request))
        return Response(LicenciaSerializer(instancia).data)
