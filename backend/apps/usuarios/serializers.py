from rest_framework import serializers

from .models import RolChoices, Usuario


class UsuarioListSerializer(serializers.ModelSerializer):
    mfa_activo = serializers.SerializerMethodField()
    esta_bloqueado = serializers.BooleanField(read_only=True)

    class Meta:
        model = Usuario
        fields = (
            "id",
            "email",
            "nombre_completo",
            "rol",
            "is_active",
            "mfa_activo",
            "debe_cambiar_password",
            "esta_bloqueado",
        )
        read_only_fields = fields

    def get_mfa_activo(self, obj: Usuario) -> bool:
        dispositivo = getattr(obj, "dispositivo_mfa", None)
        return bool(dispositivo and dispositivo.confirmado)


class UsuarioDetailSerializer(UsuarioListSerializer):
    class Meta(UsuarioListSerializer.Meta):
        fields = UsuarioListSerializer.Meta.fields + ("created_at", "updated_at")
        read_only_fields = fields


class UsuarioCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    nombre_completo = serializers.CharField(max_length=255)
    rol = serializers.ChoiceField(choices=RolChoices.choices)


class UsuarioUpdateSerializer(serializers.Serializer):
    nombre_completo = serializers.CharField(max_length=255)
    rol = serializers.ChoiceField(choices=RolChoices.choices)


class UsuarioCreateResponseSerializer(serializers.Serializer):
    usuario = UsuarioDetailSerializer()
    password_temporal = serializers.CharField()


class UsuarioResetPasswordResponseSerializer(serializers.Serializer):
    password_temporal = serializers.CharField()
