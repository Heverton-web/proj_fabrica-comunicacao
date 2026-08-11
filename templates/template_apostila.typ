// Template da Apostila (PDF) - Fabrica de Materiais de Comunicacao
// Adaptado de fabrica-de-livros/templates/template.typ (Pandoc + Typst).
//
// Variaveis Pandoc suportadas (-V chave=valor), preenchidas por
// `scripts/parametros_projeto.py <slug> --pdf-vars`:
//   title, subtitle, author            -> capa, folha de rosto e cabecalho (author = nome da marca)
//   cor_primaria, cor_secundaria       -> hex (#RRGGBB)
//   cor_destaque, cor_texto, cor_fundo -> hex (#RRGGBB)
//   fonte_titulo, fonte_corpo          -> familia tipografica (com fallback se nao instalada no Typst local)
//   logo_imagem                        -> PNG/SVG do logo (opcional; tambem usado, discreto, na contracapa)
//   imagem_produto                     -> PNG do produto (opcional)
//   capa_imagem                        -> PNG full-bleed como pagina-capa (opcional, sobrepoe capa gerada)
//   cta_final                          -> texto de chamada para acao na ultima pagina (opcional)
//   sem_capa_grafica                   -> "1" desativa capa grafica (fallback so-texto)
//   capa_titulo_size                   -> tamanho do titulo da capa (ex.: "24pt"; default 24pt).
//                                          scripts/compilar-pdf.py reduz este valor e recompila em
//                                          loop ate o titulo caber em <=2 linhas sem palavra isolada
//                                          (medido por scripts/validar-pdf.py::medir_titulo_capa) —
//                                          mesmo papel do ajuste de font-size via JS nos templates
//                                          de arte (SPEC_ARTE.md), so que resolvido no lado Python.

#set document(
  title: "$title$",
  author: "$author$",
  date: datetime.today(),
)

// ── Paleta e tipografia da marca (parametrizadas, nunca hardcoded) ─
#let cor-primaria    = rgb("$if(cor_primaria)$$cor_primaria$$else$#c9a655$endif$")
#let cor-secundaria  = rgb("$if(cor_secundaria)$$cor_secundaria$$else$#94a3b8$endif$")
#let cor-destaque    = rgb("$if(cor_destaque)$$cor_destaque$$else$#e8d48b$endif$")
#let cor-texto       = rgb("$if(cor_texto)$$cor_texto$$else$#f8fafc$endif$")
#let cor-fundo       = rgb("$if(cor_fundo)$$cor_fundo$$else$#0f172a$endif$")
#let fonte-titulo    = "$if(fonte_titulo)$$fonte_titulo$$else$Arial$endif$"
#let fonte-corpo     = "$if(fonte_corpo)$$fonte_corpo$$else$Arial$endif$"

// Para o conteúdo interno, o background das páginas deve ser branco (#ffffff)
// e o texto principal em cor escura (#1e293b) para alta legibilidade.
#let cor-fundo-conteudo = rgb("#ffffff")
#let cor-texto-conteudo = rgb("#1e293b")

// ── Gradientes e Blobs Premium (Conexão Gold — vindos de templates/arte-1080x1920.html) ──
#let gradiente-dourado = gradient.linear(
  rgb("#caa146"),
  rgb("#fff8d6"),
  rgb("#e5c158"),
  rgb("#fff3ad"),
  rgb("#caa146"),
  angle: 45deg
)

#let bg-radial = gradient.radial(
  rgb("#16213a"), // var(--bg-glow)
  rgb("#0f172a"), // var(--bg)
  center: (50%, 15%),
  radius: 80%
)

#let glow-1 = gradient.radial(
  rgb(20, 142, 203, 24%),
  rgb(20, 142, 203, 0%),
  radius: 50%
)

#let glow-2 = gradient.radial(
  rgb(20, 142, 203, 14%),
  rgb(20, 142, 203, 0%),
  radius: 50%
)


// ── Pagina, tipografia e paragrafos ────────────────────────────────
#set page(
  paper: "a4",
  margin: (top: 3cm, bottom: 2cm, left: 3cm, right: 2cm),
  fill: cor-fundo-conteudo, // Fundo branco para as páginas de conteúdo
  header: context {
    if counter(page).get().first() > 1 {
      set text(size: 8.5pt, fill: rgb("#64748b"), font: fonte-corpo)
      let data_atual = datetime.today().display("[day]/[month]/[year]")
      let edicao_texto = "$if(edicao)$$edicao$$else$1ª Edição$endif$"
      grid(
        columns: (1fr, auto),
        align(left)[$title$],
        align(right)[#edicao_texto | #data_atual]
      )
      v(0.2cm)
      line(length: 100%, stroke: 0.5pt + rgb("#e2e8f0"))
    }
  },
  footer: context {
    if counter(page).get().first() > 1 {
      set text(size: 9pt, fill: rgb("#64748b"), font: fonte-corpo)
      align(center, [#counter(page).display("1") de #counter(page).final().first()])
    }
  },
)

#set text(
  font: (fonte-corpo, "Liberation Sans", "Arial"),
  fill: cor-texto-conteudo, // Texto escuro para o conteúdo
  size: 11.5pt,
  lang: "pt",
  region: "BR",
)

#set par(
  justify: true,
  leading: 0.75em,
  first-line-indent: 0cm,
)

