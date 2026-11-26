# PLAN MAESTRO EJECUTADO: `Conecta Software Oficina` (v2.0 — Edición Videojuego 3D + Órdenes del Patrón + Sala Gamer)

- **Nombre Oficial:** **Conecta Software Oficina**
- **Solución:** `D:\Proyectos\OficinaIA\OficinaIA\OficinaIA.slnx` (se mantiene ruta física compatible con tu sesión abierta de Visual Studio)
- **Script SQL Incremental:** `D:\Proyectos\agentes\scripts-sql-pendientes\ConectaSoftwareOficina\20261126_0025_conecta_software_oficina_v2.sql`

## Resumen de Mejoras Incorporadas
1. **Órdenes Directas del Patrón (`PostAsignarOrdenPatron`)**: Cualquier agente puede recibir una misión directa escrita por Alan en modalidad `PLAN_MAESTRO` o `MODO_TURBO`, consultando la BD en modo Read-Only, reuniéndose con `agente-estratega-ia` y guardando el plan en `D:\Proyectos\agentes\planes\<Proyecto>\` + rama aislada `git worktree`.
2. **Cero Repetición de Planes Rechazados**: Validación doble (en C# Read-Only antes de crear propuestas + en `dbo.spSaveOfiaPropuesta` sin excluir `RECHAZADO`) para que ningún plan rechazado vuelva a proponerse jamás.
3. **Sala de Videojuegos 3D (`SALA_VIDEOJUEGOS`) y Sistema de Motivación (`⚡%`)**: 3 maquinitas Arcade neón, TV curva con consola, sillones puff y air-hockey donde van los agentes cuando están libres para motivarse al 100%.
4. **Avatar 3D de Alan (`👑 El Patrón`) + Monitos Humanos Realistas + Cámara Fácil**:
   - Personajes con cuello, facciones (nariz, orejas, cejas, ojos con iris/pupila, sonrisa, barba), saco con solapas, corbata y codos/rodillas articulados.
   - Modo **`🕹️ Mover a mi Monito (Patrón)`** para caminar por toda la oficina con clic en el piso o `WASD`.
   - Navegación intuitiva: **Clic izquierdo + arrastrar = moverse**, **Clic derecho = girar**, **Rueda = zoom**, **`WASD`/Flechas** y cruceta en pantalla.
