# Fábrica de Materiais de Comunicação — Orquestração Claude Code

Instruções específicas para execução via **Claude Code CLI**. Para a arquitetura conceitual completa, regras invioláveis de negócio e catálogo de módulos, consulte a fonte única de verdade em [`AGENTS.md`](file:///C:/Users/trcnologia/Desktop/proj_fabrica-comunicacao/AGENTS.md).

---

## Comandos Específicos do Claude Code

1. **`/esbocar`**: Inicia a entrevista interativa de 4 rodadas com o operador para definir escopo e gerar `config_projeto.json` + `brief_criativo.json`.
2. **`/produzir-comunicacao-completa <slug>`**: Executa o pipeline autônomo lote 4 via `pool-materiais.py` para compilar e validar todos os materiais do projeto.

---

## Governança & Regras Rápidas

- **Fonte de Verdade:** [`AGENTS.md`](file:///C:/Users/trcnologia/Desktop/proj_fabrica-comunicacao/AGENTS.md) rege o ecossistema.
- **Auto-Correção Interna:** Erros de validação devem ser autocorrigidos autonomamente antes da entrega final.
- **Árbitro Determinístico:** Validações visuais e estruturais são sempre regidas pelos scripts em `scripts/*.py` (`--estrito`).
- **Hooks de Grafo:** O Claude Code utiliza os hooks `PostToolUse`/`SessionStart` configurados em `.claude/settings.json` para atualização do `code-review-graph`.
