#!/usr/bin/env python3
"""
Instalador desatendido del Ecosistema AgentesConecta + Conecta Software Oficina para Cursor IDE.
Ejecutar desde la raíz del workspace después de clonar AgentesConecta:
    python ./agentes/herramientas/instalar_entorno_cursor.py
"""
import json
import os
import subprocess
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OFICINA_REPO_URL = "https://github.com/isc-alanortega/Oficina-IA-Conecta.git"


def step(msg: str):
    print(f"\n=== {msg} ===", flush=True)


def ensure_pyodbc():
    step("1/5 Verificando dependencia Python (pyodbc)")
    try:
        import pyodbc  # noqa: F401
        print("[OK] pyodbc ya está instalado.")
    except ImportError:
        print("[INFO] Instalando pyodbc...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyodbc"])
        print("[OK] pyodbc instalado.")


def ensure_oficina_repo():
    step("2/5 Verificando repositorio Conecta Software Oficina (./OficinaIA)")
    oficina_dir = os.path.join(ROOT_DIR, "OficinaIA")
    if os.path.isdir(os.path.join(oficina_dir, ".git")) or os.path.isfile(
        os.path.join(oficina_dir, "OficinaIA", "OficinaIA.slnx")
    ):
        print(f"[OK] OficinaIA ya existe en: {oficina_dir}")
        return
    print(f"[INFO] Clonando {OFICINA_REPO_URL} en {oficina_dir} ...")
    subprocess.check_call(["git", "clone", OFICINA_REPO_URL, oficina_dir])
    print("[OK] OficinaIA clonado exitosamente.")


def sync_cursor_config():
    step("3/6 Sincronizando reglas, 7 subagentes, 3 skills y Firewall SQL en .cursor/")
    sync_script = os.path.join(ROOT_DIR, "agentes", "herramientas", "sync_cursor.py")
    subprocess.check_call([sys.executable, sync_script])
    step("4/6 Inicializando 1 Worktree Permanente fijo para cada Agente (.worktrees/<agente>)")
    wt_script = os.path.join(ROOT_DIR, "agentes", "herramientas", "inicializar_worktrees_agentes.py")
    if os.path.isfile(wt_script):
        subprocess.call([sys.executable, wt_script])


def discover_existing_connection_string() -> str | None:
    candidates = [
        os.path.join(ROOT_DIR, "ConectaNegocios", "ConectaNegocios.API", "appsettings.Development.json"),
        os.path.join(ROOT_DIR, "ConectaNegocios", "ConectaNegocios.API", "appsettings.json"),
        os.path.join(ROOT_DIR, "GeoConecta", "GeoConecta", "GeoConecta.API", "appsettings.Development.json"),
        os.path.join(ROOT_DIR, "GeoConecta", "GeoConecta", "GeoConecta.API", "appsettings.json"),
        os.path.join(ROOT_DIR, "SANTIAGOIA", "SantiagoConectaIA", "SantiagoConectaIA.API", "appsettings.Development.json"),
        os.path.join(ROOT_DIR, "SANTIAGOIA", "SantiagoConectaIA", "SantiagoConectaIA.API", "appsettings.json"),
        os.path.join(ROOT_DIR, "PlantillaPWA", "ProjectName", "ProjectName.API", "appsettings.Development.json"),
        os.path.join(ROOT_DIR, "PlantillaPWA", "ProjectName", "ProjectName.API", "appsettings.json"),
    ]
    for path in candidates:
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            conn = (data.get("ConnectionStrings") or {}).get("EngramaCloudConnection", "")
            if conn and "TU_PASSWORD_AQUI" not in conn and "SERVIDOR_SQL" not in conn and "Password=" in conn:
                print(f"[OK] Cadena EngramaCloudConnection detectada desde: {os.path.relpath(path, ROOT_DIR)}")
                return conn
        except Exception:
            continue
    return None


