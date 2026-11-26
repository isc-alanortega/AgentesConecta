#!/usr/bin/env python3
r"""
Ejecutor Oficial Dual-IDE (Antigravity CLI `agy` + Cursor CLI `cursor-agent` / `agent`)
Cuando el Patrón o el equipo aprueba una orden desde Conecta Software Oficina:
1. Autodetecta `PROYECTOS_ROOT` (funciona en D:\Proyectos, C:\Conecta o cualquier ruta del compañero).
2. Prepara una rama y carpeta aislada `git worktree` en `<PROYECTOS_ROOT>\.worktrees\<Folio>`.
3. Detecta automáticamente qué motor CLI usar:
   - Si existe `agy.exe` (Antigravity) -> ejecuta `agy --mode auto --add-dir <ROOT> --output-format stream-json --print ...`
   - Si existe `cursor-agent` / `agent` (Cursor) -> ejecuta `cursor-agent -p --force --output-format stream-json ...`
   (También se puede forzar con `--cli agy` o `--cli cursor` o variable `CONECTA_AGENT_CLI`).
4. Transmite progreso en vivo al mundo 3D, verifica `dotnet build` (`0 errores`) y hace commit en la rama aislada.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

PROYECTOS_ROOT = os.environ.get("PROYECTOS_ROOT") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

DEFAULT_AGY_PATHS = [
    os.path.expanduser(r"~\.gemini\bin\agy.exe"),
    os.path.expanduser(r"~\AppData\Local\agy\bin\agy.exe"),
]

DEFAULT_CURSOR_PATHS = [
    os.path.expanduser(r"~\AppData\Local\Programs\cursor\resources\app\bin\cursor-agent.cmd"),
    os.path.expanduser(r"~\AppData\Local\cursor-agent\cursor-agent.exe"),
]


def resolve_agent_cli(preferred: str = "auto") -> tuple[str, str]:
    """Devuelve ('agy' | 'cursor', ruta_ejecutable)."""
    pref = (preferred or os.environ.get("CONECTA_AGENT_CLI") or "auto").lower()

    def find_agy():
        for p in DEFAULT_AGY_PATHS:
            if os.path.isfile(p):
                return p
        return shutil.which("agy") or shutil.which("agy.exe")

    def find_cursor():
        for p in DEFAULT_CURSOR_PATHS:
            if os.path.isfile(p):
                return p
        return shutil.which("cursor-agent") or shutil.which("agent")

    if pref == "cursor":
        c = find_cursor()
        if c:
            return "cursor", c
        raise FileNotFoundError("Se solicitó Cursor CLI pero no se encontró 'cursor-agent' ni 'agent' en PATH.")

    if pref == "agy":
        a = find_agy()
        if a:
            return "agy", a
        raise FileNotFoundError("Se solicitó Antigravity CLI pero no se encontró 'agy.exe'.")

    # Auto-detect: preferir agy si existe, si no usar Cursor CLI
    a = find_agy()
    if a:
        return "agy", a
    c = find_cursor()
    if c:
        return "cursor", c

    raise FileNotFoundError(
        "No se encontró ni Antigravity CLI ('agy') ni Cursor CLI ('cursor-agent' / 'agent') instalados en este equipo."
    )


def run_cmd(cmd: list[str], cwd: str | None = None, timeout: int = 180) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return proc.returncode, out.strip()


def post_live_progress(
    api_url: str | None,
    bridge_secret: str,
    propuesta_id: int,
    agente_code: str,
    thought: str,
    branch: str,
    worktree_dir: str,
    estatus: str = "PROGRAMANDO_WORKTREE",
    zona: str = "WORKTREE_LAB",
    anim: str = "BUILDING",
    sql_path: str = "",
    build_ok: bool = True,
    resumen: str = "",
) -> None:
    if not api_url or propuesta_id <= 0:
        return
    url = api_url.rstrip("/") + "/api/Propuesta/PostReportarResultadoBridge"
    payload = {
        "vchBridgeSecret": bridge_secret,
        "iIdPropuesta": propuesta_id,
        "vchCodigoAgente": agente_code,
        "vchEstatus": estatus,
        "vchZonaActual": zona,
        "vchEstadoAnimacion": anim,
        "nvchPensamientoActual": thought[:480],
        "vchRamaGit": branch,
        "nvchRutaWorktree": worktree_dir,
        "nvchRutaScriptSqlPendiente": sql_path,
        "bCompilacionExitosa": build_ok,
        "nvchResumenEjecucion": resumen,
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=6):
            pass
    except Exception:
        pass


def map_project_folder(project_name: str) -> tuple[str, str]:
    p = project_name.strip()
    low = p.lower()
    if "geo" in low:
        return os.path.join(PROYECTOS_ROOT, "GeoConecta"), "GeoConecta"
    if "landing" in low:
        for cand in ["Repo Conecta Negocios Landing", "ConectaNegociosFrontPage", "ConectaLanding"]:
            full = os.path.join(PROYECTOS_ROOT, cand)
            if os.path.isdir(full):
                return full, "ConectaLanding"
        return os.path.join(PROYECTOS_ROOT, "Repo Conecta Negocios Landing"), "ConectaLanding"
    if "negocio" in low:
        return os.path.join(PROYECTOS_ROOT, "ConectaNegocios"), "ConectaNegocios"
    if "santiago" in low:
        for cand in ["SANTIAGOIA", "SantiagoConectaIA"]:
            full = os.path.join(PROYECTOS_ROOT, cand)
            if os.path.isdir(full):
                return full, "SANTIAGOIA"
        return os.path.join(PROYECTOS_ROOT, "SANTIAGOIA"), "SANTIAGOIA"
    if "test" in low or "qa" in low or "e2e" in low:
        for cand in ["Test Proyecto", "PruebasE2E", "E2E"]:
            full = os.path.join(PROYECTOS_ROOT, cand)
            if os.path.isdir(full):
                return full, "TestProyecto"
        return os.path.join(PROYECTOS_ROOT, "Test Proyecto"), "TestProyecto"
    return os.path.join(PROYECTOS_ROOT, p), re.sub(r"\s+", "", p)


def extract_thought_from_stream_line(line: str) -> str | None:
    line = line.strip()
    if not line.startswith("{"):
        return None
    try:
        ev = json.loads(line)
    except Exception:
        return None

    raw_str = json.dumps(ev, ensure_ascii=False)
    for tool_key, label in [
        ("write_file", "✍️ Creando archivo"),
        ("edit_file", "🛠️ Editando código"),
        ("Write", "✍️ Creando archivo"),
        ("Edit", "🛠️ Editando código"),
        ("run_command", "🔨 Ejecutando validación"),
        ("Shell", "🔨 Ejecutando comando"),
        ("read_file", "📖 Analizando código fuente"),
    ]:
        if f'"{tool_key}"' in raw_str:
            m_path = re.search(r'"(?:Path|path|file_path)"\s*:\s*"([^"]+)"', raw_str)
            if m_path:
                fname = os.path.basename(m_path.group(1).replace("\\\\", "\\"))
                return f"{label}: {fname} en Worktree Lab..."
            m_sum = re.search(r'"toolSummary"\s*:\s*"([^"]+)"', raw_str)
            if m_sum:
                return f"{label}: {m_sum.group(1)}..."
            return f"{label} en el Worktree aislado..."

    return None


def prepare_worktree(repo_dir: str, worktree_dir: str, branch_name: str) -> str:
    os.makedirs(os.path.dirname(worktree_dir), exist_ok=True)
    run_cmd(["git", "config", "--global", "--add", "safe.directory", repo_dir.replace("\\", "/")])

    if os.path.isdir(worktree_dir) and os.path.exists(os.path.join(worktree_dir, ".git")):
        run_cmd(["git", "config", "--global", "--add", "safe.directory", worktree_dir.replace("\\", "/")])
        return f"Worktree reutilizado en {worktree_dir} ({branch_name})"

    if os.path.isdir(worktree_dir):
        shutil.rmtree(worktree_dir, ignore_errors=True)

    code_br, _ = run_cmd(["git", "-C", repo_dir, "rev-parse", "--verify", branch_name])
    if code_br == 0:
        rc, out = run_cmd(["git", "-C", repo_dir, "worktree", "add", worktree_dir, branch_name])
    else:
        rc, out = run_cmd(["git", "-C", repo_dir, "worktree", "add", worktree_dir, "-b", branch_name])

    if rc != 0:
        raise RuntimeError(f"No se pudo crear el git worktree ({rc}): {out}")

    run_cmd(["git", "config", "--global", "--add", "safe.directory", worktree_dir.replace("\\", "/")])
    return f"Worktree creado en {worktree_dir} sobre rama {branch_name}"


def build_agent_prompt(
    agente_code: str,
    proyecto: str,
    folio: str,
    titulo: str,
    worktree_dir: str,
    plan_file_in_wt: str,
    sql_target_file: str,
    nota_patron: str,
) -> str:
    agent_md = os.path.join(PROYECTOS_ROOT, "agentes", "plugins", "ecosistema-engrama", "agents", f"{agente_code}.md")
    plantilla_md = os.path.join(PROYECTOS_ROOT, "PlantillaPWA", "AGENTS.md")
    reader_py = os.path.join(PROYECTOS_ROOT, "agentes", "herramientas", "db_readonly_query.py")
    nota_bloque = f"\nNota adicional directa del Patrón: {nota_patron}\n" if nota_patron else ""

    return f"""MODO TURBO AUTÓNOMO APROBADO — FOLIO {folio}
