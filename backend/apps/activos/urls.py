from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.activos.views import ActivoViewSet

router = DefaultRouter()
router.register("activos", ActivoViewSet, basename="activo")

urlpatterns = [path("", include(router.urls))]
