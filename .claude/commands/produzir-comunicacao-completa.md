---
description: Passo 2 da Fábrica de Materiais de Comunicação — produção 100% autônoma de todos os materiais selecionados em config_projeto.json, em lotes paralelos, com revisão de marca e empacotamento final. Requer que /esbocar já tenha rodado para este slug.
---

# /produzir-comunicacao-completa

`$ARGUMENTS` = `<slug>`. Se `output/<slug>/config_projeto.json` não existir, rode
`/esbocar` primeiro (inline, sem novo comando do operador) e só então continue.

Este comando não pausa para nenhuma pergunta (REGRA 3). Ver `SPEC.md` para o contrato
completo do Passo 2.

## Passo 0 — Validação de pré-condições

```
python scripts/parametros_projeto.py <slug> --validar
```

Se `brief_criativo.json` ainda não existir (ex.: operador rodou `/esbocar` mas a sessão
foi interrompida antes do Passo 5 dele — gravação e preparação), invoque
`analista-insumos` e `diretor-de-arte` agora, sem perguntar nada ao operador.

## Passo 1 — Pre-flight de compatibilidade de slug

```
python scripts/preflight-compatibilidade-slug.py <slug> --estrito
```

Roda uma única vez, antes de qualquer fan-out, para detectar se algum
`scripts/compilar-*.py` compartilhado tem string de outro projeto hardcoded (mesma
causa raiz do bug de path de imagem já corrigido em `compilar-html.py`/
`compilar-arte.py`/`compilar-pdf.py`). Se retornar não-conforme, corrija o compilador
apontado (REGRA 4) antes de prosseguir — evita que múltiplos subagentes descubram o
mesmo problema de forma redundante durante a produção real.

## Passo 2 — Plano de lotes

```
python scripts/pool-materiais.py <slug> --plano --lote 4
```

Imprime os materiais de `materiais_selecionados` divididos em lotes de até 4.

## Passo 2.5 — Copy compartilhada de arte (uma única vez, antes de qualquer fan-out de arte)

Se qualquer `arte-01`/`arte-02`/`arte-03` estiver em `materiais_selecionados` e
`output/<slug>/arte/copies.json` ainda não existir (ou não tiver exatamente 3 copies),
invoque o skill `redator-arte` **inline, agora, uma única vez** — nunca delegue isso a
um `subagente-produtor-arte`. Formato (dimensão do PNG) e copy (conceito criativo) são
eixos ortogonais: as mesmas 3 copies são compartilhadas por todos os formatos
selecionados (ver `docs/05-plano-expansao-multi-copy-arte.md`). Gerar a copy dentro de
cada subagente de formato reintroduz o bug original — 3 subagentes paralelos
descobrindo/escrevendo 3 copies divergentes em vez de reaproveitar as mesmas 3 em todos
os formatos.

Este passo precisa terminar **antes** de despachar o lote que contém qualquer
`arte-0N`, mesmo que esse lote não seja o primeiro.

## Passo 3 — Fan-out em lote (disciplina de concorrência — nunca tudo de uma vez)

Para cada lote do plano, **nesta ordem, sem pular etapas**:

1. Despache, na mesma mensagem/rodada, um subagente por material do lote:
   - `pdf` → `subagente-produtor-pdf`
   - `landing-page` → `subagente-produtor-landing`
   - `apresentacao` → `subagente-produtor-apresentacao`
   - `arte-01`/`arte-02`/`arte-03` → `subagente-produtor-arte` (um por variante —
     requer que o Passo 2.5 já tenha gerado `arte/copies.json`)
   - `textos` → `subagente-produtor-textos`
2. Aguarde **todos** os subagentes do lote terminarem (cada um já auto-registra sucesso
   ou falha via `pool-materiais.py --registrar`).
3. Só então consulte `python scripts/pool-materiais.py <slug> --proximo-lote --lote 4`
   e despache o próximo lote.

Depois de todos os lotes planejados, drene pendentes:

```
python scripts/pool-materiais.py <slug> --pendentes --lote 4
```

Retentar com o backoff indicado (15s × 2^tentativas, máx. 240s), máximo 3 tentativas
por material — depois disso o material fica `esgotado` e é reportado, não bloqueia os
demais (R9 do `SPEC.md`).

## Passo 4 — Revisão de marca em lote

Se o total de materiais `concluido_autonomo` for **até 6**, despache **1 único**
`subagente-revisor-marca` cobrindo todos eles — reduz overhead de reconstrução de
contexto por subagente sem abrir mão da REGRA 7 (o subagente ainda lê tudo por
completo, só há menos subagentes no total). Se o total for **maior que 6**, divida em
lotes de até 6 (cada um só toca nos tipos do seu próprio lote, nunca todos de uma vez).

## Passo 5 — Auditoria final determinística

```
python scripts/auditar-projeto.py <slug> --estrito
```

Se retornar não-conforme, aplique as correções indicadas (REGRA 4) e rode de novo —
até 3 rodadas. Se ainda não-conforme na 3ª rodada, siga para o empacotamento mesmo
assim, reportando as não-conformidades residuais (nunca trave a entrega dos materiais
que já estão conformes).

## Passo 6 — Empacotamento final

```
python scripts/empacotar-projeto.py <slug>
```

Monta a estrutura final em `output/<slug>/{pdf,landing-page,apresentacao,arte-01,arte-02,arte-03,textos}/`
e grava `manifesto_materiais.json`.

## Passo 7 — Relatório final (REGRA 2 — telegráfico, sem preâmbulo)

Reporte: materiais entregues (com path), materiais esgotados (com motivo), decisões de
design tomadas, informações faltantes, sugestões de legenda/CTA para compartilhamento
(REGRA 6/R11 do `SPEC.md`).
