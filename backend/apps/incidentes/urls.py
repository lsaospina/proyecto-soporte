from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.incidentes.views import IncidenteViewSet

router = DefaultRouter()
router.register("incidentes", IncidenteViewSet, basename="incidente")

urlpatterns = [
    path("", include(router.urls)),
]
