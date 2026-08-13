"""Registry de adaptadores de harness — o ponto que torna o painel universal.

Cada adaptador só sabe montar um comando headless (cmd/cwd/env) para o harness
que representa; nenhuma skill, SPEC ou script da Fábrica é reescrita — o
adaptador apenas invoca o harness já existente exatamente como um operador
humano faria na CLI.
"""

from __future__ import annotations

from painel.harness_adapters.base import HarnessAdapter, HeadlessInvocation
from painel.harness_adapters.claude_code import ClaudeCodeAdapter
from painel.harness_adapters.echo import EchoAdapter
from painel.harness_adapters.opencode import OpencodeAdapter

_REGISTRY: dict[str, HarnessAdapter] = {
    "echo": EchoAdapter(),
    "claude-code": ClaudeCodeAdapter(),
    "opencode": OpencodeAdapter(),
}


class UnknownHarnessError(KeyError):
    """Harness não registrado no painel."""


def get_adapter(name: str) -> HarnessAdapter:
    try:
        return _REGISTRY[name]
    except KeyError as exc:
        raise UnknownHarnessError(
            f"Harness '{name}' não registrado. Disponíveis: {sorted(_REGISTRY)}"
        ) from exc


def list_harness_names() -> list[str]:
    return sorted(_REGISTRY)


__all__ = [
    "HarnessAdapter",
    "HeadlessInvocation",
    "UnknownHarnessError",
    "get_adapter",
    "list_harness_names",
]
