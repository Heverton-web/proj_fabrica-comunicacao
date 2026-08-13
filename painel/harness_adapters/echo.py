"""Adaptador dry-run: não chama nenhuma LLM.

Existe para provar a canalização inteira (job runner -> subprocess real ->
arquivo criado no workspace -> status/log no índice) sem custo e sem risco de
recursão de agente. É o único adaptador validado nesta entrega com um
subprocess de verdade — os adaptadores de harness real são validados só por
construção de comando (ver README do painel).
"""

from __future__ import annotations

import sys
from pathlib import Path

from painel.harness_adapters.base import HarnessAdapter, HeadlessInvocation

_SCRIPT = (
    "import pathlib, sys\n"
    "prompt = sys.argv[1]\n"
    "pathlib.Path('smoke_marker.txt').write_text(prompt, encoding='utf-8')\n"
    "print('ECHO_OK:' + prompt)\n"
)


class EchoAdapter(HarnessAdapter):
    name = "echo"

    def build_invocation(
        self,
        cwd: Path,
        prompt: str,
        credential: dict | None = None,
        model: str | None = None,
        extra_allowed_dirs: list[Path] | None = None,
        permission_mode: str | None = None,
    ) -> HeadlessInvocation:
        cmd = [sys.executable, "-c", _SCRIPT, prompt]
        env = self.credential_env(credential)
        if model:
            env["ECHO_MODEL"] = model
        return HeadlessInvocation(cmd=cmd, cwd=Path(cwd), env=env)
