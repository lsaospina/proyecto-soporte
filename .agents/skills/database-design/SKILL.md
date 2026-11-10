---
name: database-design
description: Reglas de diseño de base de datos para este proyecto (PostgreSQL + Django ORM) — normalización hasta 3FN, constraints, naming, tipos, índices, migraciones y cómo cambiar el esquema. Úsala SIEMPRE que crees o modifiques modelos, campos, relaciones, constraints o migraciones, o cuando se hable de tablas, MER, diccionario de datos o normalización.
---

# Diseño de base de datos

Fuente de verdad del esquema: `docs/agent/DATA_MODEL.md`. Léelo antes de tocar modelos.

## Proceso para cambiar el esquema
1. Revisa `DATA_MODEL.md`. Si el cambio se desvía del MER, debe estar APROBADO; si no, pregunta al usuario.
2. Actualiza `DATA_MODEL.md` (sección C: modelo implementado).
3. Modelos + constraints → `makemigrations` con nombre descriptivo → revisa el SQL con `sqlmigrate`.
4. Pruebas de integración de constraints (la BD debe rechazar lo inválido).
5. Si cambia algo del diccionario de datos del documento académico, avísalo en el reporte final.

## Normalización (obligatorio hasta 3FN)
- **1FN**: valores atómicos; nada de listas/CSV/JSON para datos consultables; sin columnas repetidas (`telefono1`, `telefono2`).
- **2FN**: en claves compuestas o N:M (p. ej. `LicenciaActivo`), cada atributo depende de toda la clave.
- **3FN**: ningún atributo depende de otro no-clave. Ejemplos: `sede` va en su tabla, no repetida en Ubicacion; la categoría depende del modelo, no del activo.
- **Datos derivados no se almacenan** (vigencia de licencia, días para vencer, responsable actual si se deduce de asignaciones). Se calculan en selectors.
- Denormalizar solo con justificación escrita en `DECISIONS.md` (rendimiento medido, no supuesto).
- Pregunta de control por cada campo nuevo: ¿depende solo de la clave de ESTA tabla? Si no, va en otra.

## Catálogos: ¿tabla o `TextChoices`?
- Valores fijos por código/negocio y sin atributos propios (estados, tipos de mantenimiento) → `TextChoices` + `CheckConstraint`.
- Valores administrados por el usuario o con atributos (Categoria, Marca, Proveedor, Sede) → tabla.

## Integridad
- PK sustituta `id`. Unicidad con `UniqueConstraint` (serial, codigo_qr, nombres de catálogos). Reglas con `CheckConstraint` (`fecha_fin > fecha_inicio`, `costo >= 0`).
- "Uno solo abierto" con restricción única parcial (`condition=Q(fecha_fin__isnull=True)`).
- `on_delete`: `PROTECT` por defecto (catálogos e históricos); `CASCADE` solo en hijos puros (RepuestoMantenimiento). Nunca borrar activos: inactivar o registrar Baja.
- `null=False` por defecto. Strings vacíos con `blank=True, default=""`, no `null=True`. `blank` ≠ `null`.
- FKs con `related_name` explícito en plural. Historial y trazabilidad: solo inserción.

## Tipos y nombres
- Dinero `DecimalField(max_digits=12, decimal_places=2)`, nunca float. Fechas de negocio `DateField`; eventos `DateTimeField` con zona horaria.
- Modelos en español PascalCase singular; campos snake_case; FK sin sufijo `_id` en el nombre del campo. Valores de estado en MAYÚSCULAS_CON_GUION_BAJO.
- Índices en columnas de filtro/búsqueda frecuente (estado, fecha_vencimiento, serial). Las FKs ya se indexan. Compuestos solo con consulta real que los justifique.

## Migraciones
- Una migración por cambio lógico, con nombre claro. Reversibles cuando sea posible.
- No editar migraciones ya compartidas/aplicadas; crear una nueva.
- Datos iniciales (roles, catálogos base) con comando `seed` idempotente o data migration.
- `python manage.py makemigrations --check --dry-run` debe pasar al cerrar la tarea.
