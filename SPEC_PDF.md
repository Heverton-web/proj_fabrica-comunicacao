# SPEC_PDF.md — Contrato Técnico: PDF (Apostila)

Ver `SPEC.md` para o fluxo geral. Este documento cobre só o material `pdf`.

## Pipeline

`redator-apostila` (conteúdo em Markdown) → `compilador-pdf` (Pandoc → `.typ` via
`templates/template_apostila.typ` → `typst compile`, usando `scripts/pdf_typst.py`,
portado verbatim de `fabrica-de-livros`) → `scripts/validar-pdf.py`.

## Requisitos técnicos (mirror do exemplo Conexão/Kit Master Flex)

- Formato A4, vertical, texto vetorial e selecionável — **nunca** imagem rasterizada
  de texto.
- Peso final **abaixo de 5 MB** (limite prático de envio por WhatsApp/e-mail).
- Corpo de texto nunca abaixo de 11pt; títulos com contraste forte contra o fundo.
- Margens seguras para impressão (herdadas do template: 3/2/3/2cm).
- Nome do arquivo: `apostila_<slug>.pdf`, salvo em `output/<slug>/pdf/`.
- Cores/fontes injetadas via `-V` a partir do design system fixo (`brand/design-system-conexao.json`,
  uso interino até que regras próprias de PDF sejam definidas — ver nota em `compilador-pdf`) — nunca hardcoded no
  `.typ` (diferença crítica em relação ao template fixo de `fabrica-de-livros`).

## Estrutura de conteúdo (default, ajustável pelo `brief_criativo.json`)

1. Abertura — nome do material/produto + frase de posicionamento (`brief_criativo.mensagem_central`).
2. Problema — extraído do texto-base, nunca inventado.
3. Solução — como o produto/oferta resolve, linguagem objetiva.
4. Destaques — 4 a 6 pontos, mapeados de `brief_criativo.hierarquia_de_conteudo`.
5. Composição/especificações — se o texto-base trouxer itens/códigos/dimensões,
   apresentar em bloco escaneável (tabela).
6. Aplicação — em que casos usar / não usar, se a fonte indicar.
7. Fechamento — CTA (`cta_final` do template) + assinatura de marca (logo + nome).

## Validação (`scripts/validar-pdf.py`)

- Arquivo existe e `size > 0`.
- `size < 5_000_000` bytes.
- Extração de texto (via `pdfminer`/equivalente) retorna conteúdo não vazio — confirma
  texto vetorial, não imagem.
- Contagem de páginas > 0 e coerente com o número de seções do brief.

Exit 1 se qualquer critério falhar; `revisor-marca` decide se é caso de auto-correção
(REGRA 4) ou de reportar como faltante.
