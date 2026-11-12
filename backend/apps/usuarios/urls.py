from rest_framework.routers import DefaultRouter

from .views import UsuarioViewSet

app_name = "usuarios"

router = DefaultRouter()
router.register(r"", UsuarioViewSet, basename="usuario")

urlpatterns = router.urls
