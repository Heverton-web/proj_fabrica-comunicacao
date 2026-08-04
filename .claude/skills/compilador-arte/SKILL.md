---
name: compilador-arte
description: Fase 3 da Fábrica de Materiais de Comunicação — renderiza cada variante de arte (arte-01/02/03) para PNG pixel-perfect via Playwright headless, a partir do conteudo.json e do template HTML/CSS correspondente, aplicando o design system fixo da Conexão. Use depois de redator-arte, antes de validar-dimensoes.py/revisor-marca.
---

# Skill: Compilador de Arte

Você renderiza as peças de arte PNG. Técnica idêntica à do `subagente-ilustrador` da
Fábrica Agêntica de Livros (HTML/CSS + Playwright screenshot, sem API, sem custo). A
paleta é fixa — **antes de gerar qualquer HTML/CSS, aplique
`.claude/skills/aplicador-marca-conexao/SKILL.md`**, não invente componente aqui.

## Entrada

- `output/<slug>/arte-0N/conteudo.json` (headline/subcopy/cta/imagem_produto)
- `brand/design-system-conexao.json` (fixo, mesmo para todo projeto)
- `templates/arte-<dimensao>.html` (1080x1080 / 1080x1350 / 1080x1920) — já vêm com o
  `:root` e os `@font-face` da marca embutidos.

## Procedimento

### 1. Copiar as fontes e injetar conteúdo no template HTML

Copie `templates/fonts/*.woff2` para `output/<slug>/<variante>/assets/fonts/` (o
template referencia esse path relativo via `@font-face` — sem isso a fonte cai
silenciosamente em Roboto/sistema). Preencha `templates/arte-<dimensao>.html` com o
`conteudo.json` da variante. Salve como HTML temporário dentro da pasta da variante
(para que o path relativo das fontes resolva).

### 2. Renderizar com Playwright (viewport exato = dimensão final)

```python
from playwright.sync_api import sync_playwright

DIMENSOES = {"arte-01": (1080, 1080), "arte-02": (1080, 1350), "arte-03": (1080, 1920)}
largura, altura = DIMENSOES[variante]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": largura, "height": altura})
    page.goto(f"file:///{caminho_html_absoluto}")
    page.wait_for_timeout(300)
    page.screenshot(path=caminho_png)
    browser.close()
```

Não use `device_scale_factor` acima de 1 — geraria um PNG maior que a dimensão-alvo, o
que `validar-dimensoes.py` vai rejeitar (R8 do `SPEC.md` exige pixel-perfect exato).

### 3. Limpeza

Delete o HTML temporário depois do screenshot.

### 4. Handoff

`scripts/validar-dimensoes.py <slug> <variante>` confirma dimensão exata + teto de
peso; `revisor-marca` faz a checagem de fidelidade.

## Naming

- `arte_<slug>_<NN>.png` onde `NN` é `01`/`02`/`03`, salvo em `output/<slug>/arte-0N/`.

## Restrições

- Nunca gere ilustração no lugar da imagem oficial do produto — use
  `conteudo.imagem_produto` como está.
- Nunca deixe o texto (headline/subcopy/cta) transbordar o layout — se
  `redator-arte` excedeu os limites de caractere de `SPEC_ARTE.md`, corrija o texto
  (REGRA 4) antes de renderizar de novo, não reduza a fonte abaixo do que a marca usa.
- PNG deve ficar abaixo do teto de peso da variante (ver `SPEC_ARTE.md`) — otimize
  compressão antes de reportar falha.
