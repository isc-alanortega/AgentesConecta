#!/usr/bin/env python3
r"""
Generador y Sincronizador Automático Antigravity <-> Cursor (`sync_cursor.py`).
Toma la fuente única de verdad en `./agentes/plugins/ecosistema-engrama/` y genera/actualiza:
  - `./AGENTS.md` (Reglas globales en raíz leídas nativamente por Cursor)
  - `./.cursor/rules/*.mdc` (Reglas siempre activas con YAML frontmatter para Cursor)
  - `./.cursor/agents/*.md` (Los 7 subagentes convertidos al frontmatter oficial de Cursor)
  - `./.cursor/skills/*/SKILL.md` (Los 3 skills adaptados para invocarse con `/skill` en Cursor)
  - `./.cursor/hooks.json` + `./.cursor/hooks/sql_guard.py` (Candado SQL `beforeShellExecution` con `failClosed: true`)
  - `./.worktrees/.gitkeep` (Carpeta lista para ramas aisladas sin ensuciar Git)

Uso en cualquier PC (Windows / Mac / Linux):
    python ./agentes/herramientas/sync_cursor.py
"""
import json
import os
import re
import shutil

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PLUGIN_DIR = os.path.join(ROOT_DIR, "agentes", "plugins", "ecosistema-engrama")
CURSOR_DIR = os.path.join(ROOT_DIR, ".cursor")


def adapt_text_for_cursor(text: str) -> str:
    """Reemplaza rutas fijas D:\\Proyectos por la ruta real del equipo actual o rutas relativas limpias,
    y traduce llamadas exclusivas de Antigravity (`invoke_subagent`) a delegación estándar de Cursor."""
    # Reemplazar D:\Proyectos o D:/Proyectos por la ruta real donde el desarrollador clonó el workspace
    root_win = ROOT_DIR
    text = text.replace(r"D:\Proyectos", root_win)
    text = text.replace("D:/Proyectos", root_win.replace("\\", "/"))

    # Adaptar instrucciones de subagentes para que funcionen tanto en Cursor como en Antigravity
    text = re.sub(
        r"`invoke_subagent`\s*con\s*`TypeName:\s*\"([^\"]+)\"`",
        r"el subagente `@\1` (definido en `.cursor/agents/\1.md`)",
        text,
    )
    text = text.replace("(`invoke_subagent`)", "(delegando al subagente en `.cursor/agents/`)")
    text = text.replace("Lanza `invoke_subagent`", "Delega la tarea al subagente")
    return text


def parse_frontmatter(md_content: str) -> tuple[dict, str]:
    if not md_content.startswith("---"):
        return {}, md_content
    parts = md_content.split("---", 2)
    if len(parts) < 3:
        return {}, md_content
    fm_raw, body = parts[1], parts[2].lstrip("\r\n")
    meta = {}
    current_key = None
    for line in fm_raw.splitlines():
        if re.match(r"^[A-Za-z0-9_-]+:\s*", line):
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if v in (">-", "|", ""):
                meta[k] = ""
                current_key = k
            else:
                meta[k] = v
                current_key = None
        elif current_key and line.startswith("  "):
            meta[current_key] = (meta[current_key] + " " + line.strip()).strip()
    return meta, body


def generate_cursor_rules():
    rules_dir = os.path.join(CURSOR_DIR, "rules")
    os.makedirs(rules_dir, exist_ok=True)

    src_rules = os.path.join(PLUGIN_DIR, "rules", "AGENTS.md")
    with open(src_rules, "r", encoding="utf-8") as f:
        ecosystem_body = adapt_text_for_cursor(f.read())

    # 1. Regla principal del ecosistema en .cursor/rules/00-ecosistema-engrama.mdc
    mdc_ecosystem = f"""---
description: "Reglas Maestras del Ecosistema Conecta & Engrama (Metodología 0-8, PlantillaPWA, Agente Estratega IA y BD 100% Read-Only)"
alwaysApply: true
---

{ecosystem_body}
"""
    with open(os.path.join(rules_dir, "00-ecosistema-engrama.mdc"), "w", encoding="utf-8") as f:
        f.write(mdc_ecosystem)

    # 2. Copiar reglas granulares .mdc de PlantillaPWA si está presente en el workspace
    plantilla_cursor_rules = os.path.join(ROOT_DIR, "PlantillaPWA", ".cursor", "rules")
    if os.path.isdir(plantilla_cursor_rules):
        for fname in os.listdir(plantilla_cursor_rules):
            if fname.endswith(".mdc"):
                shutil.copy2(
                    os.path.join(plantilla_cursor_rules, fname),
                    os.path.join(rules_dir, f"10-{fname}"),
                )

    # 3. Generar AGENTS.md en la raíz del workspace para compatibilidad directa con Cursor y otros agentes
    root_agents_md = f"""# Ecosistema Conecta & Engrama — Instrucciones Globales (Cursor & Antigravity)

> Archivo sincronizado automáticamente por `python ./agentes/herramientas/sync_cursor.py` para la ruta local `{ROOT_DIR}`.
> Compatible con **Cursor IDE** (`.cursor/rules`, `.cursor/agents`, `.cursor/skills`, `.cursor/hooks.json`) y **Google Antigravity** (`GEMINI.md`, `.agents/`).

{ecosystem_body}
"""
    with open(os.path.join(ROOT_DIR, "AGENTS.md"), "w", encoding="utf-8") as f:
        f.write(root_agents_md)


