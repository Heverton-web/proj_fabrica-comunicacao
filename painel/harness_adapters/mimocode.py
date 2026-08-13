"""Adaptador para MimoCode (Xiaomi MiMo) headless (``mimo run``).

Open source (MIT), interface compatível com a API da Anthropic. Sintaxe de
CLI validada só por construção de comando nesta entrega (ver
README/limitações). Credencial NÃO é variável de ambiente — fica em
``~/.local/share/mimocode/auth.json`` — então o cofre de credencial do
painel não se aplica de verdade a este harness; o usuário precisa logar/
configurar o MimoCode fora do painel antes de disparar um job com ele.
"""

from __future__ import annotations

from pathlib import Path

from painel.harness_adapters.base import HarnessAdapter, HeadlessInvocation


class MimoCodeAdapter(HarnessAdapter):
    name = "mimocode"

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
        cmd = ["mimo", "run", prompt]
        if model:
            cmd += ["--model", model]
        if permission_mode == "bypass":
            cmd += ["--dangerously-skip-permissions"]
        env = self.credential_env(credential)
        return HeadlessInvocation(cmd=cmd, cwd=Path(cwd), env=env)
