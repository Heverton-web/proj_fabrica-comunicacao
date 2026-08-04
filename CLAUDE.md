# Fábrica de Materiais de Comunicação

Fábrica agêntica que transforma (imagens + texto-base fornecidos por um operador) em um
conjunto de materiais de comunicação de marca — PDF (apostila), HTML (apresentação e
landing page) e Arte PNG (1080×1080, 1080×1350, 1080×1920) — de forma 100% autônoma
após uma única entrevista inicial.

**O design system é fixo, não extraído por projeto.** Landing page, apresentação e
arte seguem sempre `brand/design-system-conexao.json`, aplicado por
`.claude/skills/aplicador-marca-conexao/SKILL.md` — a única fonte de verdade de cor,
fonte e componente (botão, badge, card). O PDF usa o mesmo arquivo como solução
interina até que regras visuais próprias ("Flex Gold", inspiradas no material de
referência Master Flex) sejam desenhadas — ver `SPEC_PDF.md`.

Este projeto é modelado sobre a arquitetura da **Fábrica Agêntica de Livros**
(`fabrica-de-livros`): skills = estágios de pipeline, agentes = unidades paralelizáveis
de trabalho, scripts determinísticos = árbitro de qualidade. Ver `SPEC.md` para o
contrato completo e `PRD.md` para a visão de produto.

## REGRAS INVIOLÁVEIS

**REGRA 1 — Idioma Estrito (PT-BR):** toda comunicação interna entre skills/agentes e
todo material final é em português do Brasil, exceto quando o texto-base fornecido pelo
operador já estiver em outro idioma (nesse caso, preserva-se o idioma da fonte).

**REGRA 2 — Silenciamento Estético:** artefatos finais (PDF, HTML, PNG) nunca contêm
preâmbulo conversacional, saudação ou meta-comentário do agente. Apenas o material puro.

**REGRA 3 — Autonomia Total Após o `/esbocar`:** o `/esbocar` é o único ponto de
interação humana (Passo 1 do fluxo — ver `SPEC.md`, entrevista em 4 rodadas). Depois que `config_projeto.json` é
gravado, `/produzir-comunicacao-completa` roda do início ao fim sem pausas, com gates de
qualidade internos e auto-correção (REGRA 4) em vez de perguntas ao operador.

**REGRA 4 — Auto-Correção Interna:** desvios estruturais ou de formatação detectados
pelos scripts de validação (`validar-*.py`, `auditar-projeto.py`) são corrigidos
internamente pelo skill/subagente responsável antes da entrega — nunca surfaçados ao
operador como bloqueio, salvo esgotamento de tentativas (ver `pool-materiais.py`).

**REGRA 5 — Universalidade de Modelo:** todo arquivo em `.claude/agents/*.md` declara
`model: inherit` no frontmatter. Nunca fixar um modelo específico — a fábrica é
model-agnostic.

**REGRA 6 — Fidelidade à Fonte e à Marca (crítica, inegociável):**
- Nunca inventar claim, dado técnico, especificação ou benefício que não esteja
  presente no texto-base ou nas imagens fornecidas pelo operador. Informação ausente
  entra em uma lista de "faltantes" no relatório final — nunca é preenchida por
  suposição.
- Todo material deve ser visualmente fiel ao design system fixo
  (`brand/design-system-conexao.json`, cores + gradiente de assinatura + fontes +
  componentes) — nunca inventar um padrão visual novo fora do que
  `.claude/skills/aplicador-marca-conexao/SKILL.md` define. Se um componente
  necessário não estiver descrito ali, é faltante, não licença para improvisar.
- Todo material final deve poder produzir, ao término: (a) decisões de design tomadas
  e por quê, (b) informações faltantes que o operador precisa complementar, (c)
  sugestões de legenda/CTA para compartilhamento. Isso é contrato de saída, não um
  extra opcional — consolidado em `manifesto_materiais.json` e no relatório final de
  `/produzir-comunicacao-completa`.

**REGRA 7 — Economia de Tokens (com exceção):** compressão de logs, delegação a
subagentes e seleção cirúrgica de contexto são bem-vindas para reduzir custo — **exceto**
para conteúdo de projeto (texto-base, `brief_criativo.json`) e para o estado estrutural
do pipeline (`_pool_estado.json`, `relatorio_auditoria.json`, `manifesto_materiais.json`),
que devem sempre ser lidos por completo, nunca truncados ou "grepados" — decisões sobre
marca e fidelidade à fonte exigem contexto integral.

