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
- `backend/apps/activos/models.py` — `Activo`, `EstadoActivo`, `AsignacionActivo` (históricos, constraint de una asignación abierta y CHECK de fechas)
- `backend/apps/activos/utils.py` — `normalizar_serial`, `normalizar_mac`
- `backend/apps/activos/selectors.py` — `listar_activos` (con `responsable_actual` anotado), `listar_asignaciones`, `resumen_asignaciones`, `usuarios_asignables`
- `backend/apps/activos/services.py` — CRUD/inactivar/reactivar/cambiar_estado + `asignar_activo`, `cerrar_asignacion`, `reasignar_activo` (sincronizan estado y auditan)
- `backend/apps/activos/serializers.py` — ActivoSerializer (con `responsable_actual`), lecturas/escrituras de asignación y resumen
- `backend/apps/activos/filters.py` — `ActivoFilter` (incluye `estado_no`) y `AsignacionFilter`
- `backend/apps/activos/views.py` — `ActivoViewSet` y `AsignacionViewSet` (create/cerrar/reasignar/resumen/usuarios)
- `backend/apps/activos/urls.py` — routers `/api/v1/activos/` y `/api/v1/asignaciones/`
- `backend/apps/activos/permissions.py` — `IsActivoAccess`, `IsAsignacionAccess` (lectura ADMIN/TÉCNICO, escritura ADMIN)
- `backend/apps/activos/admin.py` — admin de activos y asignaciones (solo lectura)
- `backend/apps/activos/management/commands/seed_asignaciones_dev.py` — seed idempotente que regulariza estados y crea historial
- `backend/apps/activos/migrations/0001_initial.py` — esquema inicial
- `backend/apps/activos/migrations/0002_historicalasignacionactivo_asignacionactivo.py` — asignaciones
- `backend/apps/activos/tests/unit/test_activos_unit.py` — normalización, transiciones, fechas y propiedades de asignación
- `backend/apps/activos/tests/integration/test_activos_api.py` — permisos, unicidad, reglas, historial, auditoría, filtros, num queries
- `backend/apps/activos/tests/integration/test_asignaciones_api.py` — permisos, alta, doble asignación, estado, devolución, reasignación, filtros, resumen y responsable actual
- `backend/apps/activos/tests/integration/test_seed_asignaciones.py` — guarda DEBUG, regularización e idempotencia

### App mantenimientos
- `backend/apps/mantenimientos/models.py` — `Mantenimiento` (activo, tipo, fechas, técnico, costo, estado, `reprogramacion_de`), situación derivada, `HistoricalMantenimiento`
- `backend/apps/mantenimientos/selectors.py` — `listar_mantenimientos`, `anotar_situacion` (Case/Exists), `resumen_anual`, `calendario_mensual`
- `backend/apps/mantenimientos/services.py` — programar/completar/reprogramar (mueve 200 / crea evidencia 201)/cancelar/registrar correctivo + auditoría
- `backend/apps/mantenimientos/serializers.py` — serializer de lectura, creación preventiva, correctivo y acciones
- `backend/apps/mantenimientos/filters.py` — filtros año/mes/situación/técnico
- `backend/apps/mantenimientos/permissions.py` — `IsMantenimientoAccess` (admin/técnico; cancelar solo admin)
- `backend/apps/mantenimientos/views.py` — `MantenimientoViewSet` + `resumen`, `calendario`, `tecnicos`, `correctivos` (POST), `completar`, `reprogramar`, `cancelar`, `historial`
- `backend/apps/mantenimientos/urls.py` — router `/api/v1/mantenimientos/`
- `backend/apps/mantenimientos/admin.py` — admin
- `backend/apps/mantenimientos/management/commands/seed_mantenimientos_dev.py` — seed idempotente del año (DEBUG=True): preventivos (completados, vencidos, incumplidos, pendientes) + 3 correctivos
- `backend/apps/mantenimientos/migrations/0001_initial.py` — esquema + histórico + constraints
- `backend/apps/mantenimientos/migrations/0002_historicalmantenimiento_fecha_seguimiento_and_more.py` — `fecha_seguimiento`
- `backend/apps/mantenimientos/tests/unit/test_mantenimientos_unit.py` — situación derivada y validaciones
- `backend/apps/mantenimientos/tests/integration/test_mantenimientos_api.py` — permisos, programar/completar/reprogramar/cancelar, resumen, calendario, filtros, auditoría
- `backend/apps/mantenimientos/tests/integration/test_correctivos_api.py` — correctivo: permisos, fechas, descripción, filtro tipo, KPI excluye correctivos
- `backend/apps/mantenimientos/tests/integration/test_seed_mantenimientos.py` — guarda DEBUG y seed idempotente

