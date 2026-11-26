#!/usr/bin/env python3
r"""
Lector SQL ESTRICTAMENTE DE SOLO LECTURA para los Agentes del Ecosistema Engrama.
Permite inspeccionar esquemas (GCIA, CNIA, SCIA, dbo), tablas, columnas, tipos DT* (UDTT),
definiciones de Stored Procedures (OBJECT_DEFINITION) y consultas SELECT de diagnóstico.
BLOQUEA CUALQUIER ESCRITURA O EJECUCIÓN DE PROCEDIMIENTOS ALMACENADOS DE NEGOCIO.
"""
import argparse
import json
import os
import re
import subprocess
import sys

DEFAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROYECTOS_ROOT = os.environ.get("PROYECTOS_ROOT") or DEFAULT_ROOT

PROJECT_CONFIG = {
    "geoconecta": {
        "schema": "GCIA",
        "appsettings": [
            os.path.join(PROYECTOS_ROOT, "GeoConecta", "GeoConecta", "GeoConecta.API", "appsettings.Development.json"),
            os.path.join(PROYECTOS_ROOT, "GeoConecta", "GeoConecta", "GeoConecta.API", "appsettings.json"),
        ],
    },
    "conectanegocios": {
        "schema": "CNIA",
        "appsettings": [
            os.path.join(PROYECTOS_ROOT, "ConectaNegocios", "ConectaNegocios", "ConectaNegocios.API", "appsettings.Development.json"),
            os.path.join(PROYECTOS_ROOT, "ConectaNegocios", "ConectaNegocios", "ConectaNegocios.API", "appsettings.json"),
        ],
    },
    "santiagoia": {
        "schema": "SCIA",
        "appsettings": [
            os.path.join(PROYECTOS_ROOT, "SANTIAGOIA", "SantiagoConectaIA", "SantiagoConectaIA.API", "appsettings.Development.json"),
            os.path.join(PROYECTOS_ROOT, "SANTIAGOIA", "SantiagoConectaIA", "SantiagoConectaIA.API", "appsettings.json"),
        ],
    },
    "plantillapwa": {
        "schema": "dbo",
        "appsettings": [
            os.path.join(PROYECTOS_ROOT, "OficinaIA", "OficinaIA", "OficinaIA.API", "appsettings.Development.json"),
            os.path.join(PROYECTOS_ROOT, "PlantillaPWA", "TemplatePWA", "TemplatePWA.API", "appsettings.Development.json"),
            os.path.join(PROYECTOS_ROOT, "PlantillaPWA", "TemplatePWA", "TemplatePWA.API", "appsettings.json"),
        ],
    },
}

FORBIDDEN_REGEX = re.compile(
    r"\b("
    r"INSERT|UPDATE|DELETE|MERGE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|DENY|"
    r"BACKUP|RESTORE|DBCC|SHUTDOWN|KILL|OPENROWSET|OPENDATASOURCE|BULK|"
    r"EXEC|EXECUTE|sp_executesql|xp_cmdshell|INTO"
    r")\b",
    re.IGNORECASE,
)


def strip_comments_and_strings(sql: str) -> str:
    # Remove block comments /* ... */
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    # Remove line comments -- ...
    sql = re.sub(r"--[^\r\n]*", " ", sql)
    # Neutralize single-quoted string literals '...' so words inside strings don't false-trigger,
    # while keeping structure safe
    sql = re.sub(r"N?'(?:''|[^'])*'", "''", sql)
    return sql


def validate_readonly_sql(sql: str) -> None:
    cleaned = strip_comments_and_strings(sql).strip()
    if not cleaned:
        raise ValueError("La consulta SQL está vacía.")

    # Must start with SELECT or WITH (CTE)
    if not re.match(r"^(SELECT|WITH)\b", cleaned, re.IGNORECASE):
        raise ValueError(
            "BLOQUEADO POR SEGURIDAD READ-ONLY: Solo se permiten sentencias que inicien con SELECT o WITH. "
            "Para ver el código de un SP usa OBJECT_DEFINITION(OBJECT_ID('ESQUEMA.spNombre')) dentro de un SELECT."
        )

    match = FORBIDDEN_REGEX.search(cleaned)
    if match:
        keyword = match.group(1).upper()
        raise ValueError(
            f"BLOQUEADO POR SEGURIDAD READ-ONLY: La palabra clave '{keyword}' está estrictamente prohibida. "
            "Los agentes tienen PROHIBIDO escribir o ejecutar SPs en la base de datos. "
            f"Guarda cualquier cambio SQL en {os.path.join(PROYECTOS_ROOT, 'agentes', 'scripts-sql-pendientes', '<proyecto>')} para revisión humana."
        )


def parse_conn_string(conn_str: str) -> dict:
    parts = {}
    for item in conn_str.split(";"):
        if "=" in item:
            k, v = item.split("=", 1)
            parts[k.strip().lower()] = v.strip()
    return parts


def load_connection(project_key: str) -> tuple[dict, str]:
    cfg = PROJECT_CONFIG.get(project_key.lower())
    if not cfg:
        raise ValueError(f"Proyecto desconocido '{project_key}'. Usa: {', '.join(PROJECT_CONFIG.keys())}")

    for path in cfg["appsettings"]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            conn_str = data.get("ConnectionStrings", {}).get("EngramaCloudConnection", "")
            if conn_str:
                return parse_conn_string(conn_str), cfg["schema"]
    raise FileNotFoundError(f"No se encontró appsettings.json con EngramaCloudConnection para {project_key}.")


