"""Adaptador para OMP / Oh My Pi headless (``omp -p``).

Open source, agnóstico de provedor (github.com/can1357/oh-my-pi). Sintaxe de
CLI validada só por construção de comando nesta entrega (ver
README/limitações). Credencial é por provedor conforme o modelo escolhido
(ex.: ``ANTHROPIC_API_KEY``, ``OPENAI_API_KEY``, ``XAI_API_KEY``) — o
mecanismo genérico do painel já cobre isso sem hardcode.
"""

from __future__ import annotations

from pathlib import Path

from painel.harness_adapters.base import HarnessAdapter, HeadlessInvocation


class OmpAdapter(HarnessAdapter):
    name = "omp"

    def build_invocation(
        self,
        cwd: Path,
        prompt: str,
        credential: dict | None = None,
        model: str | None = None,
        extra_allowed_dirs: list[Path] | None = None,
        permission_mode: str | None = None,
    ) -> HeadlessInvocation:
        # Sem equivalente conhecido a --add-dir/"scoped"/"bypass" -- a
        # pesquisa nao achou flag de auto-aprovacao/skip-permissions
        # documentada (design parece girar em torno de gates interativos de
        # permissao); permission_mode e extra_allowed_dirs sao ignorados de
        # proposito (mesmo padrao do adaptador opencode pra "scoped").
        cmd = ["omp", "-p", prompt]
        if model:
            cmd += ["--model", model]
        env = self.credential_env(credential)
        return HeadlessInvocation(cmd=cmd, cwd=Path(cwd), env=env)
