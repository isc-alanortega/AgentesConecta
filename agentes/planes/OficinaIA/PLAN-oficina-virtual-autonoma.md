# PLAN MAESTRO EJECUTADO: `OficinaIA` — Sede Virtual Top-Down 2D en Tiempo Real (Esquema `dbo` + Azure Cloud Ready)

- **Ruta del Proyecto:** `D:\Proyectos\OficinaIA` (basado 100% en `PlantillaPWA` + `EngramaCoreStandar`)
- **Esquema SQL:** **`[dbo]`** con prefijo limpio `Ofia_` y SPs `spGetOfia*` / `spSaveOfia*` (sin colisionar con `Test_Table`)
- **Script SQL Pendiente:** `D:\Proyectos\agentes\scripts-sql-pendientes\OficinaIA\20261125_2310_oficina_ia_dbo_completo.sql` (reemplaza el borrador inicial)
- **Despliegue Cloud:** **Hosted Blazor WebAssembly + SignalR WebSockets en Azure App Service** (`desplegar_azure.ps1` + `.github/workflows/deploy-oficinaia-azure.yml` + `iniciar_puente_local.ps1`)

---

## 1. Arquitectura Híbrida Azure Cloud 24/7 + Estación Local Alan

1. **Un solo Azure App Service (`OficinaIA.API` sirviendo `OficinaIA.PWA`)**:
   - `OficinaIA.API` hospeda directamente los archivos de `OficinaIA.PWA` (`UseBlazorFrameworkFiles()` + `MapFallbackToFile("index.html")`) y el Hub en tiempo real `OficinaHub` (`/hubs/oficina`).
   - Cuando lo publiques en `https://<tu-app>.azurewebsites.net`, podrás abrir tu oficina en vivo desde tu celular, laptop o tablet en cualquier lugar del mundo, ver a los 6 monitos moverse a 60 FPS vía SignalR y aprobar órdenes desde los botones de tu correo (`/aprobacion-patron/{token}`) sin errores de CORS ni túneles raros.
2. **Patrullaje 24/7 en Nube + Puente Saliente Local (`LocalBridge`)**:
   - **En Azure (24/7 incluso con tu PC apagada)**: `AutonomousPatrolHostedService` audita en modo Read-Only tus esquemas `GCIA`, `CNIA` y `SCIA` en Somee (índices faltantes, SPs vulnerables/sin `NOLOCK`, salud de datos) y estado de repositorios; si aún no se ha corrido el script SQL `Ofia_*` en BD, mantiene un **Estado en Memoria Resiliente (Fallback Live Mode)** para que puedas ver la oficina funcionando desde el primer segundo.
   - **En tu PC (`iniciar_puente_local.ps1` / modo local)**: Se conecta hacia Azure de salida (sin abrir puertos en tu módem), escanea `D:\Proyectos\*`, reclama propuestas aprobadas (`spSaveOfiaReclamarTrabajoLocal`), crea un `git worktree` limpio en `D:\Proyectos\.worktrees\`, programa/compila sin tocar tus archivos abiertos y reporta en vivo a Azure cada movimiento del monito.

## 2. Capas Engrama Implementadas

- **SQL (`[dbo]`)**: `Ofia_Configuracion`, `Ofia_AgenteEstado`, `Ofia_Propuesta`, `Ofia_TokenCorreo`, `Ofia_BitacoraEvento` + 12 Stored Procedures (`spGetOfia*` / `spSaveOfia*`).
- **`OficinaIA.Share`**: `Objects/OficinaModulo/*` y `DtoModels/OficinaModulo/*`.
- **`OficinaIA.API`**:
  - `EngramaLevels/Infrastructure`: Entidades `sp*`, `IOficinaRepository`, `OficinaRepository` (usando `IDapperManagerHelper` sobre esquema `""` → `dbo`, con fallback en memoria si las tablas aún no han sido creadas por Alan).
  - `EngramaLevels/Domain`: `IOficinaDomain`, `OficinaDomain` (`MapperHelper` + `IResponseHelper`).
  - `Controllers`: `OficinaController` (`PostGetEstado`, `PostSaveConfiguracion`, `PostSaveAgente`, `PostForzarPatrulla`) y `PropuestaController` (`PostGetPropuestas`, `PostGetPorToken`, `PostSaveDecisionPatron`, `PostConfirmarTokenCorreo`, `PostReclamarTrabajoBridge`, `PostReportarResultadoBridge`, `PostLatidoBridge`).
  - `Hubs & Services`: `OficinaHub`, `OficinaLiveStateService`, `AutonomousPatrolHostedService`, `BossSmtpNotificationService`, `LocalWorktreeRunnerService`.
- **`OficinaIA.PWA`**:
  - `Pages/Index.razor` + `wwwroot/js/oficina3d.js`: **Diorama Arquitectónico Isométrico 3D WebGL (Three.js + OrbitControls + CSS2DRenderer)** con paredes cutaway y ventanales luminosos, divisiones de cristal templado, pisos de madera/alfombra, escritorios modernos con doble monitor encendido, sillas con ruedas, plantas, racks SQL con LEDs y **6 monitos 3D articulados** (caminando por pasillos y sentándose a teclear), más zoom libre, barra de cámaras por oficina, seguimiento de agentes y conmutador instantáneo **Isométrico 3D ↔ Plano 2D**.
  - `Pages/AprobacionPatron.razor` (`/aprobacion-patron/{Token}`): Vista móvil/escritorio anti-bots para aprobar, posponer o rechazar desde el correo en 1 clic.
