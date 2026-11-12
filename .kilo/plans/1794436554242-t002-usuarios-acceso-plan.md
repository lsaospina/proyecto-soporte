# Plan — T-002 Usuarios y acceso completo (RF002 + auditoría + resets)

## Objetivo
Gestión de usuarios (RF002) sobre T-001: CRUD solo Administrador, reset de contraseña con temporal +
cambio obligatorio, reset MFA por admin, revocación de sesiones y auditoría (RNF008) en `RegistroAuditoria`.
Se ejecuta en **dos fases con parada**. Fase A = backend completo + reporte + commit propuesto.
Fase B = frontend + documentación, solo cuando el usuario lo pida.

## Decisiones confirmadas
1. Alcance completo + auditoría.
2. Contraseña temporal generada por el sistema, mostrada una vez; cambio obligatorio en el siguiente login.
3. **Aprobado en DATA_MODEL.md** (solo estas filas): `RegistroAuditoria` y `Usuario.debe_cambiar_password`.
4. Fase A actualiza únicamente esas dos filas de `DATA_MODEL.md` antes de migrar. El resto de la
   documentación va en Fase B.
5. Las 9 correcciones obligatorias del usuario (sección “Ajustes obligatorios”) son parte del alcance.

## Ajustes obligatorios (aprobados por el usuario)
1. `LOGIN_EXITOSO` **solo** cuando se emite sesión: login directo `ok`, `mfa/verify`, `mfa/confirm` y
   `password/change` que termine en `ok`. Nunca en el paso 1 intermedio.
2. Email normalizado (strip + lower) en login, manager, services y **cualquier búsqueda/filtro por email**.
   Prueba: `"Ana@X.com"` inicia sesión si existe `ana@x.com`.
3. Migraciones separadas: `usuarios/0002` (campo), `0003` (data migration a minúsculas, aborta con mensaje
   si hay colisión), `0004` (`UniqueConstraint(Lower("email"))`).
4. Prueba de último admin **sin hilos**: `CaptureQueriesContext` verifica que la consulta de guarda usa
   `FOR UPDATE` y ordena por `pk`. Sin tests con `threading`.
5. Capturar `IntegrityError` de unicidad de email y devolverlo como 400 (`email_duplicado`).
6. `rotar_token_refresco` comprueba **explícitamente** `is_active` y no bloqueado (no depender de SimpleJWT).
   Acciones sobre usuarios: `usuario=actor`, `entidad="Usuario"`, `entidad_id` del afectado.
7. `mfa_activo` tolera usuarios sin dispositivo (sin excepción).
8. Comando de gestión `resetear_mfa --email <correo>`: solo consola, audita `MFA_RESETEADO`, revoca refresh,
   se niega si el usuario no existe. Es la salida si el único admin pierde su dispositivo.
9. ADR-012/013 documentan: tras inactivar, el access token se rechaza de inmediato; tras reset de
   contraseña/MFA puede vivir hasta 15 min.

## Estado actual del repo (bloqueante)
`git status` **NO está limpio** (verificado 2026-11-12):
- `D` (deleted): `docs/design/mockups/fig11..fig19*.png`.
- `M` (modified): `frontend/package-lock.json`, `frontend/src/App.tsx`,
  `frontend/src/components/shared/AppShell.tsx`, `frontend/src/features/auth/pages/LoginPage.tsx`,
  `frontend/src/features/dashboard/pages/DashboardPage.tsx`, `frontend/src/main.tsx`,
  `frontend/src/styles/tokens.css`.
- `??` (untracked): `.kilo/`, `docs/design/mockups/dashboard_principal.html`, `docs/design/mockups/login.html`.
**Gate A0**: si el árbol no está limpio, detenerse y pedir al usuario que confirme/ejecute el commit o
descarte; el agente no escribe en git. No iniciar migraciones ni código con el árbol sucio.

## FASE A — Backend (STOP al terminar)

