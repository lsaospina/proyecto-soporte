from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


def revocar_tokens_refresco(usuario) -> None:
    """Revoca todos los refresh tokens vigentes del usuario poniéndolos en lista negra."""
    tokens = OutstandingToken.objects.filter(user=usuario)
    for token in tokens:
        BlacklistedToken.objects.get_or_create(token=token)
