# SPEC_ARTE.md — Contrato Técnico: Arte PNG (redes sociais)

Ver `SPEC.md` para o fluxo geral e `docs/05-plano-expansao-multi-copy-arte.md` para o
histórico da decisão abaixo. Este documento cobre os materiais `arte-01`
(1080×1080), `arte-02` (1080×1350) e `arte-03` (1080×1920).

## Modelo: formato × copy (eixos ortogonais)

**Formato** (a dimensão do PNG: `arte-01`/`02`/`03`) e **copy** (o conceito criativo de
headline/subcopy/CTA) nunca são a mesma coisa. Existem sempre **3 copies
compartilhadas** por projeto — cada uma um ângulo distinto do dossiê (ex.: problema,
diferencial técnico, versatilidade) — e cada uma é renderizada em **todos** os formatos
selecionados em `materiais_selecionados`:

```
                     arte-01        arte-02        arte-03
                    (1080x1080)    (1080x1350)    (1080x1920)
copy-01 (ângulo A)      ✅              ✅             ✅
copy-02 (ângulo B)      ✅              ✅             ✅
copy-03 (ângulo C)      ✅              ✅             ✅
```

Se os 3 formatos forem selecionados, o resultado são **9 PNGs no total** (3 copies × 3
formatos). `materiais_selecionados` continua controlando só os **formatos**
produzidos — as 3 copies são sempre geradas juntas, independente de quantos formatos
forem pedidos.

## Pipeline

1. `redator-arte` — roda **uma única vez por projeto**, nunca uma vez por formato.
   Lê `brief_criativo.mapeamento_por_material.arte.angulos_criativos` (3 ângulos
   definidos por `diretor-de-arte`) e escreve `output/<slug>/arte/copies.json` com as
   3 copies completas (headline + subcopy + CTA cada).
2. `compilador-arte` — para cada formato selecionado, lê `arte/copies.json` e
   renderiza `templates/arte-<dimensao>.html` via Playwright headless (viewport exato =
   dimensão final, `page.screenshot()`) uma vez por copy.
3. `scripts/validar-dimensoes.py` (Pillow) — confirma exatamente 3 PNGs por formato,
   cada um pixel-perfect e abaixo do teto de peso.

Técnica de renderização portada de
`fabrica-de-livros/.claude/agents/subagente-ilustrador.md` (HTML/CSS + Playwright, sem
API, sem custo), com o design system fixo da Conexão
(`brand/design-system-conexao.json`) aplicado via
`.claude/skills/aplicador-marca-conexao/SKILL.md`.

**Disciplina de orquestração (crítica):** a geração de copy é um passo compartilhado e
único, executado pelo orquestrador (`/produzir-comunicacao-completa`, Passo 2.5)
**antes** de despachar qualquer `subagente-produtor-arte`. Gerar copy dentro de cada
subagente de formato reintroduz o bug original desta spec (1 copy por formato,
divergente entre subagentes paralelos) — ver seção 1 de
`docs/05-plano-expansao-multi-copy-arte.md`.

## Requisitos técnicos por formato

| Formato | Dimensão | Uso típico | Teto de peso | PNGs esperados |
|---|---|---|---|---|
| `arte-01` | 1080×1080 px | WhatsApp, post quadrado Instagram/LinkedIn | 1 MB | 3 (1 por copy) |
| `arte-02` | 1080×1350 px | Post retrato Instagram/LinkedIn (mais espaço vertical) | 1 MB | 3 (1 por copy) |
| `arte-03` | 1080×1920 px | Stories/Reels Instagram, Status WhatsApp | 1 MB | 3 (1 por copy) |

- Dimensão **pixel-perfect exata** — viewport do Playwright deve ser fixado exatamente
  na dimensão-alvo (sem `device_scale_factor` que gere upscale além do necessário).
- Texto do headline/CTA deve caber sem overflow no layout — `redator-arte` respeita
  limites de caracteres (headline ≤ 60 caracteres, subcopy **entre 100 e 170**, CTA ≤
  30) para garantir legibilidade em tela de celular. Esses limites são
  **format-agnósticos** — a mesma copy deve caber nos 3 formatos, por isso não há
  variação de texto por dimensão.
