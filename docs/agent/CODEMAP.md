# CODEMAP — mapa del código (el agente lo mantiene)

> Una línea por módulo/archivo relevante. Sirve para NO explorar el repo completo.
> Formato: `ruta` — responsabilidad. Actualizar al crear, mover o eliminar archivos clave.

## Backend
### Configuración
- `backend/manage.py` — entry point de gestión Django
- `backend/config/settings/base.py` — settings base: JWT, DRF, MFA_*, CORS, LOGGING, drf-spectacular, `TRUST_X_FORWARDED_FOR`
- `backend/config/settings/dev.py` — sobreescritura para desarrollo (lee `backend/.env`)
- `backend/config/settings/prod.py` — sobreescritura para producción
- `backend/config/urls.py` — raíz de URLs: health, docs, `/api/v1/auth/`, `/api/v1/usuarios/`
- `backend/requirements/base.txt` — dependencias de producción con versiones fijadas
- `backend/requirements/dev.txt` — dependencias de desarrollo (pytest, ruff, factory-boy, freezegun)
- `backend/pytest.ini` — configuración pytest: marcadores unit/integration/system, pythonpath, addopts
- `backend/conftest.py` — fixtures globales: clave MFA, desactivación de throttling, limpieza de caché
- `backend/pyproject.toml` — configuración de ruff (excluye `*/migrations/*`)

### App common
- `backend/apps/common/models.py` — `BaseModel` abstracto con `created_at`/`updated_at`
- `backend/apps/common/exceptions.py` — `DominioError`, `CredencialesInvalidasError`, `CuentaBloqueadaError`, `custom_exception_handler`
- `backend/apps/common/permissions.py` — `IsAdministrador`, `IsTecnico`, `IsUsuarioResponsable`, `IsAdminOrTecnico`, `IsAdminOrReadOnly`
- `backend/apps/common/pagination.py` — `StandardResultsSetPagination` (20/page)
- `backend/apps/common/sessions.py` — `revocar_tokens_refresco(usuario)` (blacklist de OutstandingTokens)
- `backend/apps/common/views.py` — `HealthCheckView` (GET /api/v1/health/)

### App activos
- `backend/apps/activos/models.py` — `Activo`, `EstadoActivo` (simple-history)
- `backend/apps/activos/utils.py` — `normalizar_serial`, `normalizar_mac`
- `backend/apps/activos/selectors.py` — `listar_activos` (select_related, filtros)
- `backend/apps/activos/services.py` — crear/actualizar/inactivar/reactivar/cambiar_estado
- `backend/apps/activos/serializers.py` — ActivoSerializer, ActivoCreateUpdateSerializer
- `backend/apps/activos/filters.py` — ActivoFilter
- `backend/apps/activos/views.py` — ActivoViewSet (list/create/retrieve/partial_update, inactivar/reactivar/historial)
- `backend/apps/activos/urls.py` — router `/api/v1/activos/`
- `backend/apps/activos/permissions.py` — `IsActivoAccess`
- `backend/apps/activos/admin.py` — admin
- `backend/apps/activos/migrations/0001_initial.py` — esquema inicial
- `backend/apps/activos/tests/unit/test_activos_unit.py` — normalización, transiciones, fecha futura
- `backend/apps/activos/tests/integration/test_activos_api.py` — permisos, unicidad, reglas, historial, auditoría, filtros, num queries

### App catalogos
- `backend/apps/catalogos/models.py` — `Sede`, `Ubicacion`, `Categoria`, `Marca`, `ModeloActivo` (is_active, HistoricalRecords)
- `backend/apps/catalogos/utils.py` — `normalizar_nombre`
- `backend/apps/catalogos/selectors.py` — listados con select_related
- `backend/apps/catalogos/services.py` — crear/actualizar/inactivar/reactivar + auditoría + _history_user
- `backend/apps/catalogos/serializers.py` — serializers de los 5 catálogos
- `backend/apps/catalogos/filters.py` — filtros django-filter
- `backend/apps/catalogos/views.py` — ViewSets base + 5 recursos
- `backend/apps/catalogos/urls.py` — router `/api/v1/` (sedes, ubicaciones, categorias, marcas, modelos)
- `backend/apps/catalogos/permissions.py` — `IsCatalogoAccess` (admin escribe, técnico lee, responsable sin acceso)
- `backend/apps/catalogos/admin.py` — admin de los 5 catálogos
- `backend/apps/catalogos/migrations/0001_initial.py` — esquema inicial catalogos + histórico
- `backend/apps/catalogos/tests/unit/test_normalizacion.py` — normalización de nombres
- `backend/apps/catalogos/tests/integration/test_catalogos_api.py` — permisos, unicidad CI, guardas, PROTECT, historial, auditoría, num queries, IntegrityError

