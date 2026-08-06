#!/usr/bin/env python3
"""
Helper compartilhado por pool-materiais.py, auditar-projeto.py e
empacotar-projeto.py: separa "tipo" (qual validador/dimensao/CTA se aplica) de
"pasta" (nome real do diretorio em output/<slug>/, que pode ser uma versao
regenerada por /gerar-<material> — ver REGRA 11 do AGENTS.md).

Convencao de versionamento (mesma do slug de projeto inteiro no /esbocar):
1a geracao = pasta sem sufixo (ex.: "pdf"); regeneracoes seguintes = "pdf-v2",
"pdf-v3"... Nunca sobrescreve uma pasta ja entregue.
"""

import re

RE_VERSAO = re.compile(r"^(.+)-v(\d+)$")


def tipo_base(pasta):
    """'pdf-v2' -> 'pdf'; 'pdf' -> 'pdf'."""
    m = RE_VERSAO.match(pasta)
    return m.group(1) if m else pasta


def numero_versao(pasta):
    """'pdf-v2' -> 2; 'pdf' -> 1 (1a geracao, implicita)."""
    m = RE_VERSAO.match(pasta)
    return int(m.group(2)) if m else 1


def proxima_pasta_livre(dir_slug, tipo_base_str):
    """Proximo nome de pasta livre para uma NOVA versao de tipo_base_str dentro
    de dir_slug: o proprio tipo_base_str se a pasta ainda nao existe (1a
    geracao), senao tipo_base_str-v2, -v3... (primeiro numero livre)."""
    if not (dir_slug / tipo_base_str).exists():
        return tipo_base_str
    n = 2
    while (dir_slug / f"{tipo_base_str}-v{n}").exists():
        n += 1
    return f"{tipo_base_str}-v{n}"
