#!/usr/bin/env python3
r"""
Firewall de Base de Datos Bilingüe (Antigravity `PreToolUse` + Cursor `beforeShellExecution`).
Funciona en cualquier ruta (`PROYECTOS_ROOT` autodetectado):
1. Bloquea cualquier uso directo de `sqlcmd`, `Invoke-Sqlcmd`, `pyodbc`, `SqlConnection`, etc.
   fuera del lector oficial `agentes/herramientas/db_readonly_query.py`.
2. Bloquea cualquier sentencia de mutación SQL (INSERT, UPDATE, DELETE, ALTER, CREATE, DROP, TRUNCATE, MERGE, EXEC)
   pasada por línea de comandos hacia base de datos.
"""
import json
import os
import re
import sys

PROYECTOS_ROOT = os.environ.get("PROYECTOS_ROOT") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

DIRECT_DB_CLIENTS = re.compile(
    r"\b(sqlcmd|sqlcmd\.exe|Invoke-Sqlcmd|System\.Data\.SqlClient|Microsoft\.Data\.SqlClient|pyodbc|pymssql)\b",
    re.IGNORECASE,
)

OFFICIAL_READER = re.compile(
    r"db_readonly_query\.py",
    re.IGNORECASE,
)

SQL_WRITE_KEYWORDS = re.compile(
    r"--sql\s+.*?\b(INSERT|UPDATE|DELETE|MERGE|DROP|ALTER|CREATE|TRUNCATE|EXEC|EXECUTE|GRANT|REVOKE)\b",
    re.IGNORECASE | re.DOTALL,
)


def is_cursor_payload(payload: dict) -> bool:
    if payload.get("hook_event_name") == "beforeShellExecution":
        return True
    if "command" in payload and "toolCall" not in payload:
        return True
    return False


def respond_allow(cursor_mode: bool) -> None:
    if cursor_mode:
        print(json.dumps({"permission": "allow"}))
    else:
        print(json.dumps({"decision": "allow"}))


def respond_deny(cursor_mode: bool, reason: str) -> None:
    if cursor_mode:
        print(json.dumps({
            "permission": "deny",
            "user_message": "Bloqueado por Firewall SQL Read-Only de AgentesConecta.",
            "agent_message": reason,
        }))
    else:
        print(json.dumps({
            "decision": "deny",
            "reason": reason,
        }))


def main():
    cursor_mode = False
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            respond_allow(False)
            return

        payload = json.loads(raw)
        cursor_mode = is_cursor_payload(payload)

        if cursor_mode:
            cmd = payload.get("command", "") or ""
        else:
            tool_call = payload.get("toolCall", {}) or {}
            if tool_call.get("name", "") != "run_command":
                respond_allow(False)
                return
            args = tool_call.get("args", {}) or {}
            cmd = args.get("CommandLine", "") or ""

        reader_path = os.path.join(PROYECTOS_ROOT, "agentes", "herramientas", "db_readonly_query.py")
        sql_pending_dir = os.path.join(PROYECTOS_ROOT, "agentes", "scripts-sql-pendientes", "<Proyecto>")

        if DIRECT_DB_CLIENTS.search(cmd) and not OFFICIAL_READER.search(cmd):
            respond_deny(
                cursor_mode,
                (
                    "BLOQUEADO POR FIREWALL SQL DE AGENTES: Está prohibido usar clientes SQL directos (sqlcmd / Invoke-Sqlcmd / SqlClient). "
                    f"Usa exclusivamente el lector 100% Read-Only: `python \"{reader_path}\" --project <proyecto> --mode <overview|table|udtt|sp|query>`. "
                    f"Todo cambio de BD debe guardarse como archivo .sql en `{sql_pending_dir}` para revisión y ejecución manual."
                ),
            )
            return

        if OFFICIAL_READER.search(cmd) and SQL_WRITE_KEYWORDS.search(cmd):
            respond_deny(
                cursor_mode,
                (
                    "BLOQUEADO POR FIREWALL SQL DE AGENTES: Se detectó una sentencia de escritura o EXEC en `--sql`. "
                    f"Solo se permiten consultas SELECT de lectura. Guarda los scripts de modificación en `{sql_pending_dir}`."
                ),
            )
            return

        respond_allow(cursor_mode)

    except Exception as exc:
        if cursor_mode:
            respond_deny(True, f"Error validando comando en firewall SQL: {exc}")
        else:
            respond_allow(False)


if __name__ == "__main__":
    main()
