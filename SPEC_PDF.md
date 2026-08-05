# SPEC_PDF.md — Contrato Técnico: PDF (Apostila)

Ver `SPEC.md` para o fluxo geral. Este documento cobre só o material `pdf`.

## Pipeline

`redator-apostila` (conteúdo em Markdown) → `compilador-pdf` (Pandoc → `.typ` via
`templates/template_apostila.typ` → `typst compile`, usando `scripts/pdf_typst.py`,
portado verbatim de `fabrica-de-livros`) → `scripts/validar-pdf.py`.

## Requisitos técnicos (Mosaico Conexão Premium)

- **Formato A4 Vetorial:** Orientação vertical, texto 100% vetorial e extraível (nunca imagem rasterizada de texto).
- **Peso Leve:** Arquivo final obrigatoriamente **abaixo de 5 MB** para compartilhabilidade.
- **Capa Premium Centralizada:**
  - Fundo escuro com vinheta radial (`#16213a` → `#0f172a`) e blobs decorativos de iluminação azul translúcidos (`rgba(20, 142, 203, 24%)`).
  - Faixas superior e inferior ultra-finas (**0.3cm**) preenchidas com o gradiente dourado de assinatura de 5 tons.
  - Logo horizontal com texto branco centralizado horizontalmente no topo (`dy: 1.5cm`, `width: 3.6cm`).
  - Imagem do produto transparente centralizada no centro geométrico da página (`dy: 4.3cm`, `width: 100%` / delimitada a `13.5cm`).
  - Título principal centralizado horizontalmente, em **Caixa Alta**, peso **Inter 900** (Black), preenchido com o gradiente dourado metálico, e com largura máxima de exatamente **`13.5cm`** (exatamente a mesma largura horizontal da imagem do produto).
  - Subtítulo de descrição com largura máxima também delimitada a `13.5cm` para simetria de bloco vertical perfeita.
  - Frase de direitos autorais ("2026 ©...") centralizada no rodapé com opacidade de 60%, em itálico e fonte pequena (`dy: -1.2cm`).
- **Cabeçalho Dinâmico (Páginas Internas):**
  - **Lado Esquerdo:** Título do material.
  - **Lado Direito:** Edição de preenchimento obrigatório pelo operador (ex: "1ª Edição" resgatado de `config_projeto.json`) acompanhado da Data Atualizada (`DD/MM/AAAA`).
  - Separado do conteúdo por uma linha divisória fina e sutil (`0.5pt`).
- **Respiro & Cores Internas (Mancha Gráfica):**
  - Fundo das páginas internas obrigatoriamente **branco** (`#ffffff`).
  - Texto principal em cor escura premium de altíssima legibilidade (`#1e293b`).
  - Títulos Nível 1 em dourado metálico (`cor-primaria`), e Títulos Nível 2 e 3 em azul/cinza escuro Conexão (`#0f172a` e `#1e293b`).
- **Separação Obrigatória do Sumário:**
  - O Sumário (`#outline`) deve ocupar uma página exclusiva, sendo seguido por um `#pagebreak()` obrigatório. A seção de abertura nunca deve dividir espaço com ele.
- **Contracapa Symmetrical (Página Final):**
  - Design escuro premium unificado, com faixas e blobs, e todo o seu conteúdo (título, cta final, linha e assinatura) perfeitamente centralizado na horizontal e vertical (`center + horizon`).
- **Sem Hífens:** Títulos livres de hífens, substituindo-os por dois-pontos (:).

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
