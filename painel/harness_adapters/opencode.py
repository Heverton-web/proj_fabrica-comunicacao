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
        extra_allowed_dirs: list[Path] | None = None,
        permission_mode: str | None = None,
    ) -> HeadlessInvocation:
        # opencode nao tem, na versao testada, um flag equivalente ao
        # --add-dir do claude-code; extra_allowed_dirs e' ignorado aqui de
        # proposito (ver painel/README.md). "scoped" tambem nao tem
        # equivalente conhecido — so "bypass" mapeia pra algo real (--auto).
        cmd = ["opencode", "run", prompt]
        if model:
            cmd += ["--model", model]
        if permission_mode == "bypass":
            cmd += ["--auto"]
        env = self.credential_env(credential)
        return HeadlessInvocation(cmd=cmd, cwd=Path(cwd), env=env)
