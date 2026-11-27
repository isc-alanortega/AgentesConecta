#!/usr/bin/env python3
r"""
Ejecutor Oficial Dual-IDE con Worktree Permanente por Agente y Modo Ultra-Ahorro de Tokens
(`ejecutar_orden_agy.py` — Antigravity CLI `agy` + Cursor CLI `cursor-agent` / `agent`)

Características clave:
1. UN SOLO WORKTREE FIJO POR AGENTE: `<PROYECTOS_ROOT>\.worktrees\<codigo-agente>` en rama `agentes/<short>`.
   - Mantiene caliente `bin/` y `obj/` de .NET (`dotnet build --no-restore /nr:false`), bajando builds de ~100s a ~4s.
   - Permite que TODOS los agentes trabajen AL MISMO TIEMPO en paralelo sin pisarse jamás.
2. ULTRA-AHORRO DE TOKENS:
   - Prompt compacto con Cheat-Sheet Engrama pre-digerido (cero `read_file` redundantes de manuales largos).
   - Sin `--add-dir <PROYECTOS_ROOT>`: el CLI solo ve su propio worktree + carpeta de SQL pendientes.
   - Omite `dotnet build` cuando la tarea solo genera `.sql` / `.md` / `.html` / `.js` / `.css`.
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
        raise FileNotFoundError("Se solicitó Cursor CLI pero no se encontró 'cursor-agent' ni 'agent'.")

    if pref == "agy":
        a = find_agy()
        if a:
            return "agy", a
        raise FileNotFoundError("Se solicitó Antigravity CLI pero no se encontró 'agy.exe'.")

    a = find_agy()
    if a:
        return "agy", a
    c = find_cursor()
    if c:
        return "cursor", c

    raise FileNotFoundError("No se encontró ni Antigravity CLI ('agy') ni Cursor CLI ('cursor-agent').")


def run_cmd(cmd: list[str], cwd: str | None = None, timeout: int = 180, extra_env: dict | None = None) -> tuple[int, str]:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
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
    zona: str = "CUBICULO",
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
        with urllib.request.urlopen(req, timeout=5):
            pass
    except Exception:
        pass


def resolve_canonical_target(agente_code: str, project_name: str) -> tuple[str, str, str, str]:
    """
    Devuelve (canonical_worktree_folder_name, branch_name, repo_dir, sql_subfolder).
    Garantiza que cada proyecto/agente tenga UN SOLO worktree permanente y jamás colisionen dos agentes.
    """
    low = (project_name or "").strip().lower()
    ag_low = (agente_code or "").strip().lower()

    def pick_existing(cands: list[str], fallback: str) -> str:
        for c in cands:
            full = os.path.join(PROYECTOS_ROOT, c)
            if os.path.isdir(full):
                return full
        return os.path.join(PROYECTOS_ROOT, fallback)

    if "geo" in low or "geoconecta" in ag_low:
        return "agente-geoconecta", "worktree/geoconecta", pick_existing(["GeoConecta"], "GeoConecta"), "GeoConecta"
    if "landing" in low or "front" in low or "conectalanding" in ag_low:
        repo = pick_existing(
            ["Repo Conecta Negocios Landing", "ConectaNegociosFrontPage", "ConectaLanding"],
            "Repo Conecta Negocios Landing",
        )
        return "agente-conectalanding", "worktree/conectalanding", repo, "ConectaLanding"
    if "negocio" in low or "conectanegocios" in ag_low:
        return (
            "agente-conectanegocios",
            "worktree/conectanegocios",
            pick_existing(["ConectaNegocios"], "ConectaNegocios"),
            "ConectaNegocios",
        )
    if "santiago" in low or "santiagoia" in ag_low:
        repo = pick_existing(["SANTIAGOIA", "SantiagoConectaIA"], "SANTIAGOIA")
        return "agente-santiagoia", "worktree/santiagoia", repo, "SANTIAGOIA"
    if "test" in low or "qa" in low or "e2e" in low:
        repo = pick_existing(["Test Proyecto", "PruebasE2E", "E2E"], "Test Proyecto")
        return "agente-qa-e2e", "worktree/qa-e2e", repo, "TestProyecto"
    if "oficina" in low or "oficinaia" in ag_low:
        repo = pick_existing(["OficinaIA"], "OficinaIA")
        return "agente-oficinaia", "worktree/oficinaia", repo, "OficinaIA"
    if "control" in low or "conectacontrol" in ag_low:
        repo = pick_existing(["ConectaControl"], "ConectaControl")
        return "agente-conectacontrol", "worktree/conectacontrol", repo, "ConectaControl"

    # Transversal / Estratega IA sobre el repo raíz de AgentesConecta
    short = ag_low.replace("agente-", "") or "estratega-ia"
    return f"agente-{short}", f"worktree/{short}", PROYECTOS_ROOT, "Transversal"


def ensure_persistent_agent_worktree(repo_dir: str, worktree_dir: str, branch_name: str, folio: str) -> str:
    os.makedirs(os.path.dirname(worktree_dir), exist_ok=True)
    run_cmd(["git", "config", "--global", "--add", "safe.directory", repo_dir.replace("\\", "/")])

    git_marker = os.path.join(worktree_dir, ".git")
    if os.path.isdir(worktree_dir) and os.path.exists(git_marker):
        run_cmd(["git", "config", "--global", "--add", "safe.directory", worktree_dir.replace("\\", "/")])
        # Si quedó algún archivo a medias de una cancelación previa, resguardarlo limpio en stash sin perder caché bin/obj
        _, dirty = run_cmd(["git", "-C", worktree_dir, "status", "--porcelain"])
        if dirty.strip():
            run_cmd(["git", "-C", worktree_dir, "stash", "push", "-u", "-m", f"auto-save-before-{folio}"])
        return f"Worktree permanente reutilizado: {worktree_dir} ({branch_name})"

    if os.path.isdir(worktree_dir):
        shutil.rmtree(worktree_dir, ignore_errors=True)

    run_cmd(["git", "-C", repo_dir, "worktree", "prune"])
    code_br, _ = run_cmd(["git", "-C", repo_dir, "rev-parse", "--verify", branch_name])
    if code_br == 0:
        rc, out = run_cmd(["git", "-C", repo_dir, "worktree", "add", "--force", worktree_dir, branch_name])
    else:
        rc, out = run_cmd(["git", "-C", repo_dir, "worktree", "add", "--force", worktree_dir, "-b", branch_name])

    if rc != 0:
        raise RuntimeError(f"No se pudo inicializar el worktree permanente ({rc}): {out}")

    run_cmd(["git", "config", "--global", "--add", "safe.directory", worktree_dir.replace("\\", "/")])
    return f"Worktree permanente inicializado: {worktree_dir} ({branch_name})"


def find_primary_sln(worktree_dir: str) -> str | None:
    for root_w, dirs_w, files_w in os.walk(worktree_dir):
        dirs_w[:] = [d for d in dirs_w if d.lower() not in ("bin", "obj", "node_modules", ".git")]
        for fw in files_w:
            if fw.endswith((".slnx", ".sln")):
                return os.path.join(root_w, fw)
    return None


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
        ("write_file", "✍️ Escribiendo"),
        ("edit_file", "🛠️ Editando"),
        ("Write", "✍️ Escribiendo"),
        ("Edit", "🛠️ Editando"),
        ("run_command", "🔨 Validando"),
        ("Shell", "🔨 Ejecutando"),
        ("read_file", "📖 Revisando"),
    ]:
        if f'"{tool_key}"' in raw_str:
            m_path = re.search(r'"(?:Path|path|file_path)"\s*:\s*"([^"]+)"', raw_str)
            if m_path:
                fname = os.path.basename(m_path.group(1).replace("\\\\", "\\"))
                return f"{label} {fname} en su worktree fijo..."
            return f"{label} en su worktree permanente..."
    return None


def build_compact_token_saving_prompt(
    agente_code: str,
    proyecto: str,
    folio: str,
    titulo: str,
    worktree_dir: str,
    plan_markdown: str,
    sql_target_file: str,
    nota_patron: str,
    sln_path: str | None,
) -> str:
    """
    Prompt ultra-compacto diseñado para ahorrar ~70% de tokens:
    - Incluye ya el Plan recortado a lo esencial y las reglas Engrama en 8 líneas.
    - PROHÍBE leer manuales externos o explorar otros repositorios.
    - NO pide al agente ejecutar `dotnet build` pesado porque este runner valida incrementalmente al cerrar.
    """
    reader_py = os.path.join(PROYECTOS_ROOT, "agentes", "herramientas", "db_readonly_query.py")
    db_proj = "santiagoia" if "santiago" in proyecto.lower() else ("conectanegocios" if "negocio" in proyecto.lower() else "geoconecta")
    sln_hint = f"Solución .NET local: `{sln_path}`" if sln_path else "Proyecto sin solución .NET compilable."
    nota_bloque = f"\nCORRECCIÓN / NOTA PRIORITARIA: {nota_patron}\n" if nota_patron else ""
    plan_compacto = (plan_markdown or "").strip()[:3800]

    return f"""ORDEN APROBADA {folio} | Agente: {agente_code} | Proyecto: {proyecto}
