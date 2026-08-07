---
name: rtk-memory
description: >
  Gerencia aprendizado persistente para evitar repetição de análise. Registra erros
  resolvidos, decisões arquiteturais e padrões descobertos em memória de longo prazo.
  Triggers: "rtk-memory", "registrar erro", "salvar aprendizado", "anotar padrão",
  "rtk scratchpad", "memória persistente", "não esquecer"
---

# RTK Memory

Protocolo de registro de aprendizado persistente. Objetivo: nunca re-analisar o mesmo
erro ou re-descobrir o mesmo padrão.

## Quando registrar

| Situação | O que registrar | Onde |
|----------|----------------|------|
| Bug de compilação resolvido | Causa raiz + fix | RTK SCRATCHPAD (AGENTS.md) |
| Padrão arquitetural descoberto | Regra + exemplo | RTK SCRATCHPAD |
| Configuração não óbvia | Chave + valor + por quê | RTK SCRATCHPAD |
| Erro de runtime recorrente | Sintoma + solução | RTK SCRATCHPAD |
| Decisão de design tomada | Opção escolhida + rejeitada + motivo | Notas da sessão |

## Passo a passo

1. **Detectar**: erros resolvidos, padrões novos, configurações surpresa.
2. **Avaliar**: é duradouro? Vai aparecer de novo? Outro agente precisaria saber?
3. **Registrar**: adicionar ao `## RTK SCRATCHPAD` do `AGENTS.md`.
4. **Formatar**: usar o template abaixo.
5. **Verificar**: não duplicar entradas existentes.

## Formato de registro

```markdown
### [DATA] Categoria: Título curto
- **Causa**: o que causava o problema
- **Fix**: como foi resolvido
- **Arquivo**: path/para/arquivo.ts:linha
- **Prevenção**: como evitar no futuro
```

### Categorias válidas
- `TIPO`: erros de tipo TypeScript
- `BUILD`: erros de build/bundling
- `RUNTIME`: erros de execução
- `CONFIG`: configurações não óbvias
- `PADRAO`: padrões arquiteturais
- `RLS`: erros de Row Level Security
- `MULTI-TENANT`: problemas de empresa_id

## Local de escrita

**Sempre** adicionar ao `## RTK SCRATCHPAD` no `AGENTS.md` na raiz do projeto.

```markdown
## RTK SCRATCHPAD

### [2025-01-15] TIPO: UUID vs string
- **Causa**: Supabase retorna UUID como string, mas tipos esperam UUID
- **Fix**: usar `as UUID` ou validar com regex
- **Arquivo**: service.ts:24
- **Prevenção**: sempre tipar empresa_id como UUID nos types

### [2025-01-15] RLS: empresa_id obrigatório
- **Causa**: INSERT sem empresa_id é bloqueado pelo RLS
- **Fix**: sempre incluir empresa_id do useAuth()
- **Arquivo**: todos os service.ts
- **Prevenção**: hook useAuth() sempre chamado antes de mutations
```

## NUNCA fazer
- NUNCA registrar erros temporários (typos, erros de digitação).
- NUNCA registrar informações que já estão no código (não documentar o óbvio).
- NUNCA alterar registros existentes — apenas adicionar novos.
- NUNCA registrar senhas, tokens ou credenciais.
- NUNCA registrar decisões que são óbvias pelo contexto.
- NUNCA duplicar entrada se similar já existe — atualizar a existente.
- NUNCA usar RTK Memory como substituto para código bem tipado.

## Interação com outras skills
- **pre-flight-check**: erros novos do pre-flight devem ser registrados.
- **caveman**: registrado em formato comprimido.
- **lean-ctx**: padrões descobertos via lean-ctx são registrados.
- **headroom**: erros extraídos via headroom são registrados se novos.
