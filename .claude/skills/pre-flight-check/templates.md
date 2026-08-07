# Pre-flight Check — Templates de uso

## Template 1: Deploy padrão

**Input do usuário:** "deploy"

**Execução:**
```bash
# Passo 1: Type check
npm run check:types
# → ✓ Sem erros de tipo

# Passo 2: Testes
npm run test:safe
# → ✓ 147 testes passando, 0 falhas

# Passo 3: Build
npm run build
# → ✓ Build concluído em 12.3s
```

**Reporte:**
```
✓ types | ✓ testes (147) | ✓ build (12.3s)
Deploy autorizado.
```

---

## Template 2: Type check falha

**Execução:**
```bash
# Passo 1: Type check
npx tsc --noEmit
# → error TS2345: Argument of type 'string' is not assignable to parameter of type 'UUID'
```

**Reporte com headroom:**
```
✗ types — TS2345 em service.ts:24
  Argument tipo 'string' não é atribuível a 'UUID'
  
[... output tsc compactado por headroom ...]

✗ testes — NÃO RODADO (type check falhou)
✗ build — NÃO RODADO

Corrigindo...
```

**Ação:**
```
Fix: service.ts:24 — adicionar cast ou converter para UUID
Reiniciando pre-flight...
```

---

## Template 3: Teste falha

**Execução:**
```bash
# Passo 1: ✓ types
# Passo 2: testes
npx vitest run
# → FAIL src/features/agendamentos/hooks/useAgendamentos.test.ts:15
```

**Reporte com headroom:**
```
✓ types
✗ testes — 1 falha

  useAgendamentos.test.ts:15
  Expected: { hora: "14:30" }
  Received: { hora: "14:3"  }

✗ build — NÃO RODADO

Causa provável: .slice(0,5) em service.ts:35 remove último caractere
```

**Ação:**
```
Fix: service.ts:35 — validar formato HH:MM antes do slice
Reiniciando pre-flight...
```

---

## Template 4: Build falha (erro tardio)

**Execução:**
```bash
# Passo 1: ✓ types
# Passo 2: ✓ testes (142 passando)
# Passo 3: build
npm run build
# → Error: Package path ./utils not exported from package
```

**Reporte:**
```
✓ types
✓ testes (142)
✗ build — erro de exportação

  Package path ./utils não exportado de ~/lib
  Causa: barrel export faltando em lib/index.ts

Corrigindo...
```

---

## Template 5: Tudo passa

**Execução:**
```bash
# Passo 1: ✓ types
# Passo 2: ✓ testes (156 passando)
# Passo 3: ✓ build (11.8s)
```

**Reporte (caveman):**
```
✓ types | ✓ testes (156) | ✓ build (11.8s)
Deploy autorizado.
```

---

## Template 6: Pré-commit (mudança estrutural)

**Input do usuário:** "Vou mudar o module.ts do cadastros"

**Antes de começar:**
```bash
# Rodar pre-flight ANTES de mexer
npm run check:types && npm run test:safe
# → ✓ Ambos passam — baseline OK

# [fazer as mudanças]

# Rodar pre-flight DEPOIS das mudanças
npm run check:types && npm run test:safe && npm run build
# → ✓ Tudo passa — mudança segura
```

**Reporte:**
```
Pre-mudança: ✓ types | ✓ testes
Pós-mudança: ✓ types | ✓ testes | ✓ build
Mudança validada. Seguro para commit.
```
