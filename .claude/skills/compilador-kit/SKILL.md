---
name: compilador-kit
description: Fase 3 da Fábrica de Materiais de Comunicação — renderiza as 10 copies compartilhadas (kits/copies.json) em PNGs 1080x1350 para a variante de kit pedida (kit-consultor/kit-distribuidor), aplicando CTA/assinatura fixos de brand/kits-conexao.json e escrevendo o texto_whatsapp.txt de cada item. Use depois de redator-kit-copy, antes de validar-kit.py/revisor-marca.
---

# Skill: Compilador de Kit

Você renderiza as peças do Kit do Consultor/Kit Distribuidor. Reaproveita a mesma
técnica de `compilador-arte` (HTML/CSS + Playwright, sem API, sem custo) através do
helper compartilhado `scripts/_arte_common.py` — não duplique a lógica de template ou
de render aqui, chame o script `scripts/compilar-kit.py`. Ver `SPEC_KITS.md`.

Kit-variante (consultor/distribuidor) é o eixo ortogonal aqui — formato já é único
(1080×1350). Você não escreve nem re-gera copy: `kits/copies.json` já existe (gerado
uma única vez por `redator-kit-copy`) e é **idêntico** para os 2 kits; só o CTA final
muda, e vem de `brand/kits-conexao.json`, nunca de uma nova chamada de LLM.

## Entrada

- `output/<slug>/kits/copies.json` (10 copies compartilhadas: tom, ângulo, headline,
  subcopy — sem CTA. **Falhe alto se este arquivo não existir ou não tiver exatamente
  10 copies**; nunca gere copy você mesmo aqui, isso é trabalho de `redator-kit-copy`)
- `brand/kits-conexao.json` (`variantes.<kit>.cta_padrao` + `.assinatura` — fonte fixa
  do CTA/assinatura, determinística)
- `output/<slug>/config_projeto.json` (`imagens[0].path` — imagem do produto,
  compartilhada pelas 10 copies × 2 kits; `elementos_decorativos` — booleano, default
  `true`, ver passo 2.5 abaixo)
- `brand/design-system-conexao.json` (fixo)
- `templates/arte-1080x1350.html` (mesmo template já usado por `arte-02` — já vem com
  `:root` e `@font-face` da marca embutidos)

## Procedimento

Rode `python scripts/compilar-kit.py <slug> --kit <kit-consultor|kit-distribuidor>
--pasta <pasta>`. `<pasta>` é normalmente igual a `--kit`, mas pode ser uma versão
regenerada (ex.: `"kit-consultor-v2"`) informada pelo subagente que te invoca quando
esse kit já foi entregue antes — **REGRA 11 do `AGENTS.md`: nunca escreva em uma pasta
que já tenha material entregue**. `--kit` continua fixo (define CTA/assinatura); só a
`--pasta` muda o destino em disco. Internamente, para cada um dos 5 tons de
`brand/tons-kit.json` × 2 itens (10 no total):

1. Cria `output/<slug>/<pasta>/artes-<tom>/arte-0N/` e copia fontes/logo/produto para
   `arte-0N/assets/` (mesma técnica de `preparar_assets` em `_arte_common.py`).
2. Preenche `templates/arte-1080x1350.html` com a copy (headline/subcopy) + o CTA fixo
   da variante — salva como `arte-0N/index.html` (mantido, não temporário, para
   auditoria de marca). O placeholder `{{BADGE_CONTEXTO}}` é preenchido por
   `resolver_badge()` que **sempre retorna vazio** em PNGs — 1 badge por peça
   (somente o CTA pill, ver SPEC_KITS.md endurecido); nunca injete badge de contexto
   por conta própria.
2.5. Se `elementos_decorativos` for `true` (default), escolhe **1 combinação** de
   forma/posição/tamanho/opacidade por **tom** (via `escolher_decoracao_fundo(f"{slug}:kit:{kit}:{tom}")`
   em `_arte_common.py`) — os 2 itens (`arte-01`/`arte-02`) daquele tom compartilham a
   mesma combinação, nunca sorteada de novo por item. Se `false`, injeta string vazia.
3. Renderiza via Playwright (viewport exato 1080×1350, 1 browser reaproveitado entre
   os 10 renders da variante) → `arte-0N/arte_<slug>_<kit>_<tom>_<NN>.png`.
4. Grava `arte-0N/conteudo.json` (copy final, já com CTA/assinatura da variante).
5. Grava `arte-0N/texto_whatsapp.txt` — mensagem curta pronta para WhatsApp, montada
   deterministicamente (sem nova chamada de LLM): gancho de abertura por tom em
   itálico (ver `TOM_GANCHO` em `scripts/compilar-kit.py`), headline em **negrito**,
   subcopy como bullet point, CTA comercial em destaque (negrito + emoji) e
   assinatura da variante em itálico — ver `SPEC_KITS.md`.

## Handoff

`scripts/validar-kit.py <slug> <kit> --pasta <pasta>` confirma a estrutura completa (5 tons × 2 itens ×
{PNG, conteudo.json, texto_whatsapp.txt} = 30 arquivos) **e a regra de 1 badge por
peça** (0 badges de contexto + exatamente 1 CTA por `index*.html`); `revisor-marca` faz a
checagem de fidelidade e confirma que as copies dos 2 kits são idênticas exceto
CTA/assinatura.

## Restrições

- Nunca gere ilustração no lugar da imagem oficial do produto — mesma imagem de
  `config_projeto.imagens[0]` em todas as 10 copies × 2 kits.
- Nunca escreva um CTA diferente do que está em `brand/kits-conexao.json` para aquela
  variante — isso é a única diferença de conteúdo permitida entre os 2 kits.
- PNG deve ficar abaixo do teto de 1 MB (mesmo teto de `SPEC_ARTE.md`) e ser
  pixel-perfect 1080×1350.
- Nunca compile uma variante de kit sem as 10 copies compartilhadas já existirem —
  isso reintroduziria divergência de conteúdo entre `kit-consultor` e
  `kit-distribuidor` (ver `SPEC_KITS.md`, seção "Revisão de marca").
