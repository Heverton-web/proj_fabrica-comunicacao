---
titulo: RTK SCRATCHPAD — Aprendizados e Notas de Sessões
descricao: Arquivo compartilhado para notas sessão-específicas que NÃO pertencem ao CLAUDE.md normativo. Pode crescer livremente sem afetar cache de prefixo.
---

# RTK SCRATCHPAD

Aprendizados, descobertas, padrões confirmados e ajustes táticos documentados durante
sessões com Claude Code.

**Nota:** Este arquivo é mantido FORA do `CLAUDE.md` normativo para proteger o prefixo
de cache (token budget). O `CLAUDE.md` contém apenas regras permanentes (Regras 0-8 de
Economia de Tokens, Governança, etc.); este arquivo cresce com descobertas sessão por
sessão.

---

## Índice de Entradas

(Entradas datadas serão adicionadas aqui conforme surgem — formato: data — tópico — resumo)

---

## Template para Novas Entradas

Ao documentar um aprendizado, use este formato:

```markdown
## 2026-MM-DD — [Tópico] [Breve Descrição]

**Contexto:** [O que estava acontecendo / qual era o problema]

**Descoberta:** [O que foi aprendido / confirmado / refutado]

**Aplicação:** [Como isso mudará trabalho futuro — padrão confirmado, armadilha evitada, etc.]

**Referência:** [Sessão/commit/arquivo relevante, se houver]
```

---

## Como Usar Este Arquivo

### Para Leitura (Futuras Sessões)

Se o `CLAUDE.md` menciona "ver RTK-SCRATCHPAD", este é o arquivo. Seções relevantes
estarão listadas por data e tópico abaixo.

### Para Escrita (Skill rtk-memory)

A skill `rtk-memory` (.claude/skills/rtk-memory/SKILL.md) deve gravar novas entradas
neste arquivo, NÃO em CLAUDE.md. Arquivo de destino:

```
./RTK-SCRATCHPAD.md
```

Padrão de commit:
```bash
git add RTK-SCRATCHPAD.md
git commit -m "rtk: <data> — <tópico>"
```

---

## Entrada-Exemplo (Remover Após Primeira Sessão Real)

## 2026-08-21 — Implementação de Plano de Ação (Token-Economy)

**Contexto:** Recebido plano de ação com 5 prioridades de otimização de tokens
derivado de análise de proj_fabrica-de-livros. Tarefa: implementar de forma
incremental (implementa-testa-valida-segue) neste projeto.

**Descoberta:**
1. Pre-commit hook de segredos é crítico ANTES de autorizar auto-commit/push (R7).
   O gate passou a si mesmo em testes (capturou strings `sk-` em documentação).
2. Requisições HTTP diretas não eram óbvias no código; Playwright é o vetor real.
   Funções de retry são úteis para ambos.
3. CLAUDE.md é pequeno (46 linhas) — separação de RTK SCRATCHPAD é estrutural,
   não necessário hoje, mas protege crescimento futuro.

**Aplicação:**
- Prioridade 1 (pre-commit) implementada, testada, commitada ✓
- Prioridade 2 (HTTP retry) implementada com 11 testes, reutilizável ✓
- Prioridade 3 (RTK SCRATCHPAD) estrutura criada, pronto para crescimento
- Prioridades 4-5 aguardam necessidade (projeto técnico / pré-requisito)

**Referência:** Commits 312d573, 63c53d3 | Arquivo: melhorias/plano-acao-otimizacao-tokens-2026-08-21.md

---

**Última atualização:** 2026-08-21
