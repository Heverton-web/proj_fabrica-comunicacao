---
name: compilador-pdf
description: Fase 3 da Fábrica de Materiais de Comunicação — compila apostila_<slug>.md em PDF via Pandoc + Typst, usando templates/template_apostila.typ. Use depois de redator-apostila, antes de validar-pdf.py/revisor-marca. INTERIM — regras próprias de PDF ("Flex Gold") ainda não foram definidas; por ora usa o mesmo design system fixo dos demais materiais.
---

# Skill: Compilador de PDF

Você compila o Markdown da apostila em PDF final. Pipeline idêntico ao `compilador-abnt`
da Fábrica Agêntica de Livros (Pandoc → `.typ` → Typst).

**Nota de escopo (interim):** o operador decidiu que o PDF vai ganhar regras visuais
próprias (estilo "Flex Gold" — título-gradiente, badges, selos institucionais, como no
material de referência Master Flex), mas essas regras ainda não foram desenhadas. Até
lá, o template usa o mesmo `brand/design-system-conexao.json` fixo dos outros
materiais como paleta interina — não é a decisão final, é para não deixar o PDF quebrado.

Se precisar de técnicas auxiliares de manipulação de PDF fora do que Pandoc+Typst
cobre, consulte o skill genérico `pdf` do catálogo — não reimplemente do zero.

## Entrada

- `output/<slug>/pdf/apostila_<slug>.md`
- `brand/design-system-conexao.json` (fixo, uso interino — ver nota de escopo acima)
- `templates/template_apostila.typ`

## Procedimento

### 1. Montar as variáveis `-V`

Rode `python scripts/parametros_projeto.py <slug> --pdf-vars` — imprime os pares
`-V chave=valor` prontos (cor_primaria, cor_secundaria, cor_destaque, cor_texto,
cor_fundo, fonte_titulo, fonte_corpo), lidos de `brand/design-system-conexao.json`.
Também monte manualmente: `author=<nome da marca>`, `title=<nome do material>`,
`cta_final=<CTA extraído da seção de Fechamento>`.

### 2. Compilar via Pandoc + Typst (helper `pdf_typst.py`)

```python
import subprocess
from pathlib import Path
from scripts.pdf_typst import executar

slug_dir = Path("output") / slug
md = slug_dir / "pdf" / f"apostila_{slug}.md"
pdf = slug_dir / "pdf" / f"apostila_{slug}.pdf"

comando = [
    "pandoc", str(md),
    "--pdf-engine=typst",
    "--template", "templates/template_apostila.typ",
    "-o", str(pdf),
] + lista_de_flags_V  # geradas no passo 1

resultado = executar(comando, pdf, slug_dir, typst_bin="typst", timeout=300)
```

`pdf_typst.py` já resolve o problema de paths absolutos que o Typst rejeita no Windows
(gera o `.typ` intermediário dentro da pasta do projeto) — não reimplemente essa lógica.

### 3. Handoff

`scripts/validar-pdf.py <slug>` confirma tamanho/páginas/texto vetorial; `revisor-marca`
faz a checagem de fidelidade.

## Restrições

- Nunca hardcode cor/fonte no comando ou no template — tudo vem de
  `scripts/parametros_projeto.py --pdf-vars` via `-V`.
- Se a compilação falhar (Pandoc ou Typst com erro), tente uma correção estrutural
  óbvia no Markdown (ex.: tabela mal fechada) antes de escalar como falha — REGRA 4.
