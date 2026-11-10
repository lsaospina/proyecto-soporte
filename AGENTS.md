# AGENTS.md — Sistema de Gestión de Inventarios y Activos Tecnológicos

Lee este archivo SIEMPRE primero. Es corto a propósito: no explores todo el repo, usa los índices.

## Inicio de sesión (máximo 3 lecturas)
1. `docs/agent/STATE.md` → qué está hecho, tarea actual, qué sigue.
2. `docs/agent/CODEMAP.md` → dónde está cada cosa (evita buscar/listar el árbol completo).
3. La skill que aplique a la tarea (tabla de abajo). No cargues las demás.

Lee `docs/agent/PROJECT_CONTEXT.md` solo si necesitas roles, requisitos o stack.
Lee `docs/agent/tasks/T-XXX-*.md` solo de la tarea actual.

## Reglas inquebrantables
1. **GIT SOLO LECTURA.** Prohibido `git add`, `commit`, `push`, `merge`, `rebase`, `reset`, `checkout`, `stash`, `tag`, etc.
   Permitido: `git status`, `git diff`, `git log`, `git show`. Al cerrar la tarea propones el commit
   (formato en `docs/agent/WORKFLOW.md`) y el usuario lo ejecuta.
2. **Alcance cerrado.** Haz solo la tarea pedida. Lo demás se anota en STATE.md → "Ideas y deuda", no se implementa.
3. **Pruebas siempre.** Unitarias + lint obligatorios. Si algo no se pudo ejecutar, dilo explícitamente. Ver skill `testing-strategy`.
4. **Documentación viva.** Al cerrar: actualiza STATE.md y CODEMAP.md (y DATA_MODEL.md / DECISIONS.md si cambiaron).
5. **Base de datos.** Cumplir 3FN. No te desvíes del MER salvo que el cambio esté "APROBADO" en DATA_MODEL.md.
6. **UI consistente.** Reutiliza componentes compartidos. Cero estilos ad hoc. Ver skill `frontend-design-system`.
7. **Secretos.** Nunca leas ni escribas `.env`; solo `.env.example`. Nunca hardcodees credenciales.
8. **Ambigüedad.** Si cambia el diseño o el esquema y no está definido, haz UNA pregunta concreta antes de seguir.
9. **Idioma.** Dominio en español (`Activo`, `Mantenimiento`); infraestructura, comentarios y nombres técnicos en inglés;
   textos de interfaz en español.

## Skills (cargar según la tarea)
| Si vas a... | Lee |
|---|---|
| Tocar `/backend` (modelos, vistas, serializers, servicios, permisos) | `.agents/skills/backend-architecture/SKILL.md` |
| Crear/cambiar tablas, constraints o migraciones | `.agents/skills/database-design/SKILL.md` |
| Tocar `/frontend` (pantallas, formularios, componentes) | `.agents/skills/frontend-design-system/SKILL.md` |
| Escribir o ejecutar pruebas | `.agents/skills/testing-strategy/SKILL.md` |
| Cerrar una tarea / proponer commit | `docs/agent/WORKFLOW.md` |

## Comandos (actualizar tras T-001)
```bash
docker compose up -d db                                  # solo base de datos
docker compose up -d                                     # stack completo
cd backend && pytest -m unit                             # unitarias (sin DB)
cd backend && pytest -m "not system"                     # unitarias + integración (requiere DB)
cd backend && ruff check . && ruff format --check .      # lint
cd backend && python manage.py makemigrations --check --dry-run
cd frontend && npm run lint && npm run typecheck && npm run test
# Sistema (solo si el entorno lo permite): pytest -m system  |  npm run e2e
```
