# Protocolo Técnico Base: Metodología Engrama + PlantillaPWA

Documento de referencia rápida para todos los agentes en `D:\Proyectos`.

1. **Orden de Verdad**:
   - `D:\Proyectos\PlantillaPWA\AGENTS.md` (reglas de arquitectura limpia y nombres HTTP `Post*`).
   - `D:\Proyectos\Regla-MetodologiaEngrama\0- EngramaCoreStandar.md` al `8- Guia Consultas SP.md`.
   - Código vivo de referencia: `D:\Proyectos\PlantillaPWA\TemplatePWA` (`TestModule`).
2. **Esquemas SQL Oficiales en Catálogo `Engrama`**:
   - `GeoConecta` → `"GCIA"`
   - `ConectaNegocios` → `"CNIA"`
   - `SANTIAGOIA` → `"SCIA"`
   - `PlantillaPWA` → `"dbo"`
3. **Convención HTTP Inquebrantable**:
   - Controlador: `[ApiController]` + `[Route("api/[controller]")]`.
   - Acción: `[HttpPost("PostGet")]`, `[HttpPost("PostSave")]`, `[HttpPost("Post<Accion>")]`.
   - El DTO va únicamente en `[FromBody]`, **jamás** como nombre de ruta.
4. **Seguridad BD**:
   - Lectura exclusiva con `python "D:\Proyectos\agentes\herramientas\db_readonly_query.py"`.
   - Escritura prohibida: depositar `.sql` en `D:\Proyectos\agentes\scripts-sql-pendientes\<Proyecto>\`.
