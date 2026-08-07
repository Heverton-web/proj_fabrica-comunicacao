---
name: headroom
description: >
  Compressão severa de logs e outputs de comandos. Se a saída do comando ou log
  tiver mais de 7 linhas, comprime mantendo apenas as primeiras 3 e últimas 4 linhas.
  Triggers: "headroom", "comprimir log", "resumir output", "log headroom"
---

# Headroom Log Compression

Protocolo de compressão de logs para economizar janela de contexto.

## Regra de 7 Linhas

Se o resultado de um teste, build ou comando ultrapassar **7 linhas**:
1. Extraia apenas as 3 primeiras linhas e as 4 últimas linhas (onde fica a causa raiz/resumo do erro).
2. Omita o miolo intermediário com `[... N linhas omitidas por headroom ...]`.
3. Não cole stacktraces inteiros de bibliotecas externas.
