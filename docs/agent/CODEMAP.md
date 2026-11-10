# CODEMAP — mapa del código (el agente lo mantiene)

> Una línea por módulo/archivo relevante. Sirve para NO explorar el repo completo.
> Formato: `ruta` — responsabilidad. Actualizar al crear, mover o eliminar archivos clave.

## Backend
### Configuración
- `backend/manage.py` — entry point de gestión Django
- `backend/config/settings/base.py` — settings base: JWT, DRF, MFA_*, CORS, LOGGING, drf-spectacular
- `backend/config/settings/dev.py` — sobreescritura para desarrollo (lee `backend/.env`)
- `backend/config/settings/prod.py` — sobreescritura para producción
- `backend/config/urls.py` — raíz de URLs: health, docs, `/api/v1/auth/`
- `backend/requirements/base.txt` — dependencias de producción con versiones fijadas
- `backend/requirements/dev.txt` — dependencias de desarrollo (pytest, ruff, factory-boy, freezegun)
- `backend/pytest.ini` — configuración pytest: marcadores unit/integration/system, pythonpath, addopts
- `backend/conftest.py` — fixtures globales: clave MFA, desactivación de throttling, limpieza de caché
- `backend/pyproject.toml` — configuración de ruff

### App common
- `backend/apps/common/models.py` — `BaseModel` abstracto con `created_at`/`updated_at`
- `backend/apps/common/exceptions.py` — `DominioError`, `CredencialesInvalidasError`, `CuentaBloqueadaError`, `custom_exception_handler`
- `backend/apps/common/permissions.py` — `IsAdministrador`, `IsTecnico`, `IsUsuarioResponsable`, `IsAdminOrTecnico`, `IsAdminOrReadOnly`
- `backend/apps/common/pagination.py` — `StandardResultsSetPagination` (20/page)
- `backend/apps/common/views.py` — `HealthCheckView` (GET /api/v1/health/)

### App usuarios
- `backend/apps/usuarios/models.py` — `Usuario` (AbstractUser, email único, rol TextChoices, bloqueo de cuenta)
- `backend/apps/usuarios/management/commands/seed_usuarios_dev.py` — crea 3 usuarios dev (uno por rol)
- `backend/apps/usuarios/tests/unit/test_usuario_unit.py` — 2 tests unitarios de modelo

### App autenticacion
- `backend/apps/autenticacion/models.py` — `DispositivoMFA` (OneToOne, secreto_cifrado Fernet, ultimo_paso_usado), `CodigoRecuperacion` (FK dispositivo, codigo_hash, usado_en)
- `backend/apps/autenticacion/crypto.py` — cifrado/descifrado Fernet, TOTP (pyotp, ventana ±1, anti-reúso), generación/hash de códigos de recuperación
- `backend/apps/autenticacion/tokens.py` — `generar_mfa_token` / `validar_mfa_token` (TimestampSigner, 5 min, propósito validado)
- `backend/apps/autenticacion/services.py` — `autenticar_usuario_paso1`, `iniciar_setup_mfa`, `confirmar_setup_mfa`, `verificar_mfa_sesion`, `rotar_token_refresco`, `invalidar_sesion`
- `backend/apps/autenticacion/serializers.py` — serializers de entrada/salida para todos los endpoints de auth
- `backend/apps/autenticacion/views.py` — `LoginView`, `MFASetupView`, `MFAConfirmView`, `MFAVerifyView`, `TokenRefreshView`, `LogoutView`, `MeView`
- `backend/apps/autenticacion/urls.py` — 7 rutas bajo `/api/v1/auth/`
- `backend/apps/autenticacion/throttling.py` — `LoginRateThrottle`, `MFARateThrottle` (AnonRateThrottle)
- `backend/apps/autenticacion/tests/unit/test_crypto_totp.py` — 5 tests: cifrado, ventana TOTP, anti-reúso, códigos recuperación, URI
- `backend/apps/autenticacion/tests/unit/test_mfa_tokens.py` — 4 tests: flujo válido, propósito cruzado, expiración, manipulado
- `backend/apps/autenticacion/tests/integration/test_auth_flow_integration.py` — 8 tests: flujo completo login→MFA, bloqueo, reúso, recuperación, refresh, logout, /me

## Frontend
_(vacío — se llena en T-001 FASE B)_

## Infraestructura
- `.gitattributes` — LF line endings para todo el repo
- `backend/.env.example` — plantilla de variables de entorno (nunca toca `.env`)
- `backend/apps/autenticacion/migrations/0001_initial.py` — crea `CodigoRecuperacion` y `DispositivoMFA`
- `backend/apps/autenticacion/migrations/0002_initial.py` — agrega FKs
- `backend/apps/usuarios/migrations/0001_initial.py` — crea `Usuario`

## Convenciones de nombres → ubicación
- Modelos: `backend/apps/<app>/models.py` · Casos de uso (escritura): `services.py` · Consultas (lectura): `selectors.py`
- Endpoints: `views.py` + `urls.py` bajo `/api/v1/<recurso>/` · Permisos por rol: `apps/common/permissions.py`
- Front por módulo: `frontend/src/features/<modulo>/{api,components,pages,schemas,hooks}`
