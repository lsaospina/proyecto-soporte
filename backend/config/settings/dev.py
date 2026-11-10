from .base import *

DEBUG = True

# Allow dev hosts
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Cookie security settings for dev (HTTP allowed)
AUTH_COOKIE_SECURE = False
AUTH_COOKIE_SAMESITE = "Lax"
AUTH_COOKIE_PATH = "/api/v1/auth/"
AUTH_COOKIE_HTTPONLY = True