Estás ejecutando una orden YA APROBADA desde Conecta Software Oficina para el proyecto '{proyecto}'.
{nota_bloque}
REGLAS ESTRICTAS DE EJECUCIÓN:
1. Lee primero tu definición de especialista en `{agent_md}` (y si existe `{plantilla_md}`), más el Plan aprobado en `{plan_file_in_wt}` (Título: "{titulo}").
2. TRABAJA EXCLUSIVAMENTE DENTRO DE ESTE WORKTREE AISLADO: `{worktree_dir}`.
   PROHIBIDO editar archivos fuera de `{worktree_dir}` (con la única excepción del archivo SQL pendiente del punto 3).
3. BASE DE DATOS 100% SOLO LECTURA:
   - Si necesitas consultar tablas, columnas o SPs actuales en SQL Server, usa únicamente:
     `python "{reader_py}" --project <geoconecta|conectanegocios|santiagoia> --mode <overview|table|sp|query>`
   - Si la tarea requiere cambios u optimizaciones SQL, ESCRIBE el script SQL completo, real e idempotente en:
     `{sql_target_file}`
   - NUNCA ejecutes escrituras contra la base de datos.
4. PROGRAMACIÓN COMPLETA DE CAPAS:
   - Programa TODOS los archivos reales necesarios (`.cs`, `.razor`, `.html`, `.ts`) siguiendo Clean Architecture Engrama (`Share` -> `Infrastructure` -> `Domain` -> `Controller [HttpPost("Post...")]` -> `PWA Main*` + `docs/agentes/handoff-ui.md` si hay UI).
