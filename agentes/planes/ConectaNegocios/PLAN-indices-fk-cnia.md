# PLAN MAESTRO AUTÓNOMO: Crear índices faltantes en llaves foráneas de [CNIA]

- **Empresa:** Conecta Software Oficina
- **Proyecto:** `ConectaNegocios`
- **Agente Autor:** `agente-conectanegocios` (Ing. Negocios) + Validación de `agente-estratega-ia`
- **Categoría / Severidad:** `SQL_TUNING` / `ALTA`
- **Fecha de Detección:** `2026-11-26 10:16`

## 1. Diagnóstico Ejecutivo para el Patrón
Columnas Foreign Key sin índice detectadas (CategoriaCatalogo.iIdNegocio, ConfiguracionVisual.iIdNegocio, Negocio.iIdCatalogoNegocio). Crear índices no agrupados acelerará JOINs y evitará bloqueos.

## 2. Propuesta de Elevación Profesional (`agente-estratega-ia`)
- **Cero impacto disruptivo:** Se ejecuta en rama `git worktree` aislada siguiendo estrictamente `PlantillaPWA` y `Regla-MetodologiaEngrama`.
- **Seguridad BD:** Cualquier ajuste SQL se entrega como archivo `.sql` idempotente en `D:\Proyectos\agentes\scripts-sql-pendientes\` sin ejecutar escrituras automáticas.

## 3. Plan de Acción Técnico
Generar script idempotente `CREATE NONCLUSTERED INDEX` para `CategoriaCatalogo.iIdNegocio, ConfiguracionVisual.iIdNegocio, Negocio.iIdCatalogoNegocio` en `scripts-sql-pendientes/ConectaNegocios/`.

## 4. Verificación Automatizada
- Compilación limpia `dotnet build` (`0 errores`).
- Validación de no regresión en suite `Test Proyecto`.
