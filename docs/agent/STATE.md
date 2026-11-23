# STATE — estado vivo del proyecto

> El agente actualiza este archivo al cerrar cada tarea. Mantenerlo corto (no es un historial completo).
> Última actualización: 2026-11-12 · por: agente (cierre T-002 FASE B)

## Tarea actual
**T-004 — Activos (Fase C backend COMPLETA; Fase D frontend pendiente).** Fase C: app `activos`, migración, ACTIVO_* en auditoría, seed ampliado (40 activos), tests (22 passed). Siguiente: Fase D frontend (espera orden).

## Hecho
- Documento de análisis y diseño (docx), mockups, diccionario de datos (baseline). Repo y documentación para agentes instalada.
- **T-001 FASE A (backend):** Django 5.1.15, settings base/dev/prod, JWT, CORS, drf-spectacular; apps `common`, `usuarios` (AbstractUser, email, rol, bloqueo), `autenticacion` (MFA TOTP, Fernet, mfa_token firmado, throttling, endpoints `/api/v1/auth/`, `seed_usuarios_dev`). 19/19 tests, ruff OK, migraciones aplicadas.
- **T-001 FASE B (frontend):** Vite + React 19 + TS + Tailwind 4, tokens CSS, cliente Axios con refresh HttpOnly, TanStack Query, auth (login/MFA setup+verify+recovery), `AppShell`, rutas protegidas por rol, componentes compartidos base. 18/18 tests Vitest, lint/typecheck OK.
- **T-002 FASE A (backend, commiteada):** app `auditoria` (`RegistroAuditoria`, admin solo lectura), `Usuario.debe_cambiar_password`, normalización/`UniqueConstraint(Lower(email))` (migraciones `usuarios/0002-0004`, `auditoria/0001`), CRUD admin `/api/v1/usuarios/` (crear/reset password/reset MFA/activar/desactivar, guardas self/último-admin), revocación de refresh, `POST /api/v1/auth/password/change/` (`password_change_required`), auditoría de sesión/eventos, comando `resetear_mfa`. ruff/makemigrations check OK; pytest unit 17 passed, `not system` 67 passed.
- **T-002 FASE B (frontend):** flujo de cambio obligatorio en `LoginPage`/`PasswordChangeStep`; feature `usuarios` (lista con filtros/búsqueda/paginación/acciones, crear/editar), `TempPasswordModal` y `ConfirmResetMfaDialog` (temporal solo en estado local, mutaciones `gcTime: 0` + `reset()`, respuestas `no-store`), `DataTable`/`ConfirmDialog` compartidos, `ProtectedRoute` con guardia `roles` y rutas `/usuarios*` solo ADMINISTRADOR, `AppShell` sin `var(--surface)`. Actualizada skill `frontend-design-system` según `tokens.css`. Vitest 28/28, lint/typecheck OK.

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
- [ ] Aprobar o ajustar la propuesta normalizada de `DATA_MODEL.md` (bloquea T-003).
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
- 2026-11-09: T-001 FASE A completada. Backend esqueleto + autenticación TOTP. 19/19 tests. Sin Docker (local).
- 2026-11-10: T-001 FASE B completada. Frontend React 19 + Auth TOTP + Layout AppShell. 18/18 tests. Typecheck & lint 0 errores.
- 2026-11-12: T-002 FASE A commiteada por usuario (usuarios/auditoría/auth). ruff/migrations OK, 17 unit + 67 not-system passed.
- 2026-11-12: T-002 FASE B completada (cambio obligatorio, gestión usuarios UI, docs/ADRs). Frontend lint/typecheck OK, 28/28 Vitest.