### App licencias_garantias
- `backend/apps/licencias_garantias/models.py` — `Proveedor`, `Licencia` (+ históricos), `PeriodicidadRenovacion`, `EstadoRenovacion` derivado (umbral 30 días)
- `backend/apps/licencias_garantias/selectors.py` — listados, filtro por estado de renovación, resumen con costo anualizado y proveedores
- `backend/apps/licencias_garantias/services.py` — crear/actualizar (proveedor por nombre normalizado), inactivar/reactivar, renovar y auditoría `LICENCIA_*`
- `backend/apps/licencias_garantias/serializers.py` — lectura con estado/días derivados, escritura con proveedor por nombre y resumen
- `backend/apps/licencias_garantias/filters.py` — proveedor, periodicidad, estado de renovación, activas y rango de fechas
- `backend/apps/licencias_garantias/views.py` — `LicenciaViewSet` admin-only (`resumen`, `proveedores`, `renovar`, `inactivar`, `reactivar`)
- `backend/apps/licencias_garantias/urls.py` — router `/api/v1/licencias/`
- `backend/apps/licencias_garantias/admin.py` — admin de proveedores y licencias
- `backend/apps/licencias_garantias/management/commands/seed_licencias_dev.py` — seed idempotente (15 licencias; solo DEBUG)
- `backend/apps/licencias_garantias/migrations/0001_initial.py` — esquema + históricos + constraints
- `backend/apps/licencias_garantias/tests/unit/test_licencias_unit.py` — estado derivado y validaciones del serializer
- `backend/apps/licencias_garantias/tests/integration/test_licencias_api.py` — permisos, CRUD, proveedor implícito, renovación, filtros, resumen y auditoría
- `backend/apps/licencias_garantias/tests/integration/test_seed_licencias.py` — guarda DEBUG y seed idempotente

### App incidentes
- `backend/apps/incidentes/models.py` â€” `Incidente` (activo FK, reportado_por FK, fecha, descripciÃ³n, estado REPORTADO/EN_PROCESO/RESUELTO/CERRADO/CANCELADO) + `HistoricalIncidente`
- `backend/apps/incidentes/{serializers,permissions,services,selectors,filters,views,urls}.py` â€” API `/api/v1/incidentes/` (list/create/cambiar_estado); ADMIN/TÃ‰CNICO todo, USUARIO_RESPONSABLE crea y ve solo los suyos; auditorÃ­a `INCIDENTE_*`
- `backend/apps/incidentes/migrations/0001_initial.py` â€” esquema + histÃ³rico + Ã­ndices

### App documentos (RF013)
- `backend/apps/documentos/models.py` â€” `Documento` (activo FK, nombre, tipo, archivo FileField `documentos/%Y/%m/`, descripcion, subido_por FK) + `HistoricalDocumento`
- `backend/apps/documentos/serializers.py` â€” lectura + creaciÃ³n con validaciÃ³n de extensiÃ³n y tamaÃ±o (<=10 MB)
- `backend/apps/documentos/permissions.py` â€” `IsDocumentoAccess` (solo ADMINISTRADOR y TÃ‰CNICO)
- `backend/apps/documentos/{selectors,filters,services,views,urls}.py` â€” listado/crear/eliminar + `descargar/` autenticado; auditorÃ­a `DOCUMENTO_*`; API `/api/v1/documentos/`
- `backend/apps/documentos/migrations/0001_initial.py` â€” esquema + histÃ³rico + Ã­ndices

### App bajas (RF014)
- `backend/apps/bajas/models.py` â€” `Baja` (activo OneToOne, fecha, motivo, autorizado_por FK, documento FK opcional) + `HistoricalBaja`
- `backend/apps/bajas/services.py` â€” `registrar_baja`: valida duplicado/asignación abierta/motivo/fecha, pasa el activo a DADO_DE_BAJA y audita `BAJA_REGISTRADA`
- `backend/apps/bajas/{serializers,permissions,selectors,filters,views,urls}.py` â€” API `/api/v1/bajas/` (list/retrieve/create) solo ADMINISTRADOR
- `backend/apps/bajas/migrations/0001_initial.py` â€” esquema + histórico + índice
- `frontend/src/features/bajas/` â€” `api/bajas.api.ts` y `pages/BajasPage.tsx` (lista + alta con motivo/fecha/documento soporte); ruta `/bajas` y menú ADMINISTRADOR

