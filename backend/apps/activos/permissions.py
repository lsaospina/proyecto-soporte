from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsActivoAccess(BasePermission):
    message = "Acceso denegado."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.rol == "USUARIO_RESPONSABLE":
            return False
        if request.method in SAFE_METHODS:
            return user.rol in ("ADMINISTRADOR", "TECNICO")
        if request.method in ("POST", "PATCH"):
            return user.rol in ("ADMINISTRADOR", "TECNICO")
        return user.rol == "ADMINISTRADOR"


class IsAsignacionAccess(BasePermission):
    """Técnicos consultan la trazabilidad; solo Admin gestiona asignaciones (RF005)."""

    message = "Acceso denegado."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.rol not in ("ADMINISTRADOR", "TECNICO"):
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.rol == "ADMINISTRADOR"
