from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.common.pagination import StandardResultsSetPagination
from apps.mantenimientos.filters import MantenimientoFilter
from apps.mantenimientos.models import Mantenimiento
from apps.mantenimientos.permissions import IsMantenimientoAccess
from apps.mantenimientos.selectors import (
    anotar_situacion,
    calendario_mensual,
    listar_mantenimientos,
    obtener_mantenimiento,
    resumen_anual,
)
from apps.mantenimientos.serializers import (
    CancelarMantenimientoSerializer,
    CompletarMantenimientoSerializer,
    MantenimientoCreateSerializer,
    MantenimientoSerializer,
    ReprogramarMantenimientoSerializer,
)
from apps.mantenimientos.services import (
    cancelar_mantenimiento,
    completar_mantenimiento,
    programar_mantenimiento,
    reprogramar_mantenimiento,
)
from apps.usuarios.models import Usuario


class MantenimientoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsMantenimientoAccess]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MantenimientoFilter
    search_fields = [
        "activo__serial",
        "activo__codigo_qr",
        "activo__modelo__nombre",
        "activo__modelo__marca__nombre",
    ]
    ordering_fields = ["fecha_programada", "created_at", "estado"]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        if self.action == "list":
            return listar_mantenimientos()
        return anotar_situacion(
            Mantenimiento.objects.select_related(
                "activo__modelo__marca", "activo__modelo__categoria", "tecnico"
            )
        )

    def get_serializer_class(self):
        if self.action == "create":
            return MantenimientoCreateSerializer
        if self.action == "completar":
            return CompletarMantenimientoSerializer
        if self.action == "reprogramar":
            return ReprogramarMantenimientoSerializer
        if self.action == "cancelar":
            return CancelarMantenimientoSerializer
        return MantenimientoSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if isinstance(response.data, dict):
            response.data["hoy"] = timezone.localdate()
        return response

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = programar_mantenimiento(serializer.validated_data, request.user, ip=self._ip())
        out = MantenimientoSerializer(obtener_mantenimiento(obj.pk), context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    def _ip(self):
        from apps.auditoria.utils import get_client_ip

        return get_client_ip(self.request)

    @extend_schema(responses={200: MantenimientoSerializer})
    @action(detail=True, methods=["post"])
    def completar(self, request, pk=None):
        instancia = self.get_object()
        serializer = CompletarMantenimientoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = completar_mantenimiento(
            instancia, serializer.validated_data, request.user, ip=self._ip()
        )
        return Response(MantenimientoSerializer(obtener_mantenimiento(obj.pk)).data)

    @extend_schema(request=ReprogramarMantenimientoSerializer)
    @action(detail=True, methods=["post"])
    def reprogramar(self, request, pk=None):
        instancia = self.get_object()
        serializer = ReprogramarMantenimientoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj, creado = reprogramar_mantenimiento(
            instancia, serializer.validated_data["fecha_programada"], request.user, ip=self._ip()
        )
        out = MantenimientoSerializer(obtener_mantenimiento(obj.pk)).data
        code = status.HTTP_201_CREATED if creado else status.HTTP_200_OK
        return Response(out, status=code)

    @extend_schema(request=CancelarMantenimientoSerializer)
    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        instancia = self.get_object()
        serializer = CancelarMantenimientoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = cancelar_mantenimiento(
            instancia, serializer.validated_data["motivo"], request.user, ip=self._ip()
        )
        return Response(MantenimientoSerializer(obtener_mantenimiento(obj.pk)).data)

    @action(detail=False, methods=["get"])
    def tecnicos(self, request):
        usuarios = Usuario.objects.filter(
            is_active=True, rol__in=["ADMINISTRADOR", "TECNICO"]
        ).order_by("nombre_completo")
        return Response(
            [{"id": u.id, "nombre_completo": u.nombre_completo, "email": u.email} for u in usuarios]
        )

    @action(detail=False, methods=["get"])
    def resumen(self, request):
        try:
            anio = int(request.query_params.get("anio", timezone.localdate().year))
        except (TypeError, ValueError):
            return Response({"detail": "Año inválido."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(resumen_anual(anio))

    @action(detail=False, methods=["get"])
    def calendario(self, request):
        hoy = timezone.localdate()
        try:
            anio = int(request.query_params.get("anio", hoy.year))
            mes = int(request.query_params.get("mes", hoy.month))
        except (TypeError, ValueError):
            return Response({"detail": "Año o mes inválido."}, status=status.HTTP_400_BAD_REQUEST)
        if mes < 1 or mes > 12:
            return Response({"detail": "Mes inválido."}, status=status.HTTP_400_BAD_REQUEST)
        data = calendario_mensual(anio, mes)
        data["mantenimientos"] = MantenimientoSerializer(data["mantenimientos"], many=True).data
        return Response(data)

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
