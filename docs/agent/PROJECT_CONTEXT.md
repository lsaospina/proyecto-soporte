# PROJECT_CONTEXT — resumen del proyecto (reemplaza releer el .docx)

Fuente completa: `docs/Proyecto_Ing_Software.docx`. Mockups: `docs/design/mockups/`.

## Qué es
Sistema web para gestionar inventario y activos tecnológicos de una empresa: equipos, responsables,
mantenimientos, incidentes, licencias, garantías, documentos, bajas, trazabilidad (QR), alertas,
dashboard y reportes. Proyecto académico (Ingeniería de Software II, Politécnico Grancolombiano), 2 desarrolladores.

## Roles
Administrador · Técnico · Usuario Responsable (campo `rol` del usuario; permisos por rol en backend, la UI solo oculta).

## Requisitos funcionales (resumen)
| ID | Nombre | Roles | Prio |
|---|---|---|---|
| RF001 | Inicio de sesión | Todos | Alta |
| RF002 | Gestión de usuarios | Admin | Alta |
| RF003 | Registro de activos | Admin, Téc | Alta |
| RF004 | Consulta de inventario (filtros: categoría, ubicación, responsable, estado, fecha) | Admin, Téc | Alta |
| RF005 | Asignación de responsables (con historial) | Admin | Alta |
| RF006 | Mantenimiento preventivo | Admin, Téc | Alta |
| RF007 | Mantenimiento correctivo (fallas, repuestos, costos) | Admin, Téc | Alta |
| RF008 | Gestión de incidentes | Téc, Usuario Resp. | Alta |
| RF009 | Control de licencias | Admin | Media |
| RF010 | Gestión de garantías | Admin | Media |
| RF011 | Código QR único por activo | Admin, Téc | Alta |
| RF012 | Trazabilidad (movimientos, ubicación, responsables) | Admin, Téc | Alta |
| RF013 | Gestión documental (facturas, manuales, evidencias) | Admin, Téc | Media |
| RF014 | Gestión de bajas (fecha, motivo, soporte) | Admin | Media |
| RF015 | Alertas (vencimientos, mantenimientos, actualizaciones) | Admin, Téc | Alta |
| RF016 | Dashboard gerencial | Admin | Media |
| RF017 | Reportes PDF y Excel | Admin | Alta |

## Requisitos no funcionales
RNF001 acceso por roles (JWT) · RNF002 disponibilidad 99 % horario laboral · RNF003 respuesta ≤ 3 s ·
RNF004 backup diario de BD · RNF005 usabilidad · RNF006 escalabilidad · RNF007 navegadores modernos ·
RNF008 auditoría de todas las acciones · RNF009 integridad (validar, evitar duplicados) · RNF010 arquitectura modular.

## Casos de uso → módulos
CU001 Acceso (RF001) · CU002 Usuarios (RF002) · CU003 Activos (RF003-005, 011, 012) ·
CU004 Mantenimientos e incidentes (RF006-008) · CU005 Licencias, garantías, documentos (RF009, 010, 013) ·
CU006 Gerencial (RF016, 017). Transversales: RF014 bajas, RF015 alertas, RNF008 auditoría.

## Stack (fijar versiones estables al crear el proyecto)
| Capa | Tecnología |
|---|---|
| BD | PostgreSQL 16 |
| Backend | Python 3.12, Django (LTS), Django REST Framework, SimpleJWT, django-filter, drf-spectacular, django-cors-headers, django-environ, django-simple-history, Pillow, qrcode, openpyxl, reportlab |
| Calidad back | pytest-django, factory_boy, ruff |
| Frontend | React + Vite + TypeScript, Tailwind CSS + shadcn/ui, React Router, TanStack Query, axios, React Hook Form + Zod, Recharts, lucide-react |
| Calidad front | Vitest + Testing Library + MSW, Playwright (sistema), ESLint + Prettier |
| Infra | Docker Compose (db, backend, frontend) |

## Estructura del repo (objetivo)
```
backend/  config/ · apps/{common,usuarios,activos,mantenimientos,licencias_garantias,documentos,alertas,reportes}/ · requirements/
frontend/ src/{api,features,components/{ui,shared},routes,lib,styles}
docs/     agent/ · design/mockups/ · Proyecto_Ing_Software.docx
```

## Fuera de alcance (aparece en mockups pero NO en los requisitos)
MFA, SNMP/CMDB en vivo, selector multi-tenant, LDAP/AD, curvas de depreciación, presupuestos, impresión Zebra/Dymo.
Los mockups son referencia **visual y de layout**, no de funcionalidad. El alcance lo definen los RF.
