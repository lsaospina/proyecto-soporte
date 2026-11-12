from django.conf import settings
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auditoria.models import AccionAuditoria
from apps.auditoria.services import registrar_evento
from apps.auditoria.utils import get_client_ip
from apps.common.exceptions import CredencialesInvalidasError, CuentaBloqueadaError

from .serializers import (
    LoginRequestSerializer,
    LoginResponseSerializer,
    MFAConfirmRequestSerializer,
    MFAConfirmResponseSerializer,
    MFASetupRequestSerializer,
    MFASetupResponseSerializer,
    MFAVerifyRequestSerializer,
    PasswordChangeRequestSerializer,
    TokenRefreshResponseSerializer,
    UsuarioMeSerializer,
)
from .services import (
    autenticar_usuario_paso1,
    cambiar_password_obligatorio,
    confirmar_setup_mfa,
    iniciar_setup_mfa,
    invalidar_sesion,
    rotar_token_refresco,
    verificar_mfa_sesion,
)
from .throttling import LoginRateThrottle, MFARateThrottle

REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_PATH = "/api/v1/auth/"


def set_refresh_cookie(response: Response, refresh_token_str: str) -> None:
    """Configura la cookie HttpOnly segura con el token de refresco."""
    is_secure = getattr(settings, "AUTH_COOKIE_SECURE", not settings.DEBUG)
    same_site = getattr(settings, "AUTH_COOKIE_SAMESITE", "Lax")
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token_str,
        max_age=7 * 24 * 60 * 60,
        httponly=True,
        secure=is_secure,
        samesite=same_site,
        path=REFRESH_COOKIE_PATH,
    )


def delete_refresh_cookie(response: Response) -> None:
    """Elimina la cookie del token de refresco."""
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)


class LoginView(APIView):
    """Paso 1 del inicio de sesión: credenciales y determinación de flujo siguiente."""

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    @extend_schema(
        summary="Inicio de sesión (Paso 1)",
        request=LoginRequestSerializer,
        responses={200: LoginResponseSerializer},
        tags=["Autenticación"],
    )
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip = get_client_ip(request)

        try:
            resultado = autenticar_usuario_paso1(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                ip=ip,
            )
        except (CredencialesInvalidasError, CuentaBloqueadaError):
            email_norm = serializer.validated_data.get("email", "").strip().lower()
            registrar_evento(
                usuario=None,
                accion=AccionAuditoria.LOGIN_FALLIDO,
                entidad="Usuario",
                entidad_id=email_norm if "@" in email_norm and len(email_norm) <= 64 else "",
                ip=ip,
            )
            raise

        if resultado.estado == "ok" and resultado.refresh:
            access_token = str(resultado.refresh.access_token)
            response = Response(
                {"status": "ok", "access": access_token},
                status=status.HTTP_200_OK,
            )
            set_refresh_cookie(response, str(resultado.refresh))
            registrar_evento(
                usuario=resultado.usuario,
                accion=AccionAuditoria.LOGIN_EXITOSO,
                entidad="Usuario",
                entidad_id=str(resultado.usuario.pk),
                ip=ip,
            )
            return response

        payload = {"status": resultado.estado}
        if resultado.mfa_token:
            payload["mfa_token"] = resultado.mfa_token
        if resultado.password_token:
            payload["password_token"] = resultado.password_token
        return Response(payload, status=status.HTTP_200_OK)


class PasswordChangeView(APIView):
    """Cambio obligatorio de contraseña con token de propósito password_change."""

    permission_classes = [AllowAny]
    throttle_classes = [MFARateThrottle]

    @extend_schema(
        summary="Cambio obligatorio de contraseña",
        request=PasswordChangeRequestSerializer,
        responses={200: LoginResponseSerializer},
        tags=["Autenticación"],
    )
    def post(self, request):
        serializer = PasswordChangeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip = get_client_ip(request)

        resultado = cambiar_password_obligatorio(
            password_token=serializer.validated_data["password_token"],
            new_password=serializer.validated_data["new_password"],
            ip=ip,
        )

        registrar_evento(
            usuario=resultado.usuario,
            accion=AccionAuditoria.PASSWORD_CAMBIADA,
            entidad="Usuario",
            entidad_id=str(resultado.usuario.pk),
            ip=ip,
        )

        if resultado.estado == "ok" and resultado.refresh:
            access_token = str(resultado.refresh.access_token)
            response = Response(
                {"status": "ok", "access": access_token},
                status=status.HTTP_200_OK,
            )
            set_refresh_cookie(response, str(resultado.refresh))
            response["Cache-Control"] = "no-store"
            registrar_evento(
                usuario=resultado.usuario,
                accion=AccionAuditoria.LOGIN_EXITOSO,
                entidad="Usuario",
                entidad_id=str(resultado.usuario.pk),
                ip=ip,
            )
            return response

        payload = {"status": resultado.estado}
        if resultado.mfa_token:
            payload["mfa_token"] = resultado.mfa_token
        if resultado.password_token:
            payload["password_token"] = resultado.password_token
        response = Response(payload, status=status.HTTP_200_OK)
        response["Cache-Control"] = "no-store"
        return response