- **Subcopy em no mínimo 3 linhas renderizadas, nunca com 1-2 palavras sozinhas numa
  linha** (mesmo espírito da regra de headline abaixo, aplicada ao parágrafo): escreva
  **2 frases** — 1ª o benefício, 2ª um dado/prova concreto do dossiê de insumos (nunca
  reafirmar o headline em palavras mais vagas) — o suficiente para preencher a coluna
  de 580px/1.25rem sem ficar raso. Não garantido só por caractere mínimo (palavras
  longas/curtas variam a quebra) — os templates embutem o mesmo tipo de script do
  título (mede as linhas renderizadas via `.palavra` e injeta NBSP entre as 2 últimas
  palavras se a última linha ficar com ≤ 2 palavras). Ver `templates/arte-*.html`.
- Cores/fontes só via CSS custom properties do design system fixo (mesma disciplina
  de `SPEC_HTML.md`).
- **Imagem do produto em evidência (endurecimento):** `.produto` ocupa a maior parte
  do bloco de conteúdo — `width: 680px`/`max-height: 440px` (arte-01),
  `740px`/`640px` (arte-02), `840px`/`920px` (arte-03), `object-fit: contain`,
  `margin-bottom: 48px`. Com a foto padrão (1600×1382, quase quadrada), o
  `max-height` é o fator limitante: renderiza ~680×440 (arte-01), 740×639 (arte-02),
  840×726 (arte-03). Nunca reduza para acomodar texto — ajuste o texto (REGRA 4).
  Bloco de conteúdo nunca pode colidir com o rodapé de copyright (verificar via
  bounding rect no Playwright após render).
- **Título (headline) em no máximo 2 linhas, nunca com 1 única palavra sozinha numa
  linha**, e com largura igual à do parágrafo (mesmo `max-width` de `.subcopy`), para
  causar a impressão de um bloco compacto em harmonia com o parágrafo abaixo — não
  garantido só por CSS (`text-wrap: balance` como 1ª camada); os templates embutem um
  script que mede as linhas renderizadas e reduz o `font-size` em passos pequenos até
  cumprir as 2 regras (nunca aumenta o tamanho definido no CSS). Ver `templates/arte-*.html`.
- **1 Badge por Peça (endurecimento):** cada PNG tem **exatamente 1** elemento tipo
  badge — o **CTA pill** (`class="cta"`). **Nenhum badge de contexto** (`class="badge"`,
  ex.: "USO PROFISSIONAL"/"USO INTERNO") em artes — o CTA é o único elemento
  distintivo permitido. `resolver_badge()` em `scripts/_arte_common.py` sempre retorna
  vazio para PNGs (badge de contexto só existe em HTML vivo — landing/apresentação,
  ver `SPEC_HTML.md`). Validado deterministicamente por `validar-dimensoes.py` sobre os
  `index*.html` persistidos (0 badges de contexto, exatamente 1 CTA por arquivo).
- **Elementos geométricos/wave decorativos de fundo** (bordas finas douradas —
  `stroke-width` ~0.35 num viewBox 0-100, nunca grosso —, `stroke` sem `fill`,
  opacidade baixa ~0.06-0.15, tamanho grande sangrando por um canto do canvas) para
  dar profundidade, **opt-out via `config_projeto.elementos_decorativos: false`**
  (Passo 5 do `/esbocar` — default ativo). 1 combinação (forma + canto/diagonal +
  tamanho + deslocamento + opacidade) por **bloco** de artes (o bloco é o formato em
  `arte-01/02/03` — as 3 copies de 1 formato compartilham a combinação; em
  `kit-consultor`/`kit-distribuidor` é o par kit-variante×tom — as 2 artes de 1 tom de
  1 kit compartilham a combinação). Catálogo de formas (`quadrado`, `circulo`,
  `triangulo`, `hexagono`, `wave`) e sorteio determinístico por chave
  (`escolher_decoracao_fundo`) em `scripts/_arte_common.py`; nunca aleatoriedade real
  — mesma chave (mesmo bloco) sempre resulta na mesma forma/posição/tamanho/opacidade
  (recompilar não muda o visual), chaves diferentes (blocos diferentes) tendem a
  variar em todos os eixos (forma, canto usado, tamanho, deslocamento, opacidade) —
  nunca sempre no mesmo canto, para não cansar visualmente quem vê vários materiais
  do mesmo projeto em sequência. **Sempre na camada de fundo**: `z-index` explicitamente
  abaixo do logo, do bloco de conteúdo (título/produto/parágrafo/CTA) e das faixas —
  nunca pode prejudicar a legibilidade do texto, a visibilidade do logo ou a percepção
  da imagem do produto.
