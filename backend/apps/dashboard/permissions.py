from rest_framework.permissions import SAFE_METHODS, BasePermission

ROLES_CON_ACCESO = ("ADMINISTRADOR", "TECNICO", "USUARIO_RESPONSABLE")


class IsDashboardAccess(BasePermission):
    """Lectura del tablero para los tres roles; el tablero no permite escrituras.

    El alcance de la información se ajusta por rol en la vista (un Usuario
    Responsable solo ve el resumen del inventario, sin mantenimientos ni costos).
    """

    message = "Acceso denegado: no tiene permisos para consultar el tablero."

    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS:
            return False
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "rol", None) in ROLES_CON_ACCESO
        )
