---
title: Instruções de Integração — Gate CLI para Livros Técnicos
data: 2026-08-21
fase: 4-gate-cli
---

# Gate CLI — Validação de Comandos em Livros Técnicos

## Resumo

Novo gate de conteúdo que valida se comandos, flags e caminhos citados em capítulos
técnicos foram verificados contra fonte oficial.

**Aplicável quando:** Um projeto tem `categoria_tecnica: true` em `config_projeto.json`

---

## Como Funciona

### 1. Marcação no Markdown

Cada bloco de código que cita um comando é marcado com comentário HTML (invisível no PDF):

```markdown
## Instalação Docker

Execute:

\`\`\`bash
docker run -it ubuntu:22.04 /bin/bash
\`\`\`
<!-- cli-check: fonte=B; confere=true -->
```

**Campos:**
- **fonte:** Nível de revisão (A=revisor não-técnico, B=revisor com conhecimento, C=revisor-fonte autoria)
- **confere:** `true` = comando verificado e correto | `false` = conhecido estar errado (fabricado)

### 2. Execução do Gate

```bash
python scripts/validar-comandos-cli.py <slug> [--estrito]
```

**Output:**
```
[VALIDACAO CLI] meu-livro-docker
  Total blocos de codigo: 15
  Confirmados: 12
  Fabricados: 1
  Nao verificados: 2

Avisos/Erros (1):
  - capitulo-02.md: comando FABRICADO (confere=false): docker push FAKE_IMAGE

[ERRO] Validacao reprovou (modo --estrito)
```

### 3. Resultados

| Estado | Comportamento | Em --estrito |
|--------|---|---|
| **CONFIRMADO** (confere=true) | Contabilizado, não bloqueia | ✓ Passa |
| **FABRICADO** (confere=false) | Aviso + erro | ✗ Reprova |
| **NÃO_VERIFICADO** (sem marcação) | Aviso (até 3), não bloqueia | ✓ Passa |

---

## Integração em Workflows

### Em auditar-projeto.py (gate --estrito)

Adicionar chamada ao validar-comandos-cli.py quando `categoria_tecnica: true`:

```python
# Em auditar-projeto.py, apos outros gates:
if config.get("categoria_tecnica"):
    resultado_cli = validar_comandos_cli(slug, estrito=True)
    if not resultado_cli["passou"]:
        sys.exit(1)
```

### Em revisor-tecnico (skill)

Incluir no protocolo de revisão:

1. **Antes de marcar `confere=true`:** Revisor testa o comando contra `--help` ou documentação oficial
2. **Se comando não existe ou mudou:** Marcar `confere=false` + alertar autor
3. **Se sem informação:** Deixar sem marcação (não bloqueia, gera aviso)

---

## Protocolo de Escrita (Para Redatores)

Ao escrever capítulo técnico:

1. **Citar apenas comandos que já testou**
2. **Deixar marcação vazia inicialmente** (será preenchida por revisor)
3. **Respeitar versões citadas** (ex.: "Docker 20.10+" em vez de "Docker latest")

---

## Protocolo de Revisão (Para Revisores)

Ao revisar capítulo técnico:

1. **Executar cada comando** em seu próprio ambiente (Docker, VM, etc.)
2. **Verificar contra `--help` e docs oficiais** para a versão citada
3. **Marcar resultado:**
   - Comando funciona → `confere=true`
   - Comando não funciona / não existe → `confere=false` + notificar autor
   - Não testado (ex.: é um template, não executável) → deixar sem marcação

Exemplo:
```bash
# Revisor testando comando:
$ docker run -it ubuntu:22.04 /bin/bash
# ✓ Funciona → marcar confere=true

$ apt install package-que-nao-existe
# ✗ Falha → marcar confere=false
```

---

## Testes

Cobertura: **12 testes** em `tests/test_validar_comandos_cli.py`

```bash
python -m pytest tests/test_validar_comandos_cli.py -v
```

Casos cobertos:
- ✓ Extração de blocos de código (bash, sh, python, etc.)
- ✓ Detecção de marcação cli-check
- ✓ Estados: confirmado, fabricado, não-verificado
- ✓ Lógica de gate: reprova em --estrito se houver fabricado
- ✓ Case-insensitivity, espaçamento flexível

---

## Quando Implementar Completamente

Este gate é **estruturalmente pronto** agora. Ativar quando:

1. ✓ Arquivo validar-comandos-cli.py criado
2. ✓ Testes validam comportamento
3. ⏳ Um projeto novo tiver `categoria_tecnica: true` em `config_projeto.json`
4. ⏳ Integração em auditar-projeto.py e skill revisor-tecnico

**Atualmente:** Estrutura 100% completa, aguardando ativação por demanda.

---

## Exemplos

### Markdown Original

```markdown
## Comandos Básicos

Inicie o container:

\`\`\`bash
docker run -d -p 8080:80 nginx
\`\`\`

## Debugging

Use este comando para verificar logs:

\`\`\`bash
docker logs -f meu-container
\`\`\`
```

### Após Revisão

```markdown
## Comandos Básicos

Inicie o container:

\`\`\`bash
docker run -d -p 8080:80 nginx
\`\`\`
<!-- cli-check: fonte=B; confere=true -->

## Debugging

Use este comando para verificar logs (Docker 20.10+):

\`\`\`bash
docker logs -f meu-container
\`\`\`
<!-- cli-check: fonte=B; confere=true -->
```

---

## Status

- ✅ Script validar-comandos-cli.py: implementado
- ✅ Testes: 12/12 passando
- ✅ Documentação: completa
- ⏳ Integração em auditar-projeto.py: pendente (ativar quando necessário)
- ⏳ Skill revisor-tecnico: pendente (usar este guia como referência)

---

**Documento gerado:** 2026-08-21
**Fonte:** Plano de Ação de Otimização de Tokens
**Referência:** melhorias/plano-acao-otimizacao-tokens-2026-08-21.md