class MFASetupView(APIView):
    """Inicia enrolamiento MFA y devuelve secreto + otpauth URI."""

    permission_classes = [AllowAny]
    throttle_classes = [MFARateThrottle]

    @extend_schema(
        summary="Configurar segundo factor (MFA Setup)",
        request=MFASetupRequestSerializer,
        responses={200: MFASetupResponseSerializer},
        tags=["Autenticación MFA"],
    )
    def post(self, request):
        serializer = MFASetupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos_setup = iniciar_setup_mfa(mfa_token=serializer.validated_data["mfa_token"])
        return Response(datos_setup, status=status.HTTP_200_OK)


class MFAConfirmView(APIView):
    """Confirma activación de MFA, genera recovery codes y abre sesión."""

    permission_classes = [AllowAny]
    throttle_classes = [MFARateThrottle]

    @extend_schema(
        summary="Confirmar segundo factor (MFA Confirm)",
        request=MFAConfirmRequestSerializer,
        responses={200: MFAConfirmResponseSerializer},
        tags=["Autenticación MFA"],
    )
    def post(self, request):
        serializer = MFAConfirmRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip = get_client_ip(request)

        refresh, recovery_codes, user = confirmar_setup_mfa(
            mfa_token=serializer.validated_data["mfa_token"],
            code=serializer.validated_data["code"],
        )

        access_token = str(refresh.access_token)
        response = Response(
            {"status": "ok", "access": access_token, "recovery_codes": recovery_codes},
            status=status.HTTP_200_OK,
        )
        set_refresh_cookie(response, str(refresh))
        registrar_evento(
            usuario=user,
            accion=AccionAuditoria.MFA_ACTIVADO,
            entidad="Usuario",
            entidad_id=str(user.pk),
            ip=ip,
        )
        registrar_evento(
            usuario=user,
            accion=AccionAuditoria.LOGIN_EXITOSO,
            entidad="Usuario",
            entidad_id=str(user.pk),
            ip=ip,
        )
        return response


class MFAVerifyView(APIView):
    """Verifica TOTP o código de recuperación y abre sesión."""

    permission_classes = [AllowAny]
    throttle_classes = [MFARateThrottle]

    @extend_schema(
        summary="Verificar segundo factor (MFA Verify)",
        request=MFAVerifyRequestSerializer,
        responses={
            200: inline_serializer(
                name="MFAVerifyResponse",
                fields={
                    "status": serializers.CharField(default="ok"),
                    "access": serializers.CharField(),
                },
            )
        },
        tags=["Autenticación MFA"],
    )
    def post(self, request):
        serializer = MFAVerifyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip = get_client_ip(request)

        try:
            refresh, user = verificar_mfa_sesion(
                mfa_token=serializer.validated_data["mfa_token"],
                code=serializer.validated_data.get("code"),
                recovery_code=serializer.validated_data.get("recovery_code"),
            )
        except CredencialesInvalidasError:
            registrar_evento(
                usuario=None,
                accion=AccionAuditoria.MFA_RECHAZADO,
                entidad="Auth",
                entidad_id="",
                ip=ip,
            )
            raise

        access_token = str(refresh.access_token)
        response = Response(
            {"status": "ok", "access": access_token},
            status=status.HTTP_200_OK,
        )
        set_refresh_cookie(response, str(refresh))
        registrar_evento(
            usuario=user,
            accion=AccionAuditoria.MFA_VERIFICADO,
            entidad="Usuario",
            entidad_id=str(user.pk),
            ip=ip,
        )
        registrar_evento(
            usuario=user,
            accion=AccionAuditoria.LOGIN_EXITOSO,
            entidad="Usuario",
            entidad_id=str(user.pk),
            ip=ip,
        )
        return response


class TokenRefreshView(APIView):
    """Renueva access token desde cookie HttpOnly, rotando refresh."""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Refrescar sesión",
        responses={200: TokenRefreshResponseSerializer},
        tags=["Autenticación"],
    )
    def post(self, request):
        cookie_refresh = request.COOKIES.get(REFRESH_COOKIE_NAME)
        access_token, nuevo_refresh = rotar_token_refresco(cookie_refresh)

        response = Response({"status": "ok", "access": access_token}, status=status.HTTP_200_OK)
        set_refresh_cookie(response, nuevo_refresh)
        return response


class LogoutView(APIView):
    """Cierra sesión invalidando refresh token y cookie."""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Cerrar sesión",
        responses={
            200: inline_serializer(
                name="LogoutResponse", fields={"detail": serializers.CharField()}
            )
        },
        tags=["Autenticación"],
    )
    def post(self, request):
        cookie_refresh = request.COOKIES.get(REFRESH_COOKIE_NAME)
        ip = get_client_ip(request)
        user = (
            request.user
            if getattr(request, "user", None) and request.user.is_authenticated
            else None
        )
        invalidar_sesion(cookie_refresh)

        response = Response({"detail": "Sesión cerrada correctamente."}, status=status.HTTP_200_OK)
        delete_refresh_cookie(response)
        registrar_evento(
            usuario=user,
            accion=AccionAuditoria.LOGOUT,
            entidad="Usuario",
            entidad_id=str(user.pk) if user else "",
            ip=ip,
        )
        return response


class MeView(APIView):
    """Retorna el perfil del usuario autenticado."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Usuario actual",
        responses={200: UsuarioMeSerializer},
        tags=["Autenticación"],
    )
    def get(self, request):
        serializer = UsuarioMeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
