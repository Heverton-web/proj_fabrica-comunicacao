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

## Passo 1 — Plano de lotes

```
python scripts/pool-materiais.py <slug> --plano --lote 4
```

Imprime os materiais de `materiais_selecionados` divididos em lotes de até 4.

## Passo 2 — Fan-out em lote (disciplina de concorrência — nunca tudo de uma vez)

Para cada lote do plano, **nesta ordem, sem pular etapas**:

1. Despache, na mesma mensagem/rodada, um subagente por material do lote:
   - `pdf` → `subagente-produtor-pdf`
   - `landing-page` → `subagente-produtor-landing`
   - `apresentacao` → `subagente-produtor-apresentacao`
   - `arte-01`/`arte-02`/`arte-03` → `subagente-produtor-arte` (um por variante)
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

## Passo 3 — Revisão de marca em lote

Divida os materiais `concluido_autonomo` em lotes de até 4 e despache
`subagente-revisor-marca` (um por lote, cada um só toca nos tipos do seu próprio lote).

## Passo 4 — Auditoria final determinística

```
python scripts/auditar-projeto.py <slug> --estrito
```

Se retornar não-conforme, aplique as correções indicadas (REGRA 4) e rode de novo —
até 3 rodadas. Se ainda não-conforme na 3ª rodada, siga para o empacotamento mesmo
assim, reportando as não-conformidades residuais (nunca trave a entrega dos materiais
que já estão conformes).

## Passo 5 — Empacotamento final

```
python scripts/empacotar-projeto.py <slug>
```

Monta a estrutura final em `output/<slug>/{pdf,landing-page,apresentacao,arte-01,arte-02,arte-03,textos}/`
e grava `manifesto_materiais.json`.

## Passo 6 — Relatório final (REGRA 2 — telegráfico, sem preâmbulo)

Reporte: materiais entregues (com path), materiais esgotados (com motivo), decisões de
design tomadas, informações faltantes, sugestões de legenda/CTA para compartilhamento
(REGRA 6/R11 do `SPEC.md`).
