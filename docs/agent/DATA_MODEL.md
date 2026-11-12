# DATA_MODEL — esquema de base de datos (fuente de verdad para el agente)

> Reglas: 3FN, constraints en BD, ver skill `database-design`.
> El agente NO implementa ninguna fila marcada PENDIENTE. Solo el usuario cambia el estado a APROBADO.
> Al implementar/cambiar un modelo, el agente actualiza este archivo.

## Convenciones
- Modelos en español PascalCase singular (como el diccionario de datos). Campos en snake_case (`fechaAdquisicion` → `fecha_adquisicion`).
- PK `id` (BigAutoField). Todos heredan `created_at`, `updated_at` (modelo base abstracto en `common`).
- Dinero: `DecimalField(12, 2)`. Fechas de negocio: `DateField`. Eventos: `DateTimeField` con zona horaria.
- Sin borrado físico de entidades de negocio: se inactivan (`is_active`) o se registra Baja.

## A. Baseline (MER entregado en el documento)
Usuario · Categoria · Ubicacion(nombre, sede) · ActivoTecnologico(serial, marca, modelo, fechaAdquisicion, estado, codigoQR, FK usuario/categoria/ubicacion) ·
Reporte · Mantenimiento · Incidente · Licencia · Garantia · Documento · Trazabilidad.

Problemas frente a 3FN y a los requisitos: `sede` se repite como texto en Ubicacion; `marca`/`modelo` son texto repetido y
`categoria` depende del modelo (dependencia transitiva); `proveedor` y `software` repetidos como texto; `Licencia.estado` es dato
derivado de `fechaVencimiento`; el responsable actual en Activo duplica lo que dice el historial (RF005); Trazabilidad no registra
quién ni desde/hacia dónde; faltan Baja (RF014), repuestos (RF007), Alerta (RF015) y eventos de auditoría (RNF008).

## B. Propuesta normalizada v0 — ESTADO GLOBAL: PENDIENTE DE APROBACIÓN
Opción A (recomendada, 3FN estricta). Opción B = mantener marca/modelo/categoría como en el MER (denormalización consciente).
Elección del usuario: `[ ] A   [ ] B   [ ] A con ajustes: ________`

**Aprobaciones parciales para T-002 (2026-11-12):** `RegistroAuditoria` y `Usuario.debe_cambiar_password` → **APROBADO** (solo estas filas/columnas para T-002). El resto del modelo propuesto sigue PENDIENTE.

