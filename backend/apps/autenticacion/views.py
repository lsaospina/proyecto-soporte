from django.conf import settings
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    LoginRequestSerializer,
    LoginResponseSerializer,
    MFAConfirmRequestSerializer,
    MFAConfirmResponseSerializer,
    MFASetupRequestSerializer,
    MFASetupResponseSerializer,
    MFAVerifyRequestSerializer,
    TokenRefreshResponseSerializer,
    UsuarioMeSerializer,
)
from .services import (
    autenticar_usuario_paso1,
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
        max_age=7 * 24 * 60 * 60,  # 7 días
        httponly=True,
        secure=is_secure,
        samesite=same_site,
        path=REFRESH_COOKIE_PATH,
    )


def delete_refresh_cookie(response: Response) -> None:
    """Elimina la cookie del token de refresco."""
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path=REFRESH_COOKIE_PATH,
    )


class LoginView(APIView):
    """
    Paso 1 del inicio de sesión.
    Verifica correo y contraseña. Si el usuario tiene MFA activo o es obligatorio,
    emite un mfa_token temporal de 5 minutos y no inicia sesión directa.
    """

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    @extend_schema(
        summary="Inicio de sesión (Paso 1)",
        description="Autentica las credenciales principales del usuario y determina si se requiere segundo factor.",
        request=LoginRequestSerializer,
        responses={200: LoginResponseSerializer},
        tags=["Autenticación"],
    )
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        estado, mfa_token, refresh, user = autenticar_usuario_paso1(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if estado == "ok" and refresh:
            access_token = str(refresh.access_token)
            response = Response(
                {"status": "ok", "access": access_token},
                status=status.HTTP_200_OK,
            )
            set_refresh_cookie(response, str(refresh))
            return response

        return Response(
            {"status": estado, "mfa_token": mfa_token},
            status=status.HTTP_200_OK,
        )


class MFASetupView(APIView):
    """
    Inicia el enrolamiento del segundo factor.
    Devuelve la clave secreta en texto para copiado manual y la URI otpauth://
    para que el cliente dibuje el código QR (el backend no genera imágenes).
    """

    permission_classes = [AllowAny]
    throttle_classes = [MFARateThrottle]

    @extend_schema(
        summary="Configurar segundo factor (MFA Setup)",
        description="Genera el secreto TOTP y la URI otpauth:// correspondiente a partir del mfa_token de enrolamiento.",
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
    """
    Confirma y activa el segundo factor del usuario con su primer código de 6 dígitos.
    Devuelve los 10 códigos de recuperación (mostrados una única vez) y abre la sesión.
    """

    permission_classes = [AllowAny]
    throttle_classes = [MFARateThrottle]

    @extend_schema(
        summary="Confirmar segundo factor (MFA Confirm)",
        description="Activa el dispositivo MFA con el primer código válido, genera los códigos de recuperación y abre sesión.",
        request=MFAConfirmRequestSerializer,
        responses={200: MFAConfirmResponseSerializer},
        tags=["Autenticación MFA"],
    )
    def post(self, request):
        serializer = MFAConfirmRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh, recovery_codes, user = confirmar_setup_mfa(
            mfa_token=serializer.validated_data["mfa_token"],
            code=serializer.validated_data["code"],
        )

        access_token = str(refresh.access_token)
        response = Response(
            {
                "status": "ok",
                "access": access_token,
                "recovery_codes": recovery_codes,
            },
            status=status.HTTP_200_OK,
        )
        set_refresh_cookie(response, str(refresh))
        return response


class MFAVerifyView(APIView):
    """
    Verifica el segundo factor durante el login habitual.
    Acepta un código TOTP de 6 dígitos o un código de recuperación de emergencia.
    """

    permission_classes = [AllowAny]
    throttle_classes = [MFARateThrottle]

    @extend_schema(
        summary="Verificar segundo factor (MFA Verify)",
        description="Verifica un código TOTP o de recuperación tras el paso 1 de credenciales y abre la sesión.",
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

        refresh, user = verificar_mfa_sesion(
            mfa_token=serializer.validated_data["mfa_token"],
            code=serializer.validated_data.get("code"),
            recovery_code=serializer.validated_data.get("recovery_code"),
        )

        access_token = str(refresh.access_token)
        response = Response(
            {"status": "ok", "access": access_token},
            status=status.HTTP_200_OK,
        )
        set_refresh_cookie(response, str(refresh))
        return response


class TokenRefreshView(APIView):
    """
    Renueva el access token a partir de la cookie de refresco HttpOnly.
    Rota el token de refresco y coloca el anterior en lista negra.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Refrescar sesión",
        description="Lee la cookie de refresco HttpOnly y entrega un nuevo access token, rotando la cookie.",
        responses={200: TokenRefreshResponseSerializer},
        tags=["Autenticación"],
    )
    def post(self, request):
        cookie_refresh = request.COOKIES.get(REFRESH_COOKIE_NAME)
        access_token, nuevo_refresh = rotar_token_refresco(cookie_refresh)

        response = Response(
            {"status": "ok", "access": access_token},
            status=status.HTTP_200_OK,
        )
        set_refresh_cookie(response, nuevo_refresh)
        return response


class LogoutView(APIView):
    """
    Cierra la sesión del usuario invalidando el refresh token en la lista negra
    y borrando la cookie HttpOnly.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Cerrar sesión",
        description="Invalida el token de refresco en la lista negra y elimina la cookie de sesión.",
        responses={
            200: inline_serializer(
                name="LogoutResponse",
                fields={"detail": serializers.CharField()},
            )
        },
        tags=["Autenticación"],
    )
    def post(self, request):
        cookie_refresh = request.COOKIES.get(REFRESH_COOKIE_NAME)
        invalidar_sesion(cookie_refresh)

        response = Response(
            {"detail": "Sesión cerrada correctamente."},
            status=status.HTTP_200_OK,
        )
        delete_refresh_cookie(response)
        return response


class MeView(APIView):
    """
    Retorna el perfil del usuario autenticado actualmente.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Usuario actual",
        description="Retorna id, correo, nombre completo, rol en el sistema y si tiene MFA activo.",
        responses={200: UsuarioMeSerializer},
        tags=["Autenticación"],
    )
    def get(self, request):
        serializer = UsuarioMeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
