---
description: Regenera só o material PDF (apostila) de um projeto já esboçado, sem repetir a entrevista nem re-analisar insumos. Falha rápido se o projeto ainda não tiver brief_criativo.json.
---

# /gerar-pdf

`$ARGUMENTS` = `<slug>`. Regeneração pontual — nunca re-executa `/esbocar` nem
`analista-insumos`/`diretor-de-arte`.

## Pré-condição (falhe rápido se ausente)

Confirme que `output/<slug>/brief_criativo.json` existe. Se não existir, pare e informe:
"Rode `/esbocar` (ou `/produzir-comunicacao-completa <slug>`) primeiro — este projeto
ainda não tem brief criativo." Nunca invente um brief para contornar isso.

## Procedimento

1. Se `pdf` não estiver em `config_projeto.materiais_selecionados`, adicione-o (o
   operador está pedindo explicitamente este material agora).
2. Despache `subagente-produtor-pdf` para `<slug>`.
3. Despache `subagente-revisor-marca` só para o tipo `pdf`.
4. Rode `python scripts/auditar-projeto.py <slug> --estrito --apenas pdf`.
5. Rode `python scripts/empacotar-projeto.py <slug>` (reempacota o manifesto sem tocar
   nos outros materiais já entregues).
6. Reporte (REGRA 2): path do PDF final, decisões de design, faltantes, sugestão de
   legenda de compartilhamento.
