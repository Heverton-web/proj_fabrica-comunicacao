# Molde de Postmortem (Peça 5 — postmortem que vira teste)

Toda vez que a linha de "Prevenção" descrever um comportamento verificável,
ela deve nascer junto com um teste automatizado — não ficar só em prosa
esperando que alguém leia este arquivo de novo. Use
`scripts/postmortem_para_teste.py` para gerar o stub de teste a partir do
bloco abaixo.

## Formato

```markdown
- **[DATA] [título curto do bug]:** causa: [o que realmente aconteceu, no
  nível técnico]. Fix: [o que foi mudado]. Prevenção: [regra que evita
  recorrência — e o teste automatizado que a materializa]. Arquivos:
  [caminhos tocados].
```

## Exemplo real (generalizado)

- **2026-08-11 Cheatsheet vazio:** causa: a função de agregação lia o campo
  no nível errado da estrutura de dados. Fix: mover o campo pro nível
  esperado. Prevenção: a agregação nunca pode nascer vazia quando a entrada
  tem os campos mínimos — teste de regressão garante isso.
  Arquivos: `modulo/agregador.py`.
