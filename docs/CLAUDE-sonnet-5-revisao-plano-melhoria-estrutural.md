---
title: "Revisão do Plano de Melhoria Estrutural"
subtitle: "Análise cruzada de `04-plano-melhoria-estrutural.md` e da revisão nvidia/z-ai/glm-5.2, com verificação empírica contra o repositório"
date: "2026-08-05"
author: "Auditoria técnica do pipeline (modelo: Claude Sonnet 5)"
---

# Revisão do Plano de Melhoria Estrutural

Análise dos dois documentos existentes sobre a reestruturação de diretórios e
governança da Fábrica de Materiais de Comunicação: o plano original
(`docs/04-plano-melhoria-estrutural.md`) e a revisão técnica
(`docs/OMP-nvidia-z-ai-glm-5.2-revisao-plano-melhoria-estrutural.md`). Todas as
afirmações abaixo foram verificadas empiricamente contra o estado real do
repositório em 2026-08-05, não aceitas por inferência de nenhum dos dois textos.

---

## O plano original

Diagnóstico correto na essência — duplicidade de governança e skills físicas é
real —, mas com números errados e omissões relevantes. O diff real entre
`CLAUDE.md` (219 linhas) e `AGENTS.md` (174 linhas) é de 93 linhas — a maior
parte é overlap genuíno, não as "~150 linhas idênticas" citadas literalmente,
mas a direção do diagnóstico procede. A afirmação de que `GEMINI.md` compartilha
esse mesmo cabeçalho está **errada**: `GEMINI.md` tem 46 linhas e já é
específico do Gemini.

Os dois pontos de maior risco no plano original:

- **Symlinks no Windows via `os.symlink`** — falha silenciosa sem admin/Modo
  Desenvolvedor ativo é um risco real de perda de skill sem aviso ao operador.
- **"Limpa pastas físicas redundantes"** antes de confirmar que o link
  funcionou é uma sequência destrutiva perigosa: se o link falhar depois da
  exclusão, a skill desaparece do agente.

---

## A revisão (nvidia/z-ai/glm-5.2)

Auditei as 10 observações da revisão contra o repositório real — **todas se
confirmam**:

| Verificação | Resultado |
|---|---|
| `GEMINI.md`=46, `CLAUDE.md`=219, `AGENTS.md`=174 linhas | Confirmado |
| `CODEBUDDY.md`/`QODER.md`/`.cursorrules`/`.windsurfrules` = 38 linhas cada | Confirmado |
| 4 skills comuns duplicadas fisicamente entre `.claude/`, `.gemini/`, `.codebuddy/` | Confirmado — `debug-issue/SKILL.md` é byte-idêntico entre `.claude` e `.gemini` |
| 5 arquivos `mcp.json` distintos (raiz, `.cursor`, `.vscode`, `.kiro`, `.qoder`) | Confirmado |
| Import cruzado real entre scripts que justificaria `sys.path` hack | **Não confirmado** — apenas `compilar-pdf.py` usa `sys.path.append` hoje |

Essa é uma revisão tecnicamente sólida — cada correção é verificável, e as
alternativas propostas (junction em vez de symlink, gate por
`--estrito`, checagem de `code-review-graph`/hooks na Etapa 2) são as certas
para este projeto especificamente, porque casam com a REGRA 8 e a REGRA 9 do
próprio `AGENTS.md`/`CLAUDE.md`.

---

## Achado adicional não capturado por nenhum dos dois documentos

Uma busca por caminhos absolutos hardcoded (`C:\Users\trcnologia`) no
repositório encontrou **9 arquivos** com esse problema:

- `.gemini/hooks/crg-session-start.sh`
- `.gemini/hooks/crg-update.sh`
- `.gemini/settings.json`
- `.mcp.json` (raiz)
- `.cursor/mcp.json`
- `.vscode/mcp.json`
- `.kiro/settings/mcp.json`
- `.qoder/mcp.json`
- `opencode.jsonc`

O plano original menciona esse problema de forma genérica (linhas 68-70,
"Evitar Caminhos Absolutos de Máquina") mas sem listar onde ocorre; a revisão
não comenta esse ponto. Este é um achado concreto e acionável: a
portabilidade está quebrada em 9 lugares específicos, não é um risco
hipotético — qualquer outro operador ou runner de CI que clone o repositório
terá esses 9 arquivos apontando para uma máquina que não existe no ambiente
dele.

---

## Opinião e recomendação

A revisão está correta em praticamente todos os pontos e deveria ser
incorporada ao plano, não mantida como um segundo documento paralelo.
Recomendação de fusão em um único plano corrigido:

1. **Fundir os dois documentos** num `04-plano-melhoria-estrutural.md`
   corrigido — a revisão já oferece essa opção.
2. **Trocar symlink por junction** (`mklink /J`) no Windows como mecanismo
   padrão do script de bootstrap, com fallback de cópia (`robocopy`/`rsync`)
   e **sem deleção automática** da cópia física até o link ser confirmado
   funcionando.
3. **Adicionar os 4 arquivos de governança omitidos**
   (`CODEBUDDY.md`, `QODER.md`, `.cursorrules`, `.windsurfrules`) à tabela de
   especialização — mesmo que a decisão final seja "manter como estão", isso
   precisa ser uma decisão explícita, não uma lacuna.
4. **Adotar os scripts `--estrito` existentes** (`auditar-projeto.py`,
   `verificar-consistencia-pipeline.py`) **como gate de cada etapa** — já é a
   norma do projeto (REGRA 8); o plano original propõe validação subjetiva
   ("validar se os agentes continuam operando normalmente"), o que contradiz
   a própria regra do repositório.
5. **Adicionar a lista dos 9 arquivos com caminho absoluto** como checklist
   concreto da Etapa 1/3, em vez da menção genérica atual.
6. **Adiar a modularização de `scripts/`** (compiladores/validadores/pipeline)
   da Etapa 3 até haver import cruzado real entre os scripts — hoje é
   reorganização estética sem ganho funcional comprovado.
7. **Preservar explicitamente** na Etapa 1 a coluna "Selecionável via
   `/esbocar`" e a linha "Textos de Apoio" da tabela de módulos ao consolidar
   conteúdo em `AGENTS.md`, para não regredir a documentação atual.
