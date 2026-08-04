---
name: compilador-html
description: Fase 3 da Fábrica de Materiais de Comunicação — monta apresentacao/index.html e landing-page/index.html a partir do conteúdo estruturado (slides.json/conteudo.json), aplicando o design system fixo da Conexão. Use depois de redator-apresentacao/redator-landing, antes de validar-html.py/revisor-marca.
---

# Skill: Compilador de HTML

Você monta os dois materiais HTML (apresentação e landing page) — mesmo compilador para
ambos, templates diferentes. **Antes de gerar qualquer HTML/CSS, aplique
`.claude/skills/aplicador-marca-conexao/SKILL.md`** — ela é a única fonte de verdade de
cores, fontes e componentes (botão, badge, card). Não invente padrão visual aqui.

Para qualidade visual de HTML/CSS fora do que a marca já define, apoie-se nos skills
genéricos do catálogo (`frontend-design`, `web-artifacts-builder`, `high-end-visual-design`)
em vez de reinventar orientação de design do zero.

## Entrada

- `output/<slug>/apresentacao/slides.json` **ou** `output/<slug>/landing-page/conteudo.json`
- `brand/design-system-conexao.json` (fixo, mesmo para todo projeto)
- `templates/apresentacao.html` **ou** `templates/landing.html` — já vêm com o `:root`
  e os `@font-face` da marca embutidos; normalmente você não precisa tocar nisso, só
  nos placeholders de conteúdo.

## Procedimento

### 1. Copiar as fontes da marca

Copie `templates/fonts/*.woff2` para `output/<slug>/<tipo>/assets/fonts/` — os
templates referenciam esse path relativo via `@font-face`. Sem isso, o material cai
silenciosamente em fonte de sistema (Roboto, se instalada) — confirme visualmente ou
via `document.fonts` antes de considerar concluído.

### 2. Injetar conteúdo no template

Substitua os placeholders de conteúdo do template (`{{SLIDES}}`/`{{HERO}}`/
`{{BADGE_CONTEXTO}}` etc. — ver comentários em `templates/apresentacao.html` /
`templates/landing.html`) pelo conteúdo de `slides.json`/`conteudo.json`. Copie
qualquer imagem referenciada para `output/<slug>/<tipo>/assets/` e ajuste os `src` para
paths relativos. `{{BADGE_CONTEXTO}}` = "USO INTERNO" ou "USO PROFISSIONAL"/"USO
EXTERNO" conforme a decisão de escopo registrada em `brief_criativo.json`.

### 3. Salvar

- `output/<slug>/apresentacao/index.html` (+ `assets/`, incluindo `assets/fonts/`)
- `output/<slug>/landing-page/index.html` (+ `assets/`, incluindo `assets/fonts/`)

### 4. Handoff

`scripts/validar-html.py <slug> <tipo>` roda o Playwright headless para confirmar
ausência de erro de console/asset quebrado/overflow; `scripts/validar-design-tokens.py
<slug> <tipo>` confirma fidelidade de cor contra `brand/design-system-conexao.json`;
`revisor-marca` faz a checagem de fidelidade de conteúdo e de componente.

## Restrições

- Nunca hardcode hex/nome de fonte fora do bloco `:root` — todo o resto do CSS deve
  usar `var(--accent)` etc., para que `validar-design-tokens.py` consiga confirmar
  fidelidade de marca por grep.
- Botão/CTA primário sempre usa `var(--gradiente-assinatura)`, nunca `var(--accent)`
  chapado — ver `aplicador-marca-conexao`.
- HTML deve ser autocontido (sem CDN externo, inclusive de fonte) — mesma disciplina de
  artifacts self-contained.