def build_preset_query(mode: str, schema: str, target_name: str | None) -> str:
    if mode == "overview":
        return f"""
SELECT 'TABLE' AS TipoObjeto, t.name AS Nombre
FROM sys.tables t
INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE s.name = '{schema}'
UNION ALL
SELECT 'STORED_PROCEDURE' AS TipoObjeto, p.name AS Nombre
FROM sys.procedures p
INNER JOIN sys.schemas s ON p.schema_id = s.schema_id
WHERE s.name = '{schema}'
UNION ALL
SELECT 'TABLE_TYPE_UDTT' AS TipoObjeto, tt.name AS Nombre
FROM sys.table_types tt
INNER JOIN sys.schemas s ON tt.schema_id = s.schema_id
WHERE s.name = '{schema}'
ORDER BY TipoObjeto, Nombre;
"""
    if mode == "table":
        if not target_name or not re.match(r"^[A-Za-z0-9_]+$", target_name):
            raise ValueError("Debes indicar --name NombreTabla válido.")
        return f"""
SELECT
    c.column_id AS Orden,
    c.name AS Columna,
    ty.name AS TipoDato,
    c.max_length AS MaxLen,
    c.precision AS Precision,
    c.scale AS Escala,
    c.is_nullable AS EsNullable,
    c.is_identity AS EsIdentity
FROM sys.columns c
INNER JOIN sys.tables t ON c.object_id = t.object_id
INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
INNER JOIN sys.types ty ON c.user_type_id = ty.user_type_id
WHERE s.name = '{schema}' AND t.name = '{target_name}'
ORDER BY c.column_id;
"""
    if mode == "udtt":
        if not target_name or not re.match(r"^[A-Za-z0-9_]+$", target_name):
            raise ValueError("Debes indicar --name NombreDT válido.")
        return f"""
SELECT
    c.column_id AS Orden,
    c.name AS Columna,
    ty.name AS TipoDato,
    c.max_length AS MaxLen,
    c.is_nullable AS EsNullable
FROM sys.table_types tt
INNER JOIN sys.schemas s ON tt.schema_id = s.schema_id
INNER JOIN sys.columns c ON tt.type_table_object_id = c.object_id
INNER JOIN sys.types ty ON c.user_type_id = ty.user_type_id
WHERE s.name = '{schema}' AND tt.name = '{target_name}'
ORDER BY c.column_id;
"""
    if mode == "sp":
        if not target_name or not re.match(r"^[A-Za-z0-9_]+$", target_name):
            raise ValueError("Debes indicar --name spNombre válido.")
        return f"""
SELECT OBJECT_DEFINITION(p.object_id) AS DefinicionSP
FROM sys.procedures p
INNER JOIN sys.schemas s ON p.schema_id = s.schema_id
WHERE s.name = '{schema}' AND p.name = '{target_name}';
"""
    raise ValueError(f"Modo desconocido: {mode}")


def main():
    parser = argparse.ArgumentParser(description="Consulta SQL 100% Read-Only para Agentes Engrama.")
    parser.add_argument("--project", required=True, choices=list(PROJECT_CONFIG.keys()), help="Proyecto destino")
    parser.add_argument("--schema", help="Sobrescribir esquema (por defecto usa el del proyecto: GCIA, CNIA, SCIA)")
    parser.add_argument("--mode", choices=["overview", "table", "udtt", "sp", "query"], default="overview")
    parser.add_argument("--name", help="Nombre de tabla, UDTT (DT*) o SP cuando mode != query")
    parser.add_argument("--sql", help="Consulta SELECT personalizada (solo cuando mode=query)")
    parser.add_argument("--top", type=int, default=200, help="Límite de caracteres por columna (0 = sin límite para ver SPs)")
    args = parser.parse_args()

    try:
        conn, default_schema = load_connection(args.project)
        schema = args.schema or default_schema
        if not re.match(r"^[A-Za-z0-9_]+$", schema):
            raise ValueError("Nombre de esquema inválido.")

        if args.mode == "query":
            if not args.sql:
                raise ValueError("Debes proporcionar --sql con una sentencia SELECT.")
            query = args.sql
        else:
            query = build_preset_query(args.mode, schema, args.name)

        validate_readonly_sql(query)

        # Wrap inside an implicit rollback / read-uncommitted block for extra DB safety
        safe_sql = f"SET NOCOUNT ON;\nSET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;\n{query}"

        server = conn.get("data source") or conn.get("server")
        database = conn.get("initial catalog") or conn.get("database")
        user = conn.get("user id") or conn.get("uid")
        password = conn.get("password") or conn.get("pwd")

        cmd = [
            "sqlcmd",
            "-S", server,
            "-d", database,
            "-U", user,
            "-P", password,
            "-K", "ReadOnly",  # ApplicationIntent=ReadOnly
            "-s", " | ",
        ]
        if args.mode == "sp" or args.top == 0:
            cmd.extend(["-y", "0"])
        else:
            cmd.extend(["-W", "-w", "65535"])

        cmd.extend(["-Q", safe_sql])

        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
        if proc.returncode != 0:
            print(f"ERROR SQLCMD (código {proc.returncode}):\n{proc.stderr}\n{proc.stdout}", file=sys.stderr)
            sys.exit(proc.returncode)

        print(f"=== [READ-ONLY DB] Proyecto: {args.project} | Esquema: {schema} | Modo: {args.mode} ===")
        print(proc.stdout.strip())

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
