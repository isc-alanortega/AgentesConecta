# PLAN MAESTRO AUTÓNOMO: Añadir datos estructurados Schema.org (JSON-LD) y telemetría de CTA hacia ConectaNegocios

- **Empresa:** Conecta Software Oficina
- **Proyecto:** `Repo Conecta Negocios Landing`
- **Agente Autor:** `agente-conectalanding` (Esp. Landing CRO) + Validación de `agente-estratega-ia`
- **Categoría / Severidad:** `MEJORA_PRO` / `MEDIA`
- **Fecha de Detección:** `2026-11-26 10:18`

## 1. Diagnóstico Ejecutivo para el Patrón
Mejorar posicionamiento orgánico SEO en ConectaLanding con JSON-LD y atributos data-testid estables.

## 2. Propuesta de Elevación Profesional (`agente-estratega-ia`)
- **Cero impacto disruptivo:** Se ejecuta en rama `git worktree` aislada siguiendo estrictamente `PlantillaPWA` y `Regla-MetodologiaEngrama`.
- **Seguridad BD:** Cualquier ajuste SQL se entrega como archivo `.sql` idempotente en `D:\Proyectos\agentes\scripts-sql-pendientes\` sin ejecutar escrituras automáticas.

## 3. Plan de Acción Técnico
Inyectar bloque `<script type="application/ld+json">` y selectores `data-testid` en CTAs principales.

## 4. Verificación Automatizada
- Compilación limpia `dotnet build` (`0 errores`).
- Validación de no regresión en suite `Test Proyecto`.
