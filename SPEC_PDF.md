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
  - Logo horizontal com texto branco centralizado horizontalmente no topo (`dy: 1.5cm`, `width: 4.5cm`) — omitido na **variante institucional** (ver abaixo).
  - **Bloco Único (endurecimento):** imagem do produto + título + parágrafo formam um bloco único de **11.5cm de largura** (`block(width: 11.5cm)`, centralizado em `center + horizon`).
  - **Imagem do produto em evidência:** `width: 100%`, `height: 8cm`, `fit: contain` — a imagem (quase quadrada por natureza) domina a composição; para a foto padrão 1600×1382 renderiza ~9.3×8.0cm.
  - **Variante institucional (`capa_variante=institucional`):** para materiais que falam da marca/da Fábrica em si — nunca de um produto específico (ex.: manual institucional para diretoria) — o mesmo bloco de destaque (11.5cm × 8cm, `fit: contain`) exibe `logo_imagem_hero` (normalmente o logo vertical, `Logo_Conexão_vertical_texto_branco.png`) em vez da imagem do produto, e o logo pequeno do topo é omitido (evita logo duplicado na mesma capa). Apostilas de kit **nunca** usam essa variante — a foto do produto é o que permite identificar de relance qual material é aquele num catálogo com múltiplos kits.
  - **Título Temático (endurecimento):** remete ao **tema do material extraído do texto-mãe** (`capa_titulo`, primeiro H1 da seção Abertura do Markdown — nunca o rótulo genérico "Guia de Treinamento..." nem o próprio rótulo estrutural da seção, ex.: "Abertura"), centralizado, **Caixa Alta**, **Inter 900**, preenchido com o gradiente dourado metálico, **24pt por padrão**, e **no máximo 2 linhas** — nenhuma linha com uma única palavra isolada.
    - **Enforcement determinístico (não só instrução de prompt):** `scripts/compilar-pdf.py` insere um espaço inseparável (NBSP) entre as 2 últimas palavras de `capa_titulo`/`capa_paragrafo` (impede a palavra final ficar isolada numa linha) e compila em loop reduzindo `capa_titulo_size` (variável do template, 24pt → mínimo 18pt, 1pt por vez) até o título medir ≤ 2 linhas sem linha órfã — medição via `scripts/validar-pdf.py::medir_titulo_capa` (mesma função usada no gate final, PyMuPDF sobre a página 1). O piso de 18pt nunca é violado porque é o mesmo limiar que `validar-pdf.py` usa para classificar um span como "título" (spans 9–16.5pt = parágrafo); um título abaixo de 18pt cairia numa zona cinzenta e seria reportado como "capa sem título".
  - **Parágrafo da Capa (endurecimento):** primeiro parágrafo da Abertura (`capa_paragrafo`), em **sub-bloco de 10cm** (garante ≥ 3 linhas equilibradas), **sem linha com palavra única isolada** (proporção altura/largura em `[0.12, 1.2]`) — mesma proteção de NBSP entre as 2 últimas palavras.
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
  - O Sumário (`#outline`) deve ocupar uma página exclusiva, seguido por `#pagebreak(weak: true)` — **fraco, não incondicional**: em apostilas de kit o corpo começa em heading nível 2 (sem quebra própria), então a quebra fraca garante a página nova; em documentos com heading nível 1 real logo em seguida (variante institucional, manuais com capítulos reais em `#`), o *show rule* do H1 já dispara sua própria quebra — as duas juntas sem `weak` produziam uma página em branco entre o Sumário e a primeira seção real (bug real encontrado ao gerar `manuais/MANUAL_EXECUTIVO.pdf`). A seção de abertura nunca deve dividir espaço com o Sumário.
- **Contracapa Symmetrical (Página Final):**
  - Design escuro premium unificado, com faixas e blobs, e todo o seu conteúdo (título, cta final, linha e assinatura) perfeitamente centralizado na horizontal e vertical (`center + horizon`).
  - **Logo da marca (endurecimento):** logo horizontal (mesmo arquivo `logo_imagem` usado na capa) posicionado discreto na base da página (`bottom + center`, acima da faixa dourada inferior), em tamanho reduzido (**2.4cm** de largura vs. 4.5cm na capa) para reforçar a marca sem competir com o bloco central de título/CTA/assinatura. Presente em ambas as variantes de capa.
- **Sem Hífens:** Títulos livres de hífens, substituindo-os por dois-pontos (:).

## Estrutura de conteúdo (default, ajustável pelo `brief_criativo.json`)

1. **Abertura** — estrutura obrigatória nesta ordem:
   - H1 temático (`capa_titulo` da capa): **máx. 34 caracteres / 6 palavras**, **sem hífens**,
     remetendo ao tema do texto-mãe (nunca o nome cru do produto).
   - Parágrafo de apoio (`capa_paragrafo` da capa): **120–160 caracteres**, frase de
     posicionamento do produto (nunca claim novo — REGRA 6).
   - Imagem do produto (`![](insumos/...)`).
   - Frase de posicionamento em negrito (`brief_criativo.mensagem_central`).
   - 1–2 parágrafos de contexto.
