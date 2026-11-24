from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.mantenimientos.views import MantenimientoViewSet

router = DefaultRouter()
router.register("mantenimientos", MantenimientoViewSet, basename="mantenimiento")

urlpatterns = [path("", include(router.urls))]
