# SPEC_ARTE.md — Contrato Técnico: Arte PNG (redes sociais)

Ver `SPEC.md` para o fluxo geral. Este documento cobre os materiais `arte-01`
(1080×1080), `arte-02` (1080×1350) e `arte-03` (1080×1920).

## Pipeline

`redator-arte` (headline + subcopy + CTA curtos, por variante) → `compilador-arte`
(renderiza `templates/arte-<variante>.html` via Playwright headless, viewport exato =
dimensão final, `page.screenshot()`) → `scripts/validar-dimensoes.py` (Pillow).

Técnica portada de `fabrica-de-livros/.claude/agents/subagente-ilustrador.md` (HTML/CSS
+ Playwright, sem API, sem custo), com o design system fixo da Conexão
(`brand/design-system-conexao.json`) aplicado via `.claude/skills/aplicador-marca-conexao/SKILL.md`.

## Requisitos técnicos por variante

| Variante | Dimensão | Uso típico | Teto de peso |
|---|---|---|---|
| `arte-01` | 1080×1080 px | WhatsApp, post quadrado Instagram/LinkedIn | 1 MB |
| `arte-02` | 1080×1350 px | Post retrato Instagram/LinkedIn (mais espaço vertical) | 1 MB |
| `arte-03` | 1080×1920 px | Stories/Reels Instagram, Status WhatsApp | 1 MB |

- Dimensão **pixel-perfect exata** — viewport do Playwright deve ser fixado exatamente
  na dimensão-alvo (sem `device_scale_factor` que gere upscale além do necessário).
- Texto do headline/CTA deve caber sem overflow no layout — `redator-arte` respeita
  limites de caracteres por variante (headline ≤ 60 caracteres, subcopy ≤ 120,
  CTA ≤ 30) para garantir legibilidade em tela de celular.
- Cores/fontes só via CSS custom properties do design system fixo (mesma disciplina
  de `SPEC_HTML.md`).
- Nome do arquivo: `arte_<slug>_<variante>.png`, ex.: `arte_kit-master-flex_01.png`.
- Cada arte funciona sozinha (sem depender de ver o PDF/landing). O conteúdo exato
  depende do escopo confirmado em `brief_criativo.json` — pode ser uma peça pública
  "isca visual" (nome do produto/marca + mensagem central + CTA, mirror do exemplo
  Conexão/Kit Master Flex) ou um cartão de referência rápida de uso interno (ex.:
  tabela de torque, código de cores) — ver exemplo real em `mapeamento_por_material.arte`
  do teste `kit-start-flex`.

## Validação (`scripts/validar-dimensoes.py`)

- Abre o PNG com Pillow, confirma `image.size == (largura, altura)` exata da variante.
- `size_bytes < teto` da tabela acima.
- Falha → `revisor-marca` decide reduzir texto/otimizar compressão (auto-correção,
  REGRA 4) antes de reportar esgotado.
