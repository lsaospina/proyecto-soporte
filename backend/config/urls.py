from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.common.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    # OpenAPI Docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Core API v1
    path("api/v1/health/", HealthCheckView.as_view(), name="health-check"),
    path("api/v1/auth/", include("apps.autenticacion.urls")),
    path("api/v1/usuarios/", include("apps.usuarios.urls")),
    path("api/v1/", include("apps.catalogos.urls")),
    path("api/v1/", include("apps.activos.urls")),
    path("api/v1/", include("apps.mantenimientos.urls")),
    path("api/v1/", include("apps.dashboard.urls")),
    path("api/v1/", include("apps.licencias_garantias.urls")),
    path("api/v1/", include("apps.incidentes.urls")),
    path("api/v1/", include("apps.documentos.urls")),
    path("api/v1/", include("apps.bajas.urls")),
]
