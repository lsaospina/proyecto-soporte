---
name: frontend-design-system
description: Sistema de diseño y reglas del frontend React de este proyecto — estilo sobrio y consistente, tokens de color/tipografía, patrones de página (lista, formulario, detalle, dashboard), formularios, estados y estructura por features. Úsala SIEMPRE que crees o modifiques pantallas, componentes, formularios, tablas, estilos o rutas en /frontend, aunque el usuario solo pida "una pantalla" o "un formulario".
---

# Frontend: diseño sobrio y consistente

Referencia visual: `docs/design/mockups/` (fig. 11–19). Los mockups guían **estilo y layout**, NO el alcance
(MFA, SNMP, multi-tenant, depreciación, etc. están fuera de alcance; ver PROJECT_CONTEXT.md).

## Principios
Sobrio, denso pero legible, predecible. Misma estructura en todas las pantallas del mismo tipo. Sin gradientes, sin sombras fuertes,
sin emojis, sin animaciones más allá de transiciones de ~150 ms. Iconos solo `lucide-react` (16/20 px).

## Tokens (definir en `src/styles/tokens.css` y mapear en el tema de Tailwind; no usar colores sueltos)
| Token | Valor | Uso |
|---|---|---|
| `--sidebar` | `#213145` | Barra lateral |
| `--primary` | `#024DB9` | Botón principal, ítem activo, enlaces |
| `--background` | `#F8F9FF` | Fondo de la app |
| `--surface` | `#FFFFFF` | Tarjetas, tablas, formularios |
| `--border` | `#E2E8F0` | Bordes (1 px) |
| `--text` / `--text-muted` | `#0F172A` / `#475569` | Texto principal / secundario |
| Éxito | texto `#15803D` · fondo `#DCFCE7` | Operativo, vigente |
| Advertencia | `#B45309` · `#FEF3C7` | En mantenimiento, por vencer |
| Peligro | `#B91C1C` · `#FEE2E2` | Crítico, vencido, baja |
| Info | `#1D4ED8` · `#DBEAFE` | En bodega, informativo |
| Neutro | `#334155` · `#F1F5F9` | Sin asignar, inactivo |

Tipografía: Inter. Base 14 px; títulos de página 24/600; secciones 16/600; tabla y etiquetas 13–14.
Espaciado en múltiplos de 4 (preferir 8/16/24). Radio 6 px (controles) y 8 px (tarjetas). Tarjetas planas: borde 1 px, sombra como máximo `sm`.
Los colores semánticos solo para estados, nunca decorativos. Un solo color de acento (`--primary`).

## Estructura de pantalla
- `AppShell`: sidebar (navy) + topbar + contenido con ancho máximo. Menú según rol del usuario (la UI oculta; el backend decide).
- `PageHeader`: migas de pan, título, subtítulo, acciones a la derecha (acción principal = botón primary).

| Tipo de página | Orden fijo |
|---|---|
| **Lista** | PageHeader → (opcional) fila de KPIs → `FilterBar` → `DataTable` → paginación |
| **Formulario** | PageHeader → `FormSection` (tarjetas con título + descripción) → barra de acciones al pie |
| **Detalle** | PageHeader con `StatusBadge` → pestañas (Resumen, Historial, Mantenimientos, Documentos…) |
| **Dashboard** | Fila de `KpiCard` → gráficas (Recharts) en tarjetas con título |
| **Wizard** | Solo el registro de activo (stepper de 4 pasos como en fig. 12) |

## Componentes compartidos (obligatorio reutilizar; viven en `src/components/{ui,shared}`)
`PageHeader · DataTable · FilterBar · FormSection · FormField · StatusBadge · KpiCard · ConfirmDialog · EmptyState · ErrorState · LoadingSkeleton · Toast`.
Antes de crear un componente, revisa si ya existe uno. Si falta uno genérico, créalo en `shared/` (no dentro de la feature) y regístralo en CODEMAP.

## Formularios (idénticos en todo el sistema)
- Etiqueta encima del campo; obligatorios con `*`; texto de ayuda opcional bajo el campo; error en rojo debajo del campo.
- Esquema Zod por formulario en `features/<modulo>/schemas`. Validar al salir del campo y al enviar. Mapear errores 400 del backend a sus campos.
- Acciones al pie, alineadas a la derecha: **Cancelar** (secundario) a la izquierda de **Guardar** (primario). Deshabilitar y mostrar progreso mientras envía.
- Acciones destructivas (inactivar, dar de baja) siempre con `ConfirmDialog`. Éxito → `Toast` + navegar al listado o detalle.
- Selects con búsqueda para FKs grandes (activos, usuarios). Fechas `dd/MM/yyyy`. Moneda COP con `Intl.NumberFormat("es-CO")`.

## Estados de datos
Toda vista con datos remotos maneja: carga (`LoadingSkeleton`), vacío (`EmptyState` con acción sugerida), error (`ErrorState` con "Reintentar").

## Mapa de estados → `StatusBadge`
Operativo/Vigente → éxito · En mantenimiento/Por vencer → advertencia · Crítico/Vencido/Dado de baja → peligro · En bodega/Programado → info · Sin asignar/Inactivo → neutro.

## Texto y accesibilidad
Interfaz en español neutro, sentence case. Botones con verbo ("Registrar activo", "Guardar cambios"). Labels asociados, foco visible,
contraste AA, operable con teclado, `aria-label` en botones solo-icono.

## Estructura de código
`src/features/<modulo>/{api,components,pages,schemas,hooks,types}`. Llamadas HTTP solo en `features/*/api` usando el cliente central
(nunca `fetch`/`axios` dentro de componentes). Query keys centralizadas por feature. Tipos generados desde OpenAPI cuando exista el esquema.
Componentes pequeños, sin lógica de negocio dentro del JSX; lógica en hooks o funciones puras en `lib/`.

## Checklist antes de terminar una pantalla
- [ ] Usa PageHeader y componentes compartidos · [ ] solo tokens (sin hex ni px sueltos) · [ ] estados carga/vacío/error
- [ ] formulario con el patrón estándar · [ ] visible solo con el rol correcto · [ ] pruebas de componente/schema · [ ] CODEMAP actualizado
