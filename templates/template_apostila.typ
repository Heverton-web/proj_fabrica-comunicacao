// Template da Apostila (PDF) - Fabrica de Materiais de Comunicacao
// Adaptado de fabrica-de-livros/templates/template.typ (Pandoc + Typst).
// Diferenca-chave: a fabrica de livros tem UMA identidade visual fixa (6 paletas
// hardcoded). Aqui toda cor/fonte vem de -V, nunca hardcoded - por ora (INTERIM,
// ver .claude/skills/compilador-pdf/SKILL.md) as -V usam o mesmo design system fixo
// brand/design-system-conexao.json dos outros materiais, ate que regras proprias de
// PDF ("Flex Gold") sejam desenhadas.
//
// Variaveis Pandoc suportadas (-V chave=valor), preenchidas por
// `scripts/parametros_projeto.py <slug> --pdf-vars`:
//   title, subtitle, author            -> capa, folha de rosto e cabecalho (author = nome da marca)
//   cor_primaria, cor_secundaria       -> hex (#RRGGBB)
//   cor_destaque, cor_texto, cor_fundo -> hex (#RRGGBB)
//   fonte_titulo, fonte_corpo          -> familia tipografica (com fallback se nao instalada no Typst local)
//   logo_imagem                        -> PNG/SVG do logo (opcional)
//   capa_imagem                        -> PNG full-bleed como pagina-capa (opcional, sobrepoe capa gerada)
//   cta_final                          -> texto de chamada para acao na ultima pagina (opcional)
//   sem_capa_grafica                   -> "1" desativa capa grafica (fallback so-texto)

#set document(
  title: "$title$",
  author: "$author$",
  date: datetime.today(),
)

// ── Paleta e tipografia da marca (parametrizadas, nunca hardcoded) ─
#let cor-primaria    = rgb("$if(cor_primaria)$$cor_primaria$$else$#1b2559$endif$")
#let cor-secundaria  = rgb("$if(cor_secundaria)$$cor_secundaria$$else$#3d55a5$endif$")
#let cor-destaque    = rgb("$if(cor_destaque)$$cor_destaque$$else$#f0b429$endif$")
#let cor-texto       = rgb("$if(cor_texto)$$cor_texto$$else$#1a1a1a$endif$")
#let cor-fundo       = rgb("$if(cor_fundo)$$cor_fundo$$else$#ffffff$endif$")
#let fonte-titulo    = "$if(fonte_titulo)$$fonte_titulo$$else$Arial$endif$"
#let fonte-corpo     = "$if(fonte_corpo)$$fonte_corpo$$else$Arial$endif$"

// ── Pagina, tipografia e paragrafos ────────────────────────────────
// fill: cor-fundo garante que marcas de tema escuro (fundo != branco) nao
// acabem com texto claro sobre pagina branca do Typst - o corpo da apostila
// precisa respeitar cor_fundo (-V), nao so a capa/contracapa.
#set page(
  paper: "a4",
  margin: (top: 3cm, bottom: 2cm, left: 3cm, right: 2cm),
  fill: cor-fundo,
  header: context {
    if counter(page).get().first() > 1 {
      set text(size: 9pt, fill: gray, font: fonte-corpo)
      align(center, "$title$")
    }
  },
  footer: context {
    set text(size: 9pt, font: fonte-corpo)
    align(center, [#counter(page).display("1") de #counter(page).final().first()])
  },
)

#set text(
  font: (fonte-corpo, "Liberation Sans", "Arial"),
  fill: cor-texto,
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
  line(length: 100%, stroke: 0.5pt + gray)
  v(1em)
}

