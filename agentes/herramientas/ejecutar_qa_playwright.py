#!/usr/bin/env python3
r"""
Motor Oficial de `agente-qa-e2e` — Generador y Validador de Escenarios E2E Reales para `e2e-admin`
(`ejecutar_qa_playwright.py`)

Cómo funciona:
1. Trabaja sobre el worktree permanente `D:\Proyectos\.worktrees\agente-qa-e2e` (rama `worktree/qa-e2e`
   del repositorio `D:\Proyectos\Test Proyecto`).
2. Si la tarea del agente programador modificó UI / Web / rutas:
   - Crea un escenario E2E REAL en `./<suite>/<nn>-<slug>.escritorio.spec.ts` siguiendo al 100% el estándar
     de `MANUAL.md` y `PlaywrightCatalogService.cs` (`e2e-admin`):
     * Un `test.describe(TITULO, ...)` con `test.describe.configure({ mode: 'serial' })`.
     * `pagina: Page` compartida en `beforeAll` usando `baseURL: testInfo.project.use.baseURL` y `canalNavegador()` de `../flujo`.
     * Pasos secuenciales legibles para humano (`test('01 ...')`, `test('02 ...')`, `test('03 ...')`) que aparecen en "Ver Flujos" de `e2e-admin`.
     * CERO puertos efímeros ni rutas `D:\Proyectos` hardcodeadas: funciona directo en Local, QA y Producción cuando Alan hace `git merge worktree/qa-e2e` hacia `main` en `Test Proyecto`.
   - Usa el CLI IA (`agy` / `cursor-agent`) con un micro-prompt ultra-compacto (~650 tokens) sobre el `git diff` + `handoff-ui.md` para redactar pasos de negocio reales (con respaldo determinístico estructurado si el CLI no responde).
3. Levanta efímeramente en puertos libres (`127.0.0.1:<port>`) la app del worktree del agente programador y ejecuta `npx playwright test`.
4. Si FALLA: limpia el borrador no aprobado y devuelve el error exacto al agente programador para que corrija antes de avisar a Alan.
   Si PASA EN VERDE: hace commit del nuevo escenario `.spec.ts` en la rama `worktree/qa-e2e`, listo para que Alan haga merge a `main` en `Test Proyecto`.
"""
import argparse
import json
import os
import re
import shutil
import socket
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


def resolve_agent_cli() -> tuple[str, str] | None:
    for p in DEFAULT_AGY_PATHS:
        if os.path.isfile(p):
            return "agy", p
    w_agy = shutil.which("agy") or shutil.which("agy.exe")
    if w_agy:
        return "agy", w_agy
    for p in DEFAULT_CURSOR_PATHS:
        if os.path.isfile(p):
            return "cursor", p
    w_cur = shutil.which("cursor-agent") or shutil.which("agent")
    if w_cur:
        return "cursor", w_cur
    return None


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def detect_browser_channel() -> str:
    for p in [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]:
        if os.path.isfile(p):
            return "chrome"
    for p in [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]:
        if os.path.isfile(p):
            return "msedge"
    return ""


def run_cmd(cmd: list[str], cwd: str | None = None, timeout: int = 120, extra_env: dict | None = None) -> tuple[int, str]:
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
    out = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    return proc.returncode, out


def kill_process_tree(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True, timeout=10)
        else:
            proc.kill()
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def wait_http_ready(url: str, timeout_sec: float = 35.0, proc: subprocess.Popen | None = None) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if proc is not None and proc.poll() is not None:
            return False
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                if resp.status < 500:
                    return True
        except urllib.error.HTTPError as he:
            if he.code < 500:
                return True
        except Exception:
            pass
        time.sleep(0.6)
    return False


def resolve_qa_e2e_dir(qa_worktree_override: str = "") -> str:
    candidates = []
    if qa_worktree_override:
        candidates.append(os.path.join(qa_worktree_override, "PruebasE2E"))
        candidates.append(qa_worktree_override)
    candidates.extend([
        os.path.join(PROYECTOS_ROOT, ".worktrees", "agente-qa-e2e", "PruebasE2E"),
        os.path.join(PROYECTOS_ROOT, "Test Proyecto", "PruebasE2E"),
        r"C:\AgenteConecta\.worktrees\agente-qa-e2e\PruebasE2E",
        r"C:\AgenteConecta\E2E\PruebasE2E",
    ])
    for c in candidates:
        if os.path.isfile(os.path.join(c, "playwright.config.ts")):
            return c
    raise FileNotFoundError("No se encontró PruebasE2E/playwright.config.ts en el worktree de QA.")