| Modelo | Campos clave | Constraints / notas |
|---|---|---|
| Usuario | email (único), nombre_completo, rol, is_active | AbstractUser; rol: TextChoices |
| Sede | nombre, direccion | nombre único. **Nueva** (sale de Ubicacion.sede) |
| Ubicacion | sede FK, nombre | único (sede, nombre) |
| Categoria | nombre, descripcion | nombre único |
| Marca | nombre | único. **Nueva** |
| ModeloActivo | marca FK, categoria FK, nombre | único (marca, nombre). **Nueva**; la categoría depende del modelo |
| Activo | serial, modelo FK, fecha_adquisicion, valor_adquisicion (opc.), estado, codigo_qr, ubicacion FK, is_active | serial y codigo_qr únicos; estado: TextChoices (DISPONIBLE, ASIGNADO, EN_MANTENIMIENTO, DADO_DE_BAJA) |
| AsignacionActivo | activo FK, usuario FK, asignado_por FK, fecha_inicio, fecha_fin (nulo), observacion | único parcial: un activo con una sola asignación abierta (`fecha_fin` nula). El responsable actual se **deriva**, no se guarda en Activo |
| MovimientoActivo (Trazabilidad) | activo FK, tipo_movimiento, fecha_movimiento, usuario FK, ubicacion_origen FK, ubicacion_destino FK, observacion | Solo inserción (append-only) |
| Mantenimiento | activo FK, tipo (PREVENTIVO/CORRECTIVO), estado, fecha_programada, fecha_realizacion, tecnico FK, costo, observacion, incidente FK (opc.) | CHECK costo ≥ 0 |
| RepuestoMantenimiento | mantenimiento FK, descripcion, cantidad, costo_unitario | CASCADE desde Mantenimiento; CHECK cantidad > 0 |
| Incidente | activo FK, reportado_por FK, fecha, descripcion, estado | |
| Proveedor | nombre, contacto | nombre único. **Nueva** |
| Garantia | activo FK, proveedor FK, fecha_inicio, fecha_fin, condiciones | CHECK fecha_fin > fecha_inicio |
| Software | nombre, fabricante | nombre único. **Nueva** |
| Licencia | software FK, proveedor FK (opc.), fecha_vencimiento, cantidad_equipos | Estado vigente/vencida **derivado** por selector, no almacenado |
| LicenciaActivo | licencia FK, activo FK, fecha_asignacion | único (licencia, activo); N:M |
| Documento | activo FK, tipo, nombre, archivo (FileField), subido_por FK | validar tipo y tamaño |
| Baja | activo (OneToOne), fecha, motivo, autorizado_por FK, documento FK (opc.) | RF014 |
| Alerta | tipo, activo FK, destinatario FK (opc.), fecha_evento, mensaje, leida | único (tipo, activo, fecha_evento) para no duplicar |
| Reporte | tipo, fecha_generacion, usuario FK, parametros (JSON) | bitácora de reportes generados |
| RegistroAuditoria | usuario FK, accion, entidad, entidad_id, fecha, ip | accesos y exportaciones. Cambios de datos: tablas `Historical*` de simple-history |

## C. Modelo implementado (el agente completa esta sección)

### Implementado en T-001 (apps: usuarios, autenticacion)

| Modelo | App | Campos | Notas |
|---|---|---|---|
| `Usuario` | usuarios | `email` (unique), `nombre_completo`, `rol` (TextChoices: ADMINISTRADOR/TECNICO/USUARIO_RESPONSABLE), `is_active`, `intentos_fallidos` (int, default 0), `bloqueado_hasta` (DateTimeField nulo) | Hereda `AbstractUser`; `username` desactivado; `BaseModel` (created_at/updated_at) |
| `DispositivoMFA` | autenticacion | `usuario` (OneToOne → Usuario), `secreto_cifrado` (texto, Fernet), `confirmado` (bool), `ultimo_paso_usado` (int nulo), `created_at`/`updated_at` | Secreto NUNCA en claro; `ultimo_paso_usado` evita reúso de código TOTP |
| `CodigoRecuperacion` | autenticacion | `dispositivo` (FK → DispositivoMFA), `codigo_hash` (texto, hasher Django), `usado_en` (DateTimeField nulo), `created_at` | 10 por dispositivo; de un solo uso; código en claro mostrado solo al crear |

### Aprobado e implementado en T-002 (APROBADO 2026-11-12)

| Modelo/Campo | App | Campos/Definición | Notas |
|---|---|---|---|
| `Usuario.debe_cambiar_password` | usuarios | `BooleanField(default=False)` | Fuerza cambio obligatorio tras creación/reset admin. Migración `usuarios/0002`. |
| `Usuario.email` (unicidad CI) | usuarios | `UniqueConstraint(Lower("email"), name="usuario_email_ci_unico")` + normalización strip/lower | Migraciones `0003` (data, aborta en colisión) y `0004`. |
| `RegistroAuditoria` | auditoria | `usuario` FK null SET_NULL, `accion` CharField(40) choices, `entidad` CharField(50,''), `entidad_id` CharField(64,''), `fecha` DateTimeField(auto_now_add), `ip` GenericIPAddressField null | Sin JSON (3FN). Índices fecha/accion/usuario. Solo lectura en admin. Migración `auditoria/0001`. |
