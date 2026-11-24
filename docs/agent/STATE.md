# STATE — estado vivo del proyecto

> El agente actualiza este archivo al cerrar cada tarea. Mantenerlo corto (no es un historial completo).
> Última actualización: 2026-11-24 · por: agente (Licencias T-007 parcial)

## Tarea actual
**Licencias (T-007 parcial) COMPLETO.** App `licencias_garantias` (Proveedor + Licencia con histórico), API `/api/v1/licencias/` (`resumen`, `proveedores`, `renovar`, `inactivar`, `reactivar`, filtros por estado de renovación) solo ADMINISTRADOR, y pantalla `/licencias` con KPIs, alertas, filtros, alta/edición, renovación y seed de 15 registros. Reemplaza el Excel de control de licencias; no hay importación/exportación de Excel. Siguiente: garantías por activo (segunda fase T-007/ADR-019) o repuestos/incidentes.

## Hecho
- Documento de análisis y diseño (docx), mockups, diccionario de datos (baseline). Repo y documentación para agentes instalada.
- **T-001 FASE A (backend):** Django 5.1.15, settings base/dev/prod, JWT, CORS, drf-spectacular; apps `common`, `usuarios` (AbstractUser, email, rol, bloqueo), `autenticacion` (MFA TOTP, Fernet, mfa_token firmado, throttling, endpoints `/api/v1/auth/`, `seed_usuarios_dev`). 19/19 tests, ruff OK, migraciones aplicadas.
- **T-001 FASE B (frontend):** Vite + React 19 + TS + Tailwind 4, tokens CSS, cliente Axios con refresh HttpOnly, TanStack Query, auth (login/MFA setup+verify+recovery), `AppShell`, rutas protegidas por rol, componentes compartidos base. 18/18 tests Vitest, lint/typecheck OK.
- **T-002 FASE A (backend, commiteada):** app `auditoria` (`RegistroAuditoria`, admin solo lectura), `Usuario.debe_cambiar_password`, normalización/`UniqueConstraint(Lower(email))` (migraciones `usuarios/0002-0004`, `auditoria/0001`), CRUD admin `/api/v1/usuarios/` (crear/reset password/reset MFA/activar/desactivar, guardas self/último-admin), revocación de refresh, `POST /api/v1/auth/password/change/` (`password_change_required`), auditoría de sesión/eventos, comando `resetear_mfa`. ruff/makemigrations check OK; pytest unit 17 passed, `not system` 67 passed.
- **T-002 FASE B (frontend):** flujo de cambio obligatorio en `LoginPage`/`PasswordChangeStep`; feature `usuarios` (lista con filtros/búsqueda/paginación/acciones, crear/editar), `TempPasswordModal` y `ConfirmResetMfaDialog` (temporal solo en estado local, mutaciones `gcTime: 0` + `reset()`, respuestas `no-store`), `DataTable`/`ConfirmDialog` compartidos, `ProtectedRoute` con guardia `roles` y rutas `/usuarios*` solo ADMINISTRADOR, `AppShell` sin `var(--surface)`. Actualizada skill `frontend-design-system` según `tokens.css`. Vitest 28/28, lint/typecheck OK.
- **T-004 Fase D (frontend):** pantallas de activos y matriz de pruebas cerrada (esquemas Zod, lista MSW, formulario marca→modelo, crear/editar, 400 por serial, roles, smoke `/activos`). 65 Vitest, lint/typecheck OK.
- **T-006a (mantenimientos preventivos):** app `mantenimientos` (`Mantenimiento` + `HistoricalMantenimiento`, migración `0001`), situación derivada sin cron y reprogramación con evidencia inmutable (ADR-016), auditoría `MANTENIMIENTO_*`, API `/api/v1/mantenimientos/` (`resumen`, `calendario`, `tecnicos`, `completar`, `reprogramar`, `cancelar`, `historial`) y UI `/mantenimientos` (pestañas Calendario/Lista, franja KPI de 12 meses, chips por situación, detalle, diálogos y pruebas MSW). Backend 35 unit + 164 `not system`; frontend 84 Vitest; ruff/typecheck OK. Datos de prueba cargados en dev con `seed_mantenimientos_dev` (32 registros de 2026: completados, vencidos, incumplidos y pendientes).
- **T-006a correctivos (ADR-017):** `fecha_seguimiento` en `Mantenimiento` (migración `0002`), `POST /api/v1/mantenimientos/correctivos/` y filtro `?tipo=`, registro directo `COMPLETADO` que no altera KPI/calendario preventivo; pestaña **Correctivos** en `/mantenimientos` con lista y diálogo (equipo, qué pasó, fecha evento, seguimiento, técnico). Pruebas: 7 integración correctivos + seed; frontend 88 Vitest; ruff/lint/typecheck OK. Seed añade 3 correctivos de ejemplo. Los listados/selects de equipos (Activos y mantenimientos) filtran `is_active=true` y `estado_no=DADO_DE_BAJA`.
- **Dashboard analítico (ADR-018, avance de T-011):** app `dashboard` con `GET /api/v1/dashboard/resumen/` (KPIs de inventario, valor, cumplimiento preventivo anual y mensual, próximos 14 días, vencidos con días de atraso, correctivos de 30 días y costo del año) calculado en `selectors.py`; admin/técnico reciben mantenimiento y costos, el usuario responsable solo inventario. UI `/dashboard` rediseñada con alertas operativas, KPIs, gráfica mensual apilada, distribución por estado/categoría/marca y listas accionables; se retiró "Registrar Activo". Pruebas: 5 integración backend, 6 Vitest frontend; ruff/lint/typecheck OK.
- **Licencias T-007 parcial (ADR-019):** app `licencias_garantias` (`Proveedor`, `Licencia`, históricos, migración `0001`), estado de renovación derivado (VIGENTE/POR_VENCER/VENCIDA/INACTIVA, umbral 30 días) sin campo almacenado, acciones de auditoría `LICENCIA_*` (migración `auditoria/0006`), API `/api/v1/licencias/` solo ADMINISTRADOR (`resumen` con costo anualizado, `proveedores`, `renovar`, `inactivar`, `reactivar`, filtros/búsqueda/orden/paginación) y comando `seed_licencias_dev`. UI `/licencias`: KPIs, alertas de vencidas/por vencer, filtros por proveedor/periodicidad/estado, tabla con paginación, crear/editar y diálogo de renovación. Pruebas: 23 backend, 15 Vitest; ruff/lint/typecheck OK. Garantías pendientes.

