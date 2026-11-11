# STATE — estado vivo del proyecto

> El agente actualiza este archivo al cerrar cada tarea. Mantenerlo corto (no es un historial completo).
> Última actualización: 2026-11-10 · por: agente (cierre T-001 FASE B)

## Tarea actual
**T-001 — Esqueleto + login con MFA TOTP** → `docs/agent/tasks/T-001-setup.md`. Estado: **COMPLETA**.
Siguiente tarea: **T-002 — Usuarios y acceso completo**.

## Hecho
- Documento de análisis y diseño (docx), mockups, diccionario de datos (baseline).
- Repo creado. Documentación para agentes instalada.
- **T-001 FASE A** — Backend completo:
  - Proyecto Django 5.1.15 con settings base/dev/prod, JWT, CORS, drf-spectacular.
  - App `common`: BaseModel, manejador de excepciones, permisos por rol, paginación.
  - App `usuarios`: modelo Usuario (AbstractUser, login por email, rol, bloqueo de cuenta).
  - App `autenticacion`: DispositivoMFA + CodigoRecuperacion; cifrado Fernet; TOTP con pyotp;
    mfa_token firmado (propósito validado); throttling; 7 endpoints bajo `/api/v1/auth/`.
  - Comando `seed_usuarios_dev` (3 usuarios, uno por rol).
  - 11 tests unitarios + 8 tests de integración = **19/19 passed**.
  - ruff check + format: 0 errores.
  - Migraciones aplicadas en `inventario_dev`.
- **T-001 FASE B** — Frontend completo:
  - Vite + React 19 + TypeScript + Tailwind CSS 4.
  - Sistema de diseño sobrio: tokens CSS institucionales (`tokens.css`, `globals.css`).
  - Capa API centralizada en Axios con interceptores JWT Bearer y refresco automático transparente vía HttpOnly cookies (`src/api/client.ts`). TanStack Query configurado (`src/api/query-client.ts`).
  - Auth module: Context provider `useAuth`, APIs de auth, schemas de validación Zod (`login.schema.ts`, `mfa.schema.ts`).
  - Pantallas de autenticación: `LoginPage` con flujo paso a paso (credenciales, `MFAVerifyStep`, `MFASetupStep` con QR `qrcode.react` y `RecoveryCodesDisplay`).
  - Layout institucional `AppShell`: sidebar colapsable color navy, navegación filtrada por rol de usuario (`ADMINISTRADOR`, `TECNICO`, `USUARIO_RESPONSABLE`), topbar con badge de rol y avatar, y logout.
  - Componentes compartidos (`PageHeader`, `FormField`, `FormSection`, `StatusBadge`, `EmptyState`, `LoadingSkeleton`, `ErrorState`).
  - Enrutamiento con `react-router-dom`: `ProtectedRoute` con redirección según autenticación y validación de roles, `DashboardPage`, `ComingSoonPage`, `NotFoundPage`.
  - 18 tests unitarios Vitest pasados al 100% (componentes compartidos, schemas y flujos auth).
  - Typecheck (`tsc -b`) y linter (`oxlint`) con 0 errores y 0 warnings.

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
- T-002 debe incluir endpoint de reset MFA por administrador (identificado en T-001).
- Considerar `django-simple-history` para auditoría de cambios en modelos de negocio (ADR-005).
- Soporte para Docker diferido por decisión del usuario (ejecución actual en local Vite dev server + Django runserver).

## Registro de sesiones (solo las últimas 5, una línea c/u)
- 2026-11-09: T-001 FASE A completada. Backend esqueleto + autenticación TOTP. 19/19 tests. Sin Docker (local).
- 2026-11-10: T-001 FASE B completada. Frontend React 19 + Auth TOTP + Layout AppShell. 18/18 tests. Typecheck & lint 0 errores.
