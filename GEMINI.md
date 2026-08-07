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

## Economia de Tokens

Infraestrutura compartilhada em `.token-economy/` (submodule) — ver
`docs/prompt-mestre-token-economy.md`. Comprimir logs/saídas >7 linhas (3 topo + 4
fim), exceto `output/**` e scripts de auditoria (`--estrito`), que nunca são
truncados. Preferir busca pontual à leitura integral de arquivos grandes. Builds
(Pandoc, Typst, Playwright) rodam sempre por completo, sem compressão.

## Comandos da Fábrica

Este repositório é a "Fábrica de Materiais de Comunicação". Os comandos
(`/esbocar`, `/produzir-comunicacao-completa`, `/gerar-pdf`, `/gerar-landing`,
`/gerar-apresentacao`, `/gerar-arte` e variantes por tamanho, `/gerar-textos`,
`/gerar-kit-consultor`, `/gerar-kit-distribuidor`) são universais (não exclusivos
do Claude Code) — o procedimento completo de cada um está em `SPEC_COMANDOS.md`
(fonte única de verdade; a lista canônica vive em `AGENTS.md`). Se o operador
digitar um desses comandos (ou pedir o equivalente em linguagem natural, ex.:
"inicie a fábrica para o produto X"), leia `SPEC_COMANDOS.md` por completo e siga
a seção correspondente. `AGENTS.md` é a fonte de verdade da arquitetura/regras do
projeto. Sempre que um comando/skill/rule for alterado, rode
`python scripts/verificar-universalidade.py --estrito` antes de concluir.

## Regras Invioláveis do Projeto

1. **Charset UTF-8 Obrigatório:** Todos os materiais gerados (HTML, CSS, JSON, Markdown, etc.) e todos os scripts de leitura/escrita do ecossistema devem utilizar codificação **UTF-8** de forma explícita e obrigatória (ex: `<meta charset="utf-8">` em HTML, `encoding="utf-8"` em chamadas de arquivos em Python). Nenhuma outra codificação é permitida para garantir compatibilidade multiplataforma absoluta de caracteres especiais e acentuação.
2. **Sem Hífens nos Títulos:** Os títulos de todos os materiais gerados (PDFs, apresentações, etc.) não devem conter o caractere hífen (-). Sempre que houver um hífen ou travessão de separação, ele deve ser obrigatoriamente substituído por dois-pontos (:).
3. **Layout e Respiro de Apresentação (Slides):**
   - Os painéis de conteúdo de marcadores (`.slide ul`) devem ter obrigatoriamente pelo menos **32px de padding top e bottom** (`padding: 32px 1.8rem;`) e o tamanho das fontes dos bullets deve ser ajustado para garantir leitura e respiro visual.
   - Listas de marcadores extensas (contendo 4 ou mais itens) devem ser divididas automaticamente em **duas colunas paralelas de painéis** (`duas-colunas`) de forma balanceada, para que o conteúdo preencha a tela com excelente respiro e simetria lateral, evitando grandes vazios no layout.
