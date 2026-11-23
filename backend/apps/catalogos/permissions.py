from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsCatalogoAccess(BasePermission):
    message = "Acceso denegado."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.rol == "USUARIO_RESPONSABLE":
            return False
        if request.method in SAFE_METHODS:
            return user.rol in ("ADMINISTRADOR", "TECNICO")
        return user.rol == "ADMINISTRADOR"
