from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdministrador(BasePermission):
    """Permite acceso únicamente a usuarios con rol ADMINISTRADOR."""

    message = "Acceso denegado: se requiere rol de Administrador."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "rol", None) == "ADMINISTRADOR"
        )


class IsTecnico(BasePermission):
    """Permite acceso únicamente a usuarios con rol TECNICO."""

    message = "Acceso denegado: se requiere rol de Técnico."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "rol", None) == "TECNICO"
        )


class IsUsuarioResponsable(BasePermission):
    """Permite acceso únicamente a usuarios con rol USUARIO_RESPONSABLE."""

    message = "Acceso denegado: se requiere rol de Usuario Responsable."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "rol", None) == "USUARIO_RESPONSABLE"
        )


class IsAdminOrTecnico(BasePermission):
    """Permite acceso a Administradores o Técnicos."""

    message = "Acceso denegado: se requiere rol de Administrador o Técnico."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "rol", None) in ["ADMINISTRADOR", "TECNICO"]
        )


class IsAdminOrReadOnly(BasePermission):
    """Permite lectura a cualquier usuario autenticado, pero escritura solo a Administradores."""

    message = "Acceso denegado: solo Administradores pueden realizar modificaciones."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return getattr(request.user, "rol", None) == "ADMINISTRADOR"
