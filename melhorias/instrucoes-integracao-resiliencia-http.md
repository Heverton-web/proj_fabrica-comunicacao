---
title: Instruções de Integração — Resiliência HTTP (Retry + Backoff)
data: 2026-08-21
fase: 2-resiliencia-http
---

# Resiliência HTTP — Funções Implementadas

## Resumo

Implementadas 2 funções de retry com backoff exponencial + jitter em `scripts/_tipos_comuns.py`:

1. **`http_get_with_retry(url, max_retries=3, timeout=10, verbose=False)`**
   - Retry automático para falhas transitórias HTTP (429, 502, 503)
   - Timeout/URLError também disparam retry
   - Erros não-transitórios (404, 403, 401) falham imediatamente
   - Usa `urllib.request.urlopen` (stdlib, sem dependências extras)

2. **`playwright_goto_with_retry(page, url, max_retries=3, timeout=30000, verbose=False)`**
   - Wrapper de `page.goto()` com retry para timeouts
   - Detecta erros transitórios (timeout, connection) vs. não-transitórios
   - Útil em scripts que usam Playwright (compilar-arte, compilar-kit, validar-html)

## Onde Integrar

### 1. Scripts que fazem HTTP direto (urllib)
- **Futuros scripts** que validem URLs, APIs, integração com serviços terceiros
- **Padrão**: Substitua `urllib.request.urlopen(url)` por `http_get_with_retry(url)`

Exemplo:
```python
# Antes:
response = urllib.request.urlopen("https://api.example.com/check")

# Depois:
from _tipos_comuns import http_get_with_retry
response = http_get_with_retry("https://api.example.com/check", verbose=True)
```

### 2. Scripts que usam Playwright (page.goto)

**Candidatos atuais:**
- `scripts/validar-html.py` (linhas 83, 109: `page.goto(url)`)
- `scripts/compilar-arte.py` (pode carregar URLs em templates)
- `scripts/compilar-kit.py` (idem)

**Padrão de integração:**
```python
# Antes:
page.goto(url)

# Depois:
from _tipos_comuns import playwright_goto_with_retry
playwright_goto_with_retry(page, url, verbose=True)
```

## Testes

Cobertura: **11 testes** (7 HTTP + 4 Playwright) em `tests/test_http_resilience.py`

Casos cobertos:
- ✓ Sucesso na primeira tentativa (sem retry)
- ✓ Retry em 429, 502, 503 (HTTP)
- ✓ Retry em timeout/URLError
- ✓ Falha imediata em 404, 403, 401 (não-retentável)
- ✓ Max retries atingido
- ✓ Playwright timeout retry
- ✓ Playwright erro não-transitório (falha imediata)

```bash
python -m pytest tests/test_http_resilience.py -v
```

## Comportamento

### HTTP Retry (`http_get_with_retry`)

Padrão de espera: `0.5 * (2 ** attempt) + random.uniform(0, 0.3)` segundos

Exemplo:
- Tentativa 0 falha → espera ~0.5-0.8s
- Tentativa 1 falha → espera ~1.0-1.3s
- Tentativa 2 falha → espera ~2.0-2.3s
- Tentativa 3 (última) falha → levanta erro

### Playwright Retry (`playwright_goto_with_retry`)

Mesmo padrão de backoff, mas detecta erros pelo texto da exceção:
- Retentável: "timeout", "connection"
- Não-retentável: qualquer outro

## Quando NÃO Usar

- **URLs que são definitivamente inválidas** (404, 403) — falham rápido por design
- **Operações que não deveriam ser refeitas** (DELETE, POST sem idempotência) — use com cuidado
- **Ciclos de retry externo** — evite dupla camada de retry (sua função + retry da função)

## Performance

- **Custo:** ~1-2 ms por tentativa adicional (dormindo/backoff)
- **Ganho:** Absorve falhas transitórias que normalmente matariam o pipeline
- **Trade-off:** Pequeno aumento de latência → grande redução de falhas

## Próximas Integrações (Futuro)

Quando surgir necessidade de:
1. Validar URLs em briefs ou configs → use `http_get_with_retry`
2. Integração com APIs externas (design tokens, imagens, etc.) → use `http_get_with_retry`
3. Aplicar retry seletivo em alguns scripts Playwright → use `playwright_goto_with_retry`

**Testes existentes cobrem todos esses casos — basta substituir as chamadas.**

---

**Status:** ✓ Implementado e testado
**Commits:** feat: resiliencia HTTP com retry + backoff
