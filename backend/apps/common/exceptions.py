import logging
from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


class DominioError(Exception):
    """Excepción base para errores de lógica de negocio en el dominio."""

    default_code = "error_dominio"
    default_status_code = status.HTTP_400_BAD_REQUEST

    def __init__(
        self,
        detail: str,
        code: str | None = None,
        status_code: int | None = None,
        errors: list[dict[str, Any]] | None = None,
    ):
        super().__init__(detail)
        self.detail = detail
        self.code = code or self.default_code
        self.status_code = status_code or self.default_status_code
        self.errors = errors or []


class ReglaDeNegocioError(DominioError):
    """Lanzada cuando una invariante o regla de negocio no se cumple."""

    default_code = "regla_de_negocio_violada"
    default_status_code = status.HTTP_400_BAD_REQUEST


class CuentaBloqueadaError(DominioError):
    """Lanzada cuando la cuenta se encuentra temporalmente bloqueada."""

    default_code = "cuenta_bloqueada"
    default_status_code = status.HTTP_403_FORBIDDEN


class CredencialesInvalidasError(DominioError):
    """Lanzada ante un fallo de autenticación genérico."""

    default_code = "credenciales_invalidas"
    default_status_code = status.HTTP_401_UNAUTHORIZED


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """
    Manejador global de excepciones que asegura el formato uniforme:
    {
        "detail": "Mensaje legible",
        "code": "codigo_error",
        "errors": [{"field": "campo", "message": "detalle"}]
    }
    """
    if isinstance(exc, DominioError):
        return Response(
            {
                "detail": exc.detail,
                "code": exc.code,
                "errors": exc.errors,
            },
            status=exc.status_code,
        )

    # Dejar que DRF maneje sus excepciones estándar primero
    response = exception_handler(exc, context)

    if response is not None:
        raw_data = response.data
        formatted_errors: list[dict[str, Any]] = []
        detail = "Ha ocurrido un error en la solicitud."
        code = getattr(exc, "default_code", "error")

        if isinstance(raw_data, dict):
            if "detail" in raw_data:
                detail = str(raw_data["detail"])
                if hasattr(raw_data["detail"], "code"):
                    code = raw_data["detail"].code

            for field, value in raw_data.items():
                if field == "detail":
                    continue
                if isinstance(value, list):
                    for item in value:
                        formatted_errors.append({"field": field, "message": str(item)})
                else:
                    formatted_errors.append({"field": field, "message": str(value)})

        elif isinstance(raw_data, list):
            for item in raw_data:
                formatted_errors.append({"field": "general", "message": str(item)})
            if raw_data:
                detail = str(raw_data[0])

        response.data = {
            "detail": detail,
            "code": code,
            "errors": formatted_errors,
        }
        return response

    # Excepción no controlada
    logger.exception("Excepción no controlada en la API: %s", exc)
    return Response(
        {
            "detail": "Ha ocurrido un error interno en el servidor.",
            "code": "error_interno",
            "errors": [],
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
