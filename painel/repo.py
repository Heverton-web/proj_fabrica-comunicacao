"""Localização deste repositório — usado para sugerir e reconhecer um
workspace "dentro do repo" (a configuração recomendada para harnesses reais
acharem `.claude/skills`, `AGENTS.md` e `SPEC_COMANDOS.md`).
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
