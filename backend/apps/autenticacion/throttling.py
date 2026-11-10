from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """Límite de tasa para intentos de inicio de sesión."""

    scope = "auth_login"


class MFARateThrottle(AnonRateThrottle):
    """Límite de tasa para endpoints relacionados con MFA."""

    scope = "auth_mfa"