// Definicao do horizontal rule (Pandoc gera #horizontalrule como texto)
#let horizontalrule = {
  v(1em)
  line(length: 100%, stroke: 0.5pt + rgb("#e2e8f0"))
  v(1em)
}

// Estilo de blocos de codigo
#show raw.where(block: true): it => block(
  width: 100%,
  fill: rgb("#f1f5f9"),
  inset: 8pt,
  radius: 4pt,
)[#set text(fill: rgb("#0f172a")); #it]
#show raw.where(block: false): it => box(
  fill: rgb("#f1f5f9"),
  inset: (x: 3pt, y: 0pt),
  outset: (y: 3pt),
  radius: 2pt,
)[#set text(fill: rgb("#0f172a")); #it]

// Figuras (diagramas Mermaid renderizados) — nunca extrapolam a mancha grafica
#set image(width: 88%, fit: "contain")
#show figure: it => {
  set par(first-line-indent: 0cm)
  v(0.6cm)
  align(center, it)
  v(0.6cm)
}
#show figure.caption: it => {
  set text(size: 10pt, fill: rgb("#64748b"))
  it
}

// Titulos - nivel 1
#show heading.where(level: 1): it => {
  set par(first-line-indent: 0cm)
  pagebreak()
  set text(font: fonte-titulo, size: 18pt, weight: "bold", fill: cor-primaria)
  v(2cm)
  it
  v(0.2cm)
  line(length: 30%, stroke: 2pt + cor-primaria)
  v(1cm)
}

// Titulos - nivel 2 (cor escura de alta legibilidade em fundo branco)
#show heading.where(level: 2): it => {
  set text(font: fonte-titulo, size: 14pt, weight: "bold", fill: rgb("#0f172a"))
  set par(first-line-indent: 0cm)
  v(1cm)
  it
  v(0.5cm)
}

// Titulos - nivel 3 (cor escura de alta legibilidade em fundo branco)
#show heading.where(level: 3): it => {
  set text(font: fonte-titulo, size: 12pt, weight: "bold", fill: rgb("#1e293b"))
  set par(first-line-indent: 0cm)
  v(0.75cm)
  it
  v(0.5cm)
}

#let capa-grafica-ativa = "$sem_capa_grafica$" != "1"

