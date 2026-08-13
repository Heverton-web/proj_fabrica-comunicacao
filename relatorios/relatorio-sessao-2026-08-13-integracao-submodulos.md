# Relatório de Sessão — 2026-08-13 (painel, documentação e integração de submodules)

**Status:** concluído, mergeado em `main`
**Data:** 2026-08-13
**Branches envolvidas:** `feature/determinismo-pipeline-custos` e
`feature/painel-controle-multi-harness` — ambas mergeadas em `main` e apagadas
(local + remoto) ao final desta sessão.
**Relatórios relacionados:** [`relatorio-painel-controle-multi-harness.md`](relatorio-painel-controle-multi-harness.md)
(entrega original do painel, sessão anterior) — este relatório cobre a
continuação: correções de uso real, documentação de skills/submodules e a
integração final em `main`.

---

## 1. O que foi pedido

Sessão de continuação do painel de controle (já entregue como MVP numa sessão
anterior), cobrindo: correções encontradas ao *usar* o painel de verdade,
pesquisa e decisão sobre frameworks/skills externos (Agent Skills, LoopX,
submodules DDD, `kit-fundacao-aidd`/`fable-method`/`impeccable`), e finalização
com merge das duas branches pendentes em `main`.

## 2. O que foi feito

### 2.1 Painel — correções de uso real

Todas na branch `feature/painel-controle-multi-harness`, cada uma reportada
pelo operador usando o painel de verdade (não hipotética):

- **Job ficava preso em "running" para sempre** — causa: `subprocess.run(capture_output=True)`
  só retorna quando o pipe fecha, e um neto do processo (MCP server, `node.exe`
  atrás de shim `.cmd`) mantinha o handle aberto. Correção: stdout/stderr
  redirecionados pro arquivo de log, nunca `PIPE` — o runner espera só o PID
  do filho direto.
- **Servidor "fica fazendo chamada atrás da outra"** — causa: `setInterval`
  de poll rodava pra sempre e recriava a lista de jobs inteira a cada tick,
  refazendo listagem de arquivos de jobs já terminados. Correção: poll
  auto-agendado (`setTimeout`) que para quando não há job ativo; feed de
  arquivo cacheado para jobs concluídos.
- **Barra de progresso "piscando"** — causa: lista de jobs recriada do zero
  a cada tick reiniciava um `@keyframes` em loop. Correção: elementos de
  card reaproveitados entre ticks (`replaceChildren`); largura calculada por
  tempo real decorrido, sem loop.
- **Workspaces de teste acumulando na lista** — causa: nenhuma forma de
  remover registro do índice. Correção: `DELETE /api/workspaces`, botão de
  lixeira SVG na UI.
- **Botões "feios" (texto em vez de ícone)** — correção: ícone de lixeira
  (remover), ícone "+" (criar/registrar/salvar); "usar" continua texto.
- **Ordem "Novo projeto" antes de "Projetos existentes"** — causa: fluxo de
  decisão invertido. Correção: seção "Projetos existentes" passou a vir
  antes de "Novo projeto".
- **Comando `/gerar-*` podia rodar sem `brief_criativo.json`** — causa:
  nenhuma validação de pré-requisito. Correção: `POST /api/jobs` recusa com
  HTTP 400 se faltar o brief e o comando exigir.
- **`output/` do repo podia ser removido da lista de workspaces** — causa:
  nenhuma proteção. Correção: `delete_workspace()` recusa remover esse
  workspace específico, mesmo do índice.

Também adicionados **5 harnesses novos** (`antigravity`, `grok`, `mimocode`,
`omp`, `freebuff`) via pesquisa real de sintaxe de CLI (GitHub), com
README documentando o que foi confirmado vs. melhor-esforço (`freebuff`).

**Suíte final do painel: 79/79 testes passando.**

### 2.2 Documentação — manuais e planos