### App dashboard
- `backend/apps/dashboard/selectors.py` — `resumen_dashboard` (KPIs de inventario, cumplimiento preventivo mensual, próximos 14 días, vencidos, correctivos de 30 días, activos sin preventivo y costo anual)
- `backend/apps/dashboard/serializers.py` — contrato de respuesta anidado del tablero (OpenAPI)
- `backend/apps/dashboard/permissions.py` — `IsDashboardAccess` (lectura para los 3 roles)
- `backend/apps/dashboard/views.py` — `DashboardResumenView` GET (alcance por rol: responsable sin mantenimientos/costos)
- `backend/apps/dashboard/urls.py` — `/api/v1/dashboard/resumen/`
- `backend/apps/dashboard/tests/integration/test_dashboard_api.py` — permisos por rol, agregados, alertas y caso sin datos

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
- `backend/apps/auditoria/models.py` — `AccionAuditoria` (TextChoices) y `RegistroAuditoria` (eventos de acceso/gestión, sin JSON)- `backend/apps/auditoria/services.py` — `registrar_evento(...)` (escritura única de auditoría)
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
- `frontend/src/api/client.ts` — cliente Axios centralizado con Bearer JWT y refresco automático 401 por cola; `Content-Type` lo gestiona axios (JSON/multipart con boundary)
- `frontend/src/api/query-client.ts` — cliente TanStack Query con defaults (stale/retry/refetch)

### Componentes Compartidos (`frontend/src/components/shared/`)
- `AppShell.tsx` — layout (sidebar/topbar), navegación filtrada por rol (incluye Bajas; sin Reportes/Configuración) y logout
- `PageHeader.tsx` — encabezado con breadcrumbs, título/subtítulo y acciones
- `FormField.tsx` — campo con etiqueta, requerido, helpText y error accesible
- `FormSection.tsx` — sección contenedora de formularios
- `StatusBadge.tsx` — badge semántico con variantes de estado
- `EmptyState.tsx` — estado vacío reutilizable
- `LoadingSkeleton.tsx` — skeleton loader
- `ErrorState.tsx` — estado de error con reintento
- `DataTable.tsx` — tabla genérica reutilizable para listados
- `ConfirmDialog.tsx` — diálogo de confirmación (acciones destructivas/seguras)
- `KpiCard.tsx` — tarjeta KPI reutilizable (etiqueta, valor, ayuda, icono y tono semántico)

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

### Módulo Activos (`frontend/src/features/activos/`)
- `api/activos.api.ts` — API `/api/v1/activos/` (lista, detalle, historial, crear, editar, inactivar/reactivar)
- `pages/ActivosListPage.tsx` — inventario con filtros activos/inactivos/todos, búsqueda, columna "Ver detalle" y botón "Registrar activo" (ADMIN/TÉCNICO)
- `pages/ActivosFormPage.tsx` — alta/edición (marca→modelo, validaciones)
- `pages/ActivosDetailPage.tsx` — detalle con pestañas Resumen/Asignaciones/Mantenimientos/Incidentes/Documentos/Historial y bloque de garantía

### Módulo Incidentes (`frontend/src/features/incidentes/`)
- `api/incidentes.api.ts` — API `/api/v1/incidentes/` (listar; consumido por la pestaña Incidentes del detalle)

### Módulo Documentos (`frontend/src/features/documentos/`)
- `api/documentos.api.ts` — API `/api/v1/documentos/` (listar, subir multipart, descargar, eliminar)
- `components/DocumentosTab.tsx` — formulario de subida siempre visible + tabla con descargar/eliminar

### Módulo Bajas (`frontend/src/features/bajas/`)
- `api/bajas.api.ts` — API `/api/v1/bajas/` (listar, registrar)
- `pages/BajasPage.tsx` — listado con búsqueda/paginación y diálogo "Registrar baja" (activo, fecha, motivo, documento soporte)

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

### Módulo Mantenimientos (`frontend/src/features/mantenimientos/`)
- `api/mantenimientos.api.ts` — API `/api/v1/mantenimientos/` (resumen, calendario, técnicos, lista, detalle, historial, crear, correctivos, completar, reprogramar, cancelar)
- `types/index.ts` — contratos de mantenimiento, resumen, calendario, historial
- `schemas/mantenimiento.schema.ts` — Zod de programar/completar/reprogramar/cancelar
- `utils/fechas.ts` — meses/días en español, `dd/MM/yyyy` y cuadrícula mensual desde lunes
- `pages/MantenimientosPage.tsx` — pestañas Calendario/Lista/Correctivos, KPI anual, chips por situación, detalle con historial y diálogos de acciones (incluye registrar correctivo)
- `__tests__/MantenimientosPage.test.tsx` — MSW: carga/vacío/error, chips, programar, roles, reprogramar 200/201, incumplido, cancelar, filtros
- `schemas/__tests__/mantenimiento.schema.test.ts` — pruebas Zod

