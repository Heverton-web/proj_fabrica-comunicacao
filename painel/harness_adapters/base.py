"""Contrato comum de todo adaptador de harness."""

from __future__ import annotations

import os
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
    ) -> HeadlessInvocation: ...

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
