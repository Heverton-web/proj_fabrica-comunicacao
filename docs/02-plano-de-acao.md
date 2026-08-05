---
title: "Plano de Ação — Fábrica de Materiais de Comunicação"
subtitle: "Execução das correções do Relatório de Melhorias (01-relatorio-de-melhorias)"
date: "2026-08-05"
author: "Auditoria técnica do pipeline"
---

# Plano de Ação — Fábrica de Materiais de Comunicação

Plano derivado de `01-relatorio-de-melhorias.md`, organizado por fase de dependência
(não por severidade), para implementação de início ao fim.

---

## Fase 0 — Destravar "Textos" (crítico, bloqueia produto hoje)

1. Editar `.claude/commands/esbocar.md`, Passo 4: acrescentar a 7ª opção **"Textos de
   Apoio (WhatsApp/Instagram/LinkedIn)"** ao `AskUserQuestion`, corrigir o texto de "6
   opções" → "7 opções".
2. Validar que o lado de produção (`subagente-produtor-textos`, dispatch,
   `validar-textos.py`) já suporta o tipo corretamente (confirmado na auditoria — não
   precisa de mudança).

**Esforço:** baixo · **Risco:** baixo.

---

## Fase 1 — Consolidar correções já aplicadas nesta sessão

1. Rodar regressão em `kit-start-flex` (`auditar-projeto.py kit-start-flex --estrito`)
   para confirmar que a generalização dos paths de imagem não quebrou o comportamento
   original.
2. Corrigir o nome de arquivo enganoso da imagem em `output/kit-stop-drill/` (referencia
   `kit_start_flex_frontal.png` para uma foto que é do Kit Stop Drill).

**Esforço:** baixo · **Risco:** baixo.

---

## Fase 2 — Guarda-corpo de consistência do pipeline

1. Criar `scripts/verificar-consistencia-pipeline.py`: para cada tipo em
   `TIPOS_VALIDOS`, confirma que existe (a) opção em `esbocar.md` Passo 4, (b) entrada
   no dispatch de `produzir-comunicacao-completa.md`, (c) skill `redator-*`, (d) agente
   `subagente-produtor-*`, (e) `validar-*.py`.
2. Rodar o script (deve passar 7/7 após a Fase 0).
3. Acrescentar a coluna "selecionável via `/esbocar`" na tabela de materiais de
   `SPEC.md`/`CLAUDE.md`.

**Esforço:** médio · **Risco:** baixo.

---

## Fase 3 — Otimização de processo (economia de tokens)

1. Criar script de pre-flight de compatibilidade de slug, rodado antes do fan-out de
   produção, detectando strings de outro slug hardcoded em `scripts/compilar-*.py`.
2. Consolidar lotes de `revisor-marca` em `produzir-comunicacao-completa.md` quando o
   total de materiais for pequeno (≤6 → 1 lote em vez de 2+).
3. Adicionar digest estático do design system fixo em
   `aplicador-marca-conexao/SKILL.md`.

**Esforço:** baixo-médio · **Risco:** baixo. **Não fazer:** resumir o dossiê de
insumos para os `redator-*` (violaria REGRA 6/7).

---

## Fase 4 — Documentação e limpeza

1. Corrigir `CLAUDE.md`: documentar os dois mecanismos reais de auto-atualização do
   grafo (`.claude/settings.json` no Claude Code; `.gemini/hooks/*.sh` no Gemini CLI).
2. Ajustar REGRA 9 para refletir a cobertura real do grafo (só scripts Python hoje).
3. Trocar permissões literais escopadas a `kit-start-flex` em
   `.claude/settings.local.json` por padrões wildcard.
4. Corrigir/documentar os scripts de debug `.crg-regenerate.py`/`.crg-visual.py`.

**Esforço:** baixo · **Risco:** baixo.

---

## Sequenciamento

Fase 0 → Fase 1 → Fase 2 → Fase 3 → Fase 4 — cada fase é independente das seguintes;
execução completa registrada e verificada ao final via
`scripts/verificar-consistencia-pipeline.py` e regressão em `kit-start-flex`.
