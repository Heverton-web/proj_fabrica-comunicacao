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

- `output/<slug>/<pasta>/conteudo.json` — `<pasta>` é informada pelo subagente que te
  invoca (normalmente `"landing-page"`, ou `"landing-page-v2"` numa regeneração via
  `/gerar-landing` — REGRA 11 do `AGENTS.md`: nunca escreva por cima de uma versão já
  entregue). Schema:
  `{hero: {headline, subheadline, cta}, problema_solucao: {...}, destaques: [...], prova: {...}, cta_final: {...}, enriquecimentos?: [...]}`,
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
6. **Componentes animados de dado (opcional — ver
   `.claude/skills/aplicador-marca-conexao/SKILL.md`, seção "Componentes animados de
   dado"):** se o dossiê tiver percentual do todo, estatística de destaque, processo
   sequencial ou perguntas/respostas, acrescente ao `conteudo.json` um array de topo
   `enriquecimentos: [{"secao": "destaques"|"prova"|"cta_final"|"problema_solucao",
   "tipo": "donut"|"contador"|"fluxo"|"accordion"|"barras"|"gauge", "dados": {...}}]`.
   **Nunca invente dado para caber num componente (REGRA 6)** — se o dossiê não
   sustenta nenhum gatilho, a seção continua como card/tabela simples.

### Critério de julgamento de design e copy (embutido — funciona em qualquer harness)

Esta orientação está escrita aqui, não referenciada de uma skill externa, para
funcionar igual em Claude Code, Antigravity, OpenCode, Freebuff, MiMoCode ou
qualquer outro ambiente que apenas leia este arquivo como instrução:

- **Marcador numerado só se a ordem carregar informação real** — não decore
  uma lista de destaques com números só para parecer mais estruturada.
- **Cada componente animado precisa servir o conteúdo, não decorar por
  decorar** — se um `enriquecimento` não deixa a informação mais clara que o
  texto puro, não force (REGRA 6).
- **Copy específico vence copy genérico:** escreva do ponto de vista de quem
  lê (consultor, cliente, distribuidor), nomeando o que a pessoa reconhece e
  controla — nunca do ponto de vista de como o material foi montado. CTA em
  voz ativa e específica ("Consultar guia completo", não "Saiba mais").

## Tom de voz por público-alvo (obrigatório — REGRA 6)

Leia `brief_criativo.publico_alvo` e aplique o registro de linguagem definido em
`brand/publicos-alvo.json` para esse público. A landing page é o material mais
persuasivo — o tom errado aqui é o erro mais visível.

| Público | Tom | Ênfase na landing |
|---------|-----|-------------------|
| `consultores` | Técnico-clínico | Hero com dado técnico de impacto → seção de specs → selos/certificações |
| `clientes` | Acessível/orientador | Hero com benefício de resultado → prova social → CTA de contato |
| `distribuidores` | Comercial-parceiro | Hero com proposta de parceria → diferenciais de distribuição → CTA de cadastro comercial |

O `dossie_insumos.md` gerado por `analista-insumos` já traz as implicações práticas
do público escolhido — use-as como guia, não as re-derive do texto-base.

## Restrições

- Persuasivo não é sinônimo de inflado: todo superlativo ou claim de superioridade
  precisa estar explicitamente no texto-base (REGRA 6) — senão, reescreva de forma
  factual.
- Nunca inclua cor/fonte no `conteudo.json` — estilo vem do design system fixo
  (`brand/design-system-conexao.json`) via `compilador-html`/`aplicador-marca-conexao`.
- O tom de voz vem de `brief_criativo.tom_de_voz` (escolha do operador, via
  `brand/publicos-alvo.json`) — nunca re-derive do texto-base.
- Handoff: `compilador-html` consome `conteudo.json` + `templates/landing.html`.