Cinco documentos novos em `manuais/` (.md + .pdf, verificados página por
página com PyMuPDF antes de cada entrega — ver seção 3):

- `MANUAL_AGENT_SKILLS.md` — guia prático do framework Agent Skills instalado
  via `/reload-plugins`.
- `MANUAL_LOOPX.md` — pesquisa + opinião sobre a skill LoopX (`huangruiteng/loopx`):
  não recomendado para este projeto (REGRA 3 já resolve o problema que o
  LoopX ataca; barreira de shell macOS/Linux).
- `MANUAL_ANALISE_AGENT_SKILLS.md` — análise crítica sem filtro do próprio
  Agent Skills: procedência real (`addyosmani/agent-skills`, não veio do
  plugin `i-have-adhd` como o manual anterior dizia), sobreposição extensa
  com skills já existentes neste repo, tensão com a prioridade de economia de
  token do `CLAUDE.md`.
- `MANUAL_ANALISE_SUBMODULES_DDD.md` — `shared`/`skills-ddd-clean` (forks de
  `mentoria-360`): incompatibilidade de stack total com este projeto
  (TypeScript/DDD vs. Python) — não trazer em nenhuma forma.
- `MANUAL_ANALISE_SUBMODULES_KIT_FABLE_IMPECCABLE.md` — `kit-fundacao-aidd`,
  `fable-method`, `impeccable`: os 2 primeiros já provados em produção no
  projeto irmão `proj_fabrica-de-livros` (`.gitmodules` inspecionado
  diretamente); achado extra: `fable-method` estava referenciado no
  `CLAUDE.md` global do operador mas nunca instalado de fato (referência
  morta).

Mais `melhorias/plano-painel-redesign-visual.md` — intenção confirmada via
`/interview-me` sobre o redesign visual do painel (colapsar setup, hierarquia
visual nos passos frequentes, manter jobs sempre visível — sem wizard
sequencial).

### 2.3 Integração executada (recomendações aplicadas)

- **`tooling/kit-fundacao-aidd`** (submodule, seu, já validado no projeto
  irmão): instalado via diagnóstico read-only + dry-run + aplicação real.
  Gravou `.claude/agents/builder.md`/`critic.md`, hook de pre-commit
  (`python -m pytest -q` antes de todo commit) e templates de gate
  determinístico/registro declarativo/postmortem-vira-teste.
- **`.claude/skills/impeccable`**: instalado via `npx impeccable install`
  (fluxo oficial) em vez de submodule bruto — testado que um clone cru do
  repo não produz `SKILL.md` descobrível no caminho certo.
- **`fable-method`**: instalado **globalmente** (`claude plugin marketplace
  add` + `claude plugin install fable@fable-method`, scope `user`) — conserta
  a referência morta no `CLAUDE.md` global, não gera diff neste repositório.

### 2.4 Integração ao `main`

Testado com merge simulado (branch descartável, nunca tocando nas branches
reais) antes de qualquer ação real — zero conflitos, zero sobreposição de
arquivo entre as duas branches. Sequência executada:

1. `feature/determinismo-pipeline-custos` → `main` (fast-forward).
2. `feature/painel-controle-multi-harness` → `main` (merge commit).
3. Testes rodados **depois de cada merge** (painel 79/79, raiz 17/17) antes
   do push.
4. Ambas as branches apagadas, local e remoto.

## 3. Como foi validado (evidência, não opinião)

- **PDFs**: todo `manuais/*.pdf` gerado nesta sessão foi renderizado página
  por página via PyMuPDF (`pdftoppm`/poppler não está instalado neste
  ambiente) e inspecionado visualmente antes de ser considerado pronto —
  incluindo a correção de um bug real de paginação (tabelas grandes
  quebrando/sobrepondo texto entre páginas) descoberto pelo operador no
  primeiro manual e corrigido nos seguintes (tabelas grandes viraram lista).
