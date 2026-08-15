#!/usr/bin/env python3
"""
Biblioteca fixa de ícones da Conexão (fonte única de verdade do vocabulário).

Neste módulo vive o ÚNICO ponto determinístico do vocabulário fechado de
`categoria` de cartões/bullets dos materiais HTML (landing-page e
apresentacao). O desenho visual de cada símbolo mora no sprite estático de
templates/apresentacao.html e templates/landing.html (convenção de id
`icone-<categoria>`); este módulo conhece apenas o vocabulário e o markup de
referência (`<use>`), suficiente para compilar e arbitrar (REGRA 8 do AGENTS.md).

Uso em compilar-html.py (injeção do ícone em cartões marcados com `categoria`)
e em validar-html.py --estrito (gate: card com data-categoria precisa ter o
<use> e o <symbol> correspondentes; categoria fora do vocabulário = falha).

Ver também: .claude/skills/aplicador-marca-conexao/SKILL.md, seção "Ícones".
"""

# Vocabulário fechado: o mesmo conjunto documentado no design system e na
# seção "Ícones" do SKILL. Nunca adicionar categoria sem atualizar os três
# lugares: este módulo, o sprite dos dois templates e a seção do SKILL.
CATEGORIAS_ICONES = frozenset({
    "problema",
    "solucao",
    "dado_tecnico",
    "evidencia",
    "processo",
    "checklist",
    "tempo",
    "contato",
})


def categoria_valida(categoria):
    """True se a categoria pertence ao vocabulário fechado."""
    return categoria in CATEGORIAS_ICONES


def id_simbolo(categoria):
    """Id do <symbol> no sprite dos templates para a categoria (convenção
    `icone-<categoria>`). Retorna None para categoria fora do vocabulário."""
    if not categoria_valida(categoria):
        return None
    return f"icone-{categoria}"


def html_icone(categoria):
    """Markup do ícone a injetar dentro de um cartão marcado com `categoria`
    (apresentacao/landing). Retorna string vazia para categoria desconhecida —
    o card fica sem ícone e o gate --estrito do validar-html.py aponta a falha."""
    sid = id_simbolo(categoria)
    if not sid:
        return ""
    return (f'<svg class="icone" viewBox="0 0 24 24" aria-hidden="true">'
            f'<use href="#{sid}"></use></svg>')
