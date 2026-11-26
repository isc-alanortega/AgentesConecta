# PLAN MAESTRO — ORDEN DIRECTA DEL PATRÓN: Modulo de Noticias

- **Empresa:** Conecta Software Oficina
- **Proyecto Destino:** `SANTIAGOIA` (`D:\Proyectos\SANTIAGOIA`)
- **Esquema SQL (100% Read-Only para Agentes):** `[SCIA]`
- **Agente Responsable:** `agente-santiagoia` (Ing. SantiagoIA) + Elevación Pro de `agente-estratega-ia`
- **Modalidad Solicitada:** `PLAN_MAESTRO`
- **Fecha:** `2026-11-26 10:19`

---

## 1. Instrucción Original del Patrón (Alan)
> Quiero que modifiques el modulo de noticias y que lo hagas más atractivo

## 2. Contexto Real Auditado en el Ecosistema
- **Estructura detectada en repositorio:** `BaseDatos, docs, Metodologia, SantiagoConectaIA`
- **Objetos reales inspeccionados en BD (Read-Only):** `TABLA: Empresa, TABLA: Rol, TABLA: ApiCallLogs, TABLA: WhatsAppMessage, TABLA: Documento, TABLA: Mensaje, TABLA: PageVisits, TABLA: Eventos, TABLA: EventosSucursales, TABLA: Usuario, TABLA: EmpresaRedSocial, TABLA: BuzonCiudadano, SP: spSaveUsuario, SP: spGetUsuarioAuth, SP: spGetPageVisitsByPage, SP: spGetEventos, SP: spGetDailyTraffic, SP: spGetEventosSucursales, SP: spGetRecentVisits, SP: spGetImagenesRegistro, SP: spSaveCiudadanoCodigo, SP: spValidarCiudadanoCodigo, SP: spSearchRequisitosForChat, SP: spDescartarMeme`

## 3. Mejoras Profesionales Integradas (`agente-estratega-ia`)
1. **Apego 100% a `Regla-MetodologiaEngrama` (Docs 0–8) y `PlantillaPWA`**:
   - Contratos tipados en `.Share` (`Objects` + `DtoModels`) con comentarios XML `///`.
   - Acceso a datos exclusivamente vía `IDapperManagerHelper` apuntando al esquema `[SCIA]` y Stored Procedures con `SET NOCOUNT ON`, `bResult` y `vchMessage`.
   - Endpoints HTTP bajo convención estricta `[Route("api/[controller]")]` + `[HttpPost("PostGet")]` / `[HttpPost("PostSave")]` (DTO en `[FromBody]`, jamás en la ruta).
2. **UX/UI y Calidad Empresarial**:
   - Estados de carga, empty states claros, validaciones preventivas en formulario Blazor (`Main*` + `ValidadionServicio`) y actualización automática de `docs/agentes/handoff-ui.md` (`ui-lista`).
3. **Seguridad de Base de Datos**:
   - Cero escrituras automáticas en BD: el script SQL queda depositado en `D:\Proyectos\agentes\scripts-sql-pendientes\SANTIAGOIA\` para revisión y ejecución personal de Alan.

## 4. Desglose de Implementación por Capas
1. **Capa SQL (`[SCIA]`):** Tablas / tipos `DT*` / `spGet*` y `spSave*` idempotentes.
2. **Capa `.Share`:** Modelos de dominio y DTOs de entrada.
3. **Capa `.API` (`Infrastructure` → `Domain` → `Controllers`):** Entidades `sp*`, Repositorio Dapper, `MapperHelper` + `IResponseHelper` y Controlador `Post*`.
4. **Capa Cliente (`.PWA` / UI):** Servicio `Main*`, vista Grid/Form y registro de pestaña `WorkspaceTab` si aplica.
5. **Capa QA (`Test Proyecto`):** Spec Playwright de flujo principal + compilación `dotnet build` con `0 errores`.