### App auditoria
- `backend/apps/auditoria/models.py` — `AccionAuditoria` (TextChoices) y `RegistroAuditoria` (eventos de acceso/gestión, sin JSON)
- `backend/apps/auditoria/services.py` — `registrar_evento(...)` (escritura única de auditoría)
- `backend/apps/auditoria/utils.py` — `get_client_ip(request)` y `sanitizar_entidad_id(valor)`
- `backend/apps/auditoria/admin.py` — `RegistroAuditoriaAdmin` solo lectura
- `backend/apps/auditoria/migrations/0001_initial.py` — esquema inicial de auditoría
- `backend/apps/auditoria/tests/unit/test_auditoria_utils.py` — tests unitarios de IP/sanitización

### App usuarios
- `backend/apps/usuarios/models.py` — `Usuario` (AbstractUser, email único CI, rol, bloqueo, `debe_cambiar_password`)
- `backend/apps/usuarios/utils.py` — `normalizar_email` (strip + lower)
- `backend/apps/usuarios/selectors.py` — `listar_usuarios(...)` (filtros, búsqueda normalizada, `select_related`)
- `backend/apps/usuarios/services.py` — casos de uso: crear/actualizar/activar/inactivar/reset_password/reset_mfa, temporal, guardas, revocación y auditoría
- `backend/apps/usuarios/serializers.py` — serializers de lista/detalle/create/update y respuestas con contraseña temporal
- `backend/apps/usuarios/filters.py` — `UsuarioFilter` (rol, is_active)
- `backend/apps/usuarios/views.py` — `UsuarioViewSet` admin-only (CRUD parcial + acciones reset/activar/desactivar, `no-store` en temporales)
- `backend/apps/usuarios/urls.py` — router `/api/v1/usuarios/`
- `backend/apps/usuarios/management/commands/seed_usuarios_dev.py` — crea 3 usuarios dev (uno por rol)
- `backend/apps/usuarios/migrations/0001_initial.py` — esquema inicial usuarios
- `backend/apps/usuarios/migrations/0002_usuario_debe_cambiar_password.py` — campo `debe_cambiar_password`
- `backend/apps/usuarios/migrations/0003_normalizar_emails.py` — data migration normaliza emails (aborta en colisión)
- `backend/apps/usuarios/migrations/0004_usuario_email_ci_unico.py` — constraint única case-insensitive sobre email
- `backend/apps/usuarios/tests/unit/test_usuario_unit.py` — tests unitarios de modelo
- `backend/apps/usuarios/tests/unit/test_password_temporal.py` — test de política de contraseña temporal
- `backend/apps/usuarios/tests/integration/test_usuarios_api.py` — permisos/CRUD/acciones/guardas API usuarios
- `backend/apps/usuarios/tests/integration/test_guards_and_command.py` — comando `resetear_mfa` y guarda FOR UPDATE/ORDER BY
- `backend/apps/usuarios/tests/integration/test_guards_missing_cases.py` — casos de último admin/auto-cambio rol (servicio/API)
- `backend/apps/usuarios/tests/integration/test_listado_queries.py` — `assertNumQueries` del listado
- `backend/apps/usuarios/tests/integration/test_me_serializer_mfa.py` — `mfa_activo` sin dispositivo
- `backend/apps/usuarios/tests/integration/test_reset_password_revoca.py` — reset limpia bloqueo y revoca refresh

