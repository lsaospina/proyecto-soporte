# WORKFLOW — cómo se trabaja cada sesión

## 1. Inicio
Seguir "Inicio de sesión" de `AGENTS.md`. Confirmar en una línea qué tarea vas a hacer y qué archivos tocarás.
Si el usuario te da un prompt corto ("haz T-004"), toda la información está en STATE.md + tasks/.

## 2. Durante la tarea
- Cambios pequeños y verificables. Probar a medida que avanzas (solo las pruebas afectadas).
- Usa CODEMAP.md para ubicar código; busca con `grep` dirigido, no listes el árbol completo.
- Todo lo que descubras fuera de alcance → STATE.md "Ideas y deuda".

## 3. Cierre (obligatorio, en este orden)
1. Lint + typecheck + pruebas según skill `testing-strategy` (mínimo: unitarias).
2. `git status` y `git diff --stat` (solo lectura): verifica que no haya basura, secretos, `.env`, volcados ni archivos ignorables.
3. Actualiza `STATE.md` (hecho / siguiente / sesión), `CODEMAP.md`, y `DATA_MODEL.md` / `DECISIONS.md` si aplica.
4. Entrega el **reporte final** y el **commit propuesto** (abajo). NO ejecutes git de escritura.

## 4. Reporte final (plantilla)
```
## Resultado
<2-4 líneas: qué quedó funcionando>

## Pruebas
| Nivel | Estado | Detalle |
|---|---|---|
| Lint / typecheck | ✅/❌ | comando y resultado |
| Unitarias (unit) | ✅/❌ | N pasaron |
| Integración | ✅/❌/NO EJECUTADAS | motivo (p. ej. no hay Postgres levantado) |
| Sistema (system/e2e) | ✅/❌/NO EJECUTADAS | motivo + comando exacto para correrlas manualmente |

## Notas / riesgos / decisiones que necesito de ti
- ...

## Commit propuesto
<ver formato abajo>
```
Nunca marcar ✅ algo que no se ejecutó.

## 5. Commit propuesto (lo ejecuta el usuario)
Formato Conventional Commits: `tipo(alcance): resumen en español, imperativo, ≤ 72 caracteres`
Tipos: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `build`. Alcance = app o módulo (`activos`, `front-login`, `docker`).
Cuerpo: viñetas con el qué y el por qué. Pie: `Refs: T-00X`.

```bash
git add <lista explícita de rutas; nunca "git add ." sin revisar>
git commit -m "feat(activos): registrar activos con filtros e historial" \
  -m "- Modelo Activo normalizado con constraints de serial y QR
- Servicio de creación con trazabilidad inicial
- Pantalla de listado con filtros reutilizando DataTable" \
  -m "Refs: T-004"
# git push  ← lo haces tú cuando revises
```
Si la tarea es grande, propón 2-3 commits ordenados (p. ej. `build`/`feat backend`/`feat frontend`/`docs`), pero todos los ejecuta el usuario.

## 6. Ahorro de contexto
- No pegues archivos completos en tus respuestas; resume y cita rutas/líneas.
- No releas `PROJECT_CONTEXT.md` ni el `.docx` si ya tienes lo necesario en STATE/CODEMAP.
- Si una sesión se alarga, deja STATE.md actualizado antes de que se corte: es el traspaso a la siguiente sesión.
