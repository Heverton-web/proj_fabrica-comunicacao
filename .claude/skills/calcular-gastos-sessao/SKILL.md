---
name: calcular-gastos-sessao
description: >
  Calcula e exibe gastos por ação e por sessão de qualquer agente de IA
  (OpenCode, MimoCode, Antigravity, Codex, Claude Code, Cursor, etc).
  Usa preços do módulo /global/modelos-ia como referência.
  Trigger: "quanto gastei", "custo da sessão", "gastos por ação", "session cost"
---

# Calcular Gastos por Sessão — Universal

Sistema de tracking de custos que funciona para TODOS os agentes de IA.

## Arquitetura

### Camada ERP (backend — `agentes-ia` módulo)

- Tabela `agentes_usage_log` — logs de toda chamada de IA
- Edge function `agentes-ia-chat` — captura `usage` da API, calcula preço via `modelos_ia`, insere log
- Service `buscarGastosSessao(sessionId)` — consulta custo acumulado
- Fonte de preços: `modelos_ia.input_cost` / `modelos_ia.output_cost` (por milhão de tokens)

### Camada Agente (workspace — TODOS os agentes)

- Arquivo `.agents/session-cost.jsonl` — log compartilhado entre agentes
- Formato: `{"ts":"...","action":"...","model":"...","session_id":"...","tokens_in":N,"tokens_out":N,"cost":N,"session_total":N}`
- Cada agente appenda após CADA ação

## Modelo Ativo da Sessão (OBRIGATÓRIO — nunca hardcoded)

O custo DEVE ser calculado com o **modelo que está efetivamente em uso naquela
sessão**, e não um modelo fixo. Cada sessão é independente e pode rodar um modelo
diferente em paralelo:

- Sessão A roda **Hy3** (`opencode/hy3-free`) → todos os appends usam `"model":"opencode/hy3-free"`
  e buscam o preço do Hy3 na `modelos_ia`
- Sessão B (paralela) roda **mimo V2.5** (`mimo-v2.5`) → todos os appends usam
  `"model":"mimo-v2.5"` com o preço do mimo
- Os totais são **isolados por `session_id`** e nunca se misturam entre sessões

### Como detectar o modelo ativo (resolver UMA vez no início da sessão)

| Agente | Como identificar o modelo | Exemplo de `model` |
|---|---|---|
| OpenCode | Vem no system prompt ("powered by the model named `<id>`") e/ou `opencode.json` (`model`). Formato `opencode/<id>` | `opencode/hy3-free` |
| MimoCode | Config do Mimo na sessão | `mimo-v2.5` |
| Antigravity / Codex / Claude Code / Cursor | Provider + modelo da sessão | `claude-sonnet-4-20250514` |

> Capture o `model` e o `session_id` no início da sessão e reutilize em TODOS os appends.
> Nunca assuma um modelo padrão — o cálculo sempre reflete o modelo real daquela sessão.

## Como usar (qualquer agente)

### 1. Após cada ação, appendar em `.agents/session-cost.jsonl`

```jsonl
{"ts":"2026-07-14T10:30:00Z","action":"criar-modulo","model":"opencode/hy3-free","session_id":"sess-abc-123","tokens_in":1200,"tokens_out":3400,"cost":0.0087,"session_total":0.0423}
```

### 2. Calcular custo da ação

```
custo = (tokens_in / 1_000_000 * input_cost) + (tokens_out / 1_000_000 * output_cost)
```

Onde `input_cost` e `output_cost` vêm da tabela `modelos_ia` para o **modelo da sessão
atual** (o mesmo `model` usado no append — ex: `opencode/hy3-free`), via Supabase MCP.

**Fallback** se modelo não encontrado na tabela:
| Provedor | Input (por 1M tok) | Output (por 1M tok) |
|---|---|---|
| Claude Sonnet 4 | $3.00 | $15.00 |
| Claude Haiku 3.5 | $1.00 | $5.00 |
| GPT-4o | $2.50 | $10.00 |
| GPT-4o-mini | $0.15 | $0.60 |
| Gemini 2.0 Flash | $0.10 | $0.40 |
| DeepSeek V3 | $0.50 | $2.00 |

### 3. Exibir no output

```
[💰 Ação: R$ 0,0087 | Sessão: R$ 0,0423]
```

Converter USD → BRL se aplicável (usar câmbio atual ~R$ 5,50).

## Consulta via Supabase MCP

```sql
-- Preço do modelo
select input_cost, output_cost from modelos_ia
where modelo_id = 'claude-sonnet-4-20250514'
or nome ilike '%claude-sonnet-4%'
order by versao_id desc limit 1;

-- Gastos da sessão via API
select * from agentes_usage_log
where session_id = 'uuid-da-sessao'
order by created_at;

-- Total do dia
select sum(total_cost) from agentes_usage_log
where empresa_id = 'uuid-empresa'
and created_at >= current_date;
```

## Regras

1. TODO agente DEVE exibir `[💰 Ação: R$ X | Sessão: R$ Y]` no final de cada ação
2. TODO agente DEVE appendar `.agents/session-cost.jsonl`
3. O `model` usado no cálculo DEVE ser o **modelo ativo da sessão atual**, resolvido
   uma vez no início (ver "Modelo Ativo da Sessão"). NUNCA use modelo hardcoded/fixo.
4. O cálculo e o total DEVEM ser isolados por `session_id` — sessões paralelas com
   modelos diferentes não se misturam.
5. Se não conseguir calcular custo real, usar fallback da tabela acima COM o modelo da sessão
6. Se não conseguir acesso ao Supabase, manter tracking local via JSONL
7. Valor monetário sempre em BRL (R$), 4 casas decimais
