# Manual de Operación — Central de Agentes (`D:\Proyectos\agentes`)

Esta carpeta concentra la inteligencia, reglas, candados de seguridad SQL, planes amplios y scripts pendientes de todos tus proyectos en `D:\Proyectos`.

## 1. Estructura de `D:\Proyectos\agentes`

- **`plugins/ecosistema-engrama/`**: Plugin nativo autodescubierto por Antigravity (vía `D:\Proyectos\.agents\plugins.json`). Contiene:
  - **`agents/` (Tus 6 Agentes IA)**:
    1. `agente-estratega-ia`: **Investigador y Arquitecto IA**. Recibe tu idea, investiga referentes profesionales, UX moderna, KPIs, seguridad y casos borde, y fusiona esas mejoras en el plan antes de programar.
    2. `agente-geoconecta`: Especialista en `GeoConecta` (Esquema SQL `GCIA`, Multi-tenant, Worker GPS, PWA).
    3. `agente-conectanegocios`: Especialista en `ConectaNegocios` (.NET 9, Esquema SQL `CNIA`, API + `SharedUI` + `Admin`/`Client`/`Propietarios`/`Mobile`/`MAUI`).
    4. `agente-conectalanding`: Especialista en `Repo Conecta Negocios Landing` (`ConectaLanding` estático, SEO, conversión).
    5. `agente-santiagoia`: Especialista en `SANTIAGOIA` (Esquema SQL `SCIA`, Trámites ciudadanos, IA, WhatsApp, Scrapers).
    6. `agente-qa-e2e`: Especialista en `Test Proyecto` (Panel Blazor `e2e-admin` + suite Playwright `PruebasE2E`).
  - **`skills/` (Flujos Automatizados)**:
    - `plan-maestro-engrama`: **Modalidad A** — Investiga con `agente-estratega-ia` + Metodología Engrama + `PlantillaPWA` + BD Read-Only y te entrega un Plan Maestro amplio en `agentes/planes/` + borrador `.sql`.
    - `turbo-ejecucion-engrama`: **Modalidad B** — Igual pasa por `agente-estratega-ia`, guarda el Plan Maestro, deja el `.sql` pendiente para ti, y **programa todas las capas de corrido** hasta pasar `dotnet build` sin errores.
    - `auditar-bd-lectura`: Inspección segura de tablas, columnas, `DT*` y SPs reales en Somee.
- **`herramientas/`**:
  - `db_readonly_query.py`: Conector oficial de solo lectura (`ApplicationIntent=ReadOnly` + filtro estricto anti-escritura).
  - `firewall_sql_hook.py`: Candado conectado a `D:\Proyectos\.agents\hooks.json` que bloquea cualquier intento de `INSERT/UPDATE/DELETE/CREATE/ALTER/DROP/EXEC` o uso directo de `sqlcmd` en terminal.
- **`planes/<Proyecto>/`**: Aquí se guardan todos los Planes de Trabajo amplios (`.md`) para tu revisión e historial.
- **`scripts-sql-pendientes/<Proyecto>/`**: Aquí depositan los agentes todos los scripts `.sql` listos para que tú los revises y ejecutes en SQL Server.

## 2. Cómo Pedir Desarrollos (Frases Rápidas)

- **Para armar primero el Plan Maestro mejorado con IA**:
  > *"Hazme un Plan Maestro para [tu idea] en GeoConecta"*
- **Para que lo investigue, planee y programe TODO de una sola vez (dejando solo el SQL listo para ti)**:
  > *"En modo Turbo: hazme [tu idea] en ConectaNegocios"*
- **Para ejecutar un plan que ya revisaste**:
  > *"Ejecuta el plan `PLAN-xxx.md` en modo Turbo"*

## 3. Comandos Potenciadores del Chat

- `/goal`: Úsalo junto con un plan grande cuando quieras que el agente trabaje sin parar hasta dejar todo compilado y verificado al 100%.
- `/teamwork`: Úsalo cuando quieras desplegar un equipo coordinado de agentes trabajando en paralelo sobre varios repositorios a la vez.
