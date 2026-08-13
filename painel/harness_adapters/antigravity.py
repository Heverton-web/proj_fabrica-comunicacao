"""Adaptador para Antigravity CLI headless (``agy -p``).

Sucessor oficial do Gemini CLI (Google I/O mai/2026). Sintaxe de CLI validada
só por construção de comando nesta entrega (ver README/limitações) —
credencial é sessão de login interativo cacheada, sem variável de ambiente
oficial documentada; se o usuário souber um env var específico, o mecanismo
genérico de credencial do painel já cobre isso sem precisar hardcode aqui.
"""

from __future__ import annotations

from pathlib import Path

from painel.harness_adapters.base import HarnessAdapter, HeadlessInvocation


class AntigravityAdapter(HarnessAdapter):
    name = "antigravity"

    def build_invocation(
        self,
        cwd: Path,
        prompt: str,
        credential: dict | None = None,
        model: str | None = None,
        extra_allowed_dirs: list[Path] | None = None,
        permission_mode: str | None = None,
    ) -> HeadlessInvocation:
        # Sem equivalente conhecido a --add-dir/"scoped" -- extra_allowed_dirs
        # e permission_mode="scoped" sao ignorados de proposito (mesmo padrao
        # do adaptador opencode).
        cmd = ["agy", "-p", prompt]
        if model:
            cmd += ["--model", model]
        if permission_mode == "bypass":
            cmd += ["--dangerously-skip-permissions"]
        env = self.credential_env(credential)
        return HeadlessInvocation(cmd=cmd, cwd=Path(cwd), env=env)
