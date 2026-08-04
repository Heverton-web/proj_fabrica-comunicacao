---
description: Regenera só a landing page de um projeto já esboçado, sem repetir a entrevista nem re-analisar insumos. Falha rápido se o projeto ainda não tiver brief_criativo.json.
---

# /gerar-landing

`$ARGUMENTS` = `<slug>`. Regeneração pontual — nunca re-executa `/esbocar` nem
`analista-insumos`/`diretor-de-arte`.

## Pré-condição (falhe rápido se ausente)

Confirme que `output/<slug>/brief_criativo.json` existe. Se não existir, pare e informe:
"Rode `/esbocar` (ou `/produzir-comunicacao-completa <slug>`) primeiro — este projeto
ainda não tem brief criativo."

## Procedimento

1. Se `landing-page` não estiver em `config_projeto.materiais_selecionados`, adicione-o.
2. Despache `subagente-produtor-landing` para `<slug>`.
3. Despache `subagente-revisor-marca` só para o tipo `landing-page`.
4. Rode `python scripts/auditar-projeto.py <slug> --estrito --apenas landing-page`.
5. Rode `python scripts/empacotar-projeto.py <slug>`.
6. Reporte (REGRA 2): path do `index.html`, decisões de design, faltantes.