### App autenticacion
- `backend/apps/autenticacion/models.py` — `DispositivoMFA` (OneToOne, secreto_cifrado Fernet, ultimo_paso_usado), `CodigoRecuperacion` (hash, uso único)
- `backend/apps/autenticacion/crypto.py` — cifrado/descifrado Fernet, TOTP (pyotp, ventana ±1, anti-reúso), códigos de recuperación
- `backend/apps/autenticacion/tokens.py` — `generar_mfa_token` / `validar_mfa_token` (TimestampSigner, propósitos setup/verify/password_change)
- `backend/apps/autenticacion/types.py` — `ResultadoAutenticacion` (dataclass de flujo auth)
- `backend/apps/autenticacion/services.py` — login paso 1, cambio obligatorio de contraseña, setup/confirm/verify MFA, rotación/invalidación de refresh, auditoría asociada
- `backend/apps/autenticacion/serializers.py` — serializers auth/MFA/password-change y `UsuarioMeSerializer`
- `backend/apps/autenticacion/views.py` — `LoginView`, `PasswordChangeView`, MFA setup/confirm/verify, `TokenRefreshView`, `LogoutView`, `MeView`
- `backend/apps/autenticacion/urls.py` — rutas `/api/v1/auth/` (incluye `password/change/`)
- `backend/apps/autenticacion/throttling.py` — `LoginRateThrottle`, `MFARateThrottle`
- `backend/apps/autenticacion/management/commands/resetear_mfa.py` — reset MFA por consola (emergencia), revoca refresh y audita
- `backend/apps/autenticacion/tests/unit/test_crypto_totp.py` — cifrado, ventana TOTP, anti-reúso, recuperación, URI
- `backend/apps/autenticacion/tests/unit/test_mfa_tokens.py` — flujo/propósito/expiración/manipulación de mfa_token
- `backend/apps/autenticacion/tests/integration/test_auth_flow_integration.py` — flujo login→MFA, bloqueo, reúso, recuperación, refresh, logout, /me
- `backend/apps/autenticacion/tests/integration/test_auth_t002_flows.py` — email CI, auditoría login/pasos intermedios, flujo password_change
- `backend/apps/autenticacion/tests/integration/test_auth_t002_extra.py` — MFA rechazado auditado, reset MFA→setup, emails largos/@ y `entidad_id`
- `backend/apps/autenticacion/tests/integration/test_cambiar_password_obligatorio.py` — validaciones unitarias/integradas del cambio obligatorio
- `backend/apps/autenticacion/tests/integration/test_password_change_one_time.py` — token de cambio de contraseña de un solo uso
- `backend/apps/autenticacion/tests/integration/test_refresh_me_inactive.py` — `/me` y refresh rechazan usuario inactivo

## Frontend
### Configuración y Estilos
- `frontend/package.json` — dependencias (React 19, React Router 7, TanStack Query, Axios, RHF, Zod, Vitest)
- `frontend/vite.config.ts` — configuración de Vite (React plugin, proxy `/api`, Vitest)
- `frontend/.env.example` — plantilla de variables de entorno para Vite
- `frontend/src/styles/tokens.css` — tokens CSS de diseño (fuente de verdad: superficies, primario, semánticos, radios, sombra)
- `frontend/src/styles/globals.css` — estilos globales, tipografía y resets

### API Layer
- `frontend/src/api/client.ts` — cliente Axios centralizado con Bearer JWT y refresco automático 401 por cola
- `frontend/src/api/query-client.ts` — cliente TanStack Query con defaults (stale/retry/refetch)

### Componentes Compartidos (`frontend/src/components/shared/`)
- `AppShell.tsx` — layout (sidebar/topbar), navegación filtrada por rol y logout
- `PageHeader.tsx` — encabezado con breadcrumbs, título/subtítulo y acciones
- `FormField.tsx` — campo con etiqueta, requerido, helpText y error accesible
- `FormSection.tsx` — sección contenedora de formularios
- `StatusBadge.tsx` — badge semántico con variantes de estado
- `EmptyState.tsx` — estado vacío reutilizable
- `LoadingSkeleton.tsx` — skeleton loader
- `ErrorState.tsx` — estado de error con reintento
- `DataTable.tsx` — tabla genérica reutilizable para listados
- `ConfirmDialog.tsx` — diálogo de confirmación (acciones destructivas/seguras)