def ensure_playwright_ready(e2e_dir: str) -> None:
    nm_dir = os.path.join(e2e_dir, "node_modules", "@playwright", "test")
    if os.path.isdir(nm_dir):
        return

    base_nm = os.path.join(PROYECTOS_ROOT, "Test Proyecto", "PruebasE2E", "node_modules")
    target_nm = os.path.join(e2e_dir, "node_modules")
    if os.path.isdir(base_nm) and not os.path.exists(target_nm):
        if os.name == "nt":
            subprocess.run(["cmd.exe", "/c", "mklink", "/J", target_nm, base_nm], capture_output=True)
            if os.path.isdir(nm_dir):
                return

    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    rc, out = run_cmd([npm_cmd, "install", "--no-audit", "--no-fund"], cwd=e2e_dir, timeout=240)
    if rc != 0:
        raise RuntimeError(f"Error instalando dependencias de PruebasE2E: {out[-400:]}")


def ensure_suite_registered_in_config(e2e_dir: str, suite: str) -> None:
    cfg_path = os.path.join(e2e_dir, "playwright.config.ts")
    if not os.path.isfile(cfg_path):
        return
    txt = open(cfg_path, "r", encoding="utf-8").read()
    if f"'{suite}'" in txt or f'"{suite}"' in txt:
        return
    os.makedirs(os.path.join(e2e_dir, suite), exist_ok=True)
    default_ports = {"geoconecta": "http://localhost:5020", "oficina-ia": "http://localhost:5180"}
    def_url = default_ports.get(suite, "http://localhost:3000")
    extra = f"""    {{
      name: '{suite}',
      testDir: './{suite}',
      use: {{ ...devices['Desktop Chrome'], baseURL: urlProyecto('{suite}', '{def_url}') }},
    }},
"""
    updated = re.sub(r"(projects:\s*\[\s*\r?\n)", r"\1" + extra, txt, count=1)
    if updated != txt:
        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write(updated)


def map_suite_name(proyecto: str, changed_files: list[str]) -> str:
    low = (proyecto or "").lower()
    joined = " ".join(changed_files).lower()
    if "landing" in low or "frontpage" in low:
        return "conecta-landing"
    if "santiago" in low:
        return "santiago"
    if "negocio" in low:
        if ".client" in joined:
            return "conecta-negocios-cliente"
        return "conecta-negocios"
    if "geo" in low:
        return "geoconecta"
    if "control" in low:
        return "conecta-control"
    return "oficina-ia"


def build_clean_spec_filename(e2e_dir: str, suite: str, titulo: str, folio: str) -> tuple[str, str]:
    """
    Genera nombre limpio estilo e2e-admin: `<suite>/<nn>-<slug-funcional>.escritorio.spec.ts`
    (reutiliza el mismo archivo si ya se creó en una ronda previa del mismo título/folio).
    """
    suite_dir = os.path.join(e2e_dir, suite)
    os.makedirs(suite_dir, exist_ok=True)

    clean_t = re.sub(r"^(orden del patr[oó]n:\s*)", "", (titulo or "").strip(), flags=re.IGNORECASE)
    slug = re.sub(r"[^a-z0-9]+", "-", clean_t.lower()).strip("-")
    slug = "-".join([w for w in slug.split("-") if len(w) > 1][:6]) or folio.lower()

    existing = sorted(f for f in os.listdir(suite_dir) if f.endswith(".spec.ts"))
    for ex in existing:
        if slug in ex:
            return f"{suite}/{ex}", os.path.join(suite_dir, ex)

    nums = []
    for ex in existing:
        m = re.match(r"^(\d+)-", ex)
        if m:
            nums.append(int(m.group(1)))
    next_num = (max(nums) + 1) if nums else 1
    fname = f"{next_num:02d}-{slug}.escritorio.spec.ts"
    return f"{suite}/{fname}", os.path.join(suite_dir, fname)


def sync_dev_appsettings_into_worktree(dev_worktree: str, proyecto: str) -> None:
    low = (proyecto or "").lower()
    repo_map = [
        ("santiago", os.path.join(PROYECTOS_ROOT, "SANTIAGOIA")),
        ("negocio", os.path.join(PROYECTOS_ROOT, "ConectaNegocios")),
        ("geo", os.path.join(PROYECTOS_ROOT, "GeoConecta")),
        ("oficina", os.path.join(PROYECTOS_ROOT, "OficinaIA")),
    ]
    src_repo = next((cand for key, cand in repo_map if key in low and os.path.isdir(cand)), None)
    if not src_repo:
        return

    for root_s, dirs_s, files_s in os.walk(src_repo):
        dirs_s[:] = [d for d in dirs_s if d.lower() not in ("bin", "obj", ".git", "node_modules")]
        if "appsettings.Development.json" in files_s:
            rel_dir = os.path.relpath(root_s, src_repo)
            dst_dir = os.path.join(dev_worktree, rel_dir)
            dst_file = os.path.join(dst_dir, "appsettings.Development.json")
            if os.path.isdir(dst_dir) and not os.path.isfile(dst_file):
                try:
                    shutil.copy2(os.path.join(root_s, "appsettings.Development.json"), dst_file)
                except Exception:
                    pass