def generate_cursor_subagents():
    src_agents_dir = os.path.join(PLUGIN_DIR, "agents")
    dst_agents_dir = os.path.join(CURSOR_DIR, "agents")
    os.makedirs(dst_agents_dir, exist_ok=True)

    for fname in sorted(os.listdir(src_agents_dir)):
        if not fname.endswith(".md"):
            continue
        with open(os.path.join(src_agents_dir, fname), "r", encoding="utf-8") as f:
            raw = f.read()

        meta, body = parse_frontmatter(raw)
        name = meta.get("name") or os.path.splitext(fname)[0]
        desc = adapt_text_for_cursor(meta.get("description", f"Subagente especialista {name}"))
        is_readonly = "true" if name == "agente-estratega-ia" else "false"
        adapted_body = adapt_text_for_cursor(body)

        cursor_agent_md = f"""---
name: {name}
description: "{desc.replace('"', "'")}"
model: inherit
readonly: {is_readonly}
is_background: false
---

{adapted_body}
"""
        with open(os.path.join(dst_agents_dir, fname), "w", encoding="utf-8") as f:
            f.write(cursor_agent_md)


def generate_cursor_skills():
    src_skills_dir = os.path.join(PLUGIN_DIR, "skills")
    dst_skills_dir = os.path.join(CURSOR_DIR, "skills")
    os.makedirs(dst_skills_dir, exist_ok=True)

    for skill_name in sorted(os.listdir(src_skills_dir)):
        s_dir = os.path.join(src_skills_dir, skill_name)
        skill_file = os.path.join(s_dir, "SKILL.md")
        if not os.path.isfile(skill_file):
            continue

        out_dir = os.path.join(dst_skills_dir, skill_name)
        os.makedirs(out_dir, exist_ok=True)

        with open(skill_file, "r", encoding="utf-8") as f:
            content = adapt_text_for_cursor(f.read())

        with open(os.path.join(out_dir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(content)


def generate_cursor_hooks():
    hooks_dir = os.path.join(CURSOR_DIR, "hooks")
    os.makedirs(hooks_dir, exist_ok=True)

    guard_wrapper = '''#!/usr/bin/env python3
"""Wrapper ligero para Cursor beforeShellExecution -> delega a agentes/herramientas/firewall_sql_hook.py."""
import os
import runpy
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.environ.setdefault("PROYECTOS_ROOT", ROOT)
target = os.path.join(ROOT, "agentes", "herramientas", "firewall_sql_hook.py")
sys.path.insert(0, os.path.dirname(target))
runpy.run_path(target, run_name="__main__")
'''
    with open(os.path.join(hooks_dir, "sql_guard.py"), "w", encoding="utf-8") as f:
        f.write(guard_wrapper)

    hooks_json = {
        "version": 1,
        "hooks": {
            "beforeShellExecution": [
                {
                    "command": "python .cursor/hooks/sql_guard.py",
                    "timeout": 10,
                    "failClosed": True,
                }
            ]
        },
    }
    with open(os.path.join(CURSOR_DIR, "hooks.json"), "w", encoding="utf-8") as f:
        json.dump(hooks_json, f, indent=2, ensure_ascii=False)


def ensure_worktrees_placeholder():
    wt_dir = os.path.join(ROOT_DIR, ".worktrees")
    os.makedirs(wt_dir, exist_ok=True)
    keep = os.path.join(wt_dir, ".gitkeep")
    if not os.path.exists(keep):
        with open(keep, "w", encoding="utf-8") as f:
            f.write("# Directorio efímero para ramas aisladas git worktree (contenido ignorado en Git)\n")


def main():
    os.makedirs(CURSOR_DIR, exist_ok=True)
    generate_cursor_rules()
    generate_cursor_subagents()
    generate_cursor_skills()
    generate_cursor_hooks()
    ensure_worktrees_placeholder()
    print(f"[OK] Configuración de Cursor sincronizada exitosamente en: {CURSOR_DIR}")
    print(f"     Raíz activa configurada: {ROOT_DIR}")


if __name__ == "__main__":
    main()
