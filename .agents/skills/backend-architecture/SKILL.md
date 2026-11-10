---
name: backend-architecture
description: Reglas de arquitectura y buenas prácticas del backend Django/DRF de este proyecto (capas, SOLID, serializers, services, selectors, permisos por rol, errores, paginación, OpenAPI). Úsala SIEMPRE que crees o modifiques código en /backend — modelos, vistas, serializers, servicios, permisos, URLs, filtros, comandos de gestión o integraciones — aunque el usuario no mencione arquitectura ni SOLID.
---

# Backend: arquitectura y buenas prácticas

## Capas y dirección de dependencias
```
urls → views (ViewSet delgado) → serializers (forma de entrada/salida)
                              → services (casos de uso: ESCRIBEN)  → models
                              → selectors (consultas: LEEN)        → models
```
- **views**: autenticación, permisos, llamar a service/selector, devolver respuesta. Cero reglas de negocio.
- **serializers**: validan forma y tipos; no contienen lógica de negocio ni consultas propias.
- **services**: reglas de negocio y escrituras; `transaction.atomic` cuando hay más de una escritura. No conocen `request`/HTTP.
- **selectors**: queries de lectura optimizadas (`select_related`/`prefetch_related`, anotaciones). No escriben.
- **models**: datos + invariantes simples (constraints, `clean`). No llaman servicios externos ni envían correos.
- **integrations/**: adaptadores a lo externo (QR, exportadores PDF/Excel, correo, almacenamiento).

Estructura por app: `models.py · selectors.py · services.py · serializers.py · views.py · filters.py · permissions.py · urls.py · admin.py · tests/{unit,integration}/`

## SOLID aplicado aquí
| Principio | Cómo se cumple en este proyecto |
|---|---|
| **S** Responsabilidad única | Una función = un caso de uso (`asignar_responsable`, `dar_de_baja`). Una app = un contexto del negocio. Vistas, services y selectors no se mezclan. |
| **O** Abierto/cerrado | Exportadores de reportes (PDF, Excel, futuros) como estrategias registradas: agregar un formato no modifica código existente. Igual para tipos de alerta. |
| **L** Sustitución de Liskov | Si hay varias implementaciones de un contrato (`ReportExporter`), cualquiera debe poder usarse sin romper al consumidor. Preferir composición a herencia. |
| **I** Segregación de interfaces | Contratos pequeños con `typing.Protocol`: `QRGenerator`, `Notifier`, `FileStorage`, `ReportExporter`. Nada de "interfaz gigante". |
| **D** Inversión de dependencias | Los services reciben lo externo por parámetro o constructor (con valor por defecto). Así se prueban con fakes, sin red ni disco. |

## Reglas de código
- Nunca `fields = "__all__"`. Serializers de lectura y de escritura separados cuando difieren.
- Cada view declara `permission_classes` por rol. `AllowAny` solo en login y health.
- API versionada `/api/v1/`. Recursos en plural y en español acorde al dominio (`/activos/`, `/mantenimientos/`).
- Paginación siempre en listados; filtros con `django-filter` en `filters.py`; ordenamiento explícito.
- Errores uniformes `{"detail", "code", "errors"}` vía manejador de excepciones en `common`. Excepciones de dominio propias (`ReglaDeNegocioError`) que el handler traduce a 400/409/422.
- Evitar N+1: toda lista usa `select_related/prefetch_related` en el selector; verificar con `assertNumQueries` en endpoints críticos.
- Validar archivos subidos (extensión, tipo MIME, tamaño). No servir `media` sin control de acceso en producción.
- Contraseñas con el hasher de Django. Sin secretos en código. `DEBUG=False` por defecto fuera de dev.
- `logging`, no `print`. Type hints en funciones públicas. Funciones cortas (~30 líneas) con nombres que digan lo que hacen.
- DRY sin abstracciones prematuras: abstraer cuando hay 3 usos reales.
- Auditoría: modelos de negocio con `HistoricalRecords()` (simple-history); accesos/exportaciones en `RegistroAuditoria`.
- Documentar cada endpoint con `@extend_schema` (OpenAPI).

## Checklist antes de dar un endpoint por terminado
- [ ] Permisos por rol probados (matriz rol × acción) · [ ] paginación y filtros · [ ] lógica en service/selector, no en la view
- [ ] pruebas unit del service + integration del endpoint · [ ] migración revisada · [ ] OpenAPI · [ ] CODEMAP y DATA_MODEL actualizados

## Anti-patrones (no hacer)
Lógica en views/serializers/señales · consultas dentro de loops · `save()` sobrescrito con efectos externos · estados como strings sueltos (usar `TextChoices`) ·
`except Exception: pass` · migraciones editadas a mano sin revisar · imports dentro de funciones para esquivar acoplamientos.
