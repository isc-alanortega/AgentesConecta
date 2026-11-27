# PLAN MAESTRO — Agregar etiqueta de vercionamiento

- **Folio:** `OFIA-20261127-0009`
- **Proyecto:** `ConectaControl`
- **Repo (solo lectura en la patrulla):** `C:\AgenteConecta\Conecta\ConectaControl`
- **Esquema (solo lectura):** `CCIA`
- **Agente:** `agente-conectacontrol` (Ing. Control) + `agente-estratega-ia`
- **Modalidad:** `PLAN_MAESTRO`
- **Fecha:** 2026-11-26 18:34

## 1. Objetivo y mejoras pro

Idea original del patrón:

> Quiero que la app de tengo CRM tenga una etiqueta en la parte superior con el vercionamiento empenzado por 1.0.0 y cada vez que se valla a publciar cambie a su numero consecutivo siguiente las regals de vercionamiento estandarizadas.

La etiqueta no puede ser un texto fijo en el Razor. Tiene que salir de una versión semántica (`MAJOR.MINOR.PATCH`) que empiece en `1.0.0` y suba en cada publicación:
- PATCH cuando el cambio corrige sin tocar contratos.
- MINOR cuando hay función nueva compatible.
- MAJOR cuando se rompe un contrato o un flujo que el usuario ya conoce.
La barra muestra la versión publicada, con tooltip del ensamblado. Si falta la clave, muestra `1.0.0` y el tooltip dice que es la versión de desarrollo. Nunca pinta una fila con `bSecreto = 1`.

Casos borde: valor vacío, valor que no cumple `^\d+\.\d+\.\d+$`, la etiqueta visible también sin sesión, un texto largo que no empuje el logo, y contraste sobre `modern-appbar`.

## 2. Diseño de base de datos

La barra ya existe en `MainLayout.razor` (`MudAppBar`, texto "Conecta Control" junto al logo). Ahí va un `MudChip` denso, `data-testid="app-version"`, a la derecha de la marca y antes de los botones de sesión. `ToolbarSuperior.razor` es la barra de pestañas: no es el lugar.

Dos fuentes, una sola etiqueta:
1. `<Version>1.0.0</Version>` en `ConectaControl.PWA.csproj` (hoy no declara `<Version>`). El cliente lee `AssemblyInformationalVersion`.
2. `CCIA.ConfiguracionSistema` con `vchClave = app.version`, `bSecreto = 0`, leída con el `spGetConfiguracionSistema` que ya existe. Esa es la versión publicada. Al publicar se actualiza la clave y el número del csproj al mismo semver. El chip prefiere la clave de BD y, si no responde, el ensamblado.

No hace falta tabla nueva. `ConfiguracionSistema` ya tiene `vchClave`, `nvchValor`, `vchTipo` y `bSecreto`.

Objetos reales leídos (solo nombres, sin valores):

- TABLA AdminUsuario
- TABLA AppLog
- TABLA BuzonMensaje
- TABLA BuzonRegistro
- TABLA CatalogoMotivoAjuste
- TABLA CatalogoPrioridad
- TABLA CatalogoTipoNegocio
- TABLA CicloCobro
- TABLA Cliente
- TABLA ClienteLealtad
- TABLA ConfiguracionModulo
- TABLA ConfiguracionNegocio
- TABLA ConfiguracionSistema
- TABLA ConsumoDiario
- SP spGetAdminLogin
- SP spGetAdminLoginDatos
- SP spGetAdminSesion
- SP spGetBuzon
- SP spGetBuzonAdmin
- SP spGetBuzonMensajes
- SP spGetBuzonResumen
- SP spGetCatalogoMotivoAjuste
- SP spGetCatalogoPrioridad
- SP spGetCatalogoTipoNegocio

El borrador para `app.version = 1.0.0` queda en `scripts-sql-pendientes`. No se ejecutó. Lo corre Magdaleno cuando apruebe el plan.

## 3. Contratos en `.Share`

- `AppVersion` en `Objects`: `nvchVersion`, `nvchOrigen` (`bd` o `ensamblado`), `bValida`.
- `DtoGetAppVersion` sin filtros secretos. No viaja `bSecreto` ni el `nvchValor` de otras claves.
- Comentario XML `///` en cada propiedad.

## 4. Capas backend Engrama

1. **SQL pendiente:** El borrador para `app.version = 1.0.0` queda en `scripts-sql-pendientes`. No se ejecutó. Lo corre Magdaleno cuando apruebe el plan.
2. **Repository:** el repositorio que ya usa `const string Schema = "CCIA"` llama a `spGetConfiguracionSistema` y se queda solo con la clave `app.version`.
3. **Domain:** valida el semver. Si no cumple, responde `1.0.0` con `bValida = false` y un `vchMessage` claro. `MapperHelper` + `IResponseHelper`.
4. **Controller:** `[Route("api/[controller]")]` y `[HttpPost("PostGetAppVersion")]`. El DTO va en `[FromBody]`.

## 5. Capa cliente

- Chip en la barra de `MainLayout.razor`, visible con y sin sesión.
- `MainAppVersion` pide `PostGetAppVersion` al arrancar y no bloquea el resto de la pantalla si falla: deja `1.0.0`.
- Al publicar: subir el semver en el csproj, guardar la misma cadena en `app.version` y comprobar el chip en un navegador limpio (el PWA cachea).

## 6. Plan de pruebas E2E

- El chip `[data-testid=app-version]` muestra un semver.
- Con la clave en `1.0.0`, el texto es `1.0.0`.
- Una clave mal formada no rompe la barra y el tooltip avisa.
- Actualizar `docs/agentes/handoff-ui.md` (`ui-lista`) con el selector.
- `dotnet build` del proyecto en 0 errores antes de dar el trabajo por cerrado.

## 7. Checklist

1. Aprobar este plan.
2. Revisar y, si procede, ejecutar a mano el SQL pendiente.
3. Implementar Share, Repository, Domain, Controller y el chip.
4. Subir la versión en el mismo paso en que se publica.
5. Correr el E2E del chip.

## Reglas y archivos consultados

- Leído agents/agente-estratega-ia.md
- Leído skills/plan-maestro-engrama/SKILL.md
- No hay agents/agente-conectacontrol.md en el plugin; el plan se apoya en el repo real y en el estratega.

- Raíz: `C:\AgenteConecta\Conecta\ConectaControl`
- Carpeta: `ConectaControl`
- Carpeta: `ManualDeUsuario`
- `ConectaControl\ConectaControl\ConectaControl.Share\ConectaControl.Share.csproj` (no declara <Version>)
- `ConectaControl\ConectaControl\ConectaControl.PWA\ConectaControl.PWA.csproj` (no declara <Version>)
- `ConectaControl\ConectaControl\ConectaControl.API\ConectaControl.API.csproj` (no declara <Version>)
- `ConectaControl\ConectaControl\ConectaControl.Admin.PWA\ConectaControl.Admin.PWA.csproj` (no declara <Version>)
- Barra superior: `ConectaControl\ConectaControl\ConectaControl.PWA\Shared\MainLayout.razor` (MudAppBar, marca junto al logo).
- La barra de pestañas `ConectaControl\ConectaControl\ConectaControl.PWA\Shared\Workspace\ToolbarSuperior.razor` no es el encabezado de la app.


Script SQL pendiente (no ejecutado): `C:\AgenteConecta\AgentesConecta\AgentesConecta\agentes\scripts-sql-pendientes\ConectaControl\20261126183421-agregar-etiqueta-de-vercionamiento.sql`