// Estilo de blocos de codigo (apostilas tecnicas podem trazer snippets)
// Blocos de codigo mantem fundo claro fixo por convencao (estilo "terminal
// claro") independente do tema da marca - por isso o texto interno precisa de
// cor fixa escura tambem, nunca cor-texto: numa marca de tema escuro,
// cor-texto e claro e ficaria ilegivel sobre este fundo claro.
#show raw.where(block: true): it => block(
  width: 100%,
  fill: luma(240),
  inset: 8pt,
  radius: 4pt,
)[#set text(fill: luma(20)); #it]
#show raw.where(block: false): it => box(
  fill: luma(240),
  inset: (x: 3pt, y: 0pt),
  outset: (y: 3pt),
  radius: 2pt,
)[#set text(fill: luma(20)); #it]

// Figuras (diagramas Mermaid renderizados) — nunca extrapolam a mancha grafica
#set image(width: 88%, fit: "contain")
#show figure: it => {
  set par(first-line-indent: 0cm)
  v(0.6cm)
  align(center, it)
  v(0.6cm)
}
#show figure.caption: it => {
  set text(size: 10pt, fill: luma(70))
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
  line(length: 30%, stroke: 2pt + cor-destaque)
  v(1cm)
}

// Titulos - nivel 2
#show heading.where(level: 2): it => {
  set text(font: fonte-titulo, size: 14pt, weight: "bold", fill: cor-secundaria)
  set par(first-line-indent: 0cm)
  v(1cm)
  it
  v(0.5cm)
}

// Titulos - nivel 3
#show heading.where(level: 3): it => {
  set text(font: fonte-titulo, size: 12pt, weight: "bold")
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
  page(fill: cor-primaria, margin: 0cm, header: none, footer: none, numbering: none)[
    #set par(first-line-indent: 0cm, justify: false, leading: 0.55em)
    #place(top + left, rect(width: 100%, height: 1.2cm, fill: cor-destaque))
    #place(bottom + left, rect(width: 100%, height: 4.5cm, fill: cor-secundaria))
    #place(bottom + left, dy: -4.5cm, rect(width: 100%, height: 0.15cm, fill: cor-destaque))

    $if(logo_imagem)$
    #place(top + left, dx: 2.5cm, dy: 2cm, image("$logo_imagem$", width: 3.5cm))
    $endif$

    #place(top + left, dx: 2.5cm, dy: 6.5cm, block(width: 14.5cm)[
      #text(font: fonte-titulo, size: 32pt, weight: "bold", fill: white)[$title$]
      $if(subtitle)$
      #v(0.8cm)
      #line(length: 5cm, stroke: 3pt + cor-destaque)
      #v(0.6cm)
      #text(font: fonte-corpo, size: 15pt, fill: cor-destaque)[$subtitle$]
      $endif$
    ])

    #place(bottom + left, dx: 2.5cm, dy: -1.6cm, block(width: 15cm)[
      #text(font: fonte-corpo, size: 14pt, weight: "bold", fill: white)[$author$]
      #v(0.2cm)
      #text(font: fonte-corpo, size: 9pt, fill: luma(230))[#datetime.today().display("[year]")]
    ])
  ]
  $endif$
}

// ── SUMARIO ───────────────────────────────────────────────────────
#outline(title: [Sumário], indent: 1.5cm, depth: 3)

// ── CONTEUDO PRINCIPAL ────────────────────────────────────────────
$body$

// ── PAGINA FINAL: CTA + assinatura da marca ───────────────────────
$if(cta_final)$
#if capa-grafica-ativa {
  page(fill: cor-primaria, margin: 0cm, header: none, footer: none, numbering: none)[
    #set par(first-line-indent: 0cm, justify: true, leading: 0.7em)
    #place(top + left, rect(width: 100%, height: 1.2cm, fill: cor-destaque))
    #place(top + left, dx: 2.5cm, dy: 4cm, block(width: 14.5cm)[
      #text(font: fonte-titulo, size: 18pt, weight: "bold", fill: cor-destaque)[$title$]
      #v(1cm)
      #text(font: fonte-corpo, size: 12pt, fill: white)[$cta_final$]
      #v(1.2cm)
      #line(length: 4cm, stroke: 2pt + cor-destaque)
      #v(0.5cm)
      #text(font: fonte-corpo, size: 11pt, weight: "bold", fill: white)[$author$]
    ])
  ]
} else {
  pagebreak()
}
$else$
#pagebreak()
$endif$
