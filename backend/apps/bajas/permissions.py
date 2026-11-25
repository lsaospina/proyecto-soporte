from rest_framework.permissions import BasePermission


class IsBajaAccess(BasePermission):
    message = "Solo el administrador puede gestionar bajas."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return user.rol == "ADMINISTRADOR"