## Backlog (cada tarea = módulo completo: backend + frontend + pruebas)
| ID | Alcance | Depende de |
|---|---|---|
| T-001 | Entorno: Django+DRF, React, usuario personalizado, JWT+MFA TOTP, layout base | — |
| T-002 | Usuarios y acceso completo (RF001, RF002) + auditoría de accesos + reset MFA por admin | T-001 |
| T-003 | Catálogos (Sede, Ubicación, Categoría, Marca, Modelo) | T-002, DATA_MODEL aprobado |
| T-004 | Activos: registro, consulta con filtros, historial (RF003, RF004, RNF008) | T-003 |
| T-005 | Asignación de responsables + trazabilidad + QR (RF005, RF011, RF012) | T-004 |
| T-006 | Mantenimientos e incidentes (RF006, RF007, RF008) | T-004 |
| T-007 | Proveedores, garantías, software y licencias (RF009, RF010) | T-004 |
| T-008 | Documentos adjuntos (RF013) | T-004 |
| T-009 | Bajas (RF014) | T-004 |
| T-010 | Alertas: comando diario + bandeja (RF015) | T-006, T-007 |
| T-011 | Dashboard y reportes PDF/Excel (RF016, RF017) | T-004..T-007 |
| T-012 | Backup diario de BD (RNF004), pruebas de sistema E2E, endurecimiento | todas |

## Decisiones pendientes del usuario
- [ ] Aprobar o ajustar el resto de `DATA_MODEL.md`; `Proveedor` y `Licencia` ya están aprobados para T-007 licencias. Garantías y `LicenciaActivo` siguen pendientes (ADR-019).
- [ ] ¿El Usuario Responsable puede ver sus activos asignados? (los RF no lo definen; se propone que sí, solo lectura).
- [ ] "Control de actualizaciones" aparece en el alcance pero no tiene RF ni tabla: definir o descartar.
- [ ] ¿Quién recibe las alertas (solo Admin/Técnico según RF015)?

## Ideas y deuda (fuera de alcance actual)
- `resetear_mfa` (comando de gestión) como vía de emergencia si el único admin pierde su dispositivo (sin guarda de auto-reset; usar con control operativo).
- Revocación inmediata de access tokens tras reset/cambio de contraseña/MFA (p. ej. token version o `password_changed_at`); hoy el refresh se revoca pero el access puede vivir hasta expirar (≤15 min), salvo inactivación que se rechaza de inmediato.
- Retención/depuración y política de consulta de la tabla `RegistroAuditoria` (crecimiento, archivado, índices/particionado según volumen); UI de consulta de auditoría fuera de alcance.
- Recuperación de contraseña por el propio usuario (flujo de "olvidé mi contraseña" con canal verificado); hoy solo reset administrativo con temporal.
- Considerar `django-simple-history` para auditoría de cambios en modelos de negocio (ADR-005).
- `Ubicacion` (catálogo) queda sin uso por Activo en T-004 (la ubicación efectiva se deriva de la asignación en T-005). No borrar; reutilizar en T-005.

## Registro de sesiones (solo las últimas 5, una línea c/u)
- 2026-11-12: T-002 FASE A commiteada por usuario (usuarios/auditoría/auth). ruff/migrations OK, 17 unit + 67 not-system passed.
- 2026-11-12: T-002 FASE B completada (cambio obligatorio, gestión usuarios UI, docs/ADRs). Frontend lint/typecheck OK, 28/28 Vitest.
- 2026-11-24: T-004 Fase D pruebas y T-006a preventivos (backend+frontend) completos. Backend 35 unit/164 not-system; frontend 84 Vitest; ruff/typecheck OK. Correctivos básicos añadidos (pestaña, API y seed); frontend 88 Vitest.
- 2026-11-24: Dashboard analítico (endpoint agregado por rol + UI con KPIs, gráficas y listas accionables; sin "Registrar Activo"). Backend 179 passed; frontend 94 Vitest; ruff/lint/typecheck OK. `npm run build` falla por tipos MSW preexistentes en pruebas.
- 2026-11-24: Licencias T-007 parcial (Proveedor/Licencia, API por rol admin, UI con KPIs, filtros, renovación y seed de 15 registros; sin Excel). Backend 202 passed; frontend 109 Vitest; ruff/lint/typecheck OK. Garantías pendientes.