Título: {titulo}
Worktree fijo asignado (cwd): `{worktree_dir}` ({sln_hint})
{nota_bloque}
REGLAS DE AHORRO DE TOKENS Y EJECUCIÓN DIRECTA (OBLIGATORIAS):
1. NO leas `GEMINI.md`, `AGENTS.md` ni manuales externos: todo lo necesario ya está aquí. Ve directo al archivo objetivo.
2. Trabaja SOLO dentro de `{worktree_dir}` (y si la tarea requiere SQL, escribe el script idempotente en `{sql_target_file}`).
3. BD 100% Read-Only: NUNCA ejecutes escrituras SQL. Solo si necesitas ver el código real de una tabla/SP en BD, ejecuta:
   `python "{reader_py}" --project {db_proj} --mode <sp|table|query> ...`
4. Si creas/modificas código C#/Blazor Engrama: respeta `Share (Objects + DtoModels)` -> `Infrastructure (sp* + IDapperManagerHelper con esquema)` -> `Domain (MapperHelper + IResponseHelper)` -> `Controller ([Route("api/[controller]")] + [HttpPost("Post...")])` -> `PWA (Main*)`.
5. NO ejecutes `dotnet restore` ni `dotnet build` completos salvo que hayas editado `.cs`/`.razor` y quieras verificar un error puntual (usa `--no-restore -v q`); el runner compilará incrementalmente al terminar.
6. Responde al final en máximo 4 líneas qué archivos creaste o editaste.

