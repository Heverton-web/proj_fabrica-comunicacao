---
name: aplicador-marca-conexao
description: Skill ultra-personalizada e única fonte de verdade de como o design system fixo da Conexão (brand/design-system-conexao.json) se materializa em cada tipo de material — landing-page, apresentacao e arte (o PDF NÃO usa esta skill ainda, segue regras próprias a definir depois). Use dentro de compilador-html e compilador-arte, sempre antes de gerar qualquer HTML/CSS — nunca improvise cor, fonte ou componente fora do que está aqui. Inclui fundo em gradiente, título em gradiente de texto, glows decorativos e motion — nunca entregue fundo chapado/título sólido/estático, isso é considerado design pobre e será rejeitado.
---

# Skill: Aplicador da Marca Conexão

Você é o guardião visual da fábrica: a única skill autorizada a decidir *como* um
componente (fundo, botão, badge, card, título, input, transição) se desenha em cada
material. Nenhum `compilador-*` deve inventar um padrão visual novo — se o componente
que você precisa não está descrito aqui, pare e trate como faltante (REGRA 6 do
`CLAUDE.md`), não invente um estilo ad-hoc. Mas também não entregue **menos** do que
aqui está descrito: fundo chapado, título em cor sólida ou material sem nenhuma
transição são defeitos, não economia de esforço — foram rejeitados explicitamente pelo
operador numa rodada anterior por ficarem "pobres" de design.

Diferente do fluxo antigo (per-projeto, `design_tokens.json` gerado pelo
`analista-insumos`), o design system agora é **fixo** para todo projeto, lido direto de
`brand/design-system-conexao.json`. `analista-insumos`/`diretor-de-arte` não extraem
mais marca — só processam texto-base e imagens.

## Fonte de verdade

Leia `brand/design-system-conexao.json` por completo antes de gerar qualquer HTML/CSS.
Não copie os valores abaixo de memória — se o arquivo mudar, este SKILL.md pode ficar
desatualizado; o JSON é sempre a autoridade.

## Fontes — carregamento obrigatório

Todo material HTML (landing-page, apresentacao, arte-*) precisa copiar os arquivos de
`templates/fonts/*.woff2` para `output/<slug>/<tipo>/assets/fonts/` e declarar:

```css
@font-face { font-family: 'Inter'; font-weight: 300; src: url('assets/fonts/inter-300.woff2') format('woff2'); font-display: swap; }
@font-face { font-family: 'Inter'; font-weight: 400; src: url('assets/fonts/inter-400.woff2') format('woff2'); font-display: swap; }
@font-face { font-family: 'Inter'; font-weight: 600; src: url('assets/fonts/inter-600.woff2') format('woff2'); font-display: swap; }
@font-face { font-family: 'Inter'; font-weight: 700; src: url('assets/fonts/inter-700.woff2') format('woff2'); font-display: swap; }
@font-face { font-family: 'Inter'; font-weight: 900; src: url('assets/fonts/inter-900.woff2') format('woff2'); font-display: swap; }
```

**Atualização registrada pelo operador:** títulos e corpo usam a mesma família —
Inter, pesos 300/400/600/700/900 (registro literal do operador: link Google Fonts
`family=Inter:wght@300;400;600;700;900`). Poppins **deixou de ser a fonte de título** —
segue como fonte de marca aprovada em arquivo (`templates/fonts/poppins-*.woff2`), mas
não entra mais nos stacks ativos de `--fonte-titulo`/`--fonte-corpo` a menos que o
operador peça de volta.

**Nunca** aponte para um CDN de fonte (Google Fonts via `<link>`/`@import`) — viola a
regra de material autocontido (`SPEC_HTML.md`/`SPEC_ARTE.md`) e quebra offline, mesmo
quando o operador cola um link de CDN como referência (é o registro da fonte/pesos
desejados, não uma instrução para linkar CDN — sempre auto-hospedar via
`templates/fonts/*.woff2`). Roboto não precisa de `@font-face`: é fonte de marca
aprovada e está instalada no ambiente local (confirmado via `typst fonts`), funciona
como fallback de sistema seguro caso os arquivos `.woff2` não copiem por algum motivo —
mas isso deve ser tratado como falha a corrigir (REGRA 4), não uma muleta aceitável de
longo prazo.