- Nome do arquivo: `arte_<slug>_<NN>_copy<MM>.png`, onde `NN` é o formato
  (`01`/`02`/`03`) e `MM` é a copy (`01`/`02`/`03`) — ex.:
  `arte_kit-master-flex_01_copy02.png` = formato 1080×1080, copy 2. Os dois eixos
  aparecem sempre juntos no nome, nunca um número solto.
- Cada arte funciona sozinha (sem depender de ver o PDF/landing). O conteúdo exato de
  cada copy depende do escopo confirmado em `brief_criativo.json` — pode ser uma peça
  pública "isca visual" (nome do produto/marca + mensagem central + CTA) ou um cartão
  de referência rápida de uso interno (ex.: tabela de torque, código de cores).

## Artefato compartilhado: `output/<slug>/arte/copies.json`

```jsonc
{
  "copies": [
    {"id": "copy-01", "angulo": "problema", "headline": "...", "subcopy": "...", "cta": "..."},
    {"id": "copy-02", "angulo": "diferencial-tecnico", "headline": "...", "subcopy": "...", "cta": "..."},
    {"id": "copy-03", "angulo": "versatilidade", "headline": "...", "subcopy": "...", "cta": "..."}
  ]
}
```

Pasta auxiliar (`output/<slug>/arte/`, mesmo padrão de `insumos/` e `revisao/`), não é
um dos materiais finais de R12 — os materiais finais continuam sendo `arte-01/`,
`arte-02/`, `arte-03/` (cada um com seus próprios 3 PNGs + HTMLs).

## Legenda de publicação: `output/<slug>/arte/legenda_copy<MM>_<canal>.txt`

O texto embutido no PNG (headline/subcopy/CTA) nunca é o post inteiro — quem publica
precisa de uma legenda para colar junto da imagem no Instagram/LinkedIn/WhatsApp,
igual ao `texto_whatsapp.txt` que `compilador-kit` já grava por item do
kit-consultor/kit-distribuidor. Para as 3 copies compartilhadas de arte-01/02/03,
`compilador-arte` grava **9 arquivos** (3 copies × 3 canais, format-agnóstico — a
legenda não depende do formato final, só da copy):

- `legenda_copy01_instagram.txt`, `legenda_copy01_linkedin.txt`, `legenda_copy01_whatsapp.txt`
- `legenda_copy02_instagram.txt`, `legenda_copy02_linkedin.txt`, `legenda_copy02_whatsapp.txt`
- `legenda_copy03_instagram.txt`, `legenda_copy03_linkedin.txt`, `legenda_copy03_whatsapp.txt`

Cada legenda reaproveita headline (em destaque) + subcopy expandido (agora em 2
frases, ver regra de subcopy acima) + 1 dado extra do dossiê de insumos + CTA — nunca
uma legenda genérica igual nos 3 canais. Adaptação por canal (mesmas regras de
`redator-textos/SKILL.md`):

| Canal | Adaptação |
|---|---|
| `instagram` | Blocos espaçados, hashtags do nicho, CTA para link na bio. |
| `linkedin` | Tom de autoridade profissional, parágrafo limpo, sem excesso de emoji. |
| `whatsapp` | Formatação com `*negrito*`/`_itálico_` e emojis, mensagem curta pronta para reenvio 1:1. |

## Validação (`scripts/validar-dimensoes.py`)

- Abre cada PNG com Pillow, confirma `image.size == (largura, altura)` exata do
  formato.
- Confirma **exatamente 3 PNGs** na pasta do formato (1 por copy) — menos ou mais que
  3 é falha.
- `size_bytes < teto` da tabela acima, para cada PNG.
- Mede via Playwright as linhas renderizadas do `.subcopy` nos `index*.html`
  persistidos — falha se `< 3` linhas ou se alguma linha tiver `<= 2` palavras (mesmo
  árbitro determinístico usado para o título, REGRA 8).
- Confirma **9 arquivos de legenda** em `output/<slug>/arte/` (3 copies × 3 canais),
  cada um não vazio.
- Falha → `revisor-marca` decide reduzir texto/otimizar compressão (auto-correção,
  REGRA 4) antes de reportar esgotado.
