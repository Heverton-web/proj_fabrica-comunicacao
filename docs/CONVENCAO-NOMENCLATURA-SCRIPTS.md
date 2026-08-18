# Convenção de Nomenclatura — Scripts

**Regra inegociável:** todo script CLI standalone (arquivo com shebang, executado
diretamente via `python arquivo.py` ou `bash arquivo.sh`, nunca importado por outro
módulo) segue `tipo-oque.ext`, kebab-case, `tipo` = verbo em português.

Verbos em uso: `gerar`, `validar`, `compilar`, `auditar`, `verificar`, `empacotar`,
`extrair`, `renderizar`, `configurar`, `orquestrar`.

Exemplos corretos: `validar-html.py`, `compilar-pdf.py`, `orquestrar-pool-materiais.py`,
`verificar-compatibilidade-slug.py`, `configurar-workspace.py`.

## Exceções técnicas (documentadas, não violam a regra)

1. **Módulos de teste pytest** (`test_*.py` em `tests/`, `painel/tests/`,
   `tooling/kit-fundacao-aidd/tests/`): pytest importa o arquivo como módulo Python;
   hífen no nome quebra o import. A regra `tipo-oque` vale para scripts CLI, não para
   módulos de teste importáveis.

2. **Módulos de biblioteca importados** (`from x import y` em vez de execução direta):
   pela mesma restrição de import do Python, mantêm snake_case:
   - `scripts/_arte_common.py`, `scripts/_icones_conexao.py`, `scripts/_tipos_comuns.py`
     (prefixo `_` = convenção Python de módulo interno/privado)
   - `scripts/parametros_projeto.py`, `scripts/pdf_typst.py`

3. **Pacote Python `painel/`** (`painel/*.py`, `painel/harness_adapters/*.py`): módulos
   de um pacote com imports internos, não scripts CLI standalone. Fora de escopo.

4. **Scripts fora deste repositório**: gitlink aninhado `proj_fabrica-comunicacao/` e
   submodules `.token-economy/` e `tooling/kit-fundacao-aidd/` (repos próprios/externos)
   — mudança exigiria PR separado no repositório de origem.

5. **Nomes ditados por convenção externa**: hooks (`.gemini/hooks/crg-*.sh`),
   scripts de skill de terceiros — seguem a convenção do harness/framework que os
   consome, não esta regra.

6. **Artefatos gerados** em `output/**` (ex.: `output/<slug>/arte-01/compilar.py`):
   não são script-fonte mantido, são saída do pipeline.

## Enforcement

`scripts/verificar-consistencia-pipeline.py` deve validar que todo novo `.py` direto
em `scripts/` casa `^[a-z]+(-[a-z0-9]+)+\.py$` ou está na lista de exceções acima.

Ver [`docs/12-plano-padronizacao-nomenclatura-scripts.md`](12-plano-padronizacao-nomenclatura-scripts.md)
para o histórico da rodada de renomeação que estabeleceu esta convenção.