### A0. Línea base (antes de tocar nada)
1. Confirmar `git status` limpio (gate anterior). Si no, STOP.
2. Ejecutar y reportar conteos exactos; si no se puede, “NO EJECUTADO” + comando:
   - `cd backend && pytest -m unit`
   - `cd backend && pytest -m "not system"` (requiere PostgreSQL)
   - `cd frontend && npm run test`
3. No escribir código hasta reportar la línea base.

### A1. Esquema y aprobación mínima
- Marcar en `DATA_MODEL.md` como **APROBADO** solo `RegistroAuditoria` y `Usuario.debe_cambiar_password`.
- Nueva app `auditoria` (en `LOCAL_APPS`), con `RegistroAuditoria`:
  - `usuario` FK `AUTH_USER_MODEL`, `null=True`, `on_delete=SET_NULL`, `related_name="registros_auditoria"`.
  - `accion` `CharField(40)` + `TextChoices AccionAuditoria`: `LOGIN_EXITOSO, LOGIN_FALLIDO, LOGOUT,
    MFA_ACTIVADO, MFA_VERIFICADO, MFA_RECHAZADO, PASSWORD_CAMBIADA, USUARIO_CREADO,
    USUARIO_ACTUALIZADO, USUARIO_INACTIVADO, USUARIO_REACTIVADO, PASSWORD_RESETEADA, MFA_RESETEADO`.
  - `entidad` `CharField(50, blank=True, default="")`, `entidad_id` `CharField(64, blank=True, default="")`,
    `fecha` `DateTimeField(auto_now_add=True)`, `ip` `GenericIPAddressField(null=True, blank=True)`.
  - `Meta`: `ordering=["-fecha"]`, índices en `fecha`, `accion`, `usuario`. Sin JSON (3FN).
  - Migración `auditoria/0001_initial`.
- `Usuario`: `debe_cambiar_password = BooleanField(default=False)`.
- Email normalizado + unicidad case-insensitive:
  - Helper `normalizar_email(email)` (strip + lower) en `apps/usuarios/utils.py`; usar en
    `UsuarioManager.create_user`, services de creación/edición, login y selectores/filtros.
  - **Tres migraciones separadas**:
    1. `usuarios/0002_usuario_debe_cambiar_password` (campo).
    2. `usuarios/0003_normalizar_emails` (RunPython: `Lower(email)`; si tras normalizar hay duplicados,
       **abortar** con `RuntimeError`/`CommandError` listando los emails en conflicto; reverso no-op).
    3. `usuarios/0004_usuario_email_ci_unico` (`UniqueConstraint(Lower("email"), name="usuario_email_ci_unico")`).
  - Mantener `unique=True` del campo; la constraint funcional garantiza CI.
- `backend/.env.example`: `TRUST_X_FORWARDED_FOR=False` (nunca tocar `.env`).

### A2. Auditoría (app `auditoria`)
- `apps/auditoria/utils.py`:
  - `get_client_ip(request)`: **REMOTE_ADDR por defecto**; `X-Forwarded-For` (primera IP) solo si
    `settings.TRUST_X_FORWARDED_FOR` es True.
  - `sanitizar_entidad_id(valor)`: devuelve el valor solo si contiene `"@"` y `len <= 64`; si no, `""`.
- `apps/auditoria/services.py`: `registrar_evento(*, usuario=None, accion, entidad="", entidad_id="", ip=None)`
  con una sola escritura. Nunca loggear contraseñas, tokens ni códigos.
- `apps/auditoria/admin.py`: `RegistroAuditoriaAdmin` **solo lectura**
  (`has_add_permission`/`has_change_permission`/`has_delete_permission` → False).
- Semántica transaccional:
  - `LOGIN_FALLIDO` y `MFA_RECHAZADO`: registrar **antes** de lanzar el error, fuera de un atomic que se
    revierta, para que persistan con respuesta 401/403.
  - Escrituras de usuarios: los services reciben `ip` y registran el evento **dentro del mismo
    `transaction.atomic()`** que la operación, con `usuario=actor`, `entidad="Usuario"` y
    `entidad_id=str(afectado.pk)`.