def configure_oficina_appsettings():
    step("4/5 Configurando appsettings.Development.json local para OficinaIA")
    api_dir = os.path.join(ROOT_DIR, "OficinaIA", "OficinaIA", "OficinaIA.API")
    example_path = os.path.join(api_dir, "appsettings.Development.example.json")
    dev_path = os.path.join(api_dir, "appsettings.Development.json")

    if not os.path.isdir(api_dir) or not os.path.isfile(example_path):
        print("[WARN] No se encontró OficinaIA.API/appsettings.Development.example.json todavía.")
        return False

    if os.path.isfile(dev_path):
        with open(dev_path, "r", encoding="utf-8-sig") as f:
            cfg = json.load(f)
    else:
        with open(example_path, "r", encoding="utf-8-sig") as f:
            cfg = json.load(f)

    cfg.setdefault("OficinaIA", {})["ProyectosRoot"] = ROOT_DIR

    current_conn = (cfg.get("ConnectionStrings") or {}).get("EngramaCloudConnection", "")
    needs_conn = (not current_conn) or ("TU_PASSWORD_AQUI" in current_conn) or ("SERVIDOR_SQL" in current_conn)

    if needs_conn:
        discovered = discover_existing_connection_string()
        if discovered:
            cfg.setdefault("ConnectionStrings", {})["EngramaCloudConnection"] = discovered
            needs_conn = False

    with open(dev_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)

    print(f"[OK] Archivo local listo (ignorado por Git): {dev_path}")
    print(f"     ProyectosRoot = {ROOT_DIR}")
    if needs_conn:
        print("[PENDIENTE] Falta colocar la cadena real 'EngramaCloudConnection' en:")
        print(f"            {dev_path}")
    return not needs_conn


def verify_build_and_firewall():
    step("5/5 Verificando Firewall SQL de Cursor y compilación .NET de OficinaIA")
    guard_path = os.path.join(ROOT_DIR, ".cursor", "hooks", "sql_guard.py")
    payload = json.dumps({
        "hook_event_name": "beforeShellExecution",
        "command": "sql" + "cmd -S localhost -Q \"SELECT 1\"",
        "cwd": ROOT_DIR,
    })
    proc = subprocess.run(
        [sys.executable, guard_path],
        input=payload,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )
    out = (proc.stdout or "").strip()
    if '"permission": "deny"' in out or '"permission":"deny"' in out:
        print("[OK] Firewall SQL (.cursor/hooks/sql_guard.py) activo y bloqueando escrituras directas.")
    else:
        print(f"[WARN] Respuesta inesperada del hook SQL: {out}")

    slnx = os.path.join(ROOT_DIR, "OficinaIA", "OficinaIA", "OficinaIA.slnx")
    if os.path.isfile(slnx):
        print("[INFO] Compilando OficinaIA.slnx en Release...")
        rc = subprocess.call(["dotnet", "build", slnx, "-c", "Release", "--nologo", "-v", "q"])
        if rc == 0:
            print("[OK] Compilación de Conecta Software Oficina exitosa (0 errores).")
        else:
            print(f"[WARN] dotnet build devolvió código {rc}. Revisa que tengas instalado .NET 10 SDK.")


def report_sibling_repos():
    expected = [
        "PlantillaPWA",
        "GeoConecta",
        "ConectaNegocios",
        "Repo Conecta Negocios Landing",
        "SANTIAGOIA",
        "Test Proyecto",
        "OficinaIA",
    ]
    print("\n=== Resumen de Repositorios en tu Workspace ===")
    for name in expected:
        exists = os.path.isdir(os.path.join(ROOT_DIR, name))
        mark = "[ PRESENTE ]" if exists else "[ NO CLONADO AÚN ]"
        print(f"  {mark} ./{name}")


if __name__ == "__main__":
    ensure_pyodbc()
    ensure_oficina_repo()
    sync_cursor_config()
    has_db = configure_oficina_appsettings()
    verify_build_and_firewall()
    report_sibling_repos()
    print("\n======================================================================")
    print(" INSTALACIÓN COMPLETADA PARA CURSOR IDE")
    print(" Último paso: En Cursor presiona Ctrl+Shift+P -> 'Developer: Reload Window'")
    if not has_db:
        print(" Nota: Recuerda actualizar 'EngramaCloudConnection' en")
        print("       ./OficinaIA/OficinaIA/OficinaIA.API/appsettings.Development.json")
    print("======================================================================")
