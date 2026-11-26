# PLAN MAESTRO AUTÓNOMO: Incorporar suites Playwright para GeoConecta y Conecta Software Oficina en e2e-admin

- **Empresa:** Conecta Software Oficina
- **Proyecto:** `Test Proyecto`
- **Agente Autor:** `agente-qa-e2e` (Inspector QA E2E) + Validación de `agente-estratega-ia`
- **Categoría / Severidad:** `MEJORA_PRO` / `ALTA`
- **Fecha de Detección:** `2026-11-26 10:19`

## 1. Diagnóstico Ejecutivo para el Patrón
Ampliar el catálogo de pruebas automatizadas E2E para cubrir GeoConecta y Conecta Software Oficina.

## 2. Propuesta de Elevación Profesional (`agente-estratega-ia`)
- **Cero impacto disruptivo:** Se ejecuta en rama `git worktree` aislada siguiendo estrictamente `PlantillaPWA` y `Regla-MetodologiaEngrama`.
- **Seguridad BD:** Cualquier ajuste SQL se entrega como archivo `.sql` idempotente en `D:\Proyectos\agentes\scripts-sql-pendientes\` sin ejecutar escrituras automáticas.

## 3. Plan de Acción Técnico
Registrar `geoconecta` y `oficina-ia` en `EnvironmentConfigService.cs` de `e2e-admin` y crear specs de humo.

## 4. Verificación Automatizada
- Compilación limpia `dotnet build` (`0 errores`).
- Validación de no regresión en suite `Test Proyecto`.
