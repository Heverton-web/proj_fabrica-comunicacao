---
name: redator-arte
description: Fase 2 da Fábrica de Materiais de Comunicação — escreve headline/subcopy/CTA curtos para cada variante de arte PNG (1080x1080, 1080x1350, 1080x1920) a partir do brief_criativo.json, respeitando limites de caracteres por formato. Use quando qualquer arte-01/02/03 estiver em materiais_selecionados, antes de compilador-arte.
---

# Skill: Redator de Arte

Você escreve o texto que vai dentro de cada peça de arte para redes sociais/WhatsApp —
o material mais curto e mais "isca visual" dos 6 tipos. Ver `SPEC_ARTE.md`.

## Entrada

- `output/<slug>/brief_criativo.json` (seção `mapeamento_por_material.arte`)
- `output/<slug>/insumos/dossie_insumos.md`

## Saída

- `output/<slug>/arte-0N/conteudo.json` (um por variante selecionada) — schema:
  `{headline, subcopy, cta, imagem_produto}`, consumido por `compilador-arte`.

## Procedimento

Para cada variante selecionada (`arte-01`/`arte-02`/`arte-03`), escreva:

- **headline** — a mensagem central do brief, comprimida a ≤ 60 caracteres.
- **subcopy** — um benefício de apoio, ≤ 120 caracteres.
- **cta** — chamada de ação curta, ≤ 30 caracteres (ex.: "Fale com um consultor").
- **imagem_produto** — path da imagem oficial do produto/marca a usar (nunca gerar
  ilustração no lugar dela — REGRA 6, mesma regra do exemplo Conexão: "use esta
  imagem... não invente/ilustre o produto").

Adapte a ênfase por formato: `arte-01` (quadrado) funciona bem como "isca" enviada
antes de um PDF/link; `arte-03` (vertical/stories) tem mais espaço vertical — pode
acomodar um destaque técnico extra se o subcopy permitir.

## Restrições

- Respeite os limites de caracteres à risca — texto que não cabe no layout é reportado
  por `validar-dimensoes.py`/`compilador-arte` como falha, não corrigido silenciosamente
  com fonte menor que a marca não usa.
- Nunca invente claim/número fora do dossiê de insumos.
- Handoff: `compilador-arte` consome `conteudo.json` + `templates/arte-<variante>.html`.
