#!/usr/bin/env python3
"""
Helper compartilhado por pool-materiais.py, auditar-projeto.py e
empacotar-projeto.py: separa "tipo" (qual validador/dimensao/CTA se aplica) de
"pasta" (nome real do diretorio em output/<slug>/, que pode ser uma versao
regenerada por /gerar-<material> — ver REGRA 11 do AGENTS.md).

Tambem e a FONTE UNICA da regra deterministica dos presets
/kit-completo-<publico> (SPEC_COMANDOS.md): consumida por parametros_projeto.py
(--validar) e auditar-projeto.py (gate --estrito). Nunca duplicar PRESETS_KIT_COMPLETO
ou erros_preset_kit_completo em outro script — lição do bug historico de TIPOS_VALIDOS
duplicado.

Convencao de versionamento (mesma do slug de projeto inteiro no /esbocar):
1a geracao = pasta sem sufixo (ex.: "pdf"); regeneracoes seguintes = "pdf-v2",
"pdf-v3"... Nunca sobrescreve uma pasta ja entregue.
"""

import re

RE_VERSAO = re.compile(r"^(.+)-v(\d+)$")

# Presets /kit-completo-<publico> (SPEC_COMANDOS.md, secao /kit-completo-consultor):
# publico_alvo fixo + materiais fixos por preset.
PRESETS_KIT_COMPLETO = {
    "consultores": {
        "publico_alvo": "consultores",
        "materiais": ["pdf", "kit-consultor", "landing-page", "apresentacao"],
    },
    "distribuidores": {
        "publico_alvo": "distribuidores",
        "materiais": ["pdf", "kit-distribuidor", "landing-page", "apresentacao"],
    },
    "clientes": {
        "publico_alvo": "clientes",
        "materiais": ["pdf", "landing-page", "apresentacao"],
    },
}

KITS = {"kit-consultor", "kit-distribuidor"}


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


def erros_preset_kit_completo(config):
    """Regra deterministica dos presets /kit-completo-<publico>: retorna lista de
    erros (vazia se conforme ou se o config nao usa preset). Chamado por
    parametros_projeto.py --validar e auditar-projeto.py --estrito."""
    preset = config.get("preset_kit_completo")
    if not preset:
        return []
    if preset not in PRESETS_KIT_COMPLETO:
        return [
            f"preset_kit_completo invalido: {preset!r} - esperado um de "
            f"{sorted(PRESETS_KIT_COMPLETO)}"
        ]

    erros = []
    esperado = PRESETS_KIT_COMPLETO[preset]
    publico = config.get("publico_alvo")
    if publico != esperado["publico_alvo"]:
        erros.append(
            f"preset {preset!r} exige publico_alvo {esperado['publico_alvo']!r}, "
            f"mas config.publico_alvo = {publico!r}"
        )

    materiais = set(config.get("materiais_selecionados", []))
    for m in esperado["materiais"]:
        if m not in materiais:
            erros.append(
                f"preset {preset!r} exige o material {m!r} em materiais_selecionados"
            )
    for kit in sorted(KITS):
        if kit not in esperado["materiais"] and kit in materiais:
            erros.append(
                f"preset {preset!r} nao inclui kits - material {kit!r} nao pode "
                f"estar em materiais_selecionados"
            )
    return erros