### Módulo Autenticación (`frontend/src/features/auth/`)
- `api/auth.api.ts` — API `/api/v1/auth/` (`login`, `changePassword`, MFA setup/confirm/verify, refresh, logout, me)
- `types/index.ts` — contratos TS (roles, usuario, `AuthStep` incluye `password_change`)
- `schemas/login.schema.ts` — esquemas Zod de login y cambio obligatorio de contraseña
- `schemas/mfa.schema.ts` — esquemas Zod de código TOTP y recuperación
- `hooks/useAuth.tsx` — contexto/hook de sesión, token y ciclo de vida de usuario
- `pages/LoginPage.tsx` — orquesta credenciales, cambio obligatorio, MFA verify/setup
- `components/PasswordChangeStep.tsx` — formulario de cambio obligatorio de contraseña
- `components/MFAVerifyStep.tsx` — verificación TOTP/código de recuperación
- `components/MFASetupStep.tsx` — activación MFA con QR/clave y confirmación
- `components/RecoveryCodesDisplay.tsx` — visualización/copia de códigos de recuperación
- `schemas/__tests__/login.schema.test.ts` — pruebas schema login
- `schemas/__tests__/password-change.schema.test.ts` — pruebas schema cambio de contraseña
- `schemas/__tests__/mfa.schema.test.ts` — pruebas schemas MFA
- `components/__tests__/RecoveryCodesDisplay.test.tsx` — prueba de componente recovery codes

### Módulo Catálogos (`frontend/src/features/catalogos/`)
- `api/catalogos.api.ts` — cliente HTTP catálogos
- `types/index.ts` — tipos TS de catálogos
- `pages/CatalogosPage.tsx` — pantalla genérica por pestañas

### Módulo Usuarios (`frontend/src/features/usuarios/`)
- `api/usuarios.api.ts` — API `/api/v1/usuarios/` (listar, CRUD parcial, reset password/MFA, activar/desactivar)
- `types/index.ts` — tipos TS de usuario, payloads y respuestas (incluye temporal)
- `schemas/usuario.schema.ts` — esquemas Zod de creación y edición (edición sin email)
- `pages/UsuariosListPage.tsx` — listado con filtros/búsqueda/paginación y acciones admin (mutaciones sensibles con `gcTime: 0` + `reset()`)
- `pages/UsuarioFormPage.tsx` — formulario crear/editar usuario
- `components/TempPasswordModal.tsx` — muestra contraseña temporal una sola vez (estado local, copiar)
- `components/ConfirmResetMfaDialog.tsx` — confirmación de reset MFA
- `__tests__/usuario.schema.test.ts` — pruebas schema usuario
- `__tests__/TempPasswordModal.test.tsx` — prueba modal de contraseña temporal
- `__tests__/UsuariosListPage.test.tsx` — prueba de listado (MSW/mock API + estados básicos)

### Rutas y Vistas
- `frontend/src/routes/Router.tsx` — rutas; `/usuarios`, `/usuarios/nuevo`, `/usuarios/:id/editar` bajo guardia ADMINISTRADOR
- `frontend/src/routes/ProtectedRoute.tsx` — guardia de autenticación y roles (redirige a `/dashboard` si rol no permitido)
- `frontend/src/features/dashboard/pages/DashboardPage.tsx` — dashboard inicial
- `frontend/src/pages/ComingSoonPage.tsx` — placeholder de módulos en backlog
- `frontend/src/pages/NotFoundPage.tsx` — pantalla 404

### Pruebas Frontend
- `frontend/src/test/setup.ts` — setup Vitest (jest-dom, cleanup)
- `frontend/src/components/shared/__tests__/FormField.test.tsx` — pruebas FormField
- `frontend/src/components/shared/__tests__/StatusBadge.test.tsx` — pruebas StatusBadge

## Infraestructura y documentación agente
- `.gitattributes` — LF line endings
- `backend/.env.example` — plantilla de entorno backend (incluye `TRUST_X_FORWARDED_FOR`)
- `frontend/.env.example` — plantilla de entorno frontend
- `.agents/skills/frontend-design-system/SKILL.md` — skill de diseño frontend alineada a `tokens.css` y mockups HTML actuales
- `docs/agent/tasks/T-002-usuarios.md` — resumen y cierre de tarea T-002

## Convenciones de nombres → ubicación
- Modelos: `backend/apps/<app>/models.py` · Casos de uso (escritura): `services.py` · Consultas (lectura): `selectors.py`
- Endpoints: `views.py` + `urls.py` bajo `/api/v1/<recurso>/` · Permisos por rol: `apps/common/permissions.py`
- Front por módulo: `frontend/src/features/<modulo>/{api,components,pages,schemas,hooks,types}`