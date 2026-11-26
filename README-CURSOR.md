# Guía de Instalación Rápida en CURSOR IDE — Ecosistema `AgentesConecta` + `Oficina-IA-Conecta`

Este repositorio (`AgentesConecta`) contiene la configuración completa de **7 Subagentes IA**, **3 Skills**, **Reglas Clean Architecture Engrama** y **Firewall SQL 100% Read-Only** compatible de forma nativa tanto con **Cursor IDE** como con **Google Antigravity**.

---

## 1. Estructura de Carpetas Recomendada en tu PC

Crea una carpeta raíz para todo el ecosistema (por ejemplo `D:\Proyectos` o `C:\Proyectos`) y clona ahí los repositorios:

```powershell
# 1. Clonar la raíz del ecosistema de agentes (trae .cursor/, .agents/, agentes/, Regla-MetodologiaEngrama/ y AGENTS.md)
git clone https://github.com/isc-alanortega/AgentesConecta.git D:\Proyectos
cd D:\Proyectos

# 2. Clonar Conecta Software Oficina (el mundo 3D en tiempo real) dentro de esa raíz
git clone https://github.com/isc-alanortega/Oficina-IA-Conecta.git OficinaIA
```

*(Si ya tenías una carpeta con `ConectaNegocios`, `SANTIAGOIA`, `PruebasE2E`, etc., simplemente muévelos adentro de esa misma carpeta raíz `D:\Proyectos` — el `.gitignore` de `AgentesConecta` ignora automáticamente todas las subcarpetas de proyectos para jamás estorbar a sus propios `.git`).*

---

## 2. Activar y Sincronizar Todo para CURSOR (1 solo comando)

Cada vez que clones por primera vez (o hagas `git pull` de cambios en agentes), corre este comando desde la carpeta raíz:

```powershell
python ./agentes/herramientas/sync_cursor.py
```

### ¿Qué deja configurado automáticamente en tu Cursor?
1. **`.cursor/rules/*.mdc` + `AGENTS.md`**: Reglas globales siempre activas con tus rutas locales exactas.
2. **`.cursor/agents/*.md`**: Los **7 Subagentes** listos para delegar en el chat de Cursor (`@agente-estratega-ia`, `@agente-geoconecta`, `@agente-conectanegocios`, `@agente-conectalanding`, `@agente-santiagoia`, `@agente-qa-e2e`, `@agente-oficinaia`).
3. **`.cursor/skills/*/SKILL.md`**: Los **3 flujos rápidos** invocables escribiendo `/` en el chat de Cursor:
   - `/plan-maestro-engrama` (Analiza BD en lectura + consulta a Estratega IA + guarda Plan Maestro en `agentes/planes/`).
   - `/turbo-ejecucion-engrama` (Arma Plan + genera `.sql` pendiente + programa todas las capas C#/Blazor y compila con `dotnet build`).
   - `/auditar-bd-lectura` (Inspección 100% segura de tablas, tipos `DT*` y SPs reales).
4. **`.cursor/hooks.json` (`beforeShellExecution` con `failClosed: true`)**: Candado automático que impide que cualquier agente ejecute `INSERT`, `UPDATE`, `DELETE`, `ALTER`, `CREATE` o `DROP` contra la base de datos.

> **Importante en Cursor:** Abre siempre la **carpeta raíz** (`File -> Open Folder -> D:\Proyectos`) en Cursor para que cargue `.cursor/` sobre todos los proyectos a la vez.

---

## 3. Levantar `Conecta Software Oficina` (Mundo 3D) en tu PC

1. Copia el archivo de ejemplo de configuración local (ignorado en Git para no subir contraseñas):
   ```powershell
   Copy-Item .\OficinaIA\OficinaIA\OficinaIA.API\appsettings.Development.example.json .\OficinaIA\OficinaIA\OficinaIA.API\appsettings.Development.json
   ```
2. Pon la cadena `EngramaCloudConnection` real y tu `ProyectosRoot` dentro de `appsettings.Development.json`.
3. Abre `OficinaIA\OficinaIA\OficinaIA.slnx` en Visual Studio o corre:
   ```powershell
   dotnet run --project .\OficinaIA\OficinaIA\OficinaIA.API\OficinaIA.API.csproj
   ```
4. *(Opcional)* Si tienes instalado el CLI de Cursor (`cursor-agent` / `agent` en tu `PATH`), cuando apruebes un plan en el mundo 3D, `ejecutar_orden_agy.py` detecta automáticamente Cursor CLI y programa la solución dentro de `.worktrees\<Folio>`.
