---
name: compilador-arte
description: Fase 3 da Fábrica de Materiais de Comunicação — renderiza as 3 copies compartilhadas (arte/copies.json) em cada variante de arte (arte-01/02/03) para PNG pixel-perfect via Playwright headless, aplicando o design system fixo da Conexão. 1 render por combinação copy×formato (até 9 PNGs no total). Use depois de redator-arte, antes de validar-dimensoes.py/revisor-marca.
---

# Skill: Compilador de Arte

Você renderiza as peças de arte PNG. Técnica idêntica à do `subagente-ilustrador` da
Fábrica Agêntica de Livros (HTML/CSS + Playwright screenshot, sem API, sem custo). A
paleta é fixa — **antes de gerar qualquer HTML/CSS, aplique
`.claude/skills/aplicador-marca-conexao/SKILL.md`**, não invente componente aqui.

Formato (dimensão) e copy (conceito criativo) são eixos ortogonais — ver
`docs/05-plano-expansao-multi-copy-arte.md`. Você não renderiza 1 PNG por variante,
renderiza **3** (1 por copy compartilhada), todas na mesma dimensão da variante.

## Entrada

- `output/<slug>/arte/copies.json` (3 copies compartilhadas: headline/subcopy/cta +
  `legendas.{instagram,linkedin,whatsapp}` cada — **falhe alto se este arquivo não
  existir ou não tiver exatamente 3 copies**; nunca gere copy você mesmo aqui, isso é
  trabalho de `redator-arte`, rodado uma única vez antes de qualquer formato ser
  compilado)
- `output/<slug>/config_projeto.json` (`imagens[0].path` — imagem do produto,
  compartilhada pelas 3 copies; `elementos_decorativos` — booleano, default `true`,
  ver Passo 3.5 abaixo)
- `brand/design-system-conexao.json` (fixo, mesmo para todo projeto)
- `templates/arte-<dimensao>.html` (1080x1080 / 1080x1350 / 1080x1920) — já vêm com o
  `:root`, os `@font-face` da marca, o script de ajuste de título (máx. 2 linhas, sem
  linha órfã — ver `SPEC_ARTE.md`) e o placeholder `{{FORMA_DECORATIVA}}` embutidos.

## Procedimento

### 0. Pasta de destino (`<pasta>`)

`<pasta>` é normalmente igual a `<variante>` (`arte-01`/`02`/`03`), mas pode ser uma
versão regenerada (ex.: `"arte-01-v2"`) informada pelo subagente que te invoca quando
essa variante já foi entregue antes — **REGRA 11 do `AGENTS.md`: nunca escreva em uma
pasta que já tenha material entregue**. `<variante>` continua fixa para tudo que
depende de dimensão (viewport, nome de arquivo); só o destino em disco muda. Invoque
sempre via `python scripts/compilar-arte.py <slug> --variante <variante> --pasta
<pasta>`.

### 1. Copiar as fontes e injetar conteúdo no template HTML

Copie `templates/fonts/*.woff2` para `output/<slug>/<pasta>/assets/fonts/` (o
template referencia esse path relativo via `@font-face` — sem isso a fonte cai
silenciosamente em Roboto/sistema). Para **cada uma das 3 copies** de
`arte/copies.json`, preencha `templates/arte-<dimensao>.html` com aquela copy e salve
como HTML dentro da pasta de destino (para que o path relativo das fontes resolva).

### 2. Renderizar com Playwright (viewport exato = dimensão final), 1× por copy

```python
from playwright.sync_api import sync_playwright

DIMENSOES = {"arte-01": (1080, 1080), "arte-02": (1080, 1350), "arte-03": (1080, 1920)}
largura, altura = DIMENSOES[variante]

with sync_playwright() as p:
    browser = p.chromium.launch()  # 1 browser reaproveitado nas 3 copies, nunca 1 por copy
    for indice, copy in enumerate(copies, start=1):  # copies = arte/copies.json["copies"]
        page = browser.new_page(viewport={"width": largura, "height": altura})
        page.goto(f"file:///{caminho_html_absoluto_da_copy}")
        page.wait_for_timeout(500)  # da tempo ao script de ajuste de titulo rodar
        page.screenshot(path=caminho_png_da_copy)
        page.close()
    browser.close()
```

