from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsMantenimientoAccess(BasePermission):
    message = "Acceso denegado."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.rol not in ("ADMINISTRADOR", "TECNICO"):
            return False
        if request.method in SAFE_METHODS:
            return True
        if getattr(view, "action", None) in ("cancelar",):
            return user.rol == "ADMINISTRADOR"
        return True