**REGRA 8 — Scripts são o Árbitro, não a Opinião do Agente:** toda validação objetiva
(dimensão de PNG, tamanho de PDF, presença de cor/fonte de marca, texto vetorial) é
feita por script determinístico em `scripts/`, nunca por afirmação do agente. Gates de
fase são exit codes (`--estrito` → exit 1 se não conforme), não julgamento subjetivo.

## Arquitetura em uma frase

```
brand/design-system-conexao.json (FIXO, mesmo para todo projeto)
   └─► aplicador-marca-conexao (única fonte de verdade de cor/fonte/componente)
                                                          │
/esbocar (Passo 1 — entrevista em 4 rodadas: insumos, público-alvo, objetivo/tom, materiais)
   └─► analista-insumos ─► diretor-de-arte ─► config_projeto.json + brief_criativo.json
                                                          │
/produzir-comunicacao-completa <slug> (Passo 2 — autônomo, lote 4, pool-materiais.py)
   ├─► redator-apostila      ─► compilador-pdf     ─► output/<slug>/pdf/          (interim: usa o mesmo brand fixo)
   ├─► redator-landing       ─► compilador-html    ─► output/<slug>/landing-page/
   ├─► redator-apresentacao  ─► compilador-html    ─► output/<slug>/apresentacao/
   └─► redator-arte (×3)     ─► compilador-arte    ─► output/<slug>/arte-01|02|03/
                                                          │
                                                    revisor-marca (auditar-projeto.py --estrito)
                                                          │
                                                    empacotar-projeto.py → manifesto_materiais.json
```

## Tabela de módulos por tipo de material

| Material | Skill de redação | Compilador | Script de validação | Pasta de saída |
|---|---|---|---|---|
| PDF (apostila) | `redator-apostila` | `compilador-pdf` (Pandoc→Typst) | `validar-pdf.py` | `output/<slug>/pdf/` |
| Landing Page | `redator-landing` | `compilador-html` | `validar-html.py` | `output/<slug>/landing-page/` |
| Apresentação | `redator-apresentacao` | `compilador-html` | `validar-html.py` | `output/<slug>/apresentacao/` |
| Arte 1080×1080 | `redator-arte` | `compilador-arte` (Playwright) | `validar-dimensoes.py` | `output/<slug>/arte-01/` |
| Arte 1080×1350 | `redator-arte` | `compilador-arte` (Playwright) | `validar-dimensoes.py` | `output/<slug>/arte-02/` |
| Arte 1080×1920 | `redator-arte` | `compilador-arte` (Playwright) | `validar-dimensoes.py` | `output/<slug>/arte-03/` |

Todos os materiais passam por `revisor-marca` (fidelidade de fonte + marca) e
`auditar-projeto.py --estrito` antes de `empacotar-projeto.py`.

## Skills globais reaproveitados (catálogo já disponível, não copiar)

`compilador-html` e `redator-landing` podem se apoiar em `frontend-design` /
`web-artifacts-builder` / `high-end-visual-design` para qualidade visual de HTML;
`revisor-marca` pode se apoiar em `dataviz`/`image` para checagens visuais adicionais;
`compilador-pdf` pode consultar o skill `pdf` genérico para técnicas auxiliares de
manipulação de PDF quando o Pandoc+Typst não bastar. Nenhum desses precisa ser
reimplementado neste projeto.

## Pré-requisitos de ambiente

Pandoc, Typst (CLI) e Playwright (Python) precisam estar instalados. Nenhum MCP
customizado é necessário — o estado do pipeline é 100% arquivo JSON (ver REGRA 8), e as
ferramentas nativas de leitura/escrita de arquivo do Claude Code já cobrem o que um MCP
de filesystem faria.

<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes_tool` or `query_graph_tool` instead of Grep
- **Understanding impact**: `get_impact_radius_tool` instead of manually tracing imports
- **Code review**: `detect_changes_tool` + `get_review_context_tool` instead of reading entire files
- **Finding relationships**: `query_graph_tool` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview_tool` + `list_communities_tool`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
| ------ | ---------- |
| `detect_changes_tool` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context_tool` | Need source snippets for review — token-efficient |
| `get_impact_radius_tool` | Understanding blast radius of a change |
| `get_affected_flows_tool` | Finding which execution paths are impacted |
| `query_graph_tool` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes_tool` | Finding functions/classes by name or keyword |
| `get_architecture_overview_tool` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes_tool` for code review.
3. Use `get_affected_flows_tool` to understand impact.
4. Use `query_graph_tool` pattern="tests_for" to check coverage.
