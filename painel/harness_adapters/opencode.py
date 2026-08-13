"""Adaptador para opencode headless (``opencode run``).

O opencode já é nativamente multi-provedor/BYOK — este adaptador só monta o
comando e injeta a credencial escolhida pelo usuário via variável de ambiente
do provedor selecionado. Sintaxe de CLI validada só por construção de comando
nesta entrega (ver README/limitações).
"""

from __future__ import annotations

from pathlib import Path

from painel.harness_adapters.base import HarnessAdapter, HeadlessInvocation


class OpencodeAdapter(HarnessAdapter):
    name = "opencode"

    def build_invocation(
        self,
        cwd: Path,
        prompt: str,
        credential: dict | None = None,
        model: str | None = None,
    ) -> HeadlessInvocation:
        cmd = ["opencode", "run", prompt]
        if model:
            cmd += ["--model", model]
        env = self.credential_env(credential)
        return HeadlessInvocation(cmd=cmd, cwd=Path(cwd), env=env)