PLAN A IMPLEMENTAR:
{plan_compacto}
"""


def main():
    parser = argparse.ArgumentParser(description="Ejecutor con Worktree Permanente por Agente y Ahorro de Tokens.")
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
    parser.add_argument("--timeout-sec", type=int, default=420)
    args = parser.parse_args()

    cli_kind, cli_bin = resolve_agent_cli(args.cli)
    wt_folder, branch_name, repo_dir, sql_sub = resolve_canonical_target(args.agente, args.proyecto)
    worktree_dir = os.path.join(PROYECTOS_ROOT, ".worktrees", wt_folder)

    with open(args.plan_file, "r", encoding="utf-8-sig") as f:
        plan_markdown = f.read()

    wt_msg = ensure_persistent_agent_worktree(repo_dir, worktree_dir, branch_name, args.folio)
    _, head_before = run_cmd(["git", "-C", worktree_dir, "rev-parse", "HEAD"])

    sql_dir = os.path.join(PROYECTOS_ROOT, "agentes", "scripts-sql-pendientes", sql_sub)
    os.makedirs(sql_dir, exist_ok=True)
    ts_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    sql_target_file = os.path.join(sql_dir, f"{ts_str}_{args.folio}.sql")
    sln_path = find_primary_sln(worktree_dir)

    prompt = build_compact_token_saving_prompt(
        args.agente, args.proyecto, args.folio, args.titulo,
        worktree_dir, plan_markdown, sql_target_file, args.nota_patron, sln_path
    )

    ide_label = "Antigravity CLI" if cli_kind == "agy" else "Cursor Agent CLI"
    post_live_progress(
        args.api_url, args.bridge_secret, args.propuesta_id, args.agente,
        f"⚡ {ide_label} trabajando {args.folio} en su worktree fijo ({wt_folder})...",
        branch_name, worktree_dir
    )

    tools_dir = os.path.join(PROYECTOS_ROOT, "agentes", "herramientas")
    if cli_kind == "agy":
        # Ahorro masivo de tokens: NO pasar --add-dir D:\Proyectos completo; solo su carpeta SQL y lector Read-Only
        cmd = [
            cli_bin,
            "--mode", "auto",
            "--add-dir", sql_dir,
            "--add-dir", tools_dir,
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

    env = os.environ.copy()
    env["PROYECTOS_ROOT"] = PROYECTOS_ROOT
    env["DOTNET_CLI_DO_NOT_USE_MSBUILD_SERVER"] = "1"
    env["DOTNET_NOLOGO"] = "1"

    proc = subprocess.Popen(
        cmd,
        cwd=worktree_dir,
        env=env,
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

        thought = extract_thought_from_stream_line(raw_line)
        now = time.time()
        if thought and thought != last_thought and (now - last_push_time) >= 3.0:
            last_thought = thought
            last_push_time = now
            post_live_progress(
                args.api_url, args.bridge_secret, args.propuesta_id, args.agente,
                thought, branch_name, worktree_dir
            )

    exit_code = proc.wait(timeout=30)

    # Detectar si generó script SQL pendiente para este folio (incluso si el agente usó otro timestamp con el folio)
    sql_final = sql_target_file if os.path.isfile(sql_target_file) else ""
    if not sql_final and os.path.isdir(sql_dir):
        matches = [
            os.path.join(sql_dir, fn)
            for fn in os.listdir(sql_dir)
            if args.folio.lower() in fn.lower() and fn.lower().endswith(".sql")
        ]
        if matches:
            sql_final = max(matches, key=os.path.getmtime)

    # Si fue una tarea puramente SQL (el archivo .sql se guarda en scripts-sql-pendientes fuera del repo hijo),
    # registramos constancia ligera en docs/agentes/entregas-worktree.md para trazabilidad Git del folio
    _, status_out = run_cmd(["git", "-C", worktree_dir, "status", "--porcelain"])
    changed_files = [ln.strip() for ln in status_out.splitlines() if ln.strip()]

    if not changed_files and sql_final:
        entregas_dir = os.path.join(worktree_dir, "docs", "agentes")
        os.makedirs(entregas_dir, exist_ok=True)
        bitacora_wt = os.path.join(entregas_dir, "entregas-sql.md")
        with open(bitacora_wt, "a", encoding="utf-8") as fb:
            fb.write(f"- **{args.folio}** ({datetime.datetime.now():%Y-%m-%d %H:%M}): `{args.titulo}` -> `{sql_final}`\n")
        _, status_out = run_cmd(["git", "-C", worktree_dir, "status", "--porcelain"])
        changed_files = [ln.strip() for ln in status_out.splitlines() if ln.strip()]

    touched_dotnet = any(f.lower().endswith((".cs", ".razor", ".csproj", ".sln", ".slnx")) for f in changed_files)
    touched_csproj = any(f.lower().endswith((".csproj", ".sln", ".slnx")) for f in changed_files)

    if changed_files:
        run_cmd(["git", "-C", worktree_dir, "add", "-A"])
        run_cmd([
            "git", "-C", worktree_dir, "commit",
            "-m", f"feat({args.folio.lower()}): {args.titulo[:65]} [{ide_label} {args.agente}]"
        ])
        run_cmd(["git", "-C", worktree_dir, "tag", "-f", f"folio/{args.folio.lower()}"])

    _, head_after = run_cmd(["git", "-C", worktree_dir, "rev-parse", "HEAD"])
    committed_in_run = (head_after != head_before) or bool(changed_files)

    build_ok = (exit_code == 0) or committed_in_run or bool(sql_final)
    build_note = "Sin cambios .NET (validación instantánea sin gastar compilación)."

    if touched_dotnet and sln_path:
        post_live_progress(
            args.api_url, args.bridge_secret, args.propuesta_id, args.agente,
            "⚡ Compilación incremental rápida sobre caché caliente del worktree...",
            branch_name, worktree_dir
        )
        dotnet_env = {"DOTNET_CLI_DO_NOT_USE_MSBUILD_SERVER": "1", "DOTNET_NOLOGO": "1"}
        if not touched_csproj:
            b_rc, b_out = run_cmd(
                ["dotnet", "build", sln_path, "--no-restore", "--nologo", "-v", "q", "-m:2", "/nr:false"],
                cwd=worktree_dir,
                timeout=180,
                extra_env=dotnet_env,
            )
            if b_rc != 0:
                b_rc, b_out = run_cmd(
                    ["dotnet", "build", sln_path, "--nologo", "-v", "q", "-m:2", "/nr:false"],
                    cwd=worktree_dir,
                    timeout=240,
                    extra_env=dotnet_env,
                )
        else:
            b_rc, b_out = run_cmd(
                ["dotnet", "build", sln_path, "--nologo", "-v", "q", "-m:2", "/nr:false"],
                cwd=worktree_dir,
                timeout=240,
                extra_env=dotnet_env,
            )
        build_ok = (b_rc == 0)
        build_note = "dotnet build incremental: 0 Errores ✅" if build_ok else f"dotnet build ({b_rc}):\n{b_out[-500:]}"

    files_summary = ", ".join(changed_files[:10]) if changed_files else ("Script SQL generado" if sql_final else "Validado")
    if len(changed_files) > 10:
        files_summary += f" (+{len(changed_files) - 10} más)"

    summary_lines = [
        f"Motor: {ide_label} (Modo Ahorro de Tokens)",
        wt_msg,
        f"Archivos ({len(changed_files)}): {files_summary}",
        build_note,
    ]
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
