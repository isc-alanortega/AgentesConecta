# PLAN MAESTRO AUTÓNOMO: Optimizar SPs sin SET NOCOUNT ON en [SCIA] (2 detectados)

- **Empresa:** Conecta Software Oficina
- **Proyecto:** `SANTIAGOIA`
- **Agente Autor:** `agente-santiagoia` (Ing. SantiagoIA) + Validación de `agente-estratega-ia`
- **Categoría / Severidad:** `SQL_TUNING` / `MEDIA`
- **Fecha de Detección:** `2026-11-26 10:18`

## 1. Diagnóstico Ejecutivo para el Patrón
Se detectaron procedimientos en [SCIA] (spSaveCiudadanoCodigo, spValidarCiudadanoCodigo) sin 'SET NOCOUNT ON', lo que añade mensajes DONE_IN_PROC innecesarios en Dapper.

## 2. Propuesta de Elevación Profesional (`agente-estratega-ia`)
- **Cero impacto disruptivo:** Se ejecuta en rama `git worktree` aislada siguiendo estrictamente `PlantillaPWA` y `Regla-MetodologiaEngrama`.
- **Seguridad BD:** Cualquier ajuste SQL se entrega como archivo `.sql` idempotente en `D:\Proyectos\agentes\scripts-sql-pendientes\` sin ejecutar escrituras automáticas.

## 3. Plan de Acción Técnico
Generar script `CREATE OR ALTER PROCEDURE` en `scripts-sql-pendientes/SANTIAGOIA/` agregando `SET NOCOUNT ON` a: `spSaveCiudadanoCodigo, spValidarCiudadanoCodigo`.

## 4. Verificación Automatizada
- Compilación limpia `dotnet build` (`0 errores`).
- Validación de no regresión en suite `Test Proyecto`.
