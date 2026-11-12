from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    MeView,
    MFAConfirmView,
    MFASetupView,
    MFAVerifyView,
    PasswordChangeView,
    TokenRefreshView,
)

app_name = "autenticacion"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("password/change/", PasswordChangeView.as_view(), name="password-change"),
    path("mfa/setup/", MFASetupView.as_view(), name="mfa-setup"),
    path("mfa/confirm/", MFAConfirmView.as_view(), name="mfa-confirm"),
    path("mfa/verify/", MFAVerifyView.as_view(), name="mfa-verify"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
]
