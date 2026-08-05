---
description: Regenera uma ou mais variantes de arte PNG (1080x1080/1080x1350/1080x1920) de um projeto já esboçado, sem repetir a entrevista nem re-analisar insumos. Falha rápido se o projeto ainda não tiver brief_criativo.json.
---

# /gerar-arte

O procedimento completo e canônico deste comando vive em `SPEC_COMANDOS.md`, seção
`## /gerar-arte` — este arquivo é só o ponteiro que permite ao Claude Code descobrir o
comando (REGRA: nunca duplicar a mesma instrução em 2 lugares, mesma lição do bug
histórico de `TIPOS_VALIDOS` duplicado).

**Leia `SPEC_COMANDOS.md` por completo agora e execute exatamente o que está escrito
na seção `/gerar-arte`.** `$ARGUMENTS` = `<slug> [--tamanho 1080x1080|1080x1350|1080x1920 ...]`
referenciado naquele documento.
