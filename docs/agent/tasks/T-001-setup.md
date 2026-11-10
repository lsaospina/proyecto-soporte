# T-001 — Configuración del entorno

Solo esqueleto y entorno. **Sin modelos ni lógica de negocio.** Antes de escribir código, muestra un plan de archivos
(máx. 15 líneas) y espera confirmación del usuario.

## Backend (`/backend`)
- Python 3.12, Django (última LTS), DRF, PostgreSQL con psycopg 3. Versiones fijadas en `requirements/base.txt` y `dev.txt`.
- Paquetes: ver stack en PROJECT_CONTEXT.md (los necesarios para esta tarea; el resto se instala cuando se use).
- Proyecto `config` con settings divididos (base/dev/prod) leyendo `.env` con django-environ. `TIME_ZONE=America/Bogota`, `USE_TZ=True`, `LANGUAGE_CODE=es-co`.
- Apps: `common` (permisos por rol, manejador de excepciones, modelo base con `created_at/updated_at`) y `usuarios`.
- Usuario personalizado en `usuarios` (AbstractUser, login por correo, `rol` con TextChoices ADMINISTRADOR / TECNICO / USUARIO_RESPONSABLE).
  Configurar `AUTH_USER_MODEL` **antes** de la primera migración.
- Permisos DRF por rol en `apps/common/permissions.py`.
- Defaults DRF: JWT, IsAuthenticated, paginación 20, DjangoFilterBackend, esquema drf-spectacular, manejador de errores uniforme.
- Endpoints en `/api/v1/`: `auth/login`, `auth/refresh`, `auth/me`, `health` (público). Docs en `/api/docs/` y `/api/schema/`.
- CORS para el front en desarrollo. Configuración de pytest con marcadores `unit`, `integration`, `system` (ver skill testing-strategy).

## Frontend (`/frontend`)
- Vite + React + TypeScript, Tailwind + shadcn/ui, React Router, TanStack Query, axios, React Hook Form + Zod, lucide-react.
- Estructura `src/`: `api/`, `features/`, `components/{ui,shared}`, `routes/`, `lib/`, `styles/`.
- Tokens de diseño en `src/styles/tokens.css` y tema Tailwind según skill `frontend-design-system`.
- Componentes compartidos mínimos: `AppShell`, `PageHeader`, `FormField`, `FormSection`, `StatusBadge`, `EmptyState`.
- Cliente axios con interceptor: adjunta JWT y renueva con refresh.
- Login funcional (`/api/v1/auth/login`), ruta protegida, layout con sidebar cuyo menú depende del rol (ítems placeholder).
- Proxy de Vite hacia el backend. Vitest + Testing Library + MSW configurados. Playwright instalado pero sin tests aún.

## Infraestructura
- `docker-compose.yml`: `db` (postgres 16 con volumen), `backend`, `frontend`, con hot reload.
- `.env.example` con todas las variables. El `.gitignore` ya existe (no sobrescribir; ampliar solo si hace falta).
- `README.md` con pasos para levantar y correr pruebas. Actualizar la sección "Comandos" de `AGENTS.md` con los comandos reales.
- Rellenar `CODEMAP.md`.

## Criterios de aceptación
1. `docker compose up` levanta db, backend y frontend sin errores.
2. Migraciones corren; se puede crear superusuario.
3. Login desde el front y se ve el rol del usuario.
4. `/api/docs/` muestra los endpoints de auth.
5. `ruff`, `pytest -m unit`, `npm run lint`, `npm run typecheck` y `npm run test` corren y pasan (con al menos un test real en cada lado).
6. Cierre según `WORKFLOW.md` (reporte + commit propuesto, sin ejecutar git de escritura).