2. Problema — extraído do texto-base, nunca inventado.
3. Solução — como o produto/oferta resolve, linguagem objetiva.
4. Destaques — 4 a 6 pontos, mapeados de `brief_criativo.hierarquia_de_conteudo`.
5. Composição/especificações — se o texto-base trouxer itens/códigos/dimensões,
   apresentar em bloco escaneável (tabela).
6. Aplicação — em que casos usar / não usar, se a fonte indicar.
7. Fechamento — CTA (`cta_final` do template) + assinatura de marca (logo + nome).

## Estrutura de conteúdo por público (presets `/kit-completo-<publico>`)

Quando `config_projeto.preset_kit_completo` existir, o `diretor-de-arte` monta o
`mapeamento_por_material.pdf.secoes` com a variante correspondente abaixo (canônico em
`SPEC_COMANDOS.md`, seção `/kit-completo-consultor` — canônico dos 3 presets, com as
variantes em `/kit-completo-distribuidor` e `/kit-completo-cliente`). A capa (Flex Gold) e as seções
obrigatórias da Abertura são as mesmas; muda a estrutura interna do corpo:

| Público do preset | Seções do corpo (na ordem) |
|---|---|
| `consultores` | 1. O que é · 2. Para que serve · 3. Diferenciais técnicos/comerciais · 4. Como vender: SPIN (Situação, Problema, Implicação, Necessidade de solução) · 5. Contorno de objeções (objeções reais + resposta) · 6. Fechamento/CTA |
| `distribuidores` | 1. O que é · 2. Para que serve · 3. Diferenciais técnicos/comerciais · 4. Rentabilidade para o seu negócio · 5. Como vender: SPIN · 6. Contorno de objeções · 7. Fechamento/CTA |
| `clientes` | 1. O que é · 2. Para que serve · 3. Diferenciais técnicos · 4. Diferenciais para a prática clínica · 5. Por que utilizar este produto · 6. Fechamento/CTA |

**Regras de conteúdo (REGRA 6):** a técnica de SPIN e a estrutura pergunta→resposta de
objeções são fixas, mas o conteúdo (perguntas, objeções, respostas) é extraído do
texto-base — nunca inventado. Rentabilidade (margens/preços/condições) e diferenciais
para a prática clínica vêm exclusivamente do texto-base; ausência → seção registrada
como "faltante" no relatório final. Sem preset, vale a estrutura default de 7 seções
acima.

## Validação (`scripts/validar-pdf.py`)

- Arquivo existe e `size > 0`.
- `size < 5_000_000` bytes.
- Extração de texto (via `pdfminer`/equivalente) retorna conteúdo não vazio — confirma
  texto vetorial, não imagem.
- Contagem de páginas > 0 e coerente com o número de seções do brief.
- **Capa (endurecimento, via spans PyMuPDF da página 1):**
  - Título (spans ≥ 18pt): **máx. 2 linhas**; nenhuma linha com 1 palavra isolada;
    proporção altura/largura ≥ 0.18 (bloco); **não** contém nenhum rótulo/clichê da
    lista `TITULOS_BANIDOS` de `scripts/validar-pdf.py` (ex.: "guia de treinamento",
    "gambiarra" — endurecido depois que o mesmo clichê foi reaproveitado em 3
    regenerações consecutivas de um projeto real e reportado pelo operador como
    título "ridículo"; adicione novos termos à lista sempre que isso se repetir);
    **≥ 2 palavras significativas** do título presentes no texto-mãe (remete ao tema) —
    checado contra a **união de todos os `insumos/texto-mae*.txt` do projeto**
    (`scripts/validar-pdf.py::_coletar_textos_base`), nunca só o `texto_base` atual do
    `config_projeto.json`: um projeto pode ter passado por várias rodadas de
    `/gerar-pdf`, cada uma com um texto-base novo, e uma versão antiga (ex.: `pdf-v2`)
    foi legitimamente escrita contra o texto-base vigente naquela época — checar só o
    atual gera falso-positivo (achado real: `output/kit-inlego/pdf-v2`).
  - Parágrafo (spans 9–16.5pt): **mín. 2 linhas**; nenhuma linha com 1 palavra isolada;
    proporção altura/largura em **[0.12, 1.2]** (bloco quadrado).
- **Contracapa (`validar_contracapa_logo`):** se o PDF tiver mais de 1 página, a
  última página precisa ter pelo menos 1 imagem embutida (o logo da marca).

Exit 1 se qualquer critério falhar; `revisor-marca` decide se é caso de auto-correção
(REGRA 4) ou de reportar como faltante.