### A3. Revocación de sesiones
- `apps/common/sessions.py`: `revocar_tokens_refresco(usuario)` → `OutstandingToken.objects.filter(user=usuario)`
  + `BlacklistedToken.objects.get_or_create(...)`. Sin importar `apps.autenticacion` (evita ciclos).
- Invocar en `resetear_password`, `resetear_mfa`, `inactivar_usuario` y en cambio obligatorio de contraseña.
- `rotar_token_refresco`: cargar usuario por id y comprobar **explícitamente**
  `if not user or not user.is_active or user.esta_bloqueado: raise CredencialesInvalidasError(...)`.
- Verificar que `/me` rechaza inactivos (no depender solo de SimpleJWT: probar el comportamiento).
- Documentar: access tokens vivos ≤15 min tras reset (ADR-012/013); tras inactivar se rechazan de inmediato.

### A4. Usuarios — capas
- `selectors.py`: `listar_usuarios(*, rol=None, is_active=None, search=None)`; normalizar `search` si
  parece email (`email__iexact=normalizar_email(search)`) y `select_related`.
- `services.py` (reciben `actor` e `ip`; cada escritura en `transaction.atomic()`):
  - `crear_usuario(*, email, nombre_completo, rol, actor, ip)` → temporal, `debe_cambiar_password=True`,
    devuelve `(usuario, password_temporal)`. Captura `IntegrityError` de unicidad → `ReglaDeNegocioError`
    (`code="email_duplicado"`, `errors=[{"field":"email","message":"Ya existe un usuario con ese correo."}]`).
  - `actualizar_usuario(usuario, *, nombre_completo, rol, actor, ip)` (misma captura de `IntegrityError` si
    cambia email; por ahora el email no se edita).
  - `inactivar_usuario` / `reactivar_usuario`.
  - `resetear_password(usuario, *, actor, ip)` → temporal, `debe_cambiar_password=True`, limpia bloqueo,
    revoca refresh, devuelve temporal.
  - `resetear_mfa(usuario, *, actor, ip)` → borra `DispositivoMFA` (cascade), revoca refresh.
  - `generar_password_temporal()`: ≥12 chars, mayúscula, minúscula, dígito, símbolo (`secrets`).
  - Guardas con `select_for_update()` **dentro de `transaction.atomic()`**, consulta
    `.filter(rol=ADMINISTRADOR, is_active=True).order_by("pk")` (bloqueo ordenado por pk):
    - no inactivar/desactivar al propio actor;
    - no dejar sin al menos un `ADMINISTRADOR` activo;
    - un admin **no** puede resetear su propia contraseña ni su propio MFA, ni cambiar su propio rol
      desde este módulo (sí puede editar su nombre).
  - Errores `ReglaDeNegocioError` (400) con `errors=[{"field","message"}]` cuando aplique.
- `serializers.py` (sin `__all__`):
  - `UsuarioListSerializer` (id, email, nombre_completo, rol, is_active, mfa_activo,
    debe_cambiar_password, esta_bloqueado).
  - `UsuarioDetailSerializer` (+ `created_at`, `updated_at`).
  - `UsuarioCreateSerializer` (email, nombre_completo, rol; **sin** password).
  - `UsuarioUpdateSerializer` (nombre_completo, rol).
  - `UsuarioResetPasswordResponseSerializer` (`password_temporal`).
  - `mfa_activo` = `SerializerMethodField` usando `getattr(obj, "dispositivo_mfa", None)` (tolera ausencia).
  - **Sin** `UsuarioCambioEstadoSerializer`: activar/desactivar no llevan cuerpo.
- `filters.py`: `UsuarioFilter` (`rol`, `is_active`) + `search_fields=["email","nombre_completo"]` +
  `ordering_fields=["email","nombre_completo","rol","created_at"]`.
