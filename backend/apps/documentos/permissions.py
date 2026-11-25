from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsDocumentoAccess(BasePermission):
    message = "Acceso denegado."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return user.rol in ("ADMINISTRADOR", "TECNICO")