`fonte_titulo` = `Inter, Roboto, sans-serif` (peso 900 em H1, peso 700 em H2) ·
`fonte_corpo` = `Inter, Roboto, sans-serif` (peso 400 corpo, peso 300 subtítulo/texto
de apoio, peso 600 ênfase).

## Bloco `:root` obrigatório em todo material

```css
:root {
  --bg: #0f172a;
  --bg-deep: #0a0f1e;     /* tom mais escuro que --bg, usado nas bordas da vinheta */
  --bg-glow: #16213a;     /* tom mais claro que --bg, usado no centro da vinheta */
  --surface: #1e293b;
  --surface-hover: #334155;
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --border-subtle: rgba(248, 250, 252, 0.08);
  --accent: #c9a655;
  --accent-hover: #d4b366;
  --gradiente-assinatura: linear-gradient(135deg, #c9a655 0%, #e8d48b 40%, #a8873a 70%, #c9a655 100%);
  --glow-blue: #148ecb;   /* uso exclusivo: glows decorativos de fundo, nunca texto/botao/card */
  --fonte-titulo: 'Inter', 'Roboto', sans-serif;
  --fonte-corpo: 'Inter', 'Roboto', sans-serif;
  --ease-premium: cubic-bezier(0.32, 0.72, 0, 1); /* toda transição usa esta curva, nunca linear/ease-in-out padrão */
}
```

Todo o resto do CSS usa `var(--*)` — nunca hex solto fora deste bloco (é o que
`scripts/validar-design-tokens.py` confirma).

## Fundo — SEMPRE gradiente/vinheta, NUNCA chapado

Fundo chapado (`background: var(--bg)` sozinho) foi rejeitado explicitamente pelo
operador. Todo material usa uma vinheta radial sutil: mais clara no centro/topo, mais
escura nas bordas — o mesmo espírito das peças de referência (capa Master Flex, tela de
login), nunca um bloco de cor único.

```css
body {
  background:
    radial-gradient(ellipse 70% 50% at 50% 20%, var(--bg-glow) 0%, transparent 60%),
    radial-gradient(ellipse 90% 70% at 50% 100%, var(--bg-deep) 0%, var(--bg) 50%);
}
```
Em página que rola (landing-page), coloque essa vinheta num elemento `position: fixed;
inset: 0; z-index: -2;` separado do `body`, para o gradiente não se repetir/deslocar
com o scroll.

### Glows decorativos — azul `#148ecb` (`--glow-blue`), não dourado

O operador testou glows dourados e achou "murchos"/pouco definidos contra os acentos
dourados existentes — o dourado já está em uso nos títulos/CTAs, então o glow ambiente
usa um azul dedicado (`#148ecb`, token `cores.glowBlue` em
`brand/design-system-conexao.json`) para criar profundidade e contraste de temperatura
(ambiente frio + acentos quentes), não para competir com o dourado. Esse azul é
exclusivo para este uso — nunca em texto, botão ou superfície de card. **Nunca volte a
usar dourado nos glows de fundo** sem que o operador peça de novo — é uma decisão de
design já testada e revertida (dourado → cinza-azulado → azul dedicado).

```css
:root { --glow-blue: #148ecb; /* junto com os demais tokens do bloco :root */ }

.glow { position: fixed; border-radius: 50%; pointer-events: none; filter: blur(90px); z-index: -1; }
.glow-1 { width: 34vw; height: 34vw; top: -8vw; right: -8vw; background: radial-gradient(circle, rgba(20,142,203,0.20), transparent 70%); }
.glow-2 { width: 28vw; height: 28vw; bottom: 10vh; left: -8vw; background: radial-gradient(circle, rgba(20,142,203,0.12), transparent 70%); }
```
Em `arte-*` (canvas fixo, sem scroll) use `position: absolute` em vez de `fixed`, com
tamanhos em `px` proporcionais ao canvas em vez de `vw`. Sempre `pointer-events: none`,
sempre `filter: blur()` pesado (70-100px) — nunca um glow "duro"/sem blur.