- `views.py`: `UsuarioViewSet(ModelViewSet)`, `permission_classes=[IsAdministrador]`, paginación estándar,
  `http_method_names=["get","post","patch","head","options"]` (sin DELETE físico).
  - `create` → 201 `{usuario, password_temporal}` con `Cache-Control: no-store`.
  - `partial_update` → nombre/rol.
  - `@action(detail=True, methods=["post"]) reset_password` → 200 `{password_temporal}` + `no-store`.
  - `@action(detail=True, methods=["post"]) reset_mfa` → 204.
  - `@action(detail=True, methods=["post"]) activar` / `desactivar` → 200/204 (sin body).
  - `ip = get_client_ip(request)` y se pasa a los services.
  - `@extend_schema` en todo, `tags=["Usuarios"]`.
- `urls.py`: `DefaultRouter` → `/api/v1/usuarios/`; incluir en `config/urls.py`.

### A5. Auth — dataclass + cambio obligatorio
- `apps/autenticacion/tokens.py`: `PURPOSE_PASSWORD_CHANGE`.
- `ResultadoAutenticacion` (dataclass frozen): `estado, usuario, mfa_token=None, password_token=None, refresh=None`.
  `autenticar_usuario_paso1` y `cambiar_password_obligatorio` lo devuelven; actualizar views y pruebas T-001.
- `autenticar_usuario_paso1(email, password, *, ip=None)`:
  - Normalizar email con `normalizar_email` antes de buscar (`email__iexact`).
  - Tras validar credenciales y antes de MFA: si `user.debe_cambiar_password` → estado
    `password_change_required` + `password_token` (`PURPOSE_PASSWORD_CHANGE`, 5 min).
  - **No** auditar `LOGIN_EXITOSO` en este paso intermedio; solo `LOGIN_FALLIDO` cuando aplique.
- `cambiar_password_obligatorio(password_token, new_password, *, ip=None)`:
  - Valida token y propósito; revalida `is_active` y `esta_bloqueado`.
  - Rechaza si `debe_cambiar_password` ya es False (un solo uso).
  - `validate_password(new_password, user)`; rechaza si `check_password(new_password, user.password)`.
  - `set_password`, `debe_cambiar_password=False`, `resetear_intentos_fallidos()`, revoca refresh previos.
  - Devuelve el siguiente estado (`mfa_required` / `mfa_setup_required` / `ok`) con su token/refresh.
- `serializers.py`: añadir `password_change_required` y `password_token` a `LoginResponseSerializer`;
  `PasswordChangeRequestSerializer` (`password_token`, `new_password`, `confirm_password` con coincidencia).
- `views.py`: `PasswordChangeView` `POST /api/v1/auth/password/change/` (`AllowAny`, `MFARateThrottle`).
  `Cache-Control: no-store` cuando la respuesta incluya credenciales/tokens.
- **Auditoría de sesión (solo al emitir sesión)**:
  - `LoginView` estado `ok` → `LOGIN_EXITOSO`.
  - `MFAVerifyView` éxito → `MFA_VERIFICADO` + `LOGIN_EXITOSO`.
  - `MFAConfirmView` éxito → `MFA_ACTIVADO` + `LOGIN_EXITOSO`.
  - `PasswordChangeView` que devuelve estado `ok` → `PASSWORD_CAMBIADA` + `LOGIN_EXITOSO`; si devuelve
    `mfa_required`/`mfa_setup_required`, solo `PASSWORD_CAMBIADA`.
  - `LOGIN_FALLIDO` en los `except` de credenciales/bloqueo; `MFA_RECHAZADO` antes de lanzar 401;
    `LOGOUT` al cerrar sesión.