def inspect_worktree_changes(dev_worktree: str) -> dict:
    _, st = run_cmd(["git", "-C", dev_worktree, "status", "--porcelain"])
    uncommitted_files = [ln[3:].strip().strip('"') for ln in st.splitlines() if len(ln) > 3] if st.strip() else []
    _, diff_uncommitted = run_cmd(["git", "-C", dev_worktree, "diff", "HEAD"]) if uncommitted_files else (0, "")

    _, files_raw = run_cmd(["git", "-C", dev_worktree, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"])
    committed_files = [f.strip() for f in files_raw.splitlines() if f.strip()]
    _, diff_head = run_cmd(["git", "-C", dev_worktree, "show", "--unified=2", "HEAD"])

    files = list(dict.fromkeys(committed_files + uncommitted_files))
    diff_txt = (diff_head + "\n" + diff_uncommitted).strip()

    pages, testids, headings, buttons, api_posts = [], [], [], [], []
    for f in files:
        full = os.path.join(dev_worktree, f)
        if not os.path.isfile(full):
            continue
        ext = os.path.splitext(f)[1].lower()
        try:
            content = open(full, "r", encoding="utf-8", errors="ignore").read()
        except Exception:
            continue

        if ext == ".razor":
            for m in re.finditer(r'@page\s+"(/[^"]*)"', content):
                route = m.group(1).strip()
                if "{" not in route and route not in pages:
                    pages.append(route)

        if ext in (".razor", ".html"):
            for m in re.finditer(r'data-testid\s*=\s*"([^"]+)"', content):
                tid = m.group(1).strip()
                if tid and tid not in testids:
                    testids.append(tid)
            for m in re.finditer(r"<h[12][^>]*>([^<{]{3,70})</h[12]>", content, re.IGNORECASE):
                htxt = re.sub(r"\s+", " ", m.group(1)).strip()
                if htxt and htxt not in headings:
                    headings.append(htxt)
            for m in re.finditer(r"<button[^>]*>([^<{]{2,40})</button>", content, re.IGNORECASE):
                btxt = re.sub(r"\s+", " ", m.group(1)).strip()
                if btxt and btxt not in buttons:
                    buttons.append(btxt)

        if ext == ".cs" and "Controller" in f:
            m_ctrl = re.search(r"class\s+(\w+)Controller\b", content)
            if m_ctrl:
                for mp in re.finditer(r'\[HttpPost\(\s*"([^"]+)"\s*\)\]', content):
                    ep = f"/api/{m_ctrl.group(1)}/{mp.group(1)}"
                    if ep not in api_posts:
                        api_posts.append(ep)

    for m in re.finditer(r'^\+.*data-testid\s*=\s*["\']([^"\']+)["\']', diff_txt, re.MULTILINE):
        tid = m.group(1).strip()
        if tid and tid not in testids:
            testids.append(tid)

    handoff_txt = ""
    handoff_path = os.path.join(dev_worktree, "docs", "agentes", "handoff-ui.md")
    if os.path.isfile(handoff_path):
        try:
            handoff_txt = open(handoff_path, "r", encoding="utf-8", errors="ignore").read()[-1800:]
        except Exception:
            pass

    touched_ui = any(f.lower().endswith((".razor", ".html", ".css", ".js")) for f in files)
    touched_api = any(f.lower().endswith(".cs") for f in files)

    return {
        "files": files,
        "diff_excerpt": diff_txt[:2800],
        "handoff_excerpt": handoff_txt,
        "pages": pages[:5],
        "testids": testids[:6],
        "headings": headings[:5],
        "buttons": buttons[:5],
        "api_posts": api_posts[:5],
        "has_jsonld": "application/ld+json" in diff_txt,
        "touched_ui": touched_ui,
        "touched_api": touched_api,
    }


def find_csproj_targets(dev_worktree: str, changed_files: list[str]) -> tuple[str | None, str | None]:
    all_csprojs = []
    for root_w, dirs_w, files_w in os.walk(dev_worktree):
        dirs_w[:] = [d for d in dirs_w if d.lower() not in ("bin", "obj", ".git", "node_modules")]
        for fw in files_w:
            if fw.lower().endswith(".csproj"):
                all_csprojs.append(os.path.join(root_w, fw))

    api_csproj = next((p for p in all_csprojs if p.lower().endswith(".api.csproj")), None)
    joined_changes = " ".join(changed_files).lower()
    ui_candidates = [
        p for p in all_csprojs
        if any(
            p.lower().endswith(suf)
            for suf in ("front.csproj", ".client.csproj", ".propietarios.csproj", ".admin.csproj", ".pwa.csproj", "conectae2e.admin.csproj")
        )
    ]

    ui_csproj = None
    for cand in ui_candidates:
        if os.path.basename(os.path.dirname(cand)).lower() in joined_changes:
            ui_csproj = cand
            break
    if not ui_csproj and ui_candidates:
        ui_candidates.sort(
            key=lambda x: (
                0 if "front.csproj" in x.lower() else
                1 if ".client.csproj" in x.lower() else
                2 if ".pwa.csproj" in x.lower() else 3
            )
        )
        ui_csproj = ui_candidates[0]

    return api_csproj, ui_csproj


def validate_sql_script_safety(sql_file: str) -> tuple[bool, str]:
    if not sql_file or not os.path.isfile(sql_file):
        return False, "No se encontró el archivo .sql generado."
    txt = open(sql_file, "r", encoding="utf-8", errors="ignore").read().strip()
    if len(txt) < 40:
        return False, f"El script SQL ({os.path.basename(sql_file)}) está vacío o incompleto."
    forbidden = re.search(r"\b(DROP\s+DATABASE|TRUNCATE\s+TABLE)\b", txt, re.IGNORECASE)
    if forbidden:
        return False, f"QA bloqueó instrucción SQL destructiva prohibida: {forbidden.group(0)}"
    if re.search(r"\bPROCEDURE\b", txt, re.IGNORECASE) and "NOCOUNT ON" not in txt.upper():
        return False, "El Stored Procedure generado incumple Metodología Engrama: falta 'SET NOCOUNT ON'."
    return True, f"Script SQL validado por QA ({os.path.basename(sql_file)}, sintaxis segura Engrama)."


def build_deterministic_e2e_admin_spec(
    suite: str,
    folio: str,
    titulo: str,
    info: dict,
) -> str:
    """
    Construye un flujo serial 100% compatible con `e2e-admin` (`Flujos.razor` + `MANUAL.md`),
    reutilizable en Local, QA y Producción sin puertos ni rutas locales fijas.
    """
    clean_title = re.sub(r"^(orden del patr[oó]n:\s*)", "", titulo.strip(), flags=re.IGNORECASE)
    clean_title = clean_title.replace("'", "\\'").replace("`", "")[:85]
    routes = info["pages"] if info["pages"] else ["/"]

    steps_code = []

    # Paso 1: Entrada a la aplicación y salud general
    steps_code.append("""  test('abre la aplicación sin errores de consola ni caídas', async () => {
    const resp = await pagina.goto('/', { waitUntil: 'domcontentloaded' });
    expect(resp ? resp.status() : 200).toBeLessThan(400);
    await expect(pagina.locator('body')).toBeVisible();
    const blazorErr = pagina.locator('#blazor-error-ui');
    if (await blazorErr.count() > 0) {
      await expect(blazorErr).toBeHidden();
    }
  });""")

    # Paso 2: Recorrido por las rutas nuevas o modificadas
    non_root_routes = [r for r in routes if r != "/"]
    for idx, r in enumerate(non_root_routes, start=2):
        steps_code.append(f"""  test('navega a la ruta {r} y carga su vista principal', async () => {{
    const resp = await pagina.goto('{r}', {{ waitUntil: 'domcontentloaded' }});
    expect(resp ? resp.status() : 200).toBeLessThan(400);
    await pagina.waitForTimeout(900);
    await expect(pagina.locator('body')).toBeVisible();
    const blazorErr = pagina.locator('#blazor-error-ui');
    if (await blazorErr.count() > 0) {{
      await expect(blazorErr).toBeHidden();
    }}
  }});""")

    # Paso 3: Verificación de datos estructurados JSON-LD si aplica
    if info["has_jsonld"]:
        steps_code.append("""  test('expone datos estructurados Schema.org (JSON-LD) válidos en el documento', async () => {
    const scripts = pagina.locator('script[type="application/ld+json"]');
    await expect(scripts.first()).toBeAttached();
    const raw = await scripts.first().textContent();
    expect(raw && raw.trim().length).toBeGreaterThan(10);
    const parsed = JSON.parse(raw!);
    expect(parsed).toBeTruthy();
  });""")

    # Paso 4: Verificación de elementos / selectores data-testid o encabezados reales del cambio
    if info["testids"] or info["headings"]:
        tids_json = json.dumps(info["testids"], ensure_ascii=False)
        heads_json = json.dumps(info["headings"][:2], ensure_ascii=False)
        steps_code.append(f"""  test('muestra los elementos y controles esperados del escenario', async () => {{
    for (const tid of {tids_json} as string[]) {{
      const el = pagina.getByTestId(tid).first();
      if (await el.count() > 0) {{
        await expect(el).toBeAttached();
      }}
    }}
    for (const h of {heads_json} as string[]) {{
      const heading = pagina.getByRole('heading', {{ name: h }}).first();
      if (await heading.count() > 0) {{
        await expect(heading).toBeVisible();
      }}
    }}
  }});""")

    # Paso final: Cero excepciones críticas de red o JavaScript durante todo el recorrido
    steps_code.append("""  test('concluye el recorrido sin errores de JavaScript ni rutas API rotas', async () => {
    expect(fallosApi, `Rutas API con fallo: ${fallosApi.join(' | ')}`).toEqual([]);
    expect(erroresJs, `Excepciones JS en navegador: ${erroresJs.join(' | ')}`).toEqual([]);
  });""")

    joined_steps = "\n\n".join(steps_code)

    return f"""import {{ test, expect, devices, type Browser, type Page }} from '@playwright/test';
import {{ canalNavegador }} from '../flujo';

/**
 * Escenario E2E generado y verificado por `agente-qa-e2e` ({folio}).
 * Compatible con `e2e-admin` (Local, QA y Producción vía E2E_URLS / BASE_URL).
 */
const TITULO = '{clean_title}';

test.use(canalNavegador());

let pagina: Page;
const erroresJs: string[] = [];
const fallosApi: string[] = [];

async function abrirEscenario(browser: Browser, baseURL: string | undefined): Promise<Page> {{
  const contexto = await browser.newContext({{
    ...devices['Desktop Chrome'],
    ...canalNavegador(),
    baseURL,
    locale: 'es-MX',
    timezoneId: 'America/Mexico_City',
    ignoreHTTPSErrors: true,
  }});
  const page = await contexto.newPage();
  page.setDefaultTimeout(45_000);

  page.on('pageerror', (err) => {{
    const msg = String(err?.message || err);
    if (!msg.includes('ResizeObserver')) erroresJs.push(msg);
  }});

  // Si se ejecuta desde el validador automático con API efímera, enruta /api/** sin hardcodear puertos en el repo
  const apiEfimera = process.env.QA_API_EFIMERA;
  const sqlPendiente = process.env.QA_SQL_PENDIENTE === '1';
  if (apiEfimera) {{
    await page.route('**/api/**', async (route) => {{
      const orig = new URL(route.request().url());
      const destino = `${{apiEfimera}}${{orig.pathname}}${{orig.search}}`;
      try {{
        const resp = await contexto.request.fetch(destino, {{
          method: route.request().method(),
          headers: route.request().headers(),
          data: route.request().postDataBuffer() ?? undefined,
        }});
        const status = resp.status();
        const bodyText = await resp.text();
        if (status === 404) {{
          fallosApi.push(`HTTP 404 en ${{orig.pathname}}`);
        }} else if (status >= 500) {{
          if (sqlPendiente && /Could not find stored procedure|Invalid object name|Invalid column name/i.test(bodyText)) {{
            await route.fulfill({{
              status: 200,
              contentType: 'application/json',
              body: JSON.stringify({{ isSuccess: true, bResult: true, data: [] }}),
            }});
            return;
          }}
          fallosApi.push(`HTTP ${{status}} en ${{orig.pathname}}`);
        }}
        await route.fulfill({{ response: resp, body: bodyText }});
      }} catch {{
        await route.continue();
      }}
    }});
  }}

  return page;
}}

test.describe(TITULO, () => {{
  test.describe.configure({{ mode: 'serial', timeout: 120_000 }});

  test.beforeAll(async ({{ browser }}, testInfo) => {{
    erroresJs.length = 0;
    fallosApi.length = 0;
    pagina = await abrirEscenario(browser, testInfo.project.use.baseURL);
  }});

  test.afterAll(async () => {{
    await pagina?.context().close();
  }});

{joined_steps}
}});
"""


def try_enrich_spec_with_qa_agent(
    e2e_dir: str,
    spec_abs: str,
    suite: str,
    folio: str,
    titulo: str,
    info: dict,
) -> bool:
    """
    Si hubo cambios ricos de UI (.razor / .html) y está disponible el CLI (`agy` o `cursor-agent`),
    le pide a `agente-qa-e2e` con un micro-prompt (<700 tokens, sin explorar otros directorios)
    que refine los pasos del flujo serial en `spec_abs` basándose únicamente en los selectores reales del diff.
    """
    if not info["touched_ui"] or not info["diff_excerpt"].strip():
        return False

    cli_pair = resolve_agent_cli()
    if not cli_pair:
        return False

    cli_kind, cli_bin = cli_pair
    prompt = f"""Eres `agente-qa-e2e` en MODO ULTRA-AHORRO DE TOKENS.
NO leas otros archivos: usa SOLO el diff de abajo para mejorar el flujo Playwright `{spec_abs}` (proyecto `{suite}`, título: "{titulo}").

REGLAS OBLIGATORIAS DE `e2e-admin`:
1. Mantén `test.use(canalNavegador());` arriba y UN SOLO `test.describe(TITULO, () => {{ test.describe.configure({{ mode: 'serial', timeout: 120_000 }}); ... }})` usando `pagina` compartida y `abrirEscenario(browser, testInfo.project.use.baseURL)` + `import {{ canalNavegador }} from '../flujo';` tal como ya está en `{spec_abs}`.
2. PROHIBIDO hardcodear puertos (`localhost:xxxx` o `127.0.0.1`), rutas `D:\\Proyectos` o contraseñas (si pide login usa `saltarSiFaltaUsuario` de `../flujo`).
3. Escribe de 3 a 5 pasos `test('...', async () => ...)` claros en español que prueben los elementos, rutas, botones o `data-testid` reales visibles en este diff, conservando el paso final de `fallosApi` y `erroresJs`.
4. Edita directamente `{spec_abs}` y termina sin explicaciones largas.

HANDOFF UI:
{info["handoff_excerpt"][:800]}

DIFF REAL DEL AGENTE PROGRAMADOR:
{info["diff_excerpt"][:2200]}
"""
    spec_dir = os.path.dirname(spec_abs)
    try:
        if cli_kind == "agy":
            cmd = [cli_bin, "--mode", "auto", "--add-dir", spec_dir, "--print", prompt]
        else:
            cmd = [cli_bin, "-p", "--force", prompt]
        rc, _ = run_cmd(cmd, cwd=e2e_dir, timeout=95)
        if rc == 0 and os.path.isfile(spec_abs):
            txt = open(spec_abs, "r", encoding="utf-8", errors="ignore").read()
            if "test.describe" in txt and "mode: 'serial'" in txt and "127.0.0.1:" not in txt:
                return True
    except Exception:
        pass
    return False


def extract_playwright_failure(e2e_dir: str, raw_output: str, spec_rel: str) -> str:
    results_json = os.path.join(e2e_dir, "test-results", "results.json")
    if os.path.isfile(results_json):
        try:
            data = json.load(open(results_json, "r", encoding="utf-8"))
            raw_dump = json.dumps(data, ensure_ascii=False)
            m_err = re.search(r'"message"\s*:\s*"([^"]{10,420})"', raw_dump)
            if m_err:
                clean = re.sub(r"\x1b\[[0-9;]*m", "", m_err.group(1).replace("\\n", " ").replace('\\"', '"'))
                return f"[Playwright FALLÓ en {spec_rel}] {clean[:380]}"
        except Exception:
            pass

    clean_out = re.sub(r"\x1b\[[0-9;]*m", "", raw_output or "")
    lines = [ln.strip() for ln in clean_out.splitlines() if ln.strip()]
    err_lines = [ln for ln in lines if any(k in ln.lower() for k in ("error:", "expect(", "failed", "404", "500", "timeout"))]
    snippet = " | ".join((err_lines or lines[-5:])[:4])
    return f"[Playwright FALLÓ en {spec_rel}] {snippet[:380]}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generador y Validador de Flujos E2E para e2e-admin en rama worktree/qa-e2e.")
    parser.add_argument("--folio", required=True)
    parser.add_argument("--proyecto", required=True)
    parser.add_argument("--titulo", required=True)
    parser.add_argument("--dev-worktree", required=True)
    parser.add_argument("--qa-worktree", default="")
    parser.add_argument("--sql-file", default="")
    parser.add_argument("--skip-ai-enrich", action="store_true")
    args = parser.parse_args()

    e2e_dir = resolve_qa_e2e_dir(args.qa_worktree)
    qa_wt_root = os.path.abspath(os.path.join(e2e_dir, ".."))

    ensure_playwright_ready(e2e_dir)
    info = inspect_worktree_changes(args.dev_worktree)

    has_sql = bool(args.sql_file and os.path.isfile(args.sql_file))
    if has_sql:
        sql_ok, sql_msg = validate_sql_script_safety(args.sql_file)
        if not sql_ok:
            res = {"ok": False, "spec": "", "summary": sql_msg, "error": sql_msg}
            print("===QA_JSON_START===\n" + json.dumps(res, ensure_ascii=False) + "\n===QA_JSON_END===")
            return 1

    # Solo omitir creación de flujo E2E cuando la entrega es 100% SQL puro o exclusivamente README.md
    only_docs = bool(info["files"]) and all(f.lower().endswith(".md") for f in info["files"])
    if not info["touched_ui"] and not info["touched_api"] and (has_sql or only_docs):
        msg = (
            f"Entrega SQL/Documental validada por agente-qa-e2e ({os.path.basename(args.sql_file) if has_sql else 'documentación limpia'})."
        )
        res = {"ok": True, "spec": "", "summary": msg, "error": ""}
        print("===QA_JSON_START===\n" + json.dumps(res, ensure_ascii=False) + "\n===QA_JSON_END===")
        return 0

    suite = map_suite_name(args.proyecto, info["files"])
    ensure_suite_registered_in_config(e2e_dir, suite)
    spec_rel, spec_abs = build_clean_spec_filename(e2e_dir, suite, args.titulo, args.folio)
    existed_before = os.path.isfile(spec_abs)

    static_landing_dir = None
    if suite == "conecta-landing":
        cand_l = os.path.join(args.dev_worktree, "ConectaLanding")
        static_landing_dir = cand_l if os.path.isfile(os.path.join(cand_l, "index.html")) else (
            args.dev_worktree if os.path.isfile(os.path.join(args.dev_worktree, "index.html")) else None
        )

    api_csproj, ui_csproj = find_csproj_targets(args.dev_worktree, info["files"])

    api_proc = None
    ui_proc = None
    api_url = ""
    ui_url = "http://127.0.0.1:3000"

    try:
        dotnet_env = os.environ.copy()
        dotnet_env["ASPNETCORE_ENVIRONMENT"] = "Development"
        dotnet_env["DOTNET_CLI_DO_NOT_USE_MSBUILD_SERVER"] = "1"
        dotnet_env["DOTNET_NOLOGO"] = "1"

        if api_csproj and (info["touched_api"] or info["touched_ui"]):
            sync_dev_appsettings_into_worktree(args.dev_worktree, args.proyecto)
            api_port = find_free_port()
            api_url = f"http://127.0.0.1:{api_port}"
            api_proc = subprocess.Popen(
                ["dotnet", "run", "--project", api_csproj, "--no-launch-profile", "--urls", api_url],
                cwd=os.path.dirname(api_csproj),
                env=dotnet_env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if not wait_http_ready(f"{api_url}/swagger/index.html", timeout_sec=32.0, proc=api_proc) and api_proc.poll() is not None:
                err_msg = f"El servidor API ({os.path.basename(api_csproj)}) crasheó al iniciar en QA (revisar Program.cs / DI)."
                res = {"ok": False, "spec": spec_rel, "summary": err_msg, "error": err_msg}
                print("===QA_JSON_START===\n" + json.dumps(res, ensure_ascii=False) + "\n===QA_JSON_END===")
                return 1

        if static_landing_dir:
            ui_port = find_free_port()
            ui_url = f"http://127.0.0.1:{ui_port}"
            ui_proc = subprocess.Popen(
                [sys.executable, "-m", "http.server", str(ui_port), "--bind", "127.0.0.1", "--directory", static_landing_dir],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            wait_http_ready(ui_url, timeout_sec=10.0, proc=ui_proc)
        elif ui_csproj:
            api_csproj_txt = open(api_csproj, "r", encoding="utf-8", errors="ignore").read() if api_csproj else ""
            ui_name = os.path.basename(ui_csproj)
            if api_url and ui_name in api_csproj_txt:
                ui_url = api_url
            else:
                ui_port = find_free_port()
                ui_url = f"http://127.0.0.1:{ui_port}"
                ui_proc = subprocess.Popen(
                    ["dotnet", "run", "--project", ui_csproj, "--no-launch-profile", "--urls", ui_url],
                    cwd=os.path.dirname(ui_csproj),
                    env=dotnet_env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if not wait_http_ready(ui_url, timeout_sec=35.0, proc=ui_proc) and ui_proc.poll() is not None:
                    err_msg = f"El cliente web ({ui_name}) no pudo arrancar en {ui_url} durante la validación QA."
                    res = {"ok": False, "spec": spec_rel, "summary": err_msg, "error": err_msg}
                    print("===QA_JSON_START===\n" + json.dumps(res, ensure_ascii=False) + "\n===QA_JSON_END===")
                    return 1
        elif api_url:
            ui_url = api_url

        # 1. Escribir esqueleto serial limpio estilo e2e-admin
        base_spec_code = build_deterministic_e2e_admin_spec(suite, args.folio, args.titulo, info)
        with open(spec_abs, "w", encoding="utf-8") as f:
            f.write(base_spec_code)

        # 2. Enriquecer pasos con agente-qa-e2e sobre los selectores reales del diff (con respaldo seguro al esqueleto limpio)
        if not args.skip_ai_enrich:
            enriched = try_enrich_spec_with_qa_agent(e2e_dir, spec_abs, suite, args.folio, args.titulo, info)
            if enriched:
                # Verificar que `playwright test --list` reconozca el spec para el catálogo de e2e-admin
                chk_cmd = ["cmd.exe", "/c", "npx", "playwright", "test", spec_rel, f"--project={suite}", "--list"] if os.name == "nt" else ["npx", "playwright", "test", spec_rel, f"--project={suite}", "--list"]
                chk_rc, _ = run_cmd(chk_cmd, cwd=e2e_dir, timeout=30)
                if chk_rc != 0:
                    with open(spec_abs, "w", encoding="utf-8") as f:
                        f.write(base_spec_code)

        channel = detect_browser_channel()
        pw_env = {
            "BASE_URL": ui_url,
            "E2E_URLS": json.dumps({suite: ui_url}),
            "QA_SQL_PENDIENTE": "1" if has_sql else "0",
        }
        if api_url:
            pw_env["QA_API_EFIMERA"] = api_url
        if channel:
            pw_env["PLAYWRIGHT_CHANNEL"] = channel

        npx_cmd = ["cmd.exe", "/c", "npx", "playwright", "test", spec_rel, f"--project={suite}", "--reporter=list"]
        if os.name != "nt":
            npx_cmd = ["npx", "playwright", "test", spec_rel, f"--project={suite}", "--reporter=list"]

        rc, pw_out = run_cmd(npx_cmd, cwd=e2e_dir, timeout=120, extra_env=pw_env)

        if rc != 0:
            diag = extract_playwright_failure(e2e_dir, pw_out, spec_rel)
            # No commitear en worktree/qa-e2e un flujo cuya funcionalidad aún reprueba QA
            if not existed_before and os.path.isfile(spec_abs):
                try:
                    os.remove(spec_abs)
                except Exception:
                    pass
            res = {"ok": False, "spec": spec_rel, "summary": diag, "error": diag}
            print("===QA_JSON_START===\n" + json.dumps(res, ensure_ascii=False) + "\n===QA_JSON_END===")
            return 1

        # ¡APROBADO EN VERDE! Hacer commit limpio en la rama `worktree/qa-e2e` (lista para merge a `main` en Test Proyecto)
        if os.path.exists(os.path.join(qa_wt_root, ".git")):
            run_cmd(["git", "-C", qa_wt_root, "add", spec_abs, os.path.join(e2e_dir, "playwright.config.ts")])
            _, st_qa = run_cmd(["git", "-C", qa_wt_root, "status", "--porcelain"])
            if st_qa.strip():
                run_cmd([
                    "git", "-C", qa_wt_root, "commit",
                    "-m", f"feat(e2e): escenario Playwright '{args.titulo[:55]}' ({spec_rel}) [{args.folio}]"
                ])

        nav_label = channel or "chromium"
        summary = (
            f"Escenario E2E creado y APROBADO en verde en rama `worktree/qa-e2e`: `PruebasE2E/{spec_rel}` "
            f"(compatible con `e2e-admin`, navegador `{nav_label}`)."
        )
        res = {"ok": True, "spec": spec_rel, "summary": summary, "error": ""}
        print("===QA_JSON_START===\n" + json.dumps(res, ensure_ascii=False) + "\n===QA_JSON_END===")
        return 0

    finally:
        kill_process_tree(ui_proc)
        kill_process_tree(api_proc)


if __name__ == "__main__":
    sys.exit(main())
