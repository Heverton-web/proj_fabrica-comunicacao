# RTK Memory — Templates de uso

## Template 1: Registrar bug de tipo resolvido

**Cenário:** Usuário resolveu erro TS2345 em service.ts

**Entrada no AGENTS.md:**
```markdown
## RTK SCRATCHPAD

### [2025-07-22] TIPO: string não atribuível a UUID
- **Causa**: parâmetro recebido como string, mas tipo espera UUID
- **Fix**: adicionar `as UUID` ou usar `crypto.randomUUID()`
- **Arquivo**: src/features/cadastros/usuarios/service.ts:24
- **Prevenção**: sempre importar tipo UUID de ~/lib/types
```

---

## Template 2: Registrar padrão de RLS

**Cenário:** Usuário descobriu que queries sem empresa_id são bloqueadas

**Entrada no AGENTS.md:**
```markdown
### [2025-07-22] RLS: empresa_id obrigatório em INSERT
- **Causa**: política RLS do Supabase bloqueia INSERT sem empresa_id
- **Fix**: sempre incluir `empresa_id` vindo de `useAuth()` no objeto insert
- **Arquivo**: todos os service.ts
- **Prevenção**: hook `useAuth()` deve ser chamado antes de qualquer mutation
```

---

## Template 3: Registrar configuração não óbvia

**Cenário:** Descoberta de que `npm run test:safe` roda com filtro headroom

**Entrada no AGENTS.md:**
```markdown
### [2025-07-22] CONFIG: test:safe usa filtro headroom
- **Causa**: script test:safe filtra output do vitest automaticamente
- **Fix**: não precisa aplicar headroom manualmente ao rodar test:safe
- **Arquivo**: package.json (script test:safe)
- **Prevenção**: sempre usar `test:safe` em vez de `vitest run` no pre-flight
```

---

## Template 4: Registrar padrão arquitetural

**Cenário:** Usuário percebeu que todos os módulos seguem mesma estrutura

**Entrada no AGENTS.md:**
```markdown
### [2025-07-22] PADRAO: estrutura de módulo padrão
- **Causa**: todos os módulos seguem mesma convenção
- **Fix**: novo módulo DEVE ter: module.ts, types.ts, service.ts, hooks/
- **Arquivo**: src/features/*/
- **Prevenção**: usar skill criar-modulo para novos módulos
```

---

## Template 5: Registrar erro de runtime

**Cenário:** Bug onde hora era cortada incorretamente

**Entrada no AGENTS.md:**
```markdown
### [2025-07-22] RUNTIME: .slice(0,5) corrompe horário
- **Causa**: `dados.hora.slice(0, 5)` aceita "12:3" e gera "12:3" (inválido)
- **Fix**: validar com regex `/^([01]\d|2[0-3]):[0-5]\d$/` antes do slice
- **Arquivo**: src/features/agendamentos/service.ts:35
- **Prevenção**: criar função util `validarHora(hora: string): boolean`
```

---

## Template 6: Atualizar entrada existente

**Cenário:** Nova descoberta sobre registro já existente

**Entrada no AGENTS.md (atualização):**
```markdown
### [2025-07-22] RLS: empresa_id obrigatório em INSERT
- **Causa**: política RLS do Supabase bloqueia INSERT sem empresa_id
- **Fix**: sempre incluir `empresa_id` vindo de `useAuth()` no objeto insert
- **Arquivo**: todos os service.ts
- **Prevenção**: hook `useAuth()` deve ser chamado antes de qualquer mutation
- **Atualização [2025-07-22]**: vale também para UPDATE — mesmo problema
```

---

## Template 7: Non-entry (não registrar)

**Cenário:** Erro de digitação ("useSuario" em vez de "useUsuario")

**Ação:** NÃO registrar. É erro temporário, não vai se repetir.

**Cenário:** Decisão de usar `const` em vez de `let`

**Ação:** NÃO registrar. É óbvio pelo contexto.

**Cenário:** Configuração do Supabase que está documentada no README

**Ação:** NÃO registrar. Já existe fonte de verdade.