### A6. Comando `resetear_mfa`
- `apps/autenticacion/management/commands/resetear_mfa.py`:
  - `--email` obligatorio; `CommandError` si el usuario no existe.
  - Borra `DispositivoMFA` (cascade), revoca refresh, audita `MFA_RESETEADO` con
    `usuario=target`, `entidad="Usuario"`, `entidad_id=str(target.pk)`.
  - Solo consola; **no** aplica la guarda de auto-reset (es la salida para el último admin).
  - Salida clara en español; nunca imprime secretos.

### A7. Pruebas Fase A
- Unit (sin DB): password temporal y política; `sanitizar_entidad_id`; `get_client_ip` (REMOTE_ADDR vs
  `X-Forwarded-For` con flag); `cambiar_password_obligatorio` con fakes (token inválido, propósito cruzado,
  inactivo, bloqueado, flag ya False, contraseña igual, débil); `mfa_activo` sin dispositivo.
- Integración (PostgreSQL):
  - Matriz rol × endpoint (401 sin token, 403 Técnico/Usuario Responsable, 200 Admin).
  - `create` devuelve temporal, persiste `debe_cambiar_password=True`, email en minúsculas.
  - Unicidad CI: `A@X.com` luego `a@x.com` → 400 `email_duplicado` (captura de `IntegrityError`).
  - Login `"Ana@X.com"` con `ana@x.com` existente → funciona.
  - Email 300 chars → 400 (nunca 500); con `@` >64 → `entidad_id=""`; sin `@` → `entidad_id=""`.
  - `LOGIN_FALLIDO` y `MFA_RECHAZADO` persisten con respuesta 401/403.
  - `LOGIN_EXITOSO` **no** se registra en paso 1 intermedio; sí en `ok`, verify, confirm y password/change `ok`.
  - Reset password: temporal, limpia bloqueo, revoca refresh (refresh viejo falla).
  - Reset MFA: borra dispositivo y refresca; login pasa a `mfa_setup_required`.
  - Inactivar: `/me` 401 y refresh 401; reactivar funciona.
  - Guardas self y último admin → 400. **Prueba de `FOR UPDATE` sin hilos**:
    `CaptureQueriesContext` sobre la guarda, verificando `FOR UPDATE` y `ORDER BY ... id`.
  - Comando `resetear_mfa --email`: existe → audita/revoca; inexistente → `CommandError`.
  - Flujo completo: admin crea → login temporal → `password_change_required` → cambio →
    `mfa_setup_required` → setup/confirm → `me`; verificar auditoría.
  - `assertNumQueries` en listado (sin N+1).
- Actualizar pruebas T-001 por `ResultadoAutenticacion`.
- `ruff check . && ruff format --check .`; `makemigrations --check --dry-run`.

### A8. Cierre Fase A
- Reporte con plantilla de `WORKFLOW.md` (lint, unit, integración, sistema).
- `git status` / `git diff --stat`; sin `.env`, secretos ni basura.
- Commit propuesto (lo ejecuta el usuario). **STOP**: no iniciar Fase B sin pedido explícito.

## FASE B — Frontend + documentación (solo cuando el usuario lo pida)

### B1. Feature `usuarios`
- `types/index.ts`; `api/usuarios.api.ts` (listar, obtener, crear, actualizar, resetPassword, resetMfa,
  activar, desactivar) con `client` central.
- `schemas/usuario.schema.ts` (Zod): email, nombre_completo, rol; edición sin email.
- `pages/UsuariosListPage.tsx`: `PageHeader` + filtros (rol, estado, búsqueda) + `DataTable` + paginación
  + `LoadingSkeleton`/`EmptyState`/`ErrorState`.
- `pages/UsuarioFormPage.tsx` con `FormSection` + `FormField`.
- `components/TempPasswordModal.tsx`: la temporal vive **solo** en `useState` del modal y se limpia al
  cerrar; nunca en `queryClient.setQueryData` ni logs. Botón copiar y aviso de mostrada una vez.
- `components/ConfirmResetMfaDialog.tsx` con `ConfirmDialog`.
- Crear en `shared/` y registrar en CODEMAP: `DataTable`, `ConfirmDialog` (y `FilterBar`/`Toast` si se usan).

