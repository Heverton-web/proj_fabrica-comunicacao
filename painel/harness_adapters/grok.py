"""Adaptador para Grok Build (xAI) headless (``grok -p``).

CLI first-party da xAI (lançado 14/mai/2026). Sintaxe de CLI validada só por
construção de comando nesta entrega (ver README/limitações). Credencial
convencional é ``XAI_API_KEY``, mas o painel injeta o que o usuário
configurar no cofre (mecanismo genérico, não hardcoded).
"""

from __future__ import annotations

from pathlib import Path

from painel.harness_adapters.base import HarnessAdapter, HeadlessInvocation


class GrokAdapter(HarnessAdapter):
    name = "grok"

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
        cmd = ["grok", "-p", prompt]
        if model:
            cmd += ["-m", model]
        if permission_mode == "bypass":
            cmd += ["--always-approve"]
        env = self.credential_env(credential)
        return HeadlessInvocation(cmd=cmd, cwd=Path(cwd), env=env)
