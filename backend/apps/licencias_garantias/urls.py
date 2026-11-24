from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.licencias_garantias.views import LicenciaViewSet

router = DefaultRouter()
router.register("licencias", LicenciaViewSet, basename="licencia")

urlpatterns = [path("", include(router.urls))]
