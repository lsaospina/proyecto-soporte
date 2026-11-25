from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.auditoria.utils import get_client_ip
from apps.bajas.filters import BajaFilter
from apps.bajas.permissions import IsBajaAccess
from apps.bajas.selectors import listar_bajas, obtener_baja
from apps.bajas.serializers import BajaCreateSerializer, BajaSerializer
from apps.bajas.services import registrar_baja
from apps.common.pagination import StandardResultsSetPagination


class BajaViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsBajaAccess]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BajaFilter
    search_fields = ["activo__serial", "activo__codigo_qr", "motivo"]
    ordering_fields = ["fecha", "created_at"]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return listar_bajas()

    def get_serializer_class(self):
        if self.action == "create":
            return BajaCreateSerializer
        return BajaSerializer

    def create(self, request, *args, **kwargs):
        serializer = BajaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = registrar_baja(serializer.validated_data, request.user, ip=get_client_ip(request))
        out = BajaSerializer(obtener_baja(obj.pk), context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)
