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

**Aprobaciones parciales para T-003/T-004 (2026-11-23):** Opción A para `Sede`, `Ubicacion`, `Categoria`, `Marca`, `ModeloActivo` y `Activo` (con `valor_adquisicion` opcional), más `is_active` en los catálogos → **APROBADO**. El resto sigue PENDIENTE.

**Aprobación parcial para T-007 licencias (2026-11-24):** `Proveedor` y `Licencia` (con los campos operativos que reemplazan el Excel de control de licencias) → **APROBADO**. `Software`, `LicenciaActivo` y `Garantia` siguen PENDIENTES (licencias sin asignación a activos y garantías en segunda fase). Ver ADR-019.

| Modelo | Campos clave | Constraints / notas | Estado |
|---|---|---|---|
| Usuario | email (único), nombre_completo, rol, is_active | AbstractUser; rol: TextChoices | APROBADO (T-002) |
| Sede | nombre, direccion | nombre único (CI). Nueva (sale de Ubicacion.sede) | APROBADO (T-003) |
| Ubicacion | sede FK, nombre | único (sede, nombre) CI. is_active | APROBADO (T-003) |
| Categoria | nombre, descripcion | nombre único CI. is_active | APROBADO (T-003) |
| Marca | nombre | único CI. is_active | APROBADO (T-003) |
| ModeloActivo | marca FK, categoria FK, nombre | único (marca, nombre) CI. is_active | APROBADO (T-003) |
| Activo | serial, modelo FK, fecha_adquisicion, valor_adquisicion (opc.), estado, codigo_qr, procesador (opc.), ram_gb (opc.), almacenamiento_gb (opc.), direccion_mac (opc., única si no vacía), observaciones (opc.), is_active | serial y codigo_qr únicos; estado: TextChoices (DISPONIBLE, ASIGNADO, EN_MANTENIMIENTO, DADO_DE_BAJA); sin ubicacion (ubicación efectiva se deriva de la asignación, 3FN) | APROBADO (T-004) |
| AsignacionActivo | activo FK, usuario FK, asignado_por FK, fecha_inicio, fecha_fin (nulo), observacion | único parcial: un activo con una sola asignación abierta (`fecha_fin` nula). El responsable actual se **deriva**, no se guarda en Activo | PENDIENTE |
| MovimientoActivo (Trazabilidad) | activo FK, tipo_movimiento, fecha_movimiento, usuario FK, ubicacion_origen FK, ubicacion_destino FK, observacion | Solo inserción (append-only) | PENDIENTE |
| Mantenimiento | activo FK, tipo (PREVENTIVO/CORRECTIVO), fecha_programada, fecha_realizacion, fecha_seguimiento (opc.), tecnico FK, costo, observacion, motivo_cancelacion, estado (PROGRAMADO/COMPLETADO/CANCELADO), reprogramacion_de (OneToOne self, opc.) | CHECK costo ≥ 0; índices fecha_programada/estado; situación (PENDIENTE/VENCIDO/INCUMPLIDO/COMPLETADO/CANCELADO) **derivada**, no almacenada; INCUMPLIDO = evidencia inmutable. CORRECTIVO = registro directo (evento + seguimiento) que no entra en KPI/calendario preventivo | APROBADO (T-006a) |
| RepuestoMantenimiento | mantenimiento FK, descripcion, cantidad, costo_unitario | CASCADE desde Mantenimiento; CHECK cantidad > 0 | PENDIENTE |
| Incidente | activo FK, reportado_por FK, fecha, descripcion, estado | | PENDIENTE |
| Proveedor | nombre, contacto | nombre único CI. is_active | APROBADO (T-007 licencias) |
| Garantia | activo FK, proveedor FK, fecha_inicio, fecha_fin, condiciones | CHECK fecha_fin > fecha_inicio | PENDIENTE (segunda fase T-007) |
| Software | nombre, fabricante | nombre único. Nueva | PENDIENTE — no se implementa: `Licencia.servicio` guarda el nombre (ADR-019) |
| Licencia | proveedor FK, servicio, periodicidad (MENSUAL/TRIMESTRAL/SEMESTRAL/ANUAL/BIENAL), fecha_renovacion, cantidad, valor (opc.), renovacion_automatica, medio_pago, cuenta_vinculada, responsable_uso, observacion, is_active | CHECK cantidad ≥ 1 y valor ≥ 0 o nulo; estado de renovación (VIGENTE/POR_VENCER/VENCIDA/INACTIVA) **derivado** por selector, no almacenado | APROBADO (T-007 licencias) |
| LicenciaActivo | licencia FK, activo FK, fecha_asignacion | único (licencia, activo); N:M | PENDIENTE (segunda fase T-007) |
| Documento | activo FK, tipo, nombre, archivo (FileField), subido_por FK | validar tipo y tamaño | PENDIENTE |
| Baja | activo (OneToOne), fecha, motivo, autorizado_por FK, documento FK (opc.) | RF014 | PENDIENTE |
| Alerta | tipo, activo FK, destinatario FK (opc.), fecha_evento, mensaje, leida | único (tipo, activo, fecha_evento) para no duplicar | PENDIENTE |
| Reporte | tipo, fecha_generacion, usuario FK, parametros (JSON) | bitácora de reportes generados | PENDIENTE |
| RegistroAuditoria | usuario FK, accion, entidad, entidad_id, fecha, ip | accesos y exportaciones. Cambios de datos: tablas `Historical*` de simple-history | APROBADO (T-002) |

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

