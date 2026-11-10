from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """
    Endpoint público de chequeo de salud para verificar disponibilidad del backend.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Verificación de disponibilidad",
        description="Retorna el estado del servicio y la estampa de tiempo actual del servidor.",
        responses={
            200: inline_serializer(
                name="HealthCheckResponse",
                fields={
                    "status": serializers.CharField(default="ok"),
                    "timestamp": serializers.DateTimeField(),
                },
            )
        },
        tags=["Salud"],
    )
    def get(self, request):
        return Response(
            {
                "status": "ok",
                "timestamp": timezone.now().isoformat(),
            }
        )
