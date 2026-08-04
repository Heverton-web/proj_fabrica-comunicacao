---
description: Regenera uma ou mais variantes de arte PNG (1080x1080/1080x1350/1080x1920) de um projeto já esboçado, sem repetir a entrevista nem re-analisar insumos. Falha rápido se o projeto ainda não tiver brief_criativo.json.
---

# /gerar-arte

`$ARGUMENTS` = `<slug> [--tamanho 1080x1080|1080x1350|1080x1920 ...]`. Sem `--tamanho`,
regenera todas as 3 variantes. Regeneração pontual — nunca re-executa `/esbocar` nem
`analista-insumos`/`diretor-de-arte`.

## Pré-condição (falhe rápido se ausente)

Confirme que `output/<slug>/brief_criativo.json` existe. Se não existir, pare e informe:
"Rode `/esbocar` (ou `/produzir-comunicacao-completa <slug>`) primeiro — este projeto
ainda não tem brief criativo."

## Mapeamento de `--tamanho` para tipo de material

- `1080x1080` → `arte-01`
- `1080x1350` → `arte-02`
- `1080x1920` → `arte-03`

## Procedimento

1. Resolva a lista de variantes a partir de `--tamanho` (ou as 3, se omitido). Para
   cada uma não presente em `config_projeto.materiais_selecionados`, adicione-a.
2. Despache um `subagente-produtor-arte` por variante, em paralelo.
3. Despache `subagente-revisor-marca` só para as variantes desta rodada.
4. Rode `python scripts/auditar-projeto.py <slug> --estrito --apenas <variantes>`.
5. Rode `python scripts/empacotar-projeto.py <slug>`.
6. Reporte (REGRA 2): path de cada PNG, decisões de design, faltantes, sugestões de
   legenda por variante.
