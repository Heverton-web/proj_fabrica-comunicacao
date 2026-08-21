# Fábrica de Materiais de Comunicação — Orquestração Claude Code

Instruções específicas para execução via **Claude Code CLI**. A arquitetura
conceitual, as regras invioláveis e o catálogo de módulos vivem na fonte única de
verdade: [`AGENTS.md`](file:///C:/Users/trcnologia/Desktop/proj_fabrica-comunicacao/AGENTS.md).

---

## 0. Economia Severa de Tokens (PRIORIDADE MÁXIMA)

Infraestrutura em `.token-economy/` (submodule). Ver [`docs/prompt-mestre-token-economy.md`](file:///C:/Users/trcnologia/Desktop/01_Projetos_e_Desenvolvimento/proj_fabrica-comunicacao/docs/prompt-mestre-token-economy.md) para o racional completo.

1. **Caveman ativo:** respostas telegráficas (3-5 linhas), sem preâmbulos/saudações.
2. **Headroom:** logs/builds >7 linhas → comprimir (3 topo + 4 fim). EXCEÇÃO: `output/**` e dados de obra NUNCA são comprimidos.
3. **LeanCTX:** grep antes de read em código/config; ler só a fatia de linhas necessária.
4. **Delegação:** subagentes para buscas/edições extensas (nunca para prosa criativa dos redatores).
5. **Build ISENTO:** pipelines de compilação (pandoc, typst, playwright, scripts/*.py) são liberados e obrigatórios, nunca comprimidos na saída de erro.
6. **Fidelidade de conteúdo:** `output/**`, `config_projeto.json`, `brief_criativo.json` e scripts de auditoria (`scripts/*.py --estrito`) são isentos de compressão.
7. **Auto-commit/push:** autorizado para este projeto — commitar e pushar ao concluir uma tarefa, sem precisar reconfirmar a cada vez. **Gate de segurança ativo:** pre-commit hook bloqueia automaticamente qualquer commit contendo padrão de API key (Anthropic `sk-*`, AWS `AKIA*`, GitHub `ghp_*`, Slack `xox*`) ou chave PEM. Para ativar em nova máquina: `powershell -ExecutionPolicy Bypass -File scripts/setup-hooks.ps1`.
8. **Skills disponíveis** (junctions em `.claude/skills/`, fonte em `.token-economy/`): `lean-ctx`, `headroom`, `caveman`, `rtk-memory`, `pre-flight-check`, `calcular-gastos-sessao`, `fable-method`, `fable-judge`, `self-learning`.

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

---

## RTK SCRATCHPAD

Aprendizados sessão-por-sessão, padrões confirmados e ajustes táticos são documentados
em [`RTK-SCRATCHPAD.md`](./RTK-SCRATCHPAD.md) (arquivo separado). Este arquivo pode
crescer livremente sem afetar o prefixo de cache de `CLAUDE.md`. Ver arquivo para
entradas datadas.
