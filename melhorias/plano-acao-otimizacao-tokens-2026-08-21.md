---
title: Plano de Ação — Otimização de Tokens (Baseado em "Tokens Sob Perícia")
data: 2026-08-21
projeto: proj_fabrica-comunicacao
estado_inicial: pronto-para-iniciar
---

# Plano de Ação — Otimização de Tokens

Adaptação do relatório ["Tokens Sob Perícia"](../../../proj_fabrica-de-livros/) para
este projeto. Cada seção lista uma oportunidade, prioridade, estimativa e passos
concretos.

**Abreviações:**
- **R**: Regra numerada (ex. R7 = item 7 de CLAUDE.md)
- **Arch** = AGENTS.md (fonte de verdade da arquitetura)
- **Spec** = SPEC_COMANDOS.md

---

## PRIORIDADE 1: E. Blindagem de segredos no pre-commit hook

**Por quê agora:** Este projeto autoriza auto-commit/push (R7). O gate de segredos é a
primeira linha de defesa contra exposição acidental de API keys (ex.: Anthropic,
Vercel, integração com serviços terceiros mencionados em brief_criativo.json).

**Objetivo:** bloquear commit automático se o diff staged contiver padrão de segredo.

**Arquivos a criar/modificar:**
- `scripts/hooks/pre-commit` (novo) — fonte versionada
- `scripts/setup-hooks.ps1` (novo) — script de configuração Windows
- `.claude/settings.json` — sem mudança (hooks já configurados em `core.hooksPath`)

**Passos:**
1. Criar diretório `scripts/hooks/`:
   ```powershell
   mkdir -p scripts/hooks
   ```
2. Criar `scripts/hooks/pre-commit` com gate de padrões de segredo:
   - `sk-[a-zA-Z0-9_-]{20,}` (Anthropic API keys)
   - `-----BEGIN [A-Z ]*PRIVATE KEY-----` (chaves PEM)
   - `AKIA[0-9A-Z]{16}` (AWS keys)
   - `ghp_[a-zA-Z0-9]{36}` (GitHub PAT)
   - `xox[baprs]-[0-9a-zA-Z-]+` (Slack tokens)

   O gate roda ANTES de qualquer teste, falha rápido (exit 1) se encontrar algo.

3. Criar `scripts/setup-hooks.ps1` que:
   - Copia `scripts/hooks/pre-commit` para `.git/hooks/pre-commit` (ou symlink)
   - Torna executável em Windows (via Git Bash ou `chmod +x` em subshell)

4. Atualizar `.claude/settings.json`:
   ```json
   "core": {
     "hooksPath": "scripts/hooks"
   }
   ```

5. Rodar `scripts/setup-hooks.ps1` para ativar o hook na cópia local.

6. Testar:
   - Stage um arquivo contendo padrão fictício de chave Anthropic (prefixo sk- seguido de 20+ caracteres)
   - Tentar commit — deve ser bloqueado com mensagem `[BLOQUEADO] possível segredo em <arquivo>`
   - Remover a string e reconfirmar que commit passa

7. Documentar em `CLAUDE.md` (§0, item sobre R7 auto-commit):
   > "Auto-commit/push é bloqueado automaticamente pelo pre-commit hook se detectar
   > padrão de API key, chave PEM ou token de plataforma conhecida (Anthropic, AWS,
   > GitHub, Slack, etc.). O hook roda antes da suíte de testes (falha rápida)."

**Critério de aceite:**
- [ ] Hook roda em commit normal (sem segredo) sem erro
- [ ] Hook bloqueia commit com segredo staged
- [ ] Documentação atualizada em CLAUDE.md
- [ ] `scripts/setup-hooks.ps1` pode ser rodado novamente sem efeitos colaterais

**Risco:** falso positivo (ex.: hash SHA-256 de 40+ chars). Mitigado com padrões
specificamente prefixados (sk-, AKIA, PEM headers) em vez de regex genérica.

**Estimativa:** 45 min — 1h

**Blocos de sucesso:**
```bash
# Teste 1: Commit normal (sem segredo)
git add -A
git commit -m "test: sem segredo"  # ✓ passa

# Teste 2: Commit bloqueado
echo "AKIA<16-caracteres-alfanumericos>" > test-secret.txt  # Padrão AWS key
git add test-secret.txt
git commit -m "test: com segredo"  # ✗ [BLOQUEADO] possível segredo em test-secret.txt
```