### B2. Mutaciones con contraseña temporal (ajuste del usuario)
- En las mutaciones que devuelven temporal: `gcTime: 0` (TanStack Query v5), copiar la temporal al estado
  del modal en `onSuccess` y llamar a `reset()` de la mutación. Sin caché persistente.
- Los endpoints de crear/reset devuelven `Cache-Control: no-store`.

### B3. Rutas y guardia por rol
- `Router.tsx`: `/usuarios`, `/usuarios/nuevo`, `/usuarios/:id/editar` con `roles={['ADMINISTRADOR']}`.
- `ProtectedRoute.tsx`: `roles?: UserRole[]`; sin rol → `/dashboard` (o 404). El backend manda.

### B4. Flujo de cambio obligatorio
- `auth.api.ts`: `changePassword(...)`; `AuthStep += 'password_change'`.
- `LoginPage.tsx`: manejar `password_change_required` y renderizar `PasswordChangeStep`
  (nueva/confirmar, Zod, errores backend); al éxito continuar a MFA/dashboard.

### B5. Pruebas frontend
- Schemas (usuario, cambio de contraseña), `TempPasswordModal`, `UsuariosListPage` con MSW
  (carga/vacío/error/acciones por rol). Ajustar pruebas de auth por `AuthStep`.

### B6. Documentación de cierre Fase B
- `docs/agent/tasks/T-002-usuarios.md`; `STATE.md`; `CODEMAP.md`; `DATA_MODEL.md` sección C;
  `DECISIONS.md`:
  - ADR-012: temporal + cambio obligatorio; **tras inactivar el access token se rechaza de inmediato**;
    tras reset de contraseña/MFA puede vivir hasta 15 min (refresh revocado).
  - ADR-013: app `auditoria` dedicada y semántica de eventos.
  - ADR-014: **el admin de Django no pasa por MFA**; deshabilitar o restringir en producción.
- Commit propuesto de la fase.

## Validación global
- Backend: `pytest -m unit` · `pytest -m "not system"` · `ruff check . && ruff format --check .` ·
  `makemigrations --check --dry-run`.
- Frontend: `npm run lint && npm run typecheck && npm run test`.
- Manual: admin crea usuario → login fuerza cambio → MFA → dashboard; resets; auditoría solo lectura.
- Reportar “NO EJECUTADO” con el comando exacto cuando falte entorno.

## Riesgos y casos límite
1. Árbol git sucio bloquea A0; el agente no escribe en git.
2. `DATA_MODEL` global PENDIENTE: solo se aprueban las dos filas indicadas.
3. Último admin: `select_for_update()` + `order_by("pk")` dentro de atomic; prueba con
   `CaptureQueriesContext`, sin hilos.
4. Self-reset (password/MFA/rol) y autodesactivación bloqueados.
5. Temporal: una sola vez, sin logs, `no-store`, `gcTime: 0`, estado del modal y `reset()`.
6. Orden auth: cambio de contraseña antes de MFA; token 5 min, un solo uso, no repetir la temporal.
7. Revocación cubre refresh; access tokens ≤15 min (excepto inactivo, rechazo inmediato).
8. `X-Forwarded-For` solo con `TRUST_X_FORWARDED_FOR=True`; por defecto `REMOTE_ADDR`.
9. Email: normalización + data migration (aborta en colisión) + `UniqueConstraint Lower`; `IntegrityError` → 400.
10. `entidad_id` sanitizado (contiene `@` y ≤64) evita 500 y registros accidentales.
11. `LOGIN_EXITOSO` solo al emitir sesión; evita falsos positivos en pasos intermedios.

## Fuera de alcance
- Envío de contraseña por correo; UI para visualizar `RegistroAuditoria`; revocación inmediata de access
  tokens tras reset (token version/`password_changed_at`); auditoría de exportaciones (T-011); expiración
  temporal por tiempo.
