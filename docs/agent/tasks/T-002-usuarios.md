# T-002 — Usuarios y acceso completo (RF002 + auditoría + resets)

## Objetivo
Gestión de usuarios (RF002) sobre T-001: CRUD solo Administrador, reset de contraseña con
temporal + cambio obligatorio, reset MFA por admin, revocación de sesiones y auditoría (RNF008)
en `RegistroAuditoria`.

## Fases ejecutadas
- **Fase A (backend):** completada y commiteada por el usuario.
- **Fase B (frontend + documentación):** completada en esta sesión.

## Alcance implementado
- **Esquema (APROBADO para T-002):** `Usuario.debe_cambiar_password`, unicidad case-insensitive de
  email (normalización + constraint `Lower(email)`), `RegistroAuditoria` (app `auditoria`).
- **Auth:** `ResultadoAutenticacion`, `password_change_required` + `POST /api/v1/auth/password/change/`,
  revocación de refresh en reset/cambio obligatorio/inactivación, auditoría de sesión/eventos
  (`LOGIN_EXITOSO` solo al emitir sesión).
- **Usuarios API (admin-only):** listado/filtros/búsqueda, crear (retorna temporal), editar
  (nombre/rol), activar/desactivar, `reset_password`, `reset_mfa`; guardas (self/último admin)
  y errores de dominio.
- **Comando:** `resetear_mfa --email` (consola, salida de emergencia; audita con `usuario=None`).
- **Frontend:** flujo de cambio obligatorio en login, feature `usuarios` (lista, crear/editar),
  modales de contraseña temporal y confirmación de reset MFA, guardia por rol en rutas,
  `DataTable`/`ConfirmDialog` compartidos. Contraseña temporal solo en estado local del modal,
  mutaciones con `gcTime: 0` y `reset()`.

## Pruebas y verificación (resumen)
- **Backend (Fase A, commiteada):** ruff check/format OK, `makemigrations --check --dry-run` OK,
  `pytest -m unit` 17 passed (50 deselected), `pytest -m "not system"` 67 passed.
- **Frontend (Fase B):** lint/typecheck OK, `vitest run` 28 passed (9 archivos).

## Fuera de alcance
- Envío de contraseña por correo, UI de consulta de `RegistroAuditoria`, revocación inmediata de
  access tokens tras reset (token version/`password_changed_at`), auditoría de exportaciones (T-011),
  expiración temporal por tiempo.
