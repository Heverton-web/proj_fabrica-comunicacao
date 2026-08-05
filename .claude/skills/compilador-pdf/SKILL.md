---
name: compilador-pdf
description: Fase 3 da Fábrica de Materiais de Comunicação — compila apostila_<slug>.md em PDF via Pandoc + Typst, usando templates/template_apostila.typ de padrão premium (Mosaico Conexão Premium / Flex Gold) de forma totalmente automatizada. Use depois de redator-apostila, antes de validar-pdf.py/revisor-marca.
---

# Skill: Compilador de PDF

Você compila o Markdown da apostila em PDF final aplicando as regras premium de diagramação (Mosaico Conexão Premium / Flex Gold).

O PDF ganhou regras visuais definitivas (estilo "Flex Gold"): capa com fundo escuro e blobs, faixas douradas em gradiente metálico, título em caixa alta com Inter 900 (Black), logotipo horizontal de marca e imagem do produto perfeitamente centralizados, cabeçalho dinâmico (título à esquerda, edição e data à direita) e conteúdo interno com fundo branco para leitura confortável de alta definição.

Se precisar de técnicas auxiliares de manipulação de PDF fora do que Pandoc+Typst cobre, consulte o skill genérico `pdf` do catálogo.

## Entrada

- `output/<slug>/pdf/apostila_<slug>.md`
- `brand/design-system-conexao.json`
- `templates/template_apostila.typ`

## Procedimento

### 1. Executar a Compilação via `scripts/compilar-pdf.py`

Toda compilação de PDF do projeto foi centralizada de forma robusta e automatizada no script utilitário **`scripts/compilar-pdf.py`**. Ele gerencia o carregamento de variáveis do design system, metadados do projeto, edição de escolha do operador, imagem do produto e executa o processamento. Invoque o script informando o slug:
```bash
python scripts/compilar-pdf.py <slug>
```

O script extrai dinamicamente as variáveis de marca (`--pdf-vars`), resgata a edição do `config_projeto.json` e repassa para o Pandoc e Typst as flags `-V` de forma perfeitamente separada e argv-normalizada (evitando bugs de leitura silenciosa de variáveis), compilando o arquivo final com integridade máxima de design e cores.

### 2. Handoff e Validação

`scripts/validar-pdf.py <slug>` confirma tamanho/páginas/texto vetorial; `revisor-marca` faz a checagem de fidelidade de conteúdo e de marca.

## Restrições

- Nunca hardcode cor/fonte no comando ou no template — tudo vem de `scripts/parametros_projeto.py --pdf-vars` via `-V`.
- Se a compilação falhar (Pandoc ou Typst com erro), tente uma correção estrutural óbvia no Markdown (ex.: tabela mal fechada) antes de escalar como falha — REGRA 4.
