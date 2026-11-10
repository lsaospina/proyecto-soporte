import pytest

# Clave Fernet fija y válida para pruebas unitarias aisladas
TEST_MFA_KEY = "xZ-H9iK2vX4t_qP1sY8wB3lM5nO7rE0aD2c_V6uG8jI="


def pytest_collection_modifyitems(items):
    """
    Asigna automáticamente los marcadores pytest (unit, integration, system)
    según la estructura de directorios del test.
    """
    for item in items:
        path_str = str(item.fspath).replace("\\", "/")
        if "/unit/" in path_str:
            item.add_marker(pytest.mark.unit)
        elif "/integration/" in path_str:
            item.add_marker(pytest.mark.integration)
        elif "/system/" in path_str:
            item.add_marker(pytest.mark.system)


@pytest.fixture(autouse=True)
def configure_test_mfa_key(settings):
    """
    Garantiza una clave Fernet válida para los tests sin depender de un archivo .env.
    También desactiva el throttling de DRF para evitar 429 entre tests.
    """
    if not getattr(settings, "MFA_ENCRYPTION_KEY", None):
        settings.MFA_ENCRYPTION_KEY = TEST_MFA_KEY
    if not getattr(settings, "MFA_ISSUER", None):
        settings.MFA_ISSUER = "InventarioSoporteTest"
    # Desactivar throttling globalmente en tests para evitar falsos 429
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []


@pytest.fixture(autouse=True)
def clear_cache():
    """Limpia la caché de Django entre tests para evitar que el throttling persista."""
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def disable_throttling():
    """Parchea throttle_classes en vistas sensibles para que no bloqueen tests."""
    from apps.autenticacion import views

    original_login = views.LoginView.throttle_classes
    original_mfa = getattr(views.MFAVerifyView, "throttle_classes", [])
    views.LoginView.throttle_classes = []
    if hasattr(views, "MFAVerifyView"):
        views.MFAVerifyView.throttle_classes = []
    if hasattr(views, "MFASetupView"):
        views.MFASetupView.throttle_classes = []
    if hasattr(views, "MFAConfirmView"):
        views.MFAConfirmView.throttle_classes = []
    yield
    views.LoginView.throttle_classes = original_login
    if hasattr(views, "MFAVerifyView"):
        views.MFAVerifyView.throttle_classes = original_mfa


@pytest.fixture
def api_client():
    """Cliente HTTP de pruebas de DRF."""
    from rest_framework.test import APIClient

    return APIClient()
