from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.activos.views import ActivoViewSet, AsignacionViewSet

router = DefaultRouter()
router.register("activos", ActivoViewSet, basename="activo")
router.register("asignaciones", AsignacionViewSet, basename="asignacion")

urlpatterns = [path("", include(router.urls))]