Não use `device_scale_factor` acima de 1 — geraria um PNG maior que a dimensão-alvo, o
que `validar-dimensoes.py` vai rejeitar (R8 do `SPEC.md` exige pixel-perfect exato).

### 3.5. Elementos decorativos de fundo (opt-out)

Leia `config_projeto.elementos_decorativos` (default `true` se ausente). Se `true`,
chame `escolher_decoracao_fundo(f"{slug}:arte:{variante}")` +
`gerar_forma_decorativa_html(...)` de `scripts/_arte_common.py` **uma vez por
variante** (não por copy — as 3 copies do mesmo formato compartilham a mesma
combinação de forma/posição/tamanho) e injete no placeholder `{{FORMA_DECORATIVA}}`.
Se `false`, injete string vazia. Nunca gere a forma você mesmo fora desse helper —
é o que garante bordas finas, opacidade baixa e posição sempre variando por bloco
(ver `SPEC_ARTE.md`).

### 3.7. Legendas de publicação (9 arquivos — obrigatório)

`scripts/compilar-arte.py` grava, para cada uma das 3 copies, as 3 `legendas`
(instagram/linkedin/whatsapp) já escritas por `redator-arte` em `arte/copies.json`
como `output/<slug>/arte/legenda_copy<MM>_<canal>.txt` — 9 arquivos no total,
format-agnósticos (gravados uma vez, reaproveitados pelos 3 formatos). Isso nunca é
gerado aqui do zero — se `legendas` estiver ausente numa copy, o script emite aviso e
segue (não bloqueia o render do PNG), mas `validar-dimensoes.py` cobra a presença dos
9 arquivos no gate final.

### 3.6. Badge (1 por peça — endurecimento)

Preencha o placeholder `{{BADGE_CONTEXTO}}` com `resolver_badge(slug_dir)` de
`scripts/_arte_common.py`, que **sempre retorna string vazia** em peças PNG (SPEC_ARTE
endurecido): o CTA pill (`class="cta"`) é o único elemento tipo badge da peça — nunca
injete badge de contexto ("USO PROFISSIONAL"/"USO INTERNO") por conta própria.
`validar-dimensoes.py` confirma 0 badges de contexto e exatamente 1 CTA nos
`index*.html` persistidos.

### 3. Persistência do HTML

Ao contrário de um HTML temporário único, mantenha os 3 HTMLs (1 por copy) —
`index.html` (copy-01) e `index_copy02.html`/`index_copy03.html` — no disco. Cores,
fontes e logo são idênticos entre as 3 copies (mesmo template), então
`validar-design-tokens.py`/`validar-logo.py` continuam checando só `index.html`
(copy-01) como amostra representativa; os outros 2 ficam disponíveis para auditoria
manual do `revisor-marca`.

### 4. Handoff

`scripts/validar-dimensoes.py <slug> <variante> --pasta <pasta>` confirma exatamente 3
PNGs, dimensão exata, teto de peso, parágrafo em ≥3 linhas sem linha órfã e as 9
legendas de publicação presentes; `revisor-marca` faz a checagem de fidelidade nas
3 copies e nas 9 legendas.

## Naming

- `arte_<slug>_<NN>_copy<MM>.png` onde `NN` é o formato (`01`=1080×1080,
  `02`=1080×1350, `03`=1080×1920) e `MM` é a copy (`01`/`02`/`03`), salvo em
  `output/<slug>/<pasta>/`. Nunca deixe um número solto — os dois eixos (formato e
  copy) sempre aparecem juntos no nome do arquivo.

## Restrições

- Nunca gere ilustração no lugar da imagem oficial do produto — use a imagem de
  `config_projeto.imagens[0]` como está, igual nas 3 copies.
- Nunca deixe o texto (headline/subcopy/cta) transbordar o layout — se
  `redator-arte` excedeu os limites de caractere de `SPEC_ARTE.md`, corrija o texto
  (REGRA 4) antes de renderizar de novo, não reduza a fonte abaixo do que a marca usa.
- PNG deve ficar abaixo do teto de peso da variante (ver `SPEC_ARTE.md`) — otimize
  compressão antes de reportar falha.
- Nunca compile uma variante sem as 3 copies compartilhadas já existirem — isso
  reintroduziria o bug de 1 copy por formato (ver
  `docs/05-plano-expansao-multi-copy-arte.md`, seção 1).
