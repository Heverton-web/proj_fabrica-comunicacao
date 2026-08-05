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
(dimensão de PNG, tamanho de PDF, presença de cor/fonte de marca, texto vetorial, logo
embutido, transparência de imagem) é feita por script determinístico em `scripts/`,
nunca por afirmação do agente. Gates de fase são exit codes (`--estrito` → exit 1 se
não conforme), não julgamento subjetivo.

**REGRA 9 — Grafo Primeiro, Arquivo Depois (economia de tokens inviolável) — escopo: `scripts/*.py`:**
toda exploração de **código Python do pipeline** começa pelo grafo de conhecimento (`code-review-graph`),
não por leitura direta de arquivo. A ordem obrigatória é:
1. **Grafo** — `semantic_search_nodes_tool`, `query_graph_tool`, `get_architecture_overview_tool` para localizar o que se precisa.
2. **Trecho cirúrgico** — `get_review_context_tool` ou `view_file` com `StartLine`/`EndLine` precisos, só se o grafo não trouxer o trecho completo.
3. **Arquivo inteiro** — apenas para os documentos que a REGRA 7 lista como obrigatórios de leitura integral (texto-base, `brief_criativo.json`, `_pool_estado.json`, `relatorio_auditoria.json`, `manifesto_materiais.json`).

Grep, `list_dir` e leitura de arquivo inteiro sem passar pelo grafo primeiro são proibidos quando o grafo puder responder. Fall back para leitura direta **somente** quando o grafo não cobrir o que se precisa (ex.: arquivo recém-criado ainda não indexado).

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

| Material | Selecionável via `/esbocar` | Skill de redação | Compilador | Script de validação | Pasta de saída |
|---|---|---|---|---|---|
| PDF (apostila) | Sim (Passo 4) | `redator-apostila` | `compilador-pdf` (Pandoc→Typst) | `validar-pdf.py` | `output/<slug>/pdf/` |
| Landing Page | Sim (Passo 4) | `redator-landing` | `compilador-html` | `validar-html.py` | `output/<slug>/landing-page/` |
| Apresentação | Sim (Passo 4) | `redator-apresentacao` | `compilador-html` | `validar-html.py` | `output/<slug>/apresentacao/` |
| Arte 1080×1080 | Sim (Passo 4) | `redator-arte` | `compilador-arte` (Playwright) | `validar-dimensoes.py` | `output/<slug>/arte-01/` |
| Arte 1080×1350 | Sim (Passo 4) | `redator-arte` | `compilador-arte` (Playwright) | `validar-dimensoes.py` | `output/<slug>/arte-02/` |
| Arte 1080×1920 | Sim (Passo 4) | `redator-arte` | `compilador-arte` (Playwright) | `validar-dimensoes.py` | `output/<slug>/arte-03/` |
| Textos de Apoio | Sim (Passo 4) | `redator-textos` | (sem compilador — grava `.txt` direto) | `validar-textos.py` | `output/<slug>/textos/` |

Toda vez que um material for adicionado/removido desta tabela, rode `python scripts/verificar-consistencia-pipeline.py --estrito` para validar a consistência entre todos os módulos.

Todos os materiais passam por `revisor-marca` (fidelidade de fonte + marca) e `auditar-projeto.py --estrito` antes de `empacotar-projeto.py`.

## Skills globais reaproveitados (catálogo já disponível, não copiar)

`compilador-html` e `redator-landing` podem se apoiar em `frontend-design` / `web-artifacts-builder` / `high-end-visual-design` para qualidade visual de HTML; `revisor-marca` pode se apoiar em `dataviz`/`image` para checagens visuais adicionais; `compilador-pdf` pode consultar o skill `pdf` genérico para técnicas auxiliares de manipulação de PDF quando o Pandoc+Typst não bastar.

## Pré-requisitos de ambiente

Pandoc, Typst (CLI) e Playwright (Python) precisam estar instalados. O estado do pipeline é 100% arquivo JSON (ver REGRA 8).

## Grafo de Conhecimento — MCP `code-review-graph` (REGRA 9)

Este projeto possui um grafo de conhecimento auto-atualizado (`scripts/*.py`). Para o que o grafo cobre, toda exploração começa por ele.

### Hierarquia de acesso — ordem obrigatória (REGRA 9)

```
1. Grafo           → semantic_search / query_graph / get_review_context
2. Trecho cirúrgico → view_file com StartLine+EndLine exatos
3. Arquivo inteiro  → SOMENTE para os documentos da REGRA 7
                      (texto-base, brief_criativo.json, _pool_estado.json,
                       relatorio_auditoria.json, manifesto_materiais.json)
```
