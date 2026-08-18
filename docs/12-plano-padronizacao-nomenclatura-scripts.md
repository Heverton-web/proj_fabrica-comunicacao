# Plano de Ação — Padronização de Nomenclatura de Scripts

**Regra inegociável:** todo script CLI standalone segue `tipo-oque.ext` (kebab-case,
verbo em português como tipo). Ex.: `teste-example.py`, `revisao-example.py`,
`validar-html.py`.

**Decisões já confirmadas com o operador:**
- `test_*.py` (pytest) → **exceção documentada**. Python/pytest não importam módulo
  com hífen no nome; a regra tipo-oque vale para scripts CLI, não para módulos de
  teste importáveis.
- `painel/` e `painel/harness_adapters/` → **fora de escopo**. São módulos de um
  pacote Python (import interno), não scripts CLI.
- Escopo desta rodada: **só a árvore raiz deste repo**. O gitlink aninhado
  `proj_fabrica-comunicacao/` (repo próprio) e os submodules `.token-economy/` e
  `tooling/kit-fundacao-aidd/` (repos externos) ficam de fora — exigiriam PR
  separado nos respectivos repositórios.

**Corolário técnico descoberto na varredura:** a mesma restrição do Python que
justifica a exceção dos `test_*.py` também se aplica a qualquer módulo que é
**importado** (`from x import y`) em vez de executado diretamente — hífen quebra o
import. Por isso `scripts/_arte_common.py`, `_icones_conexao.py`, `_tipos_comuns.py`,
`parametros_projeto.py` e `pdf_typst.py` entram na mesma categoria de exceção que
`painel/`: são módulos de biblioteca compartilhados, não scripts standalone.

---

## Fase 0 — Formalizar a regra e as exceções

Criar `docs/CONVENCAO-NOMENCLATURA-SCRIPTS.md` (ou seção em `AGENTS.md`) com:
1. Regra: `tipo-oque.ext`, tipo = verbo em português (`gerar`, `validar`, `compilar`,
   `auditar`, `verificar`, `empacotar`, `extrair`, `renderizar`, `configurar`).
2. As duas exceções técnicas acima (pytest e módulos importados), com a lista
   nominal de arquivos isentos.
3. Escopo (raiz do repo; submodules/gitlink ficam fora até PR próprio).

## Fase 1 — Renomear (git mv, preserva histórico)

Ordem por risco crescente (nº de referências vivas encontradas):

| # | Nome atual | Nome novo | Refs vivas a atualizar |
|---|---|---|---|
| 1 | `scripts/gerar_html_arte02.py` | `scripts/gerar-html-arte02.py` | 0 (órfão, não chamado por `compilar-arte.py` nem specs) |
| 2 | `scripts/renderizar_arte02.py` | `scripts/renderizar-arte02.py` | 0 (idem — candidatos a revisão de uso morto, fora deste plano) |
| 3 | `exemplos/expansao-layout/gerar_exemplo.py` | `exemplos/expansao-layout/gerar-exemplo-layout.py` | 0 |
| 4 | `scripts/setup-workspace.py` | `scripts/configurar-workspace.py` | só menções em docs históricos (`docs/04-*.md`, `docs/AGY...md`) |
| 5 | `scripts/preflight-compatibilidade-slug.py` | `scripts/verificar-compatibilidade-slug.py` | `SPEC_COMANDOS.md:223` (comando real) + docstring interno + 2 docs históricos |
| 6 | `scripts/pool-materiais.py` | `scripts/orquestrar-pool-materiais.py` | **~40 ocorrências**: `SPEC_COMANDOS.md` (17), `SPEC.md` (7), `AGENTS.md` (3), 6× `.claude/agents/subagente-produtor-*.md` + `subagente-revisor-marca.md`, `.claude/skills/revisor-marca/SKILL.md`, `manuais/MANUAL_FABRICA.md` |

Itens 1–3: renomear direto, zero blast radius.
Itens 4–5: renomear + 1-2 replaces em arquivo vivo.
Item 6: maior esforço — fazer por último, com busca+substituição revisada arquivo a
arquivo (não sed cego, o termo aparece em frases/tabelas, não só em paths de comando).

## Fase 2 — Atualizar apenas referências vivas

Atualizar: `SPEC_COMANDOS.md`, `SPEC.md`, `AGENTS.md`, `.claude/agents/*.md`,
`.claude/skills/*/SKILL.md`, `manuais/MANUAL_FABRICA.md`, docstrings dos próprios
scripts renomeados.

**Não tocar:** `docs/0X-plano-*.md`, `relatorios/**`, `output/**` — são registros
históricos/point-in-time ou artefatos gerados, não fonte de verdade viva.

## Fase 3 — Validação determinística

```
python scripts/auditar-projeto.py <slug-de-teste> --estrito
python scripts/verificar-consistencia-pipeline.py
python scripts/verificar-universalidade.py
pytest tests/ painel/tests/
grep -rn "pool-materiais\.py\|preflight-compatibilidade-slug\.py\|setup-workspace\.py" \
  SPEC_COMANDOS.md SPEC.md AGENTS.md .claude/ manuais/   # deve retornar vazio
```

## Fase 4 — Guarda-corpo para o futuro

Estender `scripts/verificar-consistencia-pipeline.py` (ou `auditar-projeto.py`) com
uma checagem: todo novo `.py` direto em `scripts/` deve casar
`^[a-z]+(-[a-z0-9]+)+\.py$`, exceto a lista de exceções da Fase 0. Falha bloqueia
`--estrito`.

## Fase 5 — Commit

Autorizado por `CLAUDE.md` regra 7 (auto-commit/push). Sugestão: 1 commit por item
da tabela (mensagens `refactor: renomeia X para Y (padrão tipo-oque)`), ou 1 commit
único ao final cobrindo Fases 1–2. `git mv` em cada rename para preservar `git blame`.