5. VERIFICACIÓN DE COMPILACIÓN:
   - Si tocaste código .NET en `{worktree_dir}`, ejecuta `dotnet build` sobre la solución/proyecto dentro de `{worktree_dir}` y corrige errores hasta dejar **0 Errores**.
6. Entrega un resumen breve en español listando los archivos creados/modificados.
"""


def main():
    parser = argparse.ArgumentParser(description="Ejecutor Dual-IDE (Antigravity / Cursor) sobre Git Worktrees.")
    parser.add_argument("--propuesta-id", type=int, default=0)
    parser.add_argument("--folio", required=True)
    parser.add_argument("--agente", required=True)
    parser.add_argument("--proyecto", required=True)
    parser.add_argument("--titulo", required=True)
    parser.add_argument("--plan-file", required=True)
    parser.add_argument("--nota-patron", default="")
    parser.add_argument("--api-url", default="")
    parser.add_argument("--bridge-secret", default="OFIA-LOCAL-BRIDGE-2026")
    parser.add_argument("--cli", choices=["auto", "agy", "cursor"], default="auto")
    parser.add_argument("--timeout-sec", type=int, default=900)
    args = parser.parse_args()

    cli_kind, cli_bin = resolve_agent_cli(args.cli)
    repo_dir, sql_sub = map_project_folder(args.proyecto)
    short_agent = args.agente.replace("agente-", "")
    branch_name = f"agentes/{short_agent}/{args.folio.lower()}"
    worktree_dir = os.path.join(PROYECTOS_ROOT, ".worktrees", args.folio)

    with open(args.plan_file, "r", encoding="utf-8-sig") as f:
        plan_markdown = f.read()

    post_live_progress(
        args.api_url, args.bridge_secret, args.propuesta_id, args.agente,
        f"🔧 Creando Git Worktree aislado ({branch_name})...", branch_name, worktree_dir
    )

    wt_msg = prepare_worktree(repo_dir, worktree_dir, branch_name)

    docs_dir = os.path.join(worktree_dir, "docs", "agentes")
    os.makedirs(docs_dir, exist_ok=True)
    plan_in_wt = os.path.join(docs_dir, f"PLAN-{args.folio}.md")
    with open(plan_in_wt, "w", encoding="utf-8") as f:
        f.write(plan_markdown)

    sql_dir = os.path.join(PROYECTOS_ROOT, "agentes", "scripts-sql-pendientes", sql_sub)
    os.makedirs(sql_dir, exist_ok=True)
    ts_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    sql_target_file = os.path.join(sql_dir, f"{ts_str}_{args.folio}.sql")

    prompt = build_agent_prompt(
        args.agente, args.proyecto, args.folio, args.titulo,
        worktree_dir, plan_in_wt, sql_target_file, args.nota_patron
    )

    ide_label = "Antigravity CLI" if cli_kind == "agy" else "Cursor Agent CLI"
    post_live_progress(
        args.api_url, args.bridge_secret, args.propuesta_id, args.agente,
        f"🤖 {ide_label} programando {args.folio} en Worktree Lab...", branch_name, worktree_dir
    )

    if cli_kind == "agy":
        cmd = [
            cli_bin,
            "--mode", "auto",
            "--add-dir", PROYECTOS_ROOT,
            "--output-format", "stream-json",
            "--print", prompt,
        ]
    else:
        cmd = [
            cli_bin,
            "-p",
            "--force",
            "--output-format", "stream-json",
            prompt,
        ]

    proc = subprocess.Popen(
        cmd,
        cwd=worktree_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    last_push_time = 0.0
    last_thought = ""
    start_ts = time.time()

    assert proc.stdout is not None
    for raw_line in proc.stdout:
        if time.time() - start_ts > args.timeout_sec:
            proc.kill()
            raise TimeoutError(f"Tiempo máximo excedido ({args.timeout_sec}s) ejecutando {ide_label}.")

        clean_line = raw_line.strip()
        thought = extract_thought_from_stream_line(clean_line)
        now = time.time()
        if thought and thought != last_thought and (now - last_push_time) >= 2.5:
            last_thought = thought
            last_push_time = now
            post_live_progress(
                args.api_url, args.bridge_secret, args.propuesta_id, args.agente,
                thought, branch_name, worktree_dir
            )

    exit_code = proc.wait(timeout=30)

    _, status_out = run_cmd(["git", "-C", worktree_dir, "status", "-s"])
    changed_files = [ln.strip() for ln in status_out.splitlines() if ln.strip()]

    if changed_files:
        run_cmd(["git", "-C", worktree_dir, "add", "-A"])
        run_cmd([
            "git", "-C", worktree_dir, "commit",
            "-m", f"feat({args.folio.lower()}): {args.titulo[:65]} [{ide_label} {args.agente}]"
        ])

    sql_final = sql_target_file if os.path.isfile(sql_target_file) else ""

    build_ok = (exit_code == 0)
    touched_dotnet = any(f.endswith((".cs", ".razor", ".csproj")) for f in changed_files)
    build_note = ""
    if touched_dotnet:
        post_live_progress(
            args.api_url, args.bridge_secret, args.propuesta_id, args.agente,
            "🔬 Verificando dotnet build final con 0 errores...", branch_name, worktree_dir
        )
        slns = []
        for root_w, _, files_w in os.walk(worktree_dir):
            for fw in files_w:
                if fw.endswith((".sln", ".slnx")):
                    slns.append(os.path.join(root_w, fw))
        if slns:
            b_rc, b_out = run_cmd(["dotnet", "build", slns[0], "--nologo", "-v", "quiet"], cwd=worktree_dir, timeout=240)
            build_ok = (b_rc == 0)
            build_note = "dotnet build: 0 Errores ✅" if build_ok else f"dotnet build reportó código {b_rc}:\n{b_out[-600:]}"

    files_summary = ", ".join(changed_files[:12]) if changed_files else "Plan y análisis procesados"
    if len(changed_files) > 12:
        files_summary += f" (+{len(changed_files) - 12} más)"

    summary_lines = [
        f"Motor ejecutado: {ide_label}",
        wt_msg,
        f"Archivos trabajados ({len(changed_files)}): {files_summary}",
    ]
    if build_note:
        summary_lines.append(build_note)
    if sql_final:
        summary_lines.append(f"Script SQL pendiente listo: {sql_final}")

    result_obj = {
        "ok": build_ok,
        "exit_code": exit_code,
        "branch": branch_name,
        "worktree": worktree_dir,
        "sql_file": sql_final,
        "changed_count": len(changed_files),
        "summary": "\n".join(summary_lines),
    }

    print("===RESULT_JSON_START===")
    print(json.dumps(result_obj, ensure_ascii=False))
    print("===RESULT_JSON_END===")
    sys.exit(0 if build_ok else 1)


if __name__ == "__main__":
    main()
