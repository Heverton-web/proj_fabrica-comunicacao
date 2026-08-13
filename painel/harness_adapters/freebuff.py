"""Adaptador para FreeBuff — MELHOR ESFORÇO, sintaxe NÃO confirmada.

FreeBuff (feito pela CodebuffAI, gratuito/financiado por anúncios) não tem,
na pesquisa feita para esta entrega, nenhuma flag de modo headless/one-shot
documentada publicamente (README e site oficial só mostram uma sessão
interativa abrindo). A sintaxe abaixo (``freebuff -p "<prompt>"``) é um
palpite por convenção com outras CLIs desta lista, escolhido conscientemente
mesmo sem confirmação (decisão do usuário) — **rode ``freebuff --help`` antes
de confiar neste adaptador em produção**; se a flag estiver errada, o processo
provavelmente vai abrir uma sessão interativa e o job ficar pendurado (sem
terminal pra usar) até estourar timeout, se houver um configurado.
"""

from __future__ import annotations

from pathlib import Path

from painel.harness_adapters.base import HarnessAdapter, HeadlessInvocation


class FreeBuffAdapter(HarnessAdapter):
    name = "freebuff"

    def build_invocation(
        self,
        cwd: Path,
        prompt: str,
        credential: dict | None = None,
        model: str | None = None,
        extra_allowed_dirs: list[Path] | None = None,
        permission_mode: str | None = None,
    ) -> HeadlessInvocation:
        cmd = ["freebuff", "-p", prompt]
        if model:
            cmd += ["--model", model]
        env = self.credential_env(credential)
        return HeadlessInvocation(cmd=cmd, cwd=Path(cwd), env=env)
