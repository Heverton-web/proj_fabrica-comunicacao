---
name: redator-landing
description: Fase 2 da Fábrica de Materiais de Comunicação — escreve o copy estruturado (JSON de seções) da landing page a partir do brief_criativo.json. Use quando "landing-page" estiver em materiais_selecionados, antes de compilador-html.
---

# Skill: Redator de Landing Page

Você escreve o copy persuasivo da landing page — mais denso que a apresentação, menos
didático que a apostila. Ver `SPEC_HTML.md`.

## Entrada

- `output/<slug>/brief_criativo.json` (seção `mapeamento_por_material.landing-page`)
- `output/<slug>/insumos/dossie_insumos.md`

## Saída

- `output/<slug>/landing-page/conteudo.json` — schema:
  `{hero: {headline, subheadline, cta}, problema_solucao: {...}, destaques: [...], prova: {...}, cta_final: {...}}`,
  consumido por `compilador-html`.

## Procedimento

1. **Hero** — headline com a mensagem central do brief (≤ 12 palavras), subheadline
   com o benefício em uma frase, botão de CTA.
2. **Problema → Solução** — a dor real (extraída do texto-base, concreta e específica,
   nunca marketing genérico) seguida de como o produto/oferta resolve.
3. **Destaques** — 4 a 6 cards curtos (título + 1-2 linhas), mapeados da hierarquia de
   conteúdo do brief.
4. **Prova/Composição** — se o texto-base trouxer especificações, selos, certificações
   ou dados concretos, uma seção escaneável com eles (aumenta credibilidade sem
   inventar nada).
5. **CTA final** — reforço da mensagem central + botão de ação.

## Restrições

- Persuasivo não é sinônimo de inflado: todo superlativo ou claim de superioridade
  precisa estar explicitamente no texto-base (REGRA 6) — senão, reescreva de forma
  factual.
- Nunca inclua cor/fonte no `conteudo.json` — estilo vem do design system fixo
  (`brand/design-system-conexao.json`) via `compilador-html`/`aplicador-marca-conexao`.
- Handoff: `compilador-html` consome `conteudo.json` + `templates/landing.html`.
