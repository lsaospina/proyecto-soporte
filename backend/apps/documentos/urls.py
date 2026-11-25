from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.documentos.views import DocumentoViewSet

router = DefaultRouter()
router.register("documentos", DocumentoViewSet, basename="documento")

urlpatterns = [
    path("", include(router.urls)),
]
