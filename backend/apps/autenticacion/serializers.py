from rest_framework import serializers

from apps.usuarios.models import Usuario


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "El correo electrónico es obligatorio.",
            "invalid": "Correo electrónico inválido.",
        },
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={"required": "La contraseña es obligatoria."},
    )


class LoginResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["ok", "mfa_required", "mfa_setup_required"])
    access = serializers.CharField(required=False, allow_null=True)
    mfa_token = serializers.CharField(required=False, allow_null=True)


class MFASetupRequestSerializer(serializers.Serializer):
    mfa_token = serializers.CharField(
        required=True,
        error_messages={"required": "El token de autorización MFA es obligatorio."},
    )


class MFASetupResponseSerializer(serializers.Serializer):
    secret = serializers.CharField(help_text="Clave secreta TOTP en base32 para ingreso manual.")
    otpauth_uri = serializers.CharField(
        help_text="URI estándar otpauth:// para renderizar el código QR en el cliente."
    )


class MFAConfirmRequestSerializer(serializers.Serializer):
    mfa_token = serializers.CharField(required=True)
    code = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
        error_messages={"required": "El código de verificación de 6 dígitos es obligatorio."},
    )


class MFAConfirmResponseSerializer(serializers.Serializer):
    status = serializers.CharField(default="ok")
    access = serializers.CharField()
    recovery_codes = serializers.ListField(child=serializers.CharField())


class MFAVerifyRequestSerializer(serializers.Serializer):
    mfa_token = serializers.CharField(required=True)
    code = serializers.CharField(required=False, allow_blank=True, default="")
    recovery_code = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        code = attrs.get("code", "").strip()
        recovery_code = attrs.get("recovery_code", "").strip()
        if not code and not recovery_code:
            raise serializers.ValidationError(
                "Debe proporcionar un código TOTP de 6 dígitos o un código de recuperación de emergencia."
            )
        return attrs


class TokenRefreshResponseSerializer(serializers.Serializer):
    status = serializers.CharField(default="ok")
    access = serializers.CharField()


class UsuarioMeSerializer(serializers.ModelSerializer):
    mfa_activo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ("id", "email", "nombre_completo", "rol", "mfa_activo")
        read_only_fields = fields

    def get_mfa_activo(self, obj: Usuario) -> bool:
        dispositivo = getattr(obj, "dispositivo_mfa", None)
        return bool(dispositivo and dispositivo.confirmado)
