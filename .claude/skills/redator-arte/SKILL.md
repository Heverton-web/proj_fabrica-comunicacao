---
name: redator-arte
description: Fase 2 da Fábrica de Materiais de Comunicação — escreve 3 copies (headline/subcopy/CTA + 3 legendas de publicação por canal cada) compartilhadas entre todos os formatos de arte selecionados (1080x1080, 1080x1350, 1080x1920) a partir do brief_criativo.json, respeitando limites de caracteres. Use quando qualquer arte-01/02/03 estiver em materiais_selecionados, UMA ÚNICA VEZ por projeto, antes de compilador-arte.
---

# Skill: Redator de Arte

Você escreve o texto que vai dentro de cada peça de arte para redes sociais/WhatsApp —
o material mais curto e mais "isca visual" dos 9 tipos. Ver `SPEC_ARTE.md` e
`docs/05-plano-expansao-multi-copy-arte.md`.

**Formato (dimensão do PNG) e copy (conceito criativo) são eixos ortogonais.** Você
não escreve "uma copy por variante" — você escreve **3 copies compartilhadas**, cada
uma renderizada depois em **todos** os formatos selecionados (`arte-01`/`02`/`03`).
Invocado **uma única vez por projeto**, nunca uma vez por variante — se você for
chamado de novo e `output/<slug>/arte/copies.json` já existir com 3 copies válidas,
não regrave (evita 2 subagentes de formato divergindo em paralelo). **Exceção:** se
esta chamada vem de uma regeneração pontual (`/gerar-arte-<tamanho>`) cuja entrevista
mudou público-alvo e/ou tom de voz do projeto, o `copies.json` existente reflete a
escolha antiga — regrave-o com os novos ângulos (as PNGs já entregues de outras
variantes não são afetadas, pois já foram renderizadas e vivem em pastas próprias —
ver REGRA 11 do `AGENTS.md`).

## Entrada

- `output/<slug>/brief_criativo.json` (seção `mapeamento_por_material.arte.angulos_criativos`
  — 3 ângulos definidos por `diretor-de-arte`)
- `output/<slug>/insumos/dossie_insumos.md`

## Saída

- `output/<slug>/arte/copies.json` — schema:
  ```jsonc
  {"copies": [
    {"id": "copy-01", "angulo": "...", "headline": "...", "subcopy": "...", "cta": "...",
     "legendas": {"instagram": "...", "linkedin": "...", "whatsapp": "..."}},
    {"id": "copy-02", "angulo": "...", "headline": "...", "subcopy": "...", "cta": "...",
     "legendas": {"instagram": "...", "linkedin": "...", "whatsapp": "..."}},
    {"id": "copy-03", "angulo": "...", "headline": "...", "subcopy": "...", "cta": "...",
     "legendas": {"instagram": "...", "linkedin": "...", "whatsapp": "..."}}
  ]}
  ```
  Consumido por `compilador-arte`, que renderiza cada uma das 3 copies em cada formato
  selecionado (3 copies × 3 formatos = até 9 PNGs) e grava as 9 `legendas` em
  `output/<slug>/arte/legenda_copy<MM>_<canal>.txt` (ver `SPEC_ARTE.md`).

## Procedimento

Para cada um dos 3 `angulos_criativos` definidos em `brief_criativo.json`, escreva uma
copy completa e **format-agnóstica** (os limites de caractere de `SPEC_ARTE.md` já são
os mesmos independente da dimensão final — a mesma copy cabe em 1080×1080, 1080×1350 e
1080×1920):

- **headline** — o ângulo criativo comprimido a ≤ 60 caracteres.
- **subcopy** — **entre 100 e 170 caracteres, em 2 frases**: a 1ª carrega o benefício,
  a 2ª um dado/prova concreto tirado do dossiê de insumos (número, comparação,
  consequência prática) — nunca reafirme o headline em palavras mais vagas ("é o que
  evita X" sem dizer o quê/quanto). Precisa render em pelo menos 3 linhas no layout
  (580px/1.25rem), sem linha final de 1-2 palavras — ver regra em `SPEC_ARTE.md`.
- **cta** — chamada de ação curta, ≤ 30 caracteres (ex.: "Fale com um consultor").

A imagem do produto/marca a usar não é por copy — vem de `config_projeto.imagens[0]`
(ou de uma imagem específica se o dossiê indicar mais de uma), aplicada igualmente nas
3 copies pelo `compilador-arte`. Nunca gere ilustração no lugar da imagem oficial
(REGRA 6, mesma regra do exemplo Conexão: "use esta imagem... não invente/ilustre o
produto").

## Tom de voz por público-alvo (obrigatório — REGRA 6)

Leia `brief_criativo.publico_alvo` e aplique o registro de linguagem definido em
`brand/publicos-alvo.json`. A arte tem espaço mínimo — cada palavra conta, e o tom
errado em 60 caracteres é ainda mais evidente que em 600.

| Público | Tom | Exemplo de headline |
|---------|-----|---------------------|
| `consultores` | Técnico direto | `'Torque de 15 N·cm. Plataformas 3.0 a 5.0.'` |
| `clientes` | Benefício/resultado | `'Sorria com confiança. Conheça o implante certo para você.'` |
| `distribuidores` | Oportunidade | `'Amplie seu portfólio com a linha Conexão Implantes.'` |

O `dossie_insumos.md` gerado por `analista-insumos` já traz as implicações práticas
do público escolhido — use-as como guia, não as re-derive do texto-base.

## Legendas de publicação (`legendas` — obrigatório)

O texto embutido no PNG nunca é o post inteiro. Para cada uma das 3 copies, escreva
**3 legendas** (Instagram, LinkedIn, WhatsApp) para colar junto da imagem ao publicar —
mesmo padrão de riqueza do `texto_whatsapp.txt` dos kits, mas adaptado por canal
(regras completas de formatação em `redator-textos/SKILL.md`):

- **instagram** — headline em destaque + subcopy expandido em blocos espaçados + 1
  dado extra do dossiê não usado no subcopy + hashtags do nicho + CTA para link na bio.
- **linkedin** — tom de autoridade profissional, parágrafo limpo (sem bullets
  emoji-pesados), dado técnico/de mercado do dossiê, CTA institucional.
- **whatsapp** — curta, com `*negrito*`/`_itálico_`/emojis, pronta para reenvio 1:1
  (não precisa hashtag nem link na bio).

Cada legenda é uma peça de comunicação própria — nunca as 3 iguais só trocando emoji,
e nunca apenas repetir headline+subcopy sem acrescentar conteúdo novo do dossiê.

## Restrições

- Respeite os limites de caracteres à risca — texto que não cabe no layout é reportado
  por `validar-dimensoes.py`/`compilador-arte` como falha, não corrigido silenciosamente
  com fonte menor que a marca não usa.
- Nunca invente claim/número fora do dossiê de insumos.
- O tom de voz vem de `brief_criativo.tom_de_voz` (escolha do operador, via
  `brand/publicos-alvo.json`) — nunca re-derive do texto-base.
- As 3 copies devem cobrir 3 ângulos distintos do dossiê (nunca 3 variações do mesmo
  ângulo) — cada uma é uma peça de comunicação completa por si só.
- As 9 `legendas` (3 copies × 3 canais) também nunca inventam claim fora do dossiê, e
  nunca são apenas headline+subcopy coladas sem dado novo.
- Handoff: `compilador-arte` consome `arte/copies.json` + `templates/arte-<dimensao>.html`,
  um render por combinação copy×formato, e grava as `legendas` como arquivos `.txt`.
