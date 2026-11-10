---
name: testing-strategy
description: Estrategia de pruebas del proyecto (unitarias, integración y sistema/E2E) para backend pytest-django y frontend Vitest/Playwright, con reglas para ejecutar solo lo que el entorno permite y reportar con honestidad. Úsala SIEMPRE que escribas, ejecutes o reportes pruebas, y al cerrar cualquier tarea de código, aunque el usuario no pida pruebas explícitamente.
---

# Estrategia de pruebas

## Niveles
| Nivel | Qué prueba | Requiere | Cuándo se ejecuta |
|---|---|---|---|
| **unit** | Lógica pura: services (con fakes), selectors sin DB cuando se pueda, validadores, utilidades, esquemas Zod, helpers, componentes aislados | Nada externo (sin DB, sin red, sin Docker) | **Siempre**, en cada tarea |
| **integration** | Modelos y constraints reales, endpoints con `APIClient`, permisos por rol, comandos de gestión | PostgreSQL de pruebas (`docker compose up -d db`) | Al cerrar tarea si hay DB disponible |
| **system** | Stack completo levantado: flujos extremo a extremo (login → crear activo → mantenimiento → reporte) | Docker Compose completo, navegador (Playwright) | Solo si el usuario lo pide o el entorno lo permite (p. ej. T-012) |

El mínimo obligatorio en toda tarea es **lint + unit**. Si no hay entorno para integration/system, NO se omiten en silencio:
se reportan como "NO EJECUTADAS" con el motivo y el comando exacto para correrlas (ver plantilla en WORKFLOW.md).

## Backend (pytest + pytest-django + factory_boy)
- Ubicación: `apps/<app>/tests/unit/`, `apps/<app>/tests/integration/`, `backend/tests/system/`.
- Marcadores `unit`, `integration`, `system` declarados en `pytest.ini` (`--strict-markers`). Un `conftest.py` los asigna **automáticamente por carpeta** para que no se olviden.
- `addopts` por defecto excluye system: `-m "not system"`. Comandos: `pytest -m unit` · `pytest -m "not system"` · `pytest -m system`.
- Datos con `factory_boy` (no fixtures JSON). Reloj inyectable (o `freezegun`) para vencimientos y alertas. Archivos con `tmp_path`.

## Frontend (Vitest + Testing Library + MSW + Playwright)
- Unit/componente: `*.test.ts(x)` junto al código. API simulada con MSW. Playwright en `frontend/e2e/` (= system).
- Probar: esquemas Zod, formateadores, `StatusBadge`/`DataTable`/`FormField`, validación y envío de cada formulario, visibilidad de menú por rol.

## Qué probar (mínimos por módulo)
1. Reglas de negocio en services: caso feliz + cada regla que rechaza (serial duplicado, activo dado de baja no se asigna, `fecha_fin > fecha_inicio`).
2. Permisos: matriz rol × endpoint (403 donde corresponda, 401 sin token).
3. Constraints de BD (integration): unicidad, checks, único parcial.
4. Serializers: validación de entrada/salida. Selectors: filtros y N+1 (`assertNumQueries` en listados críticos).
5. Comando de alertas, exportadores PDF/Excel (contenido básico), generación de QR (valor único y estable).

## Estilo
- Patrón Arrange-Act-Assert; un comportamiento por test. Nombre: `test_<unidad>_<escenario>_<resultado>`.
- Deterministas: sin `sleep`, sin depender del orden ni de datos externos. Cada test crea lo que necesita.
- Un bug corregido empieza con un test que lo reproduce. Cobertura orientativa: services/selectors ≥ 85 %; no perseguir 100 %.
- No se modifican ni eliminan pruebas para "hacerlas pasar": si una prueba falla, se arregla el código o se explica por qué la regla cambió.

## Honestidad en el reporte
Reporta exactamente lo ejecutado: comando, cantidad de pruebas y resultado. Nunca declares ✅ lo no ejecutado. Si una prueba falla y no la pudiste resolver, dilo y deja el detalle.