---

## PRIORIDADE 2: C. Resiliência de rede em scripts HTTP

**Por quê agora:** Projetos que compilam HTML/PDF/arte via Playwright ou integram com
APIs externas (ex.: Vercel, Unsplash, serviços de validação) sofrem com falhas
transitórias de rede. Atualmente, uma timeout mata o pipeline.

**Objetivo:** adicionar retry com backoff + jitter para chamadas HTTP, paralelizar
quando possível.

**Arquivos afetados:**
- `scripts/compilar-html.py` (Playwright, pode fazer HTTP)
- `scripts/compilar-art.py` (idem)
- `scripts/compilar-pdf.py` (idem)
- `scripts/auditar-projeto.py` (validação de URLs se houver)
- Novos testes em `tests/` cobrindo retry/backoff

**Passos:**
1. Criar função utilitária em `scripts/_tipos_comuns.py` (já existe):
   ```python
   def http_get_with_backoff(url, max_retries=3):
       """Retry com backoff exponencial + jitter para GET/HEAD."""
       for attempt in range(max_retries):
           try:
               # sua chamada HTTP aqui (urllib, requests, etc.)
               return response
           except (HTTPError, URLError, TimeoutError) as e:
               if attempt == max_retries - 1:
                   raise
               wait = 0.5 * (2 ** attempt) + random.uniform(0, 0.3)
               time.sleep(wait)
   ```

2. Em cada script que faz HTTP (Playwright, etc.), substituir chamadas diretas por
   `http_get_with_backoff`.

3. Se um script validar múltiplos URLs/recursos em paralelo (ex.: compilar-html.py
   com múltiplas imagens), envolver em `concurrent.futures.ThreadPoolExecutor` com
   `max_workers=3` (conservador para respeitar rate limits).

4. Manter modo `--sem-rede` intocado (não entra retry/paralelismo se offline).

5. Rodar testes: `python -m pytest -q tests/` — só commitar com 100% verde.

6. Medir tempo antes/depois com uma compilação real:
   ```bash
   time python scripts/compilar-html.py <slug> --medir-rede
   ```

**Critério de aceite:**
- [ ] Um GET que falha na primeira tentativa com 502 é absorvido e reexecutado com sucesso
- [ ] Suíte 100% verde
- [ ] Tempo de compilação não piorou (idealmente melhorou em casos de paralelismo)

**Estimativa:** 2-3h (inclui testes)

**Risco:** paralelismo disparar rate limit se `max_workers` for muito alto. Resposta:
documentar por quê é 3 no próprio código.

---

## PRIORIDADE 3: D. Separação RTK SCRATCHPAD do CLAUDE.md

**Por quê depois:** Este projeto ainda tem CLAUDE.md muito pequeno (45 linhas), então o
impacto de cache é mínimo por enquanto. Porém, conforme o CLAUDE.md cresce (mais
regras, mais hooks), esta separação protege o prefixo de cache e deixa o scratchpad
cresce livremente.

**Objetivo:** isolar aprendizados de sessão (RTK SCRATCHPAD) em arquivo separado, mantendo
CLAUDE.md normativo estável.

**Arquivos afetados:**
- `CLAUDE.md` — reduzir seção RTK SCRATCHPAD a uma linha de referência
- `RTK-SCRATCHPAD.md` (novo) — corpo das entradas datadas
- `.claude/skills/rtk-memory/SKILL.md` — ajustar caminho de escrita

**Passos:**
1. Verificar se `CLAUDE.md` já tem seção RTK SCRATCHPAD:
   ```bash
   grep -n "RTK SCRATCHPAD" CLAUDE.md
   ```
   (Resposta esperada: nenhuma — não existe ainda neste projeto)

2. Criar `RTK-SCRATCHPAD.md` na raiz com frontmatter:
   ```markdown
   ---
   title: RTK SCRATCHPAD — Aprendizados de Sessões
   ---

   # RTK SCRATCHPAD

   Entradas datadas e sessão-específicas que não pertencem ao CLAUDE.md normativo.

   ---
   ```

