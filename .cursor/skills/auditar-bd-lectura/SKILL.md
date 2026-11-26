---
name: auditar-bd-lectura
description: >-
  Inspecciona en modo 100% SOLO LECTURA la base de datos SQL Server de GeoConecta (GCIA), ConectaNegocios (CNIA), SANTIAGOIA (SCIA) o PlantillaPWA (dbo). Úsalo para listar tablas, columnas, tipos DT* (UDTT), leer el código real de Stored Procedures existentes o ejecutar consultas SELECT de análisis sin riesgo de escritura.
---

# Skill: Auditoría y Análisis de Base de Datos en Solo Lectura (`auditar-bd-lectura`)

Usa siempre el script blindado `./agentes\herramientas\db_readonly_query.py`.

## Comandos Rápidos Permitidos

1. **Ver inventario completo del esquema del proyecto (Tablas + SPs + Tipos `DT*`)**:
   ```powershell
   python "./agentes\herramientas\db_readonly_query.py" --project geoconecta --mode overview
   python "./agentes\herramientas\db_readonly_query.py" --project conectanegocios --mode overview
   python "./agentes\herramientas\db_readonly_query.py" --project santiagoia --mode overview
   ```

2. **Ver columnas exactas y tipos de una tabla**:
   ```powershell
   python "./agentes\herramientas\db_readonly_query.py" --project conectanegocios --mode table --name NombreTabla
   ```

3. **Ver estructura de un User-Defined Table Type (`DT*`)**:
   ```powershell
   python "./agentes\herramientas\db_readonly_query.py" --project geoconecta --mode udtt --name DTNombreTipo
   ```

4. **Leer el código fuente actual de un Stored Procedure en el servidor**:
   ```powershell
   python "./agentes\herramientas\db_readonly_query.py" --project santiagoia --mode sp --name spGetTramites
   ```

5. **Ejecutar una consulta `SELECT` o `WITH` personalizada de análisis**:
   ```powershell
   python "./agentes\herramientas\db_readonly_query.py" --project geoconecta --mode query --sql "SELECT TOP 20 * FROM GCIA.CatModulos"
   ```

## Restricción Absoluta
Nunca intentes usar `sqlcmd` directo ni sentencias `INSERT`, `UPDATE`, `DELETE`, `ALTER`, `CREATE`, `DROP` o `EXEC`: tanto el validador del script como el Hook `firewall_sql_hook.py` bloquearán la ejecución. Cualquier cambio propuesto a la BD debe escribirse como archivo `.sql` en `./agentes\scripts-sql-pendientes\<Proyecto>\`.
