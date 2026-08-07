---
name: pre-flight-check
description: >
  Validação local obrigatória antes de qualquer modificação estrutural, refatoração
  ou deploy. Roda type-check, testes e build. Bloqueia se qualquer etapa falhar.
  Triggers: "pre-flight-check", "pre flight", "validar antes de deploy",
  "checar build", "rodar testes", "verificar antes de commit"
---

# Pre-flight Check

Protocolo obrigatório de validação local. DEVE ser executado ANTES de:
- Qualquer deploy
- Commit de mudanças estruturais
- Refatoração de service layer
- Alterações em types.ts ou module.ts

## Passo a passo

1. **Type check**: `npm run check:types` (ou `npx tsc --noEmit`).
2. **Testes**: `npm run test:safe` (ou `npx vitest run`).
3. **Build**: `npm run build`.
4. **Análise**: se qualquer etapa falhar → PARAR, corrigir, repetir do passo 1.
5. **Reportar**: listar resultados de cada etapa.

## Ordem rigorosa (NUNCA alterar)

```
1. Type Check  →  2. Testes  →  3. Build  →  4. Deploy
```

**NUNCA** pular etapas. **NUNCA** rodar build antes de testes. **NUNCA** deploy antes de build.

## Regras

### Se type check falhar
- Ler erro via **headroom** (compactar output).
- Diagnosticar via **lean-ctx** (ler apenas assinaturas afetadas).
- Corrigir o tipo.
- REINICIAR do passo 1 (type check novamente).

### Se testes falharem
- Aplicar headroom no output do vitest.
- Identificar teste que falhou (arquivo + linha).
- Ler teste + código testado via lean-ctx.
- Corrigir código OU teste (conforme a intenção).
- REINICIAR do passo 1.

### Se build falhar
- Aplicar headroom no output do build.
- Geralmente é erro de tipo não detectado no passo 1 (dependências circulares, etc.).
- Corrigir e REINICIAR do passo 1.

### Se tudo passar
- Reportar: `✓ types | ✓ testes | ✓ build — pronto para deploy`
- Prosseguir com ação solicitada.

## NUNCA fazer
- NUNCA declarar tarefa como concluída sem rodar pre-flight-check.
- NUNCA fazer deploy com testes falhando.
- NUNCA pular type check "porque é mudança pequena".
- NUNCA usar `--no-verify` para pular hooks de validação.
- NUNCA ignorar warnings de deprecated sem avaliar impacto.
- NUNCA rodar pre-flight-check em background — é bloqueante.
- NUNCA alterar a ordem dos passos.

## Interação com outras skills
- **headroom**: OBRIGATÓRIO antes de reportar falhas (compactar output de erro).
- **lean-ctx**: usado para diagnosticar erros identificados no pre-flight.
- **caveman**: resultado do pre-flight pode ser reportado em modo caveman.
- **rtk-memory**: erros novos descobertos devem ser registrados.
