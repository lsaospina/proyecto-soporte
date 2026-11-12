from dataclasses import dataclass

from rest_framework_simplejwt.tokens import RefreshToken

from apps.usuarios.models import Usuario


@dataclass(frozen=True)
class ResultadoAutenticacion:
    estado: str
    usuario: Usuario
    mfa_token: str | None = None
    password_token: str | None = None
    refresh: RefreshToken | None = None
