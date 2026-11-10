# DECISIONS — decisiones de arquitectura (ADR breve)

> Agregar al final. Formato: ID · fecha · decisión · motivo. No reabrir una decisión sin motivo nuevo.

- **ADR-001 · 2026-11-09 · Stack** Django + DRF + PostgreSQL / React + Vite + TS. Motivo: modelo muy relacional, roles, archivos, reportes; front desacoplado que consume API REST.
- **ADR-002 · Monorepo** `backend/` y `frontend/` en un solo repo. Motivo: 2 desarrolladores, cambios coordinados front/back.
- **ADR-003 · Arquitectura por capas** views → serializers → services/selectors → models. Motivo: SOLID, RNF010 (modularidad), pruebas unitarias sin DB.
- **ADR-004 · Autenticación** JWT (SimpleJWT) + permisos por rol en backend. Motivo: RNF001, SPA desacoplada.
- **ADR-005 · Auditoría** `django-simple-history` para cambios de datos + tabla de eventos de acceso/exportación. Motivo: RNF008.
- **ADR-006 · Alertas** comando de gestión diario (cron) al inicio; Celery solo si se necesita. Motivo: simplicidad.
- **ADR-007 · Agente sin escritura en git** El agente no hace add/commit/push; propone el commit. Motivo: control del historial por el usuario.
- **ADR-008 · Pruebas en 3 niveles** unit / integration / system con marcadores. Motivo: las de sistema no siempre se pueden ejecutar.
- **ADR-009 · Nombres de dominio en español** igual que el diccionario de datos; campos en snake_case. Motivo: trazabilidad con el MER en la sustentación.
- **ADR-010 · 2026-11-09 · Sin Docker** Stack ejecutado local: PostgreSQL 18 instalado, Python 3.13.13 con venv, Node v24.15.0 LTS. Motivo: preferencia explícita del usuario (T-001 revisada).
- **ADR-011 · 2026-11-09 · MFA con TOTP** pyotp (6 dígitos, 30s, ventana ±1 paso). Secreto guardado cifrado con Fernet (`cryptography`). Códigos de recuperación (10) hasheados con el hasher de Django. mfa_token: `TimestampSigner` de Django (5 min, propósito validado). Access token en body; refresh en cookie HttpOnly SameSite=Lax. Motivo: seguridad según T-001 revisada.
