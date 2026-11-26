---
name: plan-maestro-engrama
description: >-
  Genera un Plan Maestro de Desarrollo amplio, profesional y listo para ejecutar en cualquiera de los proyectos (GeoConecta, ConectaNegocios, Repo Conecta Negocios Landing, SANTIAGOIA, Test Proyecto). Úsalo cuando el usuario pida analizar un requerimiento, diseñar una funcionalidad o armar un plan de trabajo sin programar aún el código C#/Blazor. Consulta obligatoriamente a `agente-estratega-ia`, Metodología Engrama, PlantillaPWA y la BD en modo solo lectura.
---

# Skill: Modalidad A — Generar Plan Maestro Profesional (`plan-maestro-engrama`)

Ejecuta este procedimiento de corrido y **sin hacer micro-preguntas** al usuario.

## Paso 1: Investigación en Paralelo (Contexto + BD Read-Only + Estratega IA)

En un solo turno paralelo:
1. **Metodología y Molde**: Lee `./PlantillaPWA\AGENTS.md` y los documentos relevantes de `./Regla-MetodologiaEngrama\` (`0` al `8`).
2. **Estado Actual del Proyecto y BD**:
   - Inspecciona los módulos relacionados del proyecto destino en `./<Proyecto>`.
   - Si el proyecto tiene BD (`geoconecta` [`GCIA`], `conectanegocios` [`CNIA`], `santiagoia` [`SCIA`]), ejecuta en modo **100% lectura**:
     `python "./agentes\herramientas\db_readonly_query.py" --project <proyecto> --mode overview` (y `--mode table` / `--mode sp` en las tablas/SPs relacionados).
3. **Elevación Profesional con `agente-estratega-ia`**:
   - Lanza el subagente `@agente-estratega-ia` (definido en `.cursor/agents/agente-estratega-ia.md`) pasándole el requerimiento del usuario, el proyecto destino y el resumen de lo que ya existe, pidiéndole investigar mejoras de nivel empresarial (UX/UI, KPIs, seguridad, rendimiento, casos borde y criterios E2E).

## Paso 2: Redactar y Guardar el Plan Maestro + Borrador SQL

1. Fusiona lo que pidió el usuario con las mejores propuestas de `agente-estratega-ia`.
2. Guarda el Plan Maestro completo en:
   `./agentes\planes\<Proyecto>\PLAN-<slug-descriptivo>.md`
   El documento DEBE contener:
   - **1. Objetivo y Mejoras Pro Integradas** (qué pidió Alan + qué aportó `agente-estratega-ia`).
   - **2. Diseño de Base de Datos (Esquema `GCIA`/`CNIA`/`SCIA`)**: Tablas nuevas/modificadas, tipos `DT*` (TVP), y contrato exacto de Stored Procedures (`spGet*`, `spSave*` con `bResult` y `vchMessage`).
   - **3. Contratos en `.Share`**: Clases en `Objects/` y `DtoModels/`.
   - **4. Capas Backend Engrama (`.API`)**: Entidades `sp*`, `I*Repository` / `*Repository` (con esquema explícito), `I*Domain` / `*Domain` (`MapperHelper` + `IResponseHelper`), y `*Controller` (`[Route("api/[controller]")]` + `[HttpPost("Post...")]`).
   - **5. Capa Cliente PWA / UI**: Rutas `@page` o pestañas `WorkspaceTab`, `Main*`, `Grid*`, `Form*`, estados vacíos/carga y validaciones.
   - **6. Plan de Pruebas Automatizadas (`Test Proyecto`)**: Flujos exactos para `PruebasE2E` y `e2e-admin`.
   - **7. Checklist de Ejecución Rápida** por fases.
3. Si el desarrollo requiere cambios en SQL Server, deja de una vez el script `.sql` propuesto listo para revisión humana en:
   `./agentes\scripts-sql-pendientes\<Proyecto>\<YYYYMMDD_HHMM>_<slug>.sql` (recuerda: **NUNCA** ejecutarlo contra la BD).

## Paso 3: Entrega al Usuario + Recordatorio Obligatorio de Comandos

Entrega un resumen ejecutivo con enlaces clicables (`file:///...`) al Plan Maestro `.md` y al Script `.sql` pendiente, y **SIEMPRE cierra tu mensaje con este recordatorio exacto**:

> **Potenciadores que puedes usar ahora en el chat:**
> - `/goal`: Cuando me des luz verde a este plan gigante y quieras que trabaje de corrido hasta terminar y compilar todo sin detenerme antes de tiempo (o dime directo *"Ejecútalo en modo Turbo"*).
> - `/teamwork`: Si quieres lanzar varios agentes al mismo tiempo (por ejemplo, que `agente-conectanegocios`, `agente-conectalanding` y `agente-qa-e2e` trabajen coordinados en paralelo).