### Aprobado para T-003/T-004 (APROBADO 2026-11-23) — pendiente de implementar en Fase A/C

| Modelo | App | Campos/Definición | Notas |
|---|---|---|---|
| `Sede` | catalogos | `nombre` (único CI), `direccion` (texto, blank), `is_active` | Fase A |
| `Ubicacion` | catalogos | `sede` FK PROTECT, `nombre` (único por sede CI), `is_active` | Fase A |
| `Categoria` | catalogos | `nombre` (único CI), `descripcion` (texto, blank), `is_active` | Fase A |
| `Marca` | catalogos | `nombre` (único CI), `is_active` | Fase A |
| `ModeloActivo` | catalogos | `marca` FK PROTECT, `categoria` FK PROTECT, `nombre` (único por marca CI), `is_active` | Fase A |
| `Activo` | activos | `serial` (único CI, normalizado MAYÚSCULAS), `modelo` FK PROTECT, `fecha_adquisicion` (DateField, no futura), `valor_adquisicion` (Decimal 12,2, opcional, ≥0), `estado` (TextChoices, default DISPONIBLE, read-only), `codigo_qr` (único inmutable, AST-AAAA-NNNNNN), `procesador` (texto, opc.), `ram_gb` (int, opc., >0), `almacenamiento_gb` (int, opc., >0), `direccion_mac` (opc., única si no vacía, formato AA:BB:CC:DD:EE:FF), `observaciones` (texto, opc.), `is_active` | Fase C (sin ubicacion; ubicación efectiva derivada en T-005) |

### Aprobado e implementado en T-006a (APROBADO 2026-11-24) — mantenimiento preventivo

| Modelo | App | Campos/Definición | Notas |
|---|---|---|---|
| `Mantenimiento` | mantenimientos | `activo` FK PROTECT, `tipo` (PREVENTIVO/CORRECTIVO, default PREVENTIVO), `fecha_programada` DateField, `fecha_realizacion` DateField nulo, `tecnico` FK Usuario PROTECT nulo, `costo` Decimal 12,2 nulo ≥0, `observacion` texto, `motivo_cancelacion` texto, `estado` (PROGRAMADO/COMPLETADO/CANCELADO), `reprogramacion_de` OneToOne self PROTECT nulo | `situacion` y `es_evidencia` se calculan (estado + fecha + existencia de reprogramación); `HistoricalMantenimiento` (simple-history). Acciones de auditoría `MANTENIMIENTO_*`. Endpoints `/api/v1/mantenimientos/` con `resumen/`, `calendario/`, `tecnicos/`, `completar/`, `reprogramar/`, `cancelar/`, `historial/`. Correctivos y repuestos quedan para otra tarea. |

### Aprobado e implementado en T-007 licencias (APROBADO 2026-11-24)

| Modelo | App | Campos/Definición | Notas |
|---|---|---|---|
| `Proveedor` | licencias_garantias | `nombre` (único CI), `contacto` (opc.), `is_active` | `HistoricalProveedor`. El alta/edición es implícita al guardar una licencia (ADR-019). |
| `Licencia` | licencias_garantias | `proveedor` FK PROTECT, `servicio` (texto), `periodicidad` (TextChoices), `fecha_renovacion` DateField, `cantidad` int ≥1, `valor` Decimal 12,2 nulo ≥0, `renovacion_automatica` bool, `medio_pago`, `cuenta_vinculada`, `responsable_uso`, `observacion`, `is_active` | `HistoricalLicencia`. `dias_para_renovacion` y `estado_renovacion` derivados (hoy + 30 días). Índices por fecha/proveedor. Migración `licencias_garantias/0001`. Endpoints `/api/v1/licencias/` con `resumen/`, `proveedores/`, `renovar/`, `inactivar/`, `reactivar/`; solo ADMINISTRADOR (RF009). Seed `seed_licencias_dev`. |
