# PLAN MAESTRO — Worktree Permanente por Agente, Ejecución Paralela y Ahorro de Tokens

- **Proyecto:** `Conecta Software Oficina` (`OficinaIA`) + `AgentesConecta`
- **Autor:** Cerebro Orquestador + `agente-estratega-ia`
- **Objetivo de Negocio (Patrón Alan):**
  1. Que **cada agente tenga un único Worktree fijo permanente** en `.worktrees/<codigo-agente>` sobre su propia rama `agentes/<especialidad>` (cero creación repetitiva de carpetas por cada folio).
  2. **Ahorro agresivo de tokens** en Antigravity CLI (`agy`) y Cursor CLI (`cursor-agent`).
  3. **Trabajo simultáneo real en paralelo**: que todos los agentes con tareas aprobadas programen al mismo tiempo en sus escritorios sin bloquearse en una sola fila global.

---

## 1. Mapa Oficial de Worktrees Permanentes por Agente

| Agente | Carpeta Worktree Permanente | Rama Fija del Agente | Repositorio Base |
| :--- | :--- | :--- | :--- |
| `agente-geoconecta` | `.worktrees/agente-geoconecta` | `worktree/geoconecta` | `GeoConecta` |
| `agente-conectanegocios` | `.worktrees/agente-conectanegocios` | `worktree/conectanegocios` | `ConectaNegocios` |
| `agente-conectalanding` | `.worktrees/agente-conectalanding` | `worktree/conectalanding` | `Repo Conecta Negocios Landing` |
| `agente-santiagoia` | `.worktrees/agente-santiagoia` | `worktree/santiagoia` | `SANTIAGOIA` |
| `agente-qa-e2e` | `.worktrees/agente-qa-e2e` | `worktree/qa-e2e` | `Test Proyecto` |
| `agente-oficinaia` | `.worktrees/agente-oficinaia` | `worktree/oficinaia` | `OficinaIA` |
| `agente-estratega-ia` | `.worktrees/agente-estratega-ia` | `worktree/estratega-ia` | Raíz `AgentesConecta` |

---

## 2. Arquitectura de Ahorro de Tokens (~65% a 75% menos consumo por orden)

1. **Eliminación de lecturas de arranque redundantes**:
   - Antes: el prompt ordenaba al CLI abrir y leer `agente-*.md`, `PlantillaPWA/AGENTS.md` y `PLAN-*.md` en cada ronda (~3–5 turnos y ~12,000 tokens extra).
   - Ahora: `ejecutar_orden_agy.py` inyecta directamente el Plan + un **Cheat-Sheet Engrama ultracompacto de 10 líneas** + ruta exacta de solución `.sln`, entrando directo a editar el archivo objetivo en el turno 1.
2. **Restricción estricta de contexto (`--add-dir`)**:
   - Se elimina `--add-dir D:\Proyectos` (que permitía indexar otros repositorios) y se limita exclusivamente al worktree del agente + su subcarpeta de `scripts-sql-pendientes`.
3. **Caché de compilación `bin/` y `obj/` siempre caliente**:
   - Al reutilizar siempre `.worktrees/<codigo-agente>`, los paquetes NuGet y binarios ya están compilados (`dotnet build --no-restore /nr:false -m:2`), bajando la compilación de ~100s a ~4s y eliminando reintentos de QA por timeout.
4. **Cero `dotnet build` innecesario en tareas SQL/Frontend estático**:
   - Si el commit del folio solo generó scripts `.sql` o archivos `.md`/`.html`/`.js`/`.css`, se omite `dotnet build`.

---

## 3. Ejecución Multi-Agente en Paralelo (`OfiaEjecucionQaHostedService`)

- Se reemplaza el candado único global `SemaphoreSlim(1, 1)` por un diccionario de candados **por worktree/agente** (`ConcurrentDictionary<string, SemaphoreSlim>`).
- `OfiaCampusSql.ReclamarTrabajosAgentesLibresAsync` reclama en cada pulso todas las tareas `APROBADO_EN_COLA` cuyos agentes no estén ocupados, despachando a `agente-santiagoia`, `agente-conectanegocios`, `agente-conectalanding`, `agente-qa-e2e`, etc. **simultáneamente en `Task.Run` independientes**.
