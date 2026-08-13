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


class ClaudeCodeAdapter(HarnessAdapter):
    name = "claude-code"

    def build_invocation(
        self,
        cwd: Path,
        prompt: str,
        credential: dict | None = None,
        model: str | None = None,
    ) -> HeadlessInvocation:
        cmd = ["claude", "-p", prompt]
        if model:
            cmd += ["--model", model]
        env = self.credential_env(credential)
        return HeadlessInvocation(cmd=cmd, cwd=Path(cwd), env=env)
