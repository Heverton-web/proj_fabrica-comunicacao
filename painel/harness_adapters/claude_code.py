"""Adaptador para Claude Code headless (``claude -p``).

Cobre Anthropic direto, Bedrock ou Vertex — a credencial informada pelo
usuário define qual variável de ambiente é injetada (ex.: ``ANTHROPIC_API_KEY``).
Sintaxe de CLI validada só por construção de comando nesta entrega; rodar de
verdade requer o binário ``claude`` instalado e credencial real do usuário
(ver README/limitações).
"""

from __future__ import annotations

from pathlib import Path

from painel.harness_adapters.base import HarnessAdapter, HeadlessInvocation

# Ferramentas que o pipeline da Fabrica de fato usa (Bash pra scripts/*.py,
# pandoc, typst, playwright; Task pro fan-out de subagentes dos comandos
# /produzir-*). Achado real na validacao: sem isso, claude -p headless para
# pedindo aprovacao interativa (que nao existe sem terminal) e desiste.
FERRAMENTAS_ESCOPO_FABRICA = "Bash Read Write Edit Glob Grep Task"


class ClaudeCodeAdapter(HarnessAdapter):
    name = "claude-code"

    def build_invocation(
        self,
        cwd: Path,
        prompt: str,
        credential: dict | None = None,
        model: str | None = None,
        extra_allowed_dirs: list[Path] | None = None,
        permission_mode: str | None = None,
    ) -> HeadlessInvocation:
        cmd = ["claude", "-p", prompt]
        if model:
            cmd += ["--model", model]
        for extra_dir in extra_allowed_dirs or []:
            cmd += ["--add-dir", str(extra_dir)]
        if permission_mode == "scoped":
            cmd += ["--allowedTools", FERRAMENTAS_ESCOPO_FABRICA]
        elif permission_mode == "bypass":
            cmd += ["--allow-dangerously-skip-permissions"]
        env = self.credential_env(credential)
        return HeadlessInvocation(cmd=cmd, cwd=Path(cwd), env=env)
