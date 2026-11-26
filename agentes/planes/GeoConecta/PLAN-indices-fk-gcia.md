# PLAN MAESTRO AUTÓNOMO: Crear índices faltantes en llaves foráneas de [GCIA]

- **Empresa:** Conecta Software Oficina
- **Proyecto:** `GeoConecta`
- **Agente Autor:** `agente-geoconecta` (Ing. GeoConecta) + Validación de `agente-estratega-ia`
- **Categoría / Severidad:** `SQL_TUNING` / `ALTA`
- **Fecha de Detección:** `2026-11-26 10:16`

## 1. Diagnóstico Ejecutivo para el Patrón
Columnas Foreign Key sin índice detectadas (BitacoraCombustible.iId_Unidad_Vehicular, BitacoraMantenimiento.iId_Unidad_Vehicular, BitacoraMantenimiento.iIdTipoMantenimiento). Crear índices no agrupados acelerará JOINs y evitará bloqueos.

## 2. Propuesta de Elevación Profesional (`agente-estratega-ia`)
- **Cero impacto disruptivo:** Se ejecuta en rama `git worktree` aislada siguiendo estrictamente `PlantillaPWA` y `Regla-MetodologiaEngrama`.
- **Seguridad BD:** Cualquier ajuste SQL se entrega como archivo `.sql` idempotente en `D:\Proyectos\agentes\scripts-sql-pendientes\` sin ejecutar escrituras automáticas.

## 3. Plan de Acción Técnico
Generar script idempotente `CREATE NONCLUSTERED INDEX` para `BitacoraCombustible.iId_Unidad_Vehicular, BitacoraMantenimiento.iId_Unidad_Vehicular, BitacoraMantenimiento.iIdTipoMantenimiento` en `scripts-sql-pendientes/GeoConecta/`.

## 4. Verificación Automatizada
- Compilación limpia `dotnet build` (`0 errores`).
- Validación de no regresión en suite `Test Proyecto`.