## Título — SEMPRE gradiente de texto, NUNCA cor sólida

Título sólido também foi rejeitado — a assinatura visual da marca (capa "MASTER FLEX")
é o texto em gradiente metálico dourado, não cor chapada. Isso vale em **todo**
material, incluindo HTML (não é mais exclusivo do PDF/"Flex Gold"):

```css
h1 { font-family: var(--fonte-titulo); font-weight: 900; }
h2 { font-family: var(--fonte-titulo); font-weight: 700; }
h1, h2 {
  background: var(--gradiente-assinatura);
  background-clip: text; -webkit-background-clip: text; color: transparent;
}
```
Aplique em headlines de hero, títulos de seção e títulos de slide. Texto de apoio
(subheadline, parágrafo, bullet) continua em `var(--text-main)`/`var(--text-muted)` —
gradiente é só para o título, nunca para o corpo (perde legibilidade em texto longo).

## Componentes — padrões obrigatórios (não são sugestões)

### Botão/CTA primário
Sempre o gradiente de assinatura, nunca `accent` chapado — o produto real (tela de
login) usa gradiente no botão principal, não cor sólida. Hover/active com física real
(scale + shadow), nunca troca instantânea de cor.

```css
.btn-primario {
  background: var(--gradiente-assinatura);
  color: var(--bg);
  font-family: var(--fonte-corpo); font-weight: 700;
  border: none; border-radius: 999px;
  padding: 0.9rem 2rem;
  transition: transform 420ms var(--ease-premium), box-shadow 420ms var(--ease-premium);
}
.btn-primario:hover { transform: translateY(-2px) scale(1.02); box-shadow: 0 12px 32px -8px rgba(201,166,85,0.45); }
.btn-primario:active { transform: scale(0.98); }
```

### Badge / pill
Para specs, selos institucionais, tags de status/contexto (ex.: "USO INTERNO").

```css
.badge {
  display: inline-block;
  border: 1px solid var(--accent);
  border-radius: 999px;
  padding: 0.35rem 1rem;
  font-size: 0.8rem; font-weight: 700;
  letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--accent);
  background: transparent;
}
.badge.preenchida { background: color-mix(in srgb, var(--accent) 15%, transparent); }
```

### Card / painel ("double-bezel")
Nunca um card flat sem relevo — sempre com sombra interna sutil + hover com leve
elevação, para dar sensação de painel técnico/hardware, não de texto solto.

```css
.card {
  background: var(--surface);
  border: 1px solid var(--border-subtle);
  border-radius: 1rem;
  padding: 1.6rem;
  box-shadow: inset 0 1px 1px rgba(255,255,255,0.04);
  transition: transform 420ms var(--ease-premium), border-color 420ms var(--ease-premium);
}
.card:hover { transform: translateY(-4px); border-color: rgba(201,166,85,0.35); }
```
Listas de bullets dentro de um card/painel (ex.: slides de apresentação) seguem o
mesmo espírito: fundo `rgba(255,255,255,0.02)`, borda `var(--border-subtle)`, marcador
`::before` circular na cor `var(--accent)` em vez de bullet padrão do navegador.

### Input (quando o material tiver formulário)
```css
.input {
  background: var(--bg);
  border: 1px solid var(--surface-hover);
  border-radius: 0.5rem;
  color: var(--text-main);
  padding: 0.75rem 1rem;
}
.input:focus { border-color: var(--accent); outline: none; }
```

## Motion — todo material tem alguma transição, nunca é estático

Material sem nenhuma animação/transição foi rejeitado junto com fundo chapado e título
sólido. Use sempre `var(--ease-premium)`, nunca `linear`/`ease-in-out` padrão, e anime
só `opacity`/`transform` (GPU-safe, nunca `top`/`left`/`width`/`height`).

- **Apresentação (slides):** troca de slide anima opacidade + `translateY` + leve
  `scale` (~600ms, `var(--ease-premium)`) — nunca corte seco (`display:none↔flex`
  direto sem transição).
- **Landing page (scroll):** seções entram com fade-up (`opacity 0→1`,
  `translateY(28px)→0`) disparado por `IntersectionObserver` quando entram na
  viewport — nunca aparecem estáticas no load. Ver classe `.revela`/`.visivel` nos
  templates.
