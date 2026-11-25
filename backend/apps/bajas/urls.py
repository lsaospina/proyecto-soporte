from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.bajas.views import BajaViewSet

router = DefaultRouter()
router.register("bajas", BajaViewSet, basename="baja")

urlpatterns = [
    path("", include(router.urls)),
]
