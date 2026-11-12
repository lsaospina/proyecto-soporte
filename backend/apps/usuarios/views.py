from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.auditoria.utils import get_client_ip
from apps.common.permissions import IsAdministrador

from .filters import UsuarioFilter
from .models import Usuario
from .selectors import listar_usuarios
from .serializers import (
    UsuarioCreateResponseSerializer,
    UsuarioCreateSerializer,
    UsuarioDetailSerializer,
    UsuarioListSerializer,
    UsuarioResetPasswordResponseSerializer,
    UsuarioUpdateSerializer,
)
from .services import (
    actualizar_usuario,
    crear_usuario,
    inactivar_usuario,
    reactivar_usuario,
    resetear_mfa,
    resetear_password,
)


@extend_schema_view(
    list=extend_schema(tags=["Usuarios"], summary="Listar usuarios"),
    retrieve=extend_schema(tags=["Usuarios"], summary="Detalle de usuario"),
    create=extend_schema(tags=["Usuarios"], summary="Crear usuario"),
    partial_update=extend_schema(tags=["Usuarios"], summary="Actualizar usuario"),
)
class UsuarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdministrador]
    queryset = Usuario.objects.all().select_related("dispositivo_mfa")
    serializer_class = UsuarioListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UsuarioFilter
    search_fields = ["email", "nombre_completo"]
    ordering_fields = ["email", "nombre_completo", "rol", "created_at"]
    ordering = ["email"]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        return listar_usuarios(
            rol=self.request.query_params.get("rol"),
            is_active=self.request.query_params.get("is_active"),
            search=self.request.query_params.get("search"),
        )

    def get_serializer_class(self):
        if self.action == "list":
            return UsuarioListSerializer
        if self.action == "retrieve":
            return UsuarioDetailSerializer
        if self.action == "create":
            return UsuarioCreateSerializer
        if self.action in {"partial_update", "update"}:
            return UsuarioUpdateSerializer
        return UsuarioListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip = get_client_ip(request)
        usuario, password_temporal = crear_usuario(
            email=serializer.validated_data["email"],
            nombre_completo=serializer.validated_data["nombre_completo"],
            rol=serializer.validated_data["rol"],
            actor=request.user,
            ip=ip,
        )
        out = UsuarioCreateResponseSerializer(
            {"usuario": usuario, "password_temporal": password_temporal}
        )
        response = Response(out.data, status=status.HTTP_201_CREATED)
        response["Cache-Control"] = "no-store"
        return response

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip = get_client_ip(request)
        usuario = actualizar_usuario(
            instance,
            nombre_completo=serializer.validated_data["nombre_completo"],
            rol=serializer.validated_data["rol"],
            actor=request.user,
            ip=ip,
        )
        return Response(UsuarioDetailSerializer(usuario).data)

    @extend_schema(
        tags=["Usuarios"],
        summary="Resetear contraseña",
        request=None,
        responses={200: UsuarioResetPasswordResponseSerializer},
    )
    @action(detail=True, methods=["post"], url_path="reset_password")
    def reset_password(self, request, pk=None):
        usuario = self.get_object()
        ip = get_client_ip(request)
        password_temporal = resetear_password(usuario, actor=request.user, ip=ip)
        response = Response({"password_temporal": password_temporal}, status=status.HTTP_200_OK)
        response["Cache-Control"] = "no-store"
        return response

    @extend_schema(tags=["Usuarios"], summary="Resetear MFA", request=None, responses={204: None})
    @action(detail=True, methods=["post"], url_path="reset_mfa")
    def reset_mfa(self, request, pk=None):
        usuario = self.get_object()
        ip = get_client_ip(request)
        resetear_mfa(usuario, actor=request.user, ip=ip)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        tags=["Usuarios"],
        summary="Activar usuario",
        request=None,
        responses={200: UsuarioDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="activar")
    def activar(self, request, pk=None):
        usuario = self.get_object()
        ip = get_client_ip(request)
        usuario = reactivar_usuario(usuario, actor=request.user, ip=ip)
        return Response(UsuarioDetailSerializer(usuario).data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Usuarios"],
        summary="Desactivar usuario",
        request=None,
        responses={200: UsuarioDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="desactivar")
    def desactivar(self, request, pk=None):
        usuario = self.get_object()
        ip = get_client_ip(request)
        usuario = inactivar_usuario(usuario, actor=request.user, ip=ip)
        return Response(UsuarioDetailSerializer(usuario).data, status=status.HTTP_200_OK)
