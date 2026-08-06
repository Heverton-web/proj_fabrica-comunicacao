# Fábrica de Materiais de Comunicação — Orquestração Claude Code

Instruções específicas para execução via **Claude Code CLI**. A arquitetura
conceitual, as regras invioláveis e o catálogo de módulos vivem na fonte única de
verdade: [`AGENTS.md`](file:///C:/Users/trcnologia/Desktop/proj_fabrica-comunicacao/AGENTS.md).

---

## Comandos (universais — não exclusivos do Claude Code)

Os comandos da fábrica (`/esbocar`, `/produzir-comunicacao-completa`, `/gerar-pdf`,
`/gerar-landing`, `/gerar-apresentacao`, `/gerar-arte` e variantes por tamanho,
`/gerar-textos`, `/gerar-kit-consultor`, `/gerar-kit-distribuidor`) funcionam em
**qualquer harness** que leia os arquivos deste repositório — o procedimento completo
e canônico de cada um vive em
[`SPEC_COMANDOS.md`](file:///C:/Users/trcnologia/Desktop/proj_fabrica-comunicacao/SPEC_COMANDOS.md).
Os arquivos em `.claude/commands/*.md` são apenas o mecanismo de descoberta de
slash-command **específico do Claude Code** (autocomplete `/`) — cada um é um ponteiro
fino para a seção correspondente de `SPEC_COMANDOS.md`, nunca uma segunda cópia da
instrução.

---

## Governança & Regras Rápidas

- **Fonte de Verdade:** [`AGENTS.md`](file:///C:/Users/trcnologia/Desktop/proj_fabrica-comunicacao/AGENTS.md) rege o ecossistema.
- **Comandos:** [`SPEC_COMANDOS.md`](file:///C:/Users/trcnologia/Desktop/proj_fabrica-comunicacao/SPEC_COMANDOS.md) é a fonte única de verdade do procedimento de cada comando, universal a qualquer harness.
- **Auto-Correção Interna:** Erros de validação devem ser autocorrigidos autonomamente antes da entrega final.
- **Árbitro Determinístico:** Validações visuais e estruturais são sempre regidas pelos scripts em `scripts/*.py` (`--estrito`).
- **Hooks de Grafo:** O Claude Code utiliza os hooks `PostToolUse`/`SessionStart` configurados em `.claude/settings.json` para atualização do `code-review-graph`.