- **Arte (`arte-*`):** é uma imagem estática (screenshot único) — não precisa de
  motion, mas o fundo em gradiente + glows + título-gradiente valem do mesmo jeito.

## Logo — OBRIGATÓRIO em todo material (não é opcional)

O logo deixou de ser "se disponível". Todo artefato final deve conter o logo correto,
copiado de `assets/logos-marca/` para `output/<slug>/<tipo>/assets/logos/`, e
referenciado no HTML/Typst. A ausência de logo é falha de compilação detectada por
`scripts/validar-logo.py` (REGRA 8) — nunca entregue material sem logo.

### Qual variante usar

O design system usa fundo escuro (`--bg: #0f172a`). Regra por contraste:

| Contexto de fundo | Arquivo de logo |
|---|---|
| Fundo escuro (padrão — landing, apresentação, arte, capa PDF) | `Logo_Conexão_horizontal_texto_branco.png` |
| Fundo claro (exceção — só se o operador solicitar tema claro) | `Logo_Conexão_horizontal_texto_preto.png` |

**Nunca** use a variante vertical (`.._vertical_..`) em header/cabeçalho — reservada
para composições de capa onde há espaço vertical livre (ex.: capa PDF centralizada).

### Posição por tipo de material

- **landing-page / apresentação**: header fixo, topo-esquerda, altura 32–40px,
  `object-fit: contain`. Exemplo:
  ```html
  <header class="cabecalho">
    <img src="assets/logos/Logo_Conexão_horizontal_texto_branco.png"
         alt="Conexão Implantes" class="logo" height="36">
    <span class="badge">USO PROFISSIONAL</span>
  </header>
  ```
- **arte-01/02/03**: canto superior esquerdo do canvas, margem de 48px, altura 28–32px.
  Nunca centrado — reservar centro para headline e imagem do produto.
- **PDF (capa)**: centrado na área superior da capa, altura 56–64px. O `compilador-pdf`
  copia o arquivo para `output/<slug>/pdf/assets/logos/` e o template Typst o
  referencia via `image("assets/logos/Logo_Conexão_horizontal_texto_branco.png")`.

### Como copiar o arquivo (obrigatório antes de compilar)

```python
import shutil
from pathlib import Path

def copiar_logo(dir_projeto: Path, slug: str, tipo: str):
    src = dir_projeto / "assets" / "logos-marca" / "Logo_Conexão_horizontal_texto_branco.png"
    dst = dir_projeto / "output" / slug / tipo / "assets" / "logos"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
```

## Por tipo de material

- **landing-page / apresentacao**: cabeçalho = logo obrigatório (variante
  `texto_branco`, topo-esquerda, ver seção "Logo") + `.badge` de contexto à direita
  (ex.: "USO INTERNO", "USO PROFISSIONAL"). Títulos em gradiente de texto, Inter peso
  900 (H1) / 700 (H2), corpo em Inter peso 400 (300 para subtítulo/texto de apoio).
  CTA final sempre usa `.btn-primario`.
- **arte-01/02/03**: mesmo `:root` + fontes + vinheta + glows + título-gradiente + logo
  obrigatório no canto superior esquerdo (ver seção "Logo"). O layout usa o padrão
  `.card`/painel quando há conteúdo tabular/lista, com `.badge` para o selo de contexto.
- **PDF**: logo obrigatório na capa (variante `texto_branco`, centrado no topo) — ver
  seção "Logo". O resto do estilo PDF é definido pelas regras próprias do PDF ("Flex
  Gold") a documentar em rodada futura.

## Cores que NÃO vêm desta skill (exceção legítima)

Cores que representam um **fato físico do produto** (ex.: código de cor real de
O-rings/drivers — roxa/azul/verde/vermelha) não são tokens de marca e ficam de fora do
gate de `validar-design-tokens.py` por design — ver exemplo em
`.claude/skills/redator-arte/SKILL.md`. Isso nunca é desculpa para introduzir uma cor
de conveniência estética fora da marca; só se aplica quando a cor em si é o dado sendo
comunicado.
