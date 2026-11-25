from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsIncidenteAccess(BasePermission):
    message = "Acceso denegado."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.rol not in ("ADMINISTRADOR", "TECNICO", "USUARIO_RESPONSABLE"):
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == "POST":
            return True
        if request.method in ("PUT", "PATCH"):
            return user.rol in ("ADMINISTRADOR", "TECNICO")
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.rol in ("ADMINISTRADOR", "TECNICO"):
            return True
        if user.rol == "USUARIO_RESPONSABLE":
            if request.method in SAFE_METHODS:
                return obj.reportado_por_id == user.id
            return False
        return False
