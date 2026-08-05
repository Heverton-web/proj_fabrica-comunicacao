---
name: redator-kit-copy
description: Fase 2 da Fábrica de Materiais de Comunicação — escreve as 10 copies compartilhadas (headline/subcopy, sem CTA) do Kit do Consultor/Kit Distribuidor, 2 por tom nos 5 tons fixos de brand/tons-kit.json, a partir do brief_criativo.json. Use quando kit-consultor OU kit-distribuidor estiver em materiais_selecionados, UMA ÚNICA VEZ por projeto, antes de compilador-kit.
---

# Skill: Redator de Copy do Kit

Você escreve o conteúdo compartilhado de `kit-consultor` e `kit-distribuidor` — os dois
kits usam **exatamente as mesmas 10 copies**; o que muda entre eles é só o CTA e a
assinatura, aplicados depois por `compilador-kit` de forma determinística
(`brand/kits-conexao.json`). Ver `SPEC_KITS.md`.

**Invocado uma única vez por projeto**, nunca uma vez por kit — se você for chamado de
novo e `output/<slug>/kits/copies.json` já existir com 10 copies válidas, não regrave
(evita `kit-consultor` e `kit-distribuidor` divergindo em paralelo, mesma disciplina de
`redator-arte`/`docs/05-plano-expansao-multi-copy-arte.md`).

## Entrada

- `output/<slug>/brief_criativo.json` (seção
  `mapeamento_por_material.kit.angulos_por_tom` — 2 ângulos por tom, definidos por
  `diretor-de-arte`)
- `output/<slug>/insumos/dossie_insumos.md`
- `brand/tons-kit.json` (definição dos 5 tons fixos)
- `brand/publicos-alvo.json` (entrada `dentista_implantodontista` — público fixo dos
  kits, **nunca** o `publico_alvo` escolhido pelo operador para o resto do projeto)

## Saída

- `output/<slug>/kits/copies.json` — schema:
  ```jsonc
  {"copies": [
    {"id": "kit-01", "tom": "informativa",      "angulo": "...", "headline": "...", "subcopy": "..."},
    {"id": "kit-02", "tom": "informativa",      "angulo": "...", "headline": "...", "subcopy": "..."},
    {"id": "kit-03", "tom": "contra-intuitiva", "angulo": "...", "headline": "...", "subcopy": "..."},
    {"id": "kit-04", "tom": "contra-intuitiva", "angulo": "...", "headline": "...", "subcopy": "..."},
    {"id": "kit-05", "tom": "tecnica",          "angulo": "...", "headline": "...", "subcopy": "..."},
    {"id": "kit-06", "tom": "tecnica",          "angulo": "...", "headline": "...", "subcopy": "..."},
    {"id": "kit-07", "tom": "efeito-uau",       "angulo": "...", "headline": "...", "subcopy": "..."},
    {"id": "kit-08", "tom": "efeito-uau",       "angulo": "...", "headline": "...", "subcopy": "..."},
    {"id": "kit-09", "tom": "educativa",        "angulo": "...", "headline": "...", "subcopy": "..."},
    {"id": "kit-10", "tom": "educativa",        "angulo": "...", "headline": "...", "subcopy": "..."}
  ]}
  ```
  **Sem campo `cta`** — o CTA final é sempre resolvido por `compilador-kit` a partir de
  `brand/kits-conexao.json`, nunca escrito aqui. Consumido por `compilador-kit`, que
  renderiza cada copy em 1 PNG 1080×1350 por kit-variante selecionado (até 20 PNGs: 10
  copies × 2 kits) e escreve o `texto_whatsapp.txt` correspondente.

## Procedimento

Para cada um dos 5 tons de `brand/tons-kit.json` (`informativa`, `contra-intuitiva`,
`tecnica`, `efeito-uau`, `educativa`), escreva **2 copies** a partir dos 2
`angulos_por_tom` correspondentes definidos pelo `diretor-de-arte`:

- **headline** — o ângulo comprimido a ≤ 60 caracteres (mesmo teto de `SPEC_ARTE.md`).
- **subcopy** — um benefício/detalhe de apoio, ≤ 120 caracteres.
- Escreva no registro do público fixo `dentista_implantodontista` (ver
  `brand/publicos-alvo.json`): fala **com** o dentista/implantodontista, 2ª pessoa
  implícita, 1 ideia por peça, sem jargão de vendas/parceria no corpo (isso fica só no
  CTA, que você não escreve).
- Aplique o **registro** do tom (`brand/tons-kit.json.tons.<tom>.registro`) — as 2
  copies de um mesmo tom devem soar visivelmente daquele tom, e as 10 copies no total
  devem cobrir 5 registros distintos, nunca convergir para o mesmo estilo.

## Restrições

- Respeite os limites de caracteres à risca — mesma disciplina de `redator-arte`.
- Nunca invente claim/número fora do dossiê de insumos (REGRA 6).
- Nunca escreva CTA, assinatura ou qualquer menção a "consultor"/"distribuidor" nas
  copies — isso quebraria o compartilhamento entre os 2 kits. CTA/assinatura são
  sempre resolvidos por `compilador-kit` a partir de `brand/kits-conexao.json`.
- As 10 copies devem cobrir os 5 tons, 2 por tom, cada uma um ângulo genuinamente
  distinto do dossiê — nunca 2 variações do mesmo ângulo dentro do mesmo tom, nem
  ângulos repetidos entre tons.
- Nunca derive público ou tom do texto-base — ambos são fixos (`brand/publicos-alvo.json`
  e `brand/tons-kit.json`), independentes do `publico_alvo`/`objetivo_tom` do operador.
- Handoff: `compilador-kit` consome `kits/copies.json` + `brand/kits-conexao.json` +
  `templates/arte-1080x1350.html`, um render por combinação copy × kit-variante.