// ── CAPA ────────────────────────────────────────────────────────────
#if capa-grafica-ativa {
  $if(capa_imagem)$
  page(fill: rgb("#ffffff"), margin: 0cm, header: none, footer: none, numbering: none)[
    #image("$capa_imagem$", width: 100%, height: 100%, fit: "cover")
  ]
  $else$
  page(fill: bg-radial, margin: 0cm, header: none, footer: none, numbering: none)[
    #set par(first-line-indent: 0cm, justify: false, leading: 0.55em)
    
    // Blobs de fundo (glow-1 no canto superior direito, glow-2 no canto inferior esquerdo)
    #place(top + right, dx: 4cm, dy: -4cm, circle(radius: 10cm, fill: glow-1))
    #place(bottom + left, dx: -4cm, dy: 4cm, circle(radius: 8cm, fill: glow-2))

    // Faixas douradas superior e inferior mais finas (0.3cm) em gradiente dourado
    #place(top + left, rect(width: 100%, height: 0.3cm, fill: gradiente-dourado))
    #place(bottom + left, rect(width: 100%, height: 0.3cm, fill: gradiente-dourado))

    // Logo horizontal centralizado no topo (width 3.6cm)
    $if(logo_imagem)$
    #place(top + center, dy: 1.5cm, image("$logo_imagem$", width: 3.6cm))
    $else$
    #place(top + center, dy: 1.5cm, image("pdf/assets/logos/Logo_Conexão_horizontal_texto_branco.png", width: 3.6cm))
    $endif$

    // Bloco Único de Conteúdo: Imagem do produto, Título e Parágrafo explicativo
    // Todos centralizados horizontalmente e verticalmente (center + horizon)
    // Bloco de 11.5cm: a imagem do produto em evidência (width 100% / height 8cm)
    // domina a composição; título em no máximo 2 linhas e parágrafo em bloco
    // (10cm), sem linhas com uma única palavra isolada (SPEC_PDF).
    #place(center + horizon, block(width: 11.5cm)[
      #set align(center)
      
      // Imagem do produto em evidência — ocupa quase toda a largura do bloco
      $if(imagem_produto)$
      #image("$imagem_produto$", width: 100%, height: 8cm, fit: "contain")
      $else$
      #image("insumos/kit_start_flex_frontal.png", width: 100%, height: 8cm, fit: "contain")
      $endif$

      #v(0.6cm) // Espaçamento elegante entre a imagem e o título

      // Título do material (CAIXA ALTA, Inter 900, 24pt por padrão) — remete ao
      // tema do material (capa_titulo da seção Abertura); em 11.5cm cabe no
      // máximo 2 linhas. `capa_titulo_size` é reduzido por compilar-pdf.py em
      // loop até o título medir <=2 linhas sem palavra isolada (ver cabeçalho).
      #text(font: "Inter", size: $if(capa_titulo_size)$$capa_titulo_size$$else$24pt$endif$, weight: 900, fill: gradiente-dourado)[#upper[$if(capa_titulo)$$capa_titulo$$else$$title$$endif$]]
      
      #v(0.4cm) // Espaçamento elegante entre o título e o parágrafo

      // Parágrafo explicativo (parágrafo de apoio da Abertura; sub-bloco de 10cm
      // garante >= 3 linhas equilibradas — bloco quadrado, sem palavra isolada)
      #block(width: 10cm)[
        #text(font: fonte-corpo, size: 11.5pt, fill: rgb("#e2e8f0"))[
          $if(capa_paragrafo)$
          $capa_paragrafo$
          $else$
          $if(subtitle)$
          $subtitle$
          $else$
          Guia de treinamento técnico e de vendas para o consultor Conexão.
          $endif$
          $endif$
        ]
      ]
    ])

    // No rodapé acima da faixa dourada o texto de direitos autorais (centralizado)
    #place(bottom + center, dy: -1.2cm, block(width: 17cm)[
      #set align(center)
      #text(font: fonte-corpo, size: 8.5pt, style: "italic", fill: rgb(255, 255, 255, 60%))[
        2026 © Todos os direitos reservados a Conexão Sistemas de Próteses
      ]
    ])
  ]
  $endif$
}

// ── SUMARIO ───────────────────────────────────────────────────────
#outline(title: [Sumário], indent: 1.5cm, depth: 3)
#pagebreak()

// ── CONTEUDO PRINCIPAL ────────────────────────────────────────────
$body$

// ── PAGINA FINAL: CTA + assinatura da marca ───────────────────────
$if(cta_final)$
#if capa-grafica-ativa {
  page(fill: bg-radial, margin: 0cm, header: none, footer: none, numbering: none)[
    #set par(first-line-indent: 0cm, justify: false, leading: 0.7em)
    
    // Blobs de fundo para a contracapa
    #place(top + right, dx: 4cm, dy: -4cm, circle(radius: 10cm, fill: glow-1))
    #place(bottom + left, dx: -4cm, dy: 4cm, circle(radius: 8cm, fill: glow-2))

    // Faixas douradas superior e inferior mais finas (0.3cm)
    #place(top + left, rect(width: 100%, height: 0.3cm, fill: gradiente-dourado))
    #place(bottom + left, rect(width: 100%, height: 0.3cm, fill: gradiente-dourado))

    #place(center + horizon, block(width: 16cm)[
      #set align(center)
      #text(font: "Inter", size: 22pt, weight: 900, fill: gradiente-dourado)[#upper[$if(capa_titulo)$$capa_titulo$$else$$title$$endif$]]
      #v(1cm)
      #text(font: fonte-corpo, size: 13pt, fill: rgb("#f8fafc"))[$cta_final$]
      #v(1.5cm)
      #align(center)[#line(length: 5cm, stroke: 2pt + gradiente-dourado)]
      #v(0.6cm)
      #text(font: fonte-corpo, size: 12pt, weight: "bold", fill: rgb("#f8fafc"))[$author$]
    ])

    // Logo horizontal discreto no rodapé da contracapa — reforça a marca sem
    // competir com o bloco central (título + CTA + assinatura). Mesma logo da
    // capa, em tamanho menor (2.4cm vs 3.6cm), posicionado acima da faixa
    // dourada inferior.
    $if(logo_imagem)$
    #place(bottom + center, dy: -1.6cm, image("$logo_imagem$", width: 2.4cm))
    $endif$
  ]
} else {
  pagebreak()
}
$else$
#pagebreak()
$endif$
