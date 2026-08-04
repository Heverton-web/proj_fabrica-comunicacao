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

- Estrutura em slides (`brief_criativo.mapeamento_por_material.apresentacao.slides`):
  capa, problema, solução, 1 destaque por slide, fechamento/CTA.
- Navegação simples (setas/teclado) — sem exigir biblioteca externa pesada; JS inline
  mínimo.
- Saída: `output/<slug>/apresentacao/index.html` (+ `assets/` se houver imagens).

## Landing Page

- Estrutura em seções (`brief_criativo.mapeamento_por_material.landing-page.secoes`):
  hero, problema→solução, destaques, prova/composição, CTA final.
- Copy persuasiva mas fiel à fonte (REGRA 6) — sem superlativo não sustentado pelo
  texto-base.
- Saída: `output/<slug>/landing-page/index.html` (+ `assets/` se houver imagens).

## Validação (`scripts/validar-html.py`)

- Abre `index.html` via Playwright (`file://`), captura console e network.
- Falha se: erro de console, request de asset com status de erro, ou largura de
  conteúdo excedendo a viewport (overflow horizontal).
- Reporta achados em JSON; `revisor-marca` decide auto-correção (REGRA 4) ou faltante.
