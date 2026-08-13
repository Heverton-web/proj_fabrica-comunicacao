"""Contrato comum de todo adaptador de harness."""

from __future__ import annotations

import os
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class HeadlessInvocation:
    """Comando pronto para ser passado a ``subprocess`` pelo job runner."""

    cmd: list[str]
    cwd: Path
    env: dict[str, str] = field(default_factory=dict)

    def full_env(self) -> dict[str, str]:
        """Ambiente do processo atual + overrides do adaptador (credencial/modelo)."""
        merged = dict(os.environ)
        merged.update(self.env)
        return merged

    def resolved_cmd(self) -> list[str]:
        """Resolve o executável via PATH antes de passar ao ``subprocess``.

        Sem isso, CLIs instaladas via npm (que no Windows são shims
        ``.cmd``/``.bat``, não um ``.exe``) falham com "arquivo não
        encontrado" quando o ``subprocess`` roda com ``shell=False`` — mesmo
        com o binário instalado e funcionando normalmente no terminal.
        """
        if not self.cmd:
            return self.cmd
        resolved = shutil.which(self.cmd[0])
        return [resolved, *self.cmd[1:]] if resolved else self.cmd


class HarnessAdapter(ABC):
    """Monta a invocação headless de um harness a partir de prompt/credencial/modelo.

    Nenhum adaptador executa subprocess diretamente — isso é responsabilidade
    do job runner (``painel/jobs.py``), para manter a construção do comando
    (testável sem tocar em processo real) separada da execução.
    """

    name: str

    @abstractmethod
    def build_invocation(
        self,
        cwd: Path,
        prompt: str,
        credential: dict | None = None,
        model: str | None = None,
        extra_allowed_dirs: list[Path] | None = None,
        permission_mode: str | None = None,
    ) -> HeadlessInvocation:
        """``extra_allowed_dirs``: diretórios fora de ``cwd`` que o harness
        precisa poder ler (ex.: a raiz do repo, quando o projeto vive numa
        subpasta dele — sem isso, `claude -p` recusa ler `AGENTS.md`/
        `SPEC_COMANDOS.md` por ficarem acima do cwd).

        ``permission_mode`` — quem dispara o job escolhe, por execução,
        quanto de autonomia dar (headless não tem terminal pra aprovar nada
        interativamente):
        - ``None``/outro valor: comportamento padrão do harness (mais
          seguro; pode parar pedindo aprovação e desistir sem travar).
        - ``"scoped"``: libera só as ferramentas que o pipeline da Fábrica
          usa (Bash/Read/Write/Edit/Glob/Grep/Task), sem desligar nenhuma
          verificação de segurança do harness.
        - ``"bypass"``: desliga toda verificação de permissão do harness —
          maior raio de risco, mas às vezes é a única forma de rodar 100%
          autônomo; quem dispara o job decide.

        Adaptadores sem equivalente nativo podem ignorar os parâmetros.
        """
        ...

    @staticmethod
    def credential_env(credential: dict | None) -> dict[str, str]:
        """Convenção genérica: credencial traz ``env_var`` + ``api_key``.

        Isso permite suportar qualquer provedor (Anthropic, OpenAI, Google...)
        sem hardcodar nome de variável de ambiente no adaptador.
        """
        if not credential:
            return {}
        env_var = credential.get("env_var")
        api_key = credential.get("api_key")
        if env_var and api_key:
            return {env_var: api_key}
        return {}
