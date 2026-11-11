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
### Configuración y Estilos
- `frontend/package.json` — dependencias (React 19, React Router 7, TanStack Query, Axios, RHF, Zod, Vitest)
- `frontend/vite.config.ts` — configuración de Vite (React plugin, proxy `/api` a backend, configuración Vitest)
- `frontend/.env.example` — plantilla de variables de entorno para Vite (`VITE_API_BASE_URL`)
- `frontend/src/styles/tokens.css` — tokens CSS de diseño (colores primario/navy, neutrales, semánticos, bordes, radios)
- `frontend/src/styles/globals.css` — estilos globales, tipografía y resets

### API Layer
- `frontend/src/api/client.ts` — cliente Axios centralizado con inyección Bearer JWT y refresco automático 401 por cola
- `frontend/src/api/query-client.ts` — cliente TanStack Query con defaults de reconexión y reintento

### Componentes Compartidos (`frontend/src/components/shared/`)
- `AppShell.tsx` — layout institucional con sidebar colapsable, navegación filtrada por rol, topbar y logout
- `PageHeader.tsx` — encabezado uniforme con breadcrumbs y contenedor de acciones
- `FormField.tsx` — contenedor accesible de etiqueta, campo, asterisco de requerido, helpText y error alert
- `FormSection.tsx` — sección contenedora para formularios extensos con título y descripción
- `StatusBadge.tsx` — badge semántico (`success`, `warning`, `danger`, `info`, `neutral`) con punto indicador
- `EmptyState.tsx` — estado vacío reutilizable con icono, título, descripción y acción opcional
- `LoadingSkeleton.tsx` — skeleton loader uniforme con efecto pulse configurable
- `ErrorState.tsx` — pantalla de error con advertencia visual y botón de reintento

### Módulo Autenticación (`frontend/src/features/auth/`)
- `api/auth.api.ts` — llamadas a API `/api/v1/auth/` (`login`, `mfaSetup`, `mfaConfirm`, `mfaVerify`, `logout`, `getMe`)
- `types/index.ts` — contratos TypeScript de autenticación, roles, pasos y respuestas de API
- `schemas/login.schema.ts` — esquema Zod de credenciales (email y password)
- `schemas/mfa.schema.ts` — esquema Zod de código de 6 dígitos y código de recuperación
- `hooks/useAuth.tsx` — contexto y hook `useAuth` para estado de sesión, tokens y ciclo de vida de usuario
- `pages/LoginPage.tsx` — pantalla principal de login orquestando pasos de credenciales y segundo factor
- `components/MFAVerifyStep.tsx` — paso de validación TOTP de 6 dígitos con switch a código de recuperación
- `components/MFASetupStep.tsx` — paso de activación inicial MFA con renderizado de QR y clave manual
- `components/RecoveryCodesDisplay.tsx` — visualización segura de códigos de respaldo con copia al portapapeles

### Rutas y Vistas
- `frontend/src/routes/Router.tsx` — definición central de rutas con BrowserRouter
- `frontend/src/routes/ProtectedRoute.tsx` — HOC de guardia para validar sesión activa y roles permitidos
- `frontend/src/features/dashboard/pages/DashboardPage.tsx` — vista inicial de bienvenida tras autenticación
- `frontend/src/pages/ComingSoonPage.tsx` — placeholder para módulos en backlog
- `frontend/src/pages/NotFoundPage.tsx` — pantalla 404

### Pruebas Frontend
- `frontend/src/test/setup.ts` — setup de vitest con jest-dom y limpieza de componentes
- `frontend/src/components/shared/__tests__/` — pruebas unitarias de FormField y StatusBadge
- `frontend/src/features/auth/schemas/__tests__/` — pruebas unitarias de esquemas login y MFA
- `frontend/src/features/auth/components/__tests__/` — prueba unitaria de RecoveryCodesDisplay

## Infraestructura
- `.gitattributes` — LF line endings para todo el repo
- `backend/.env.example` — plantilla de variables de entorno (nunca toca `.env`)
- `frontend/.env.example` — plantilla de variables de entorno para Vite
- `backend/apps/autenticacion/migrations/` — migraciones autenticación
- `backend/apps/usuarios/migrations/` — migraciones usuarios

## Convenciones de nombres → ubicación
- Modelos: `backend/apps/<app>/models.py` · Casos de uso (escritura): `services.py` · Consultas (lectura): `selectors.py`
- Endpoints: `views.py` + `urls.py` bajo `/api/v1/<recurso>/` · Permisos por rol: `apps/common/permissions.py`
- Front por módulo: `frontend/src/features/<modulo>/{api,components,pages,schemas,hooks}`
