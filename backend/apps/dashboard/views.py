from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.dashboard.permissions import IsDashboardAccess
from apps.dashboard.selectors import resumen_dashboard
from apps.dashboard.serializers import DashboardResumenSerializer

ROLES_CON_MANTENIMIENTOS = ("ADMINISTRADOR", "TECNICO")


class DashboardResumenView(APIView):
    """Resumen agregado del inventario y los mantenimientos para el tablero."""

    permission_classes = [IsDashboardAccess]

    @extend_schema(
        summary="Resumen del tablero",
        description=(
            "Agrega indicadores de inventario y mantenimiento en una sola consulta. "
            "Los Usuarios Responsables solo reciben el bloque de inventario, sin "
            "mantenimientos ni valores."
        ),
        responses={200: DashboardResumenSerializer},
        tags=["Dashboard"],
    )
    def get(self, request):
        rol = getattr(request.user, "rol", None)
        data = resumen_dashboard(incluir_mantenimientos=rol in ROLES_CON_MANTENIMIENTOS)
        return Response(DashboardResumenSerializer(data).data)
