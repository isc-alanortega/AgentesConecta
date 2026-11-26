#!/usr/bin/env python3
"""Wrapper ligero para Cursor beforeShellExecution -> delega a agentes/herramientas/firewall_sql_hook.py."""
import os
import runpy
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.environ.setdefault("PROYECTOS_ROOT", ROOT)
target = os.path.join(ROOT, "agentes", "herramientas", "firewall_sql_hook.py")
sys.path.insert(0, os.path.dirname(target))
runpy.run_path(target, run_name="__main__")
