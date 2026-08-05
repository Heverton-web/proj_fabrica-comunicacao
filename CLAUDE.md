# Fábrica de Materiais de Comunicação — Orquestração Claude Code

Instruções específicas para execução via **Claude Code CLI**. Para a arquitetura conceitual completa, regras invioláveis de negócio e catálogo de módulos, consulte a fonte única de verdade em [`AGENTS.md`](file:///C:/Users/trcnologia/Desktop/proj_fabrica-comunicacao/AGENTS.md).

---

## Comandos (universais — não exclusivos do Claude Code)

Os 6 comandos abaixo funcionam em **qualquer harness** que leia os arquivos deste
repositório — o procedimento completo e canônico de cada um vive em
[`SPEC_COMANDOS.md`](file:///C:/Users/trcnologia/Desktop/proj_fabrica-comunicacao/SPEC_COMANDOS.md).
Os arquivos em `.claude/commands/*.md` listados abaixo são apenas o mecanismo de
descoberta de slash-command **específico do Claude Code** (aparecem no autocomplete
`/`) — cada um é um ponteiro fino para a seção correspondente de `SPEC_COMANDOS.md`,
nunca uma segunda cópia da instrução.

1. **`/esbocar`**: Inicia a entrevista interativa de 4 rodadas com o operador para definir escopo e gerar `config_projeto.json` + `brief_criativo.json`.
2. **`/produzir-comunicacao-completa <slug>`**: Executa o pipeline autônomo lote 4 via `pool-materiais.py` para compilar e validar todos os materiais do projeto.
3. **`/gerar-pdf <slug>`**: Regenera só o PDF (apostila) de um projeto já esboçado.
4. **`/gerar-landing <slug>`**: Regenera só a landing page de um projeto já esboçado.
5. **`/gerar-apresentacao <slug>`**: Regenera só a apresentação HTML de um projeto já esboçado.
6. **`/gerar-arte <slug> [--tamanho ...]`**: Regenera uma ou mais variantes de arte PNG de um projeto já esboçado.

---

## Governança & Regras Rápidas

- **Fonte de Verdade:** [`AGENTS.md`](file:///C:/Users/trcnologia/Desktop/proj_fabrica-comunicacao/AGENTS.md) rege o ecossistema.
- **Comandos:** [`SPEC_COMANDOS.md`](file:///C:/Users/trcnologia/Desktop/proj_fabrica-comunicacao/SPEC_COMANDOS.md) é a fonte única de verdade do procedimento de cada comando, universal a qualquer harness.
- **Auto-Correção Interna:** Erros de validação devem ser autocorrigidos autonomamente antes da entrega final.
- **Árbitro Determinístico:** Validações visuais e estruturais são sempre regidas pelos scripts em `scripts/*.py` (`--estrito`).
- **Hooks de Grafo:** O Claude Code utiliza os hooks `PostToolUse`/`SessionStart` configurados em `.claude/settings.json` para atualização do `code-review-graph`.