- **Merge**: simulado numa branch local descartável (`_teste-merge-descartavel`)
  antes de tocar em `main` de verdade — `git diff --name-only --diff-filter=U`
  vazio confirmou zero conflito.
- **Instalação de submodules**: diagnóstico read-only (`analisar-projeto.py`)
  → dry-run (`instalar.py` sem `--aplicar`, mostra diff) → só então aplicação
  real — nenhum arquivo existente sobrescrito.
- **Suítes de teste**: painel (79/79) e raiz (17/17) verdes depois de cada
  merge, antes de cada push.

## 4. Erros cometidos nesta sessão e como foram corrigidos (transparência)

1. **`rm -rf` acidental em arquivos já rastreados.** Ao limpar o excesso de
   uma instalação ampla do `impeccable` (que se espalhou por 7 harnesses),
   um `rm -rf .cursor .kiro .opencode` apagou também arquivos **rastreados**
   pré-existentes desse projeto (comandos do opencode, configs MCP) que não
   tinham nada a ver com o impeccable. Detectado imediatamente pelo `git
   status` (apareceram como `D`, não como sumiço silencioso) e restaurado via
   `git checkout -- .cursor .kiro .opencode` antes de qualquer commit — sem
   perda real.
2. **Hook de pre-commit bloqueando o próprio commit.** O hook instalado pelo
   `kit-fundacao-aidd` tratava qualquer exit code não-zero do pytest como
   "vermelho" — mas `tests/` deste repo está vazio hoje, e pytest retorna
   exit 5 ("nenhum teste coletado"), não 0. Corrigido o hook pra só bloquear
   em exit 1-4 (falha/erro real), não em 5 (ausência de teste).

Nenhum dos dois chegou a ser commitado ou pushado antes de ser corrigido.

## 5. Gastos da sessão

Números reais extraídos diretamente do log de transcript da sessão
(`~/.claude/projects/.../68ef6268-*.jsonl`), não estimativa — somando o
campo `usage` de cada uma das 782 mensagens do assistente:

| Métrica | Valor |
|---|---|
| Modelo | `claude-sonnet-5` |
| Mensagens do assistente | 782 |
| Tokens de input (sem cache) | 1.556 |
| Tokens de output (total) | 678.614 (dos quais 388.171 de *thinking*) |
| Tokens lidos do cache | 278.094.233 |
| Tokens gravados em cache (1h) | 1.233.866 |

Custo calculado com o preço promocional do Sonnet 5 vigente até 31/ago/2026
(input \$2,00/output \$10,00 por milhão de tokens; leitura de cache a 10% do
input, escrita de cache de 1h a 200% do input — multiplicadores padrão da
Anthropic):

| Componente | Custo (USD) |
|---|---|
| Input novo | \$0,0031 |
| Output | \$6,7861 |
| Leitura de cache | \$55,6188 |
| Escrita de cache (1h) | \$4,9355 |
| **Total** | **≈ \$67,34** |

**Total estimado: ≈ US\$ 67,34 (≈ R\$ 370,39 no câmbio de R\$5,50).**

A maior fatia (≈83%) é leitura de cache — esperado numa sessão longa (782
turnos) que reaproveita bastante contexto entre turnos via prompt caching, em
vez de reprocessar tudo do zero a cada mensagem.

## 6. Estado final do repositório

- `main` é a única branch (local e remota) — as duas branches de feature
  foram mergeadas e apagadas.
- Submodules: `.token-economy` (já existia) + `tooling/kit-fundacao-aidd`
  (novo).
- `.claude/skills/impeccable` instalado e funcional (confirmado: aparece na
  lista de skills disponíveis).
- `fable-method` instalado globalmente (fora deste repositório).
- Hook de pre-commit ativo (`.git/hooks/pre-commit`, local, não versionado
  por git — como todo hook).
- 79/79 testes do painel + 17/17 testes da raiz passando em `main`.
