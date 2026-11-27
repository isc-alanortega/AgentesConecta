# PLAN MAESTRO — Mejorar el diseño de las noticias

- **Folio:** `OFIA-20261127-0011`
- **Proyecto:** `SantiagoConectaIA`
- **Repo (solo lectura en la patrulla):** `C:\AgenteConecta\Conecta\SantiagoConectaIA`
- **Esquema (solo lectura):** `SCIA`
- **Agente:** `agente-santiagoia` (Ing. SantiagoIA) + `agente-estratega-ia`
- **Modalidad:** `PLAN_MAESTRO`
- **Fecha:** 2026-11-26 19:16

## 1. Objetivo y mejoras pro

Idea original del patrón:

> Agregar sombra al rededor de las cards de las noticas para que sea vea mejor

El estratega convierte la frase en un flujo con estado vacío, validación antes de guardar, permiso de quien puede usarlo, y una prueba del camino feliz y de un caso borde (dato vacío, sin permiso, o lista sin filas). No se amplía el alcance a otra pantalla.

## 2. Diseño de base de datos

Se respeta lo que ya existe en `SantiagoConectaIA` y solo se agregan los contratos que la idea necesita. El esquema de trabajo es `SCIA`.

Objetos reales leídos (solo nombres, sin valores):

- TABLA ApiCallLogs
- TABLA BuzonCiudadano
- TABLA CatalogoEmpresa
- TABLA Catalogos
- TABLA CategoriaCatalogo
- TABLA CategoriaEvento
- TABLA CategoriaNoticia
- TABLA Chat
- TABLA Ciudadano
- TABLA CiudadanoVerificacion
- TABLA ConfiguracionVisual
- TABLA Documento
- TABLA Empresa
- TABLA EmpresaRedSocial
- SP spGetCatalogoEmpresa
- SP spGetCatalogos
- SP spGetCategoriaEventos
- SP spGetCategoriasPorEmpresa
- SP spGetChat
- SP spGetCiudadanoAuth
- SP spGetConfiguracionVisual
- SP spGetDailyTraffic
- SP spGetDocumentosPorTramite
- SP spGetEmprendimientosFeed

Si más adelante hace falta SQL, el script queda en `scripts-sql-pendientes` y no se ejecuta desde la oficina.

## 3. Contratos en `.Share`

- Un objeto de dominio y un DTO de entrada en `.Share`, con XML `///`.
- El DTO no lleva cadenas de conexión ni secretos.

## 4. Capas backend Engrama

1. **SQL pendiente:** Si más adelante hace falta SQL, el script queda en `scripts-sql-pendientes` y no se ejecuta desde la oficina.
2. **Repository:** Dapper contra el esquema `SCIA`, solo con `spGet*` / `spSave*` y `bResult` + `vchMessage`.
3. **Domain:** `MapperHelper` + `IResponseHelper`. La regla de negocio sale de la idea de arriba, no de un texto genérico.
4. **Controller:** `[Route("api/[controller]")]` y `[HttpPost("PostGet")]` o `[HttpPost("PostSave")]`. El DTO va en `[FromBody]`.

## 5. Capa cliente

- Pantalla o pestaña en el PWA del proyecto, con carga, vacío y error.
- El texto que pidió el patrón se ve en la pantalla, no solo en un log.

## 6. Plan de pruebas E2E

- Un spec del flujo principal y uno del caso borde (vacío o sin permiso).
- Actualizar `docs/agentes/handoff-ui.md` con los selectores nuevos.
- `dotnet build` en 0 errores.

## 7. Checklist

1. Aprobar este plan.
2. Revisar y, si procede, ejecutar a mano el SQL pendiente.
3. Implementar Share, Repository, Domain, Controller y el chip.
4. Subir la versión en el mismo paso en que se publica.
5. Correr el E2E del chip.

## Reglas y archivos consultados

- Leído agents/agente-estratega-ia.md
- Leído skills/plan-maestro-engrama/SKILL.md
- Leído agents/agente-santiagoia.md

- Raíz: `C:\AgenteConecta\Conecta\SantiagoConectaIA`
- Carpeta: `BaseDatos`
- Carpeta: `docs`
- Carpeta: `Metodologia`
- Carpeta: `SantiagoConectaIA`
- `SantiagoConectaIA\SantiagoConectaIA.Test\SantiagoConectaIA.Test.csproj` (no declara <Version>)
- `SantiagoConectaIA\SantiagoConectaIA.Share\SantiagoConectaIA.Share.csproj` (no declara <Version>)
- `SantiagoConectaIA\SantiagoConectaIA.PWA\SantiagoConectaIA.PWA.csproj` (no declara <Version>)
- `SantiagoConectaIA\SantiagoConectaIA.API\SantiagoConectaIA.API.csproj` (no declara <Version>)
- `SantiagoConectaIA\SantiagoConectaFront\SantiagoConectaFront.csproj` (no declara <Version>)
- `SantiagoConectaIA\SantiagoConecta.SharedUI\SantiagoConecta.SharedUI.csproj` (no declara <Version>)
- Barra superior: `SantiagoConectaIA\SantiagoConectaIA.PWA\Shared\MainLayout.razor` (MudAppBar, marca junto al logo).
- La barra de pestañas `SantiagoConectaIA\SantiagoConectaIA.PWA\Shared\Workspace\ToolbarSuperior.razor` no es el encabezado de la app.
