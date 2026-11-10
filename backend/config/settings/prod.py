from .base import *

DEBUG = False

# In production, cookies must be Secure (HTTPS only)
AUTH_COOKIE_SECURE = True
AUTH_COOKIE_SAMESITE = "Lax"
AUTH_COOKIE_PATH = "/api/v1/auth/"
AUTH_COOKIE_HTTPONLY = True

# Security headers
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
