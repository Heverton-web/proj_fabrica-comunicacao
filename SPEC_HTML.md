# SPEC_HTML.md — Contrato Técnico: Apresentação e Landing Page

Ver `SPEC.md` para o fluxo geral. Este documento cobre os materiais `apresentacao` e
`landing-page` — ambos HTML estático autocontido, montados por `compilador-html`.

## Pipeline

`redator-apresentacao` ou `redator-landing` (conteúdo estruturado) → `compilador-html`
(injeta conteúdo em `templates/apresentacao.html` ou `templates/landing.html`, que já
trazem o design system fixo — `brand/design-system-conexao.json` — como CSS custom
properties e `@font-face` embutidos; ver `.claude/skills/aplicador-marca-conexao/SKILL.md`)
→ `scripts/validar-html.py` (Playwright headless).

## Requisitos técnicos comuns

- HTML autocontido: CSS inline ou em `<style>` no próprio arquivo, sem dependência de
  CDN externo (mesma disciplina de artifacts self-contained).
- Cores/fontes só via CSS custom properties (`--bg`, `--surface`, `--text-main`,
  `--text-muted`, `--accent`, `--gradiente-assinatura`, `--fonte-titulo`, `--fonte-corpo`)
  — nunca hex/fonte hardcoded fora do bloco `:root` fixo definido em
  `.claude/skills/aplicador-marca-conexao/SKILL.md`.
- Responsivo: sem overflow horizontal, testável em viewport mobile e desktop.
- Sem erro de console no carregamento (Playwright `page.on("console")` sem `error`).
- Sem asset quebrado (toda imagem referenciada existe em `output/<slug>/<tipo>/assets/`).

## Apresentação

- **Estrutura de Slides:** Capa, diferenciais, composição, especificações, scripts/SPIN, objeções, fechamento/CTA.
- **Design de Títulos:** Todos os títulos de slides devem ser em **Caixa Alta** (uppercase), com peso de fonte **Inter 900** (Black) e preenchidos com o gradiente metálico linear Conexão (`--gradiente-assinatura`).
- **Sem Hífens:** Hífens (-) nos títulos são proibidos, devendo ser obrigatoriamente substituídos por dois-pontos (:).
- **Cabeçalho Dinâmico:** O cabeçalho fixo (`.topo-deck`) deve dispor o logotipo horizontal Conexão à esquerda e a Edição definida (ex: "1ª Edição" carregada dinamicamente de `config_projeto.json`) à direita de forma sutil e elegante.
- **Respiro de Painéis (Padding):** Os painéis de conteúdo (`.slide ul`) devem ter obrigatoriamente pelo menos **32px de padding superior e inferior** (`padding: 32px 1.8rem;`) com tamanhos de fonte equilibrados para evitar overflow.
- **Divisão Dinâmica de Listas (Split 4+):** Se uma lista de bullets contiver 4 ou mais itens, ela deve ser dividida dinamicamente pelo compilador em **duas colunas paralelas de painéis** (`.duas-colunas`), preenchendo a largura da tela de forma balanceada e simétrica.
- **Medidor de Torque (SVG Gauge):** O slide relacionado a torques cirúrgicos deve conter uma tabela técnica à esquerda e um **indicador de torque seguro (Gauge SVG inline) animado** à direita. O ponteiro e a cor do arco devem realizar uma transição suave de varredura quando o slide recebe a classe `.ativo`.
- **Efeitos Neon nas Cores de Captura:** O compilador HTML deve fazer o parsing do markdown (`**` para `<strong>` e `*` para `<em>`) e aplicar classes de estilo com brilho neon nas tags `strong` contendo palavras-chave das cores de captura da marca Conexão (Roxa, Azul, Verde, Vermelha).
- **Navegação:** Suporta navegação interativa nativa por setas, barra de espaço e cliques (efeito fade-in/slide vertical).
- **Saída:** `output/<slug>/apresentacao/index.html` (+ `assets/` incluindo fontes locais e logotipos).

## Landing Page

- **Estrutura de Seções:** Hero, problema→solução, destaques, prova/composição técnica e comercial, CTA final.
- **Design Unificado:** Títulos em Caixa Alta e Inter 900 com gradiente de assinatura, badges com fundo dourado translúcido (12% opacidade) e bordas finas, botões primários translúcidos com efeito hover sutil.
- **Faixas Premium:** Presença de finas faixas douradas (3px) preenchidas com o gradiente Conexão fixadas no topo e rodapé de forma persistente.
- **Parser de Markdown:** Tratamento de markdown em todo o copy e tabelas para renderização limpa de negritos/itálicos.
- **Copy Persuasiva:** Fiel à fonte (REGRA 6) — sem superlativos não sustentados pelo texto-base.
- **Saída:** `output/<slug>/landing-page/index.html` (+ `assets/` incluindo fontes e logotipos locais).

## Estrutura por público (presets `/kit-completo-<publico>`)

Quando `config_projeto.preset_kit_completo` existir, o `diretor-de-arte` monta o
`mapeamento_por_material` com as variantes de foco abaixo (canônico em
`SPEC_COMANDOS.md`, seção `/kit-completo-consultor` — canônico dos 3 presets, com as
variantes em `/kit-completo-distribuidor` e `/kit-completo-cliente`). Requisitos técnicos, design
system e validações são os mesmos — muda apenas a estrutura de conteúdo:

| Público do preset | Apresentação (foco dos slides) | Landing page |
|---|---|---|
| `consultores` | O que é · Para que serve · Diferenciais técnicos | Fluxo atual inalterado (estrutura default acima) |
| `distribuidores` | O que é · Para que serve · Diferenciais técnicos · Rentabilidade para o seu negócio | Fluxo atual inalterado |
| `clientes` | O que é · Para que serve · Diferenciais técnicos · Diferenciais para a prática clínica · Por que utilizar este produto | Foco: O que é · Para que serve · Diferenciais técnicos · Diferenciais para a prática clínica · Por que utilizar este produto |

Regras de conteúdo (REGRA 6): conteúdo de rentabilidade e de prática clínica vem
exclusivamente do texto-base — ausência vira "faltante" no relatório, nunca suposição.
Sem preset, valem as estruturas default acima.

## Validação (`scripts/validar-html.py`)

- Abre `index.html` via Playwright (`file://`), captura console e network.
- Falha se: erro de console, request de asset com status de erro, ou largura de
  conteúdo excedendo a viewport (overflow horizontal).
- Reporta achados em JSON; `revisor-marca` decide auto-correção (REGRA 4) ou faltante.
