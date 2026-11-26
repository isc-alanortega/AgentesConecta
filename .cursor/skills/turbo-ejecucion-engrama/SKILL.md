---
name: turbo-ejecucion-engrama
description: >-
  Modalidad Turbo End-to-End: Investiga mejoras profesionales con `agente-estratega-ia`, guarda el Plan Maestro en `agentes/planes/`, genera el script SQL pendiente en `agentes/scripts-sql-pendientes/` (sin ejecutarlo en BD) y PROGRAMA DE CORRIDO todas las capas C#/Blazor/TS siguiendo Metodología Engrama y PlantillaPWA hasta compilar con `dotnet build` sin errores. Úsalo cuando el usuario pida hacer/programar un requerimiento completo de una vez o aprobar y ejecutar un Plan Maestro.
---

# Skill: Modalidad B — Turbo: Plan Mejorado con IA + Programación Completa (`turbo-ejecucion-engrama`)

Diseñado para máxima velocidad y cero interrupciones al usuario.

## Fase 1: Análisis + Estratega IA + Guardado de Plan (si aún no existe un plan aprobado)

Si el usuario te dio una instrucción nueva directa para programar:
1. Lee `D:\Proyectos\PlantillaPWA\AGENTS.md` y los docs aplicables de `D:\Proyectos\Regla-MetodologiaEngrama\`.
2. Inspecciona en paralelo el código actual del proyecto y la BD en modo **solo lectura** con `python "D:\Proyectos\agentes\herramientas\db_readonly_query.py"`.
3. Invoca a `agente-estratega-ia` (delegando al subagente en `.cursor/agents/`) para enriquecer el requerimiento con mejoras profesionales de UX, negocio, rendimiento y seguridad que encajen en Engrama.
4. Guarda el Plan Maestro resultante en `D:\Proyectos\agentes\planes\<Proyecto>\PLAN-<slug>.md`.

*(Si el usuario ya aprobó un archivo `PLAN-*.md` existente, léelo directo y pasa a la Fase 2).*

## Fase 2: Generación de Script SQL Pendiente (Cero Escritura en BD)

1. Escribe el script SQL completo, idempotente (`IF NOT EXISTS` / `CREATE OR ALTER PROCEDURE`), comentado y con el esquema correcto (`GCIA`, `CNIA` o `SCIA`) en:
   `D:\Proyectos\agentes\scripts-sql-pendientes\<Proyecto>\<YYYYMMDD_HHMM>_<slug>.sql`
2. **JAMÁS** ejecutes ese script en la base de datos. Alan lo revisará y correrá personalmente.

## Fase 3: Programación End-to-End Autónoma (Molde `PlantillaPWA`)

Delega al subagente del proyecto (`agente-geoconecta`, `agente-conectanegocios`, `agente-conectalanding`, `agente-santiagoia`) o ejecútalo directamente siguiendo estrictamente este orden sin saltarte capas:
1. **`.Share`**: `Objects` + `DtoModels` con XML docs `///` y propiedades idénticas a las columnas SQL.
2. **`.API / Infrastructure`**: Clases `DT*` (si usa TVP), entidades `spGet*` / `spSave*` (`SpRequest` / `DbResult`), interfaz `I*Repository` e implementación `*Repository` usando `IDapperManagerHelper` con el esquema del proyecto (`"GCIA"`, `"CNIA"` o `"SCIA"`).
3. **`.API / Domain`**: Interfaz `I*Domain` e implementación `*Domain` (`MapperHelper` + `IResponseHelper.Validacion`), inicializando listas TVP explícitamente (nunca `null`) y registrando DI en `Program.cs` si no es automático.
4. **`.API / Controllers`**: Controlador delgado `[Route("api/[controller]")]` con acciones `[HttpPost("PostGet")]`, `[HttpPost("PostSave")]` o `[HttpPost("Post...")]` (DTO siempre en `[FromBody]`, nunca en el nombre de la ruta).
5. **`.PWA` / Clientes**: Clase `Main*` (`IHttpService` + `ValidadionServicio`), componentes `Grid*` / `Form*` / página o pestaña `WorkspaceTab` (recordando: `EntityId` y `ForceNewTab` van en `WorkspaceTab`, jamás dentro de `DynamicComponent Parameters`).
6. **Handoff UI**: Actualiza `docs/agentes/handoff-ui.md` en el repo del proyecto con fecha, rutas, estados de UI y forma de datos (`ui-lista`).

## Fase 4: Compilación y Verificación E2E

1. Ejecuta `dotnet build` en la solución o proyectos modificados. Si aparece cualquier error o warning crítico de tipos, **corrígelo tú mismo en el acto** y vuelve a compilar hasta obtener `0 Error(s)`.
2. Si aplica actualizar o crear spec en `D:\Proyectos\Test Proyecto\PruebasE2E`, coordínalo con `agente-qa-e2e`.

## Fase 5: Entrega Ejecutiva

Presenta al usuario:
- Enlace al **Plan Maestro** ejecutado en `D:\Proyectos\agentes\planes\...`.
- **ACCIÓN REQUERIDA POR ALAN (BD)**: Enlace directo al **Script SQL** en `D:\Proyectos\agentes\scripts-sql-pendientes\...` listo para que lo revise y corra en SQL Server.
- Resumen de capas/archivos creados y confirmación de `dotnet build` exitoso.
- Recordatorio de los comandos `/goal` y `/teamwork` para siguientes iteraciones o pruebas masivas.
