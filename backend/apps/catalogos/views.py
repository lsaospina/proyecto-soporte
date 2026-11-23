from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.catalogos.filters import (
    CategoriaFilter,
    MarcaFilter,
    ModeloActivoFilter,
    SedeFilter,
    UbicacionFilter,
)
from apps.catalogos.models import Categoria, Marca, ModeloActivo, Sede, Ubicacion
from apps.catalogos.permissions import IsCatalogoAccess
from apps.catalogos.selectors import (
    listar_categorias,
    listar_marcas,
    listar_modelos,
    listar_sedes,
    listar_ubicaciones,
)
from apps.catalogos.serializers import (
    CategoriaSerializer,
    MarcaSerializer,
    ModeloActivoSerializer,
    SedeSerializer,
    UbicacionSerializer,
)
from apps.catalogos.services import (
    actualizar_catalogo,
    crear_catalogo,
    inactivar_catalogo,
    reactivar_catalogo,
)
from apps.common.pagination import StandardResultsSetPagination


class BaseCatalogoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsCatalogoAccess]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_ip(self):
        from apps.auditoria.utils import get_client_ip

        return get_client_ip(self.request)

    def perform_create(self, serializer):
        obj = crear_catalogo(
            self.ENTIDAD,
            serializer.validated_data,
            self.request.user,
            ip=self.get_ip(),
        )
        serializer.instance = obj

    def perform_update(self, serializer):
        instancia = self.get_object()
        datos = serializer.validated_data
        if "is_active" in datos and datos["is_active"] != instancia.is_active:
            if datos["is_active"] is False:
                inactivar_catalogo(self.ENTIDAD, instancia, self.request.user, ip=self.get_ip())
                for k, v in datos.items():
                    if k != "is_active":
                        setattr(instancia, k, v)
                instancia.save()
                return
            else:
                reactivar_catalogo(self.ENTIDAD, instancia, self.request.user, ip=self.get_ip())
                for k, v in datos.items():
                    if k != "is_active":
                        setattr(instancia, k, v)
                instancia.save()
                return
        actualizar_catalogo(self.ENTIDAD, instancia, datos, self.request.user, ip=self.get_ip())
        serializer.instance = instancia


class SedeViewSet(BaseCatalogoViewSet):
    ENTIDAD = "Sede"
    queryset = Sede.objects.all()
    serializer_class = SedeSerializer
    filterset_class = SedeFilter
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "created_at"]

    def get_queryset(self):
        return listar_sedes()


class UbicacionViewSet(BaseCatalogoViewSet):
    ENTIDAD = "Ubicacion"
    queryset = Ubicacion.objects.all()
    serializer_class = UbicacionSerializer
    filterset_class = UbicacionFilter
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "created_at"]

    def get_queryset(self):
        return listar_ubicaciones()


class CategoriaViewSet(BaseCatalogoViewSet):
    ENTIDAD = "Categoria"
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    filterset_class = CategoriaFilter
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "created_at"]

    def get_queryset(self):
        return listar_categorias()


class MarcaViewSet(BaseCatalogoViewSet):
    ENTIDAD = "Marca"
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    filterset_class = MarcaFilter
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "created_at"]

    def get_queryset(self):
        return listar_marcas()


class ModeloActivoViewSet(BaseCatalogoViewSet):
    ENTIDAD = "ModeloActivo"
    queryset = ModeloActivo.objects.all()
    serializer_class = ModeloActivoSerializer
    filterset_class = ModeloActivoFilter
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "created_at"]

    def get_queryset(self):
        return listar_modelos()
