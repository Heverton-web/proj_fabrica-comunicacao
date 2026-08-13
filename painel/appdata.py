"""Resolve o diretório de dados da aplicação (fora de qualquer workspace do usuário).

Nunca grava credenciais ou índice de execuções dentro da pasta de artefatos do
usuário. Por padrão usa ``~/.fabrica-painel``; testes sobrescrevem via a
variável de ambiente ``FABRICA_PAINEL_HOME`` para nunca tocar o home real.
"""

from __future__ import annotations

import os
from pathlib import Path


def appdata_dir() -> Path:
    override = os.environ.get("FABRICA_PAINEL_HOME")
    base = Path(override) if override else Path.home() / ".fabrica-painel"
    base.mkdir(parents=True, exist_ok=True)
    return base
