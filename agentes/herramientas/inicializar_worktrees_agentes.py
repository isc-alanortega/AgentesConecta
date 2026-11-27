#!/usr/bin/env python3
r"""
Inicializador Idempotente de Worktrees Permanentes por Agente (`inicializar_worktrees_agentes.py`).
Crea una única vez un worktree fijo para cada agente en `<PROYECTOS_ROOT>\.worktrees\<codigo-agente>`
sobre su rama dedicada `agentes/<especialidad>`, evitando recrear worktrees por cada folio y
manteniendo caliente la caché `bin/obj` de .NET para ahorrar tokens y tiempo de compilación.

Uso:
    python ./agentes/herramientas/inicializar_worktrees_agentes.py
"""
import os
import subprocess
import sys

PROYECTOS_ROOT = os.environ.get("PROYECTOS_ROOT") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
WORKTREES_BASE = os.path.join(PROYECTOS_ROOT, ".worktrees")

# Mapa oficial: codigo_agente -> (candidatos_carpeta_repo, rama_fija)
AGENT_SPECS = [
    ("agente-geoconecta", ["GeoConecta"], "worktree/geoconecta"),
    ("agente-conectanegocios", ["ConectaNegocios", r"Conecta\ConectaNegocios"], "worktree/conectanegocios"),
    (
        "agente-conectalanding",
        ["Repo Conecta Negocios Landing", "ConectaNegociosFrontPage", "ConectaLanding", r"Conecta\ConectaNegociosFrontPage"],
        "worktree/conectalanding",
    ),
    ("agente-santiagoia", ["SANTIAGOIA", "SantiagoConectaIA", r"Conecta\SantiagoConectaIA"], "worktree/santiagoia"),
    ("agente-qa-e2e", ["Test Proyecto", "PruebasE2E", "E2E"], "worktree/qa-e2e"),
    ("agente-oficinaia", ["OficinaIA", r"OficinaIA\Oficina-IA-Conecta"], "worktree/oficinaia"),
    ("agente-conectacontrol", ["ConectaControl", r"Conecta\ConectaControl"], "worktree/conectacontrol"),
    ("agente-estratega-ia", ["."], "worktree/estratega-ia"),
]


def run_git(args: list[str], cwd: str | None = None) -> tuple[int, str]:
    proc = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    return proc.returncode, out


def find_git_repo(candidates: list[str]) -> str | None:
    for rel in candidates:
        full = os.path.abspath(os.path.join(PROYECTOS_ROOT, rel))
        if os.path.isdir(os.path.join(full, ".git")) or os.path.isfile(os.path.join(full, ".git")):
            return full
    return None


def ensure_agent_worktree(agent_code: str, repo_dir: str, branch_name: str) -> tuple[bool, str]:
    wt_dir = os.path.join(WORKTREES_BASE, agent_code)
    run_git(["config", "--global", "--add", "safe.directory", repo_dir.replace("\\", "/")])

    if os.path.isdir(wt_dir) and (
        os.path.isfile(os.path.join(wt_dir, ".git")) or os.path.isdir(os.path.join(wt_dir, ".git"))
    ):
        run_git(["config", "--global", "--add", "safe.directory", wt_dir.replace("\\", "/")])
        return True, f"[LISTO] {agent_code:<24} -> {wt_dir} ({branch_name})"

    # Limpiar registros huérfanos de worktrees previos si existieran
    run_git(["-C", repo_dir, "worktree", "prune"])

    code_br, _ = run_git(["-C", repo_dir, "rev-parse", "--verify", branch_name])
    if code_br == 0:
        rc, out = run_git(["-C", repo_dir, "worktree", "add", "--force", wt_dir, branch_name])
    else:
        rc, out = run_git(["-C", repo_dir, "worktree", "add", "--force", wt_dir, "-b", branch_name])

    if rc != 0:
        return False, f"[ERROR] {agent_code:<24} -> No se pudo crear desde {repo_dir}: {out[:220]}"

    run_git(["config", "--global", "--add", "safe.directory", wt_dir.replace("\\", "/")])
    return True, f"[CREADO] {agent_code:<23} -> {wt_dir} ({branch_name})"


def main() -> int:
    os.makedirs(WORKTREES_BASE, exist_ok=True)
    keep = os.path.join(WORKTREES_BASE, ".gitkeep")
    if not os.path.exists(keep):
        with open(keep, "w", encoding="utf-8") as f:
            f.write("# Directorio de worktrees permanentes por agente (contenido ignorado en Git)\n")

    print(f"=== Aprovisionando Worktrees Permanentes por Agente en: {WORKTREES_BASE} ===")
    created_or_ready = 0
    for agent_code, candidates, branch in AGENT_SPECS:
        repo = find_git_repo(candidates)
        if not repo:
            print(f"[OMITIDO] {agent_code:<22} -> Repo base no clonado en esta PC ({candidates[0]})")
            continue
        ok, msg = ensure_agent_worktree(agent_code, repo, branch)
        print(msg)
        if ok:
            created_or_ready += 1

    print(f"=== Total Worktrees Fijos Activos: {created_or_ready} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