### Módulo Licencias (`frontend/src/features/licencias/`)
- `api/licencias.api.ts` — API `/api/v1/licencias/` (lista, detalle, resumen, proveedores, crear, actualizar, renovar, inactivar, reactivar)
- `types/index.ts` — contratos de licencia, resumen y payloads
- `schemas/licencia.schema.ts` — Zod de alta/edición y renovación (valor opcional, cantidad ≥ 1)
- `utils/licencias.ts` — etiquetas, variantes de estado, suma de periodos y textos de días
- `components/campos.ts` — estilo compartido de campos de la feature
- `components/RenovarLicenciaDialog.tsx` — diálogo de renovación con fecha sugerida y valor opcional
- `pages/LicenciasPage.tsx` — KPIs, alertas, filtros, tabla con paginación, renovar/inactivar/reactivar
- `pages/LicenciaFormPage.tsx` — alta/edición en tres secciones con datalist de proveedores
- `__tests__/LicenciasPage.test.tsx` — MSW: KPIs, filtros, renovación, inactivación, vacío y error
- `__tests__/LicenciaFormPage.test.tsx` — crear, editar y validación de obligatorios
- `schemas/__tests__/licencia.schema.test.ts` — validaciones Zod
- `utils/__tests__/licencias.test.ts` — suma de meses y textos de días

### Módulo Asignaciones (`frontend/src/features/asignaciones/`)
- `api/asignaciones.api.ts` — API `/api/v1/asignaciones/` (lista, resumen, usuarios, crear, cerrar, reasignar)
- `types/index.ts` — contratos de asignación, resumen y payloads
- `schemas/asignacion.schema.ts` — Zod de asignación/reasignación y devolución (fechas válidas)
- `utils/asignaciones.ts` — etiquetas de rol, estilo de campos y duración
- `components/AsignarDialog.tsx` — alta y reasignación con selects de equipos disponibles/colaboradores
- `components/DevolverDialog.tsx` — registro de devolución
- `pages/AsignacionesPage.tsx` — KPIs, filtros activas/historial, tabla, paginación y acciones
- `__tests__/AsignacionesPage.test.tsx` — MSW: carga, filtros, alta, reasignación, devolución, rol técnico y error
- `schemas/__tests__/asignacion.schema.test.ts` — validaciones Zod

### Rutas y Vistas
- `frontend/src/routes/Router.tsx` — rutas; `/usuarios*`, `/licencias*` y `/bajas` bajo guardia ADMINISTRADOR; `/activos*`, `/asignaciones` y `/mantenimientos` bajo ADMINISTRADOR/TECNICO
- `frontend/src/routes/ProtectedRoute.tsx` — guardia de autenticación y roles (redirige a `/dashboard` si rol no permitido)
- `frontend/src/lib/format.ts` — moneda COP, fechas dd/MM/yyyy, día/mes corto y `aISO`
- `frontend/src/features/dashboard/api/dashboard.api.ts` — API `/api/v1/dashboard/resumen/`
- `frontend/src/features/dashboard/hooks/useDashboardResumen.ts` — query con `staleTime` de 60 s para el tablero
- `frontend/src/features/dashboard/types/index.ts` — contratos del resumen del tablero
- `frontend/src/features/dashboard/pages/DashboardPage.tsx` — tablero por rol: alertas, KPIs, cumplimiento, próximos/vencidos/correctivos, distribución y últimas adquisiciones
- `frontend/src/features/dashboard/components/AlertasTablero.tsx` — alertas derivadas (vencidos, incumplidos, próximos 7 días, sin preventivo)
- `frontend/src/features/dashboard/components/CumplimientoMensual.tsx` — barras apiladas por mes (completados/pendientes/vencidos/incumplidos)
- `frontend/src/features/dashboard/components/BarrasHorizontales.tsx` — barras de distribución reutilizables
- `frontend/src/features/dashboard/components/ListaMantenimientos.tsx` — lista compacta con chip de fecha y días restantes/atraso
- `frontend/src/features/dashboard/components/UltimasAdquisiciones.tsx` — activos recientes con badge de estado
- `frontend/src/features/dashboard/components/SeccionPanel.tsx` — tarjeta de sección del tablero
- `frontend/src/features/dashboard/__tests__/DashboardPage.test.tsx` — MSW: KPIs, alertas, rol responsable, error y ausencia de "Registrar activo"
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