# INSTALADOR AUTOMÁTICO PARA CURSOR AI — Ecosistema `AgentesConecta` + `Conecta Software Oficina`

> **¿Cómo usar este archivo? (Para el desarrollador en Cursor IDE):**
> 1. Abre **Cursor IDE** y abre la carpeta raíz donde tienes (o quieres tener) todos tus proyectos de Conecta (`File -> Open Folder...`, por ejemplo `C:\Proyectos` o `D:\Proyectos`).
> 2. Abre el panel de Chat en modo **Agent** (`Ctrl + I`).
> 3. Arrastra este archivo `INSTALAR-EN-CURSOR.md` al chat y escribe:
>    **"Ejecuta las instrucciones de este archivo e instala todo automáticamente."**

---

## INSTRUCCIONES EJECUTABLES PARA EL AGENTE DE CURSOR (MODO AUTÓNOMO)

Actúa como un **Ingeniero DevOps Autónomo**. El usuario acaba de entregarte este manifiesto para instalar y configurar en su máquina todo el ecosistema de agentes IA (**`AgentesConecta`**) y la oficina virtual 3D (**`Conecta Software Oficina`**).

**Regla de oro:** NO le devuelvas estos pasos al usuario para que los corra a mano. **Ejecútalos tú mismo en la terminal integrada de principio a fin** sobre el directorio raíz abierto actualmente en el workspace (`$PWD`). Solo detente a preguntar si falla el acceso de red/credenciales de GitHub o al final si falta la contraseña SQL.

### Paso 1. Verificar prerrequisitos en la terminal
Ejecuta en una sola llamada de terminal la verificación de herramientas instaladas:
```powershell
git --version ; python --version ; dotnet --list-sdks
```
- Si falta Python o Git, avísale claramente al usuario qué instalar. Si están presentes, continúa de inmediato sin preguntar.

### Paso 2. Conectar y descargar `AgentesConecta` en la carpeta raíz actual (`$PWD`)
Revisa primero si la carpeta actual ya tiene el repositorio `AgentesConecta` conectado (`git status` / `git remote -v`):

- **Caso A — La carpeta actual NO es un repositorio Git todavía** (aunque ya tenga adentro subcarpetas como `ConectaNegocios`, `SANTIAGOIA`, `GeoConecta`, `PlantillaPWA` o este mismo archivo `INSTALAR-EN-CURSOR.md`):
  Ejecuta exactamente esto en la raíz del workspace (el `.gitignore` de `AgentesConecta` es de *lista blanca*, así que **NO tocará ni borrará** ningún repositorio hijo existente):
  ```powershell
  git init -b main
  git remote add origin https://github.com/isc-alanortega/AgentesConecta.git
  git fetch origin
  git checkout -f -t origin/main
  ```
- **Caso B — La carpeta actual YA tiene `origin` apuntando a `AgentesConecta.git`**:
  Ejecuta `git pull origin main`.
- **Caso C — El usuario abrió por error un subproyecto individual** (por ejemplo abrió `ConectaNegocios` en vez de la carpeta padre donde viven todos los proyectos):
  Detente de inmediato y pídele que abra en Cursor la **carpeta padre raíz** (`File -> Open Folder`) antes de continuar, para no mezclar `AgentesConecta` dentro de un proyecto hijo.

### Paso 3. Ejecutar el instalador desatendido (Clona `OficinaIA`, instala `pyodbc`, sincroniza `.cursor/`, configura `appsettings.Development.json` y compila)
Una vez descargado `AgentesConecta` en la raíz, ejecuta el script oficial de auto-instalación:
```powershell
python ./agentes/herramientas/instalar_entorno_cursor.py
```
Este script realiza automáticamente:
1. Instala `pyodbc` si no existe.
2. Clona `https://github.com/isc-alanortega/Oficina-IA-Conecta.git` dentro de `./OficinaIA` (si aún no está clonado).
3. Ejecuta `sync_cursor.py` para activar:
   - `./AGENTS.md` y `./.cursor/rules/*.mdc` (Reglas Clean Architecture Engrama + Metodología 0–8).
   - `./.cursor/agents/*.md` (`@agente-estratega-ia`, `@agente-geoconecta`, `@agente-conectanegocios`, `@agente-conectalanding`, `@agente-santiagoia`, `@agente-qa-e2e`, `@agente-oficinaia`).
   - `./.cursor/skills/*/SKILL.md` (`/plan-maestro-engrama`, `/turbo-ejecucion-engrama`, `/auditar-bd-lectura`).
   - `./.cursor/hooks.json` + `./.cursor/hooks/sql_guard.py` (Firewall SQL 100% Read-Only en `beforeShellExecution`).
   - `./.worktrees/.gitkeep` (Carpeta aislada para ramas de agentes).
4. Crea `./OficinaIA/OficinaIA/OficinaIA.API/appsettings.Development.json` con la ruta `ProyectosRoot` exacta de esta PC y reutiliza automáticamente `EngramaCloudConnection` si la encuentra en otro proyecto hermano (`ConectaNegocios`, `GeoConecta`, `SANTIAGOIA` o `PlantillaPWA`).
5. Prueba que el Firewall SQL bloquee clientes directos y compila `./OficinaIA/OficinaIA/OficinaIA.slnx` en modo `Release`.

### Paso 4. Verificación final y reporte al desarrollador
Al terminar el script:
1. Revisa si en la salida apareció `[PENDIENTE] Falta colocar la cadena real 'EngramaCloudConnection'`. Si apareció, avísale al usuario en qué línea de `./OficinaIA/OficinaIA/OficinaIA.API/appsettings.Development.json` pegar su cadena de conexión SQL de desarrollo (y opcionalmente su correo en `EmailPatronDefault`).
2. Muéstrale qué repositorios hermanos ya fueron detectados (`PlantillaPWA`, `ConectaNegocios`, `GeoConecta`, `SANTIAGOIA`, `OficinaIA`, etc.) y recuérdale clonar en esta misma carpeta raíz los que le falten.
3. Indícale que presione **`Ctrl + Shift + P` -> `Developer: Reload Window`** en Cursor para que carguen en memoria los 7 subagentes (`@agente-...`), los 3 skills (`/plan-maestro-engrama`, `/turbo-ejecucion-engrama`, `/auditar-bd-lectura`) y el Firewall SQL Read-Only.
4. Indícale cómo levantar la oficina virtual 3D cuando quiera verla en el navegador:
   ```powershell
   dotnet run --project ./OficinaIA/OficinaIA/OficinaIA.API/OficinaIA.API.csproj
   ```