3. Se `.claude/skills/rtk-memory` existir, ajustar para gravar em `RTK-SCRATCHPAD.md`.

4. **Não há nada para migrar hoje** — apenas estrutura para futuro crescimento.

**Critério de aceite:**
- [ ] `RTK-SCRATCHPAD.md` existe e contém instruções de uso
- [ ] Próximas entradas de `rtk-memory` vão para lá em vez de CLAUDE.md
- [ ] `CLAUDE.md` continua sendo a fonte de verdade normativa

**Estimativa:** 20 min (apenas setup, sem migration)

**Nota:** Adiado até que CLAUDE.md cresça de verdade. Baixa prioridade agora.

---

## PRIORIDADE 4: A. Gate de verificação de comandos/CLI citados

**Por quê depois:** Este projeto é mais focado em **materiais de comunicação** (apresentações,
landing pages, kits de distribuição) do que em **livros técnicos**. O gate de comandos
CLI só faz sentido para livros sobre tooling/frameworks.

**Objetivo:** novo gate de conteúdo que valida se comandos/flags citados em capítulos
técnicos realmente existem.

**Aplicabilidade para proj_fabrica-comunicacao:**
- ✗ Baixa — projetos aqui raramente incluem capítulos técnicos com CLIs
- Possível uso futuro: se começar a gerar "guias técnicos" ou "apostilas"

**Quando implementar:**
Esperar até que surja um projeto com `categoria_tecnica: true` em `config_projeto.json`.
Então usar este plano como referência.

**Estimativa:** 4-6h (quando necesário)

---

## PRIORIDADE 5: B. Token-guard (cross-check de gasto)

**Por quê depois:** Condicional. Precisa de pré-requisito: ferramenta `ccusage` rodando
e histórico JSONL acessível.

**Objetivo:** medir gasto real de sessão como validação cruzada do auto-relato.

**Pré-requisito:** testar no ambiente local (Windows + Claude Code)
```bash
npx ccusage@latest --version
```

Se falhar, **este item fica NÃO_VERIFICÁVEL** — não implementar nada.

**Passos (só se pré-requisito passar):**
1. Criar `scripts/token-guard.ps1` chamando `ccusage` e comparando contra `.agents/session-cost.jsonl`
2. Integrar na skill `calcular-gastos-sessao` como passo opcional

**Estimativa:** 30 min (pré-requisito) + 1-2h (implementação, se viável)

---

## Sequência de Implementação Recomendada

| Prioridade | Item | Tempo | Quando | Blocos dependentes |
|------------|------|------|--------|-------------------|
| **1** | E. Pre-commit hook | 45m–1h | Agora | Nenhum |
| **2** | C. Resiliência HTTP | 2–3h | Semana que vem | Testes de regressão |
| **3** | D. RTK SCRATCHPAD | 20m | Quando CLAUDE.md crescer | Nenhum |
| **4** | A. Gate CLI | 4–6h | Se projeto técnico surgir | Gate system/validação |
| **5** | B. Token-guard | 30m + 1–2h | Após validar pré-req | Skill calcular-gastos |

---

## Métricas de Sucesso

Ao final de todas as implementações, esperamos:
1. **Segurança:** 0 commits com segredo escapando ao gate
2. **Confiabilidade:** tolerância a falhas transitórias de rede (3 retries com backoff)
3. **Cache:** CLAUDE.md mantém tamanho estável (<51 KB) mesmo conforme projeto cresce
4. **Validação:** novos gates opcionais disponíveis para futuros tipos de projeto

---

## Próximos Passos

1. **Hoje:** Iniciar Prioridade 1 (pre-commit hook) — é o ganho de segurança mais
   imediato.
2. **Esta semana:** Prioridade 2 (resiliência HTTP) — melhora confiabilidade dos builds.
3. **Próximas semanas:** Prioridades 3–5 conforme necessidade.

---

**Documento gerado por:** Claude Code (fable-method)
**Referência:** D:/proj_fabrica-de-livros/melhorias/21-08-2026-plano-acao-tokens-sob-pericia.md
**Atividade:** Análise de aplicabilidade de relatório externo + adaptação para este projeto
