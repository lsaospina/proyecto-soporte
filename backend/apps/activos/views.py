from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.activos.filters import ActivoFilter, AsignacionFilter
from apps.activos.models import Activo
from apps.activos.permissions import IsActivoAccess, IsAsignacionAccess
from apps.activos.selectors import (
    listar_activos,
    listar_asignaciones,
    resumen_asignaciones,
    usuarios_asignables,
)
from apps.activos.serializers import (
    ActivoCreateUpdateSerializer,
    ActivoSerializer,
    AsignacionSerializer,
    AsignarActivoSerializer,
    CerrarAsignacionSerializer,
    ResumenAsignacionesSerializer,
    UsuarioAsignableSerializer,
)
from apps.activos.services import (
    actualizar_activo,
    asignar_activo,
    cerrar_asignacion,
    crear_activo,
    inactivar_activo,
    reactivar_activo,
    reasignar_activo,
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
        qs = listar_activos()
        params = self.request.query_params
        mostrar_todos = str(params.get("todos", "")).lower() in ("1", "true", "si", "sí")
        if "is_active" not in params and not mostrar_todos:
            qs = qs.filter(is_active=True)
        return qs

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


class AsignacionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAsignacionAccess]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AsignacionFilter
    search_fields = [
        "activo__serial",
        "activo__codigo_qr",
        "usuario__nombre_completo",
        "usuario__email",
        "activo__modelo__marca__nombre",
        "activo__modelo__nombre",
    ]
    ordering_fields = ["fecha_inicio", "fecha_fin", "created_at"]
    ordering = ["-fecha_inicio", "-id"]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return listar_asignaciones()

    def get_serializer_class(self):
        if self.action in ("create", "reasignar"):
            return AsignarActivoSerializer
        if self.action == "cerrar":
            return CerrarAsignacionSerializer
        return AsignacionSerializer

    def _ip(self):
        from apps.auditoria.utils import get_client_ip

        return get_client_ip(self.request)

    @extend_schema(request=AsignarActivoSerializer, responses={201: AsignacionSerializer})
    def create(self, request, *args, **kwargs):
        serializer = AsignarActivoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        instancia = asignar_activo(
            datos["activo"],
            datos["usuario"],
            fecha_inicio=datos.get("fecha_inicio"),
            observacion=datos.get("observacion", ""),
            actor=request.user,
            ip=self._ip(),
        )
        return Response(AsignacionSerializer(instancia).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=CerrarAsignacionSerializer, responses={200: AsignacionSerializer})
    @action(detail=True, methods=["post"])
    def cerrar(self, request, pk=None):
        asignacion = self.get_object()
        serializer = CerrarAsignacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instancia = cerrar_asignacion(
            asignacion,
            fecha_fin=serializer.validated_data.get("fecha_fin"),
            actor=request.user,
            ip=self._ip(),
        )
        return Response(AsignacionSerializer(instancia).data)

    @extend_schema(request=AsignarActivoSerializer, responses={201: AsignacionSerializer})
    @action(detail=False, methods=["post"])
    def reasignar(self, request):
        serializer = AsignarActivoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        instancia = reasignar_activo(
            datos["activo"],
            datos["usuario"],
            fecha_inicio=datos.get("fecha_inicio"),
            observacion=datos.get("observacion", ""),
            actor=request.user,
            ip=self._ip(),
        )
        return Response(AsignacionSerializer(instancia).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses={200: ResumenAsignacionesSerializer})
    @action(detail=False, methods=["get"])
    def resumen(self, request):
        return Response(ResumenAsignacionesSerializer(resumen_asignaciones()).data)

    @extend_schema(responses={200: UsuarioAsignableSerializer(many=True)})
    @action(detail=False, methods=["get"])
    def usuarios(self, request):
        return Response(UsuarioAsignableSerializer(usuarios_asignables(), many=True).data)
