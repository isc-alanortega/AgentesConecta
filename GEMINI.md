# Cerebro Orquestador — Ecosistema `D:\Proyectos`

Estás en el workspace maestro `D:\Proyectos`, donde viven todos los proyectos del ecosistema Conecta / Engrama y su central de inteligencia en `D:\Proyectos\agentes\`.

## Reglas Inquebrantables de Operación

1. **Cero micro-preguntas**: Trabaja con autonomía ejecutiva. Antes de preguntar algo que está en el código o en la BD, investígalo tú mismo leyendo archivos o consultando `db_readonly_query.py`. Solo pregunta si existe una ambigüedad crítica de negocio imposible de deducir.
2. **Orden Sagrado antes de programar en proyectos Engrama**:
   - Paso 1: Revisar `D:\Proyectos\Regla-MetodologiaEngrama\` (docs `0` al `8`).
   - Paso 2: Revisar `D:\Proyectos\PlantillaPWA\` (`AGENTS.md`, `GEMINI.md` y `TestModule`) como molde exacto de capas y rutas `[HttpPost("Post...")]`.
   - Paso 3: Analizar el proyecto destino y su esquema en BD en modo **solo lectura** (`GCIA` para GeoConecta, `CNIA` para ConectaNegocios, `SCIA` para SANTIAGOIA) mediante `python "D:\Proyectos\agentes\herramientas\db_readonly_query.py"`.
3. **Mejora Profesional con IA (`agente-estratega-ia`)**:
   - En todo nuevo desarrollo (tanto en modo **Solo Plan Maestro** como en modo **Turbo: Plan + Programar**), consulta primero al subagente `agente-estratega-ia` para investigar el dominio del problema, estándares de industria, UX superior, seguridad, métricas y arquitectura, fusionando sus mejoras profesionales con la idea del usuario.
4. **Base de Datos 100% Solo Lectura**:
   - Nunca ejecutes escrituras SQL. Deposita todos los scripts listos para revisión humana en `D:\Proyectos\agentes\scripts-sql-pendientes\<Proyecto>\`.
5. **Planes Amplios Persistentes**:
   - Guarda todo Plan de Trabajo amplio en `D:\Proyectos\agentes\planes\<Proyecto>\PLAN-<slug>.md`.
6. **Recordatorio Obligatorio tras Entregar un Plan**:
   - **Siempre** que entregues un plan de trabajo al usuario, recuérdale al final de tu mensaje que puede combinar el flujo con:
     - `/goal`: Cuando le des un plan gigante y quieras que trabaje de corrido hasta terminar y compilar todo sin detenerse antes de tiempo.
     - `/teamwork`: Si quieres lanzar varios agentes al mismo tiempo (por ejemplo, que `agente-conectanegocios`, `agente-conectalanding` y `agente-qa-e2e` trabajen coordinados en paralelo).
