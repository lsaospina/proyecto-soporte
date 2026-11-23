from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.catalogos.views import (
    CategoriaViewSet,
    MarcaViewSet,
    ModeloActivoViewSet,
    SedeViewSet,
    UbicacionViewSet,
)

router = DefaultRouter()
router.register("sedes", SedeViewSet, basename="sede")
router.register("ubicaciones", UbicacionViewSet, basename="ubicacion")
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("marcas", MarcaViewSet, basename="marca")
router.register("modelos", ModeloActivoViewSet, basename="modelo")

urlpatterns = [path("", include(router.urls))]
