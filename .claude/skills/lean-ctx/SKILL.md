---
name: lean-ctx
description: >
  Economia severa de contexto. Prioriza grep_search antes de view_file, lê apenas
  assinaturas de funções antes de corpos completos e usa slices restritos de linhas.
  Triggers: "lean-ctx", "lean context", "economia de contexto", "ler so assinatura",
  "grep antes de read"
---

# Lean Context (Economia Severa de Contexto)

Protocolo estrito de leitura de código para minimizar o consumo de tokens de entrada.

## Diretrizes

1. **Grep Antes de Read**: NUNCA execute `view_file` em um arquivo inteiro sem antes usar `grep_search` para localizar a linha exata.
2. **Assinaturas Antes de Corpos**: Quando precisar entender uma interface ou classe, leia apenas a declaração de tipos, exports e assinaturas.
3. **Slice Restrito**: Quando fizer `view_file`, especifique `StartLine` e `EndLine` para carregar no máximo 20-50 linhas por trecho.
4. **Sem Re-leitura Redundante**: Não releia arquivos cujas informações já estão no contexto atual.
