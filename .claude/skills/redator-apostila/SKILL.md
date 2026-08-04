---
name: redator-apostila
description: Fase 2 da Fábrica de Materiais de Comunicação — escreve o conteúdo Markdown da apostila (PDF) a partir do brief_criativo.json e do dossiê de insumos, seguindo a estrutura de 7 seções de SPEC_PDF.md. Use quando "pdf" estiver em materiais_selecionados, antes de compilador-pdf.
---

# Skill: Redator de Apostila

Você escreve o conteúdo final (Markdown) do material PDF — o mais longo e didático dos
6 tipos. Ver `SPEC_PDF.md` para o contrato técnico completo.

## Entrada

- `output/<slug>/brief_criativo.json` (seção `mapeamento_por_material.pdf`, e o
  `tom_de_voz`/`publico_alvo` gerais do brief)
- `output/<slug>/insumos/dossie_insumos.md`

## Saída

- `output/<slug>/pdf/apostila_<slug>.md` — Markdown pronto para `compilador-pdf`.

## Procedimento

Escreva as 7 seções na ordem de `SPEC_PDF.md` (Abertura, Problema, Solução, Destaques,
Composição/especificações, Aplicação, Fechamento), usando `##` para cada seção. Cada
seção deve:

- Usar exclusivamente fatos presentes em `dossie_insumos.md` — se uma seção não tiver
  evidência suficiente (ex.: sem dados de "Aplicação"), escreva o que houver e registre
  a lacuna em um comentário `<!-- FALTANTE: ... -->` no fim da seção (removido antes da
  entrega final, mas primeiro repassado para `manifesto_materiais.informacoes_faltantes`
  por `revisor-marca`).
- Manter `objetivo` e `tom_de_voz` de `brief_criativo.json` (escolhas do operador nas
  rodadas 2 e 3 — fonte de verdade, nunca re-derivar do texto-base).
- Se o texto-base trouxer itens/códigos/dimensões, formatar a seção "Composição" como
  tabela Markdown — mais escaneável que prosa.
- Referenciar a(s) imagem(ns) oficial(is) do produto via `![](caminho)` na seção de
  Abertura — nunca gerar uma ilustração no lugar da foto real.
- Terminar com uma seção de Fechamento contendo CTA + nome da marca (isso alimenta a
  variável `cta_final` do template Typst).

## Tom de voz por público-alvo (obrigatório — REGRA 6)

Leia `brief_criativo.publico_alvo` e aplique o registro de linguagem definido em
`brand/publicos-alvo.json` para esse público. Nunca use tom genérico de marketing.

| Público | Tom | Ênfase na apostila |
|---------|-----|--------------------|
| `consultores` | Técnico-clínico | Specs completas, tabela de composição, protocolo de uso |
| `clientes` | Acessível/orientador | Problema do paciente → como resolve → o que esperar |
| `distribuidores` | Comercial-técnico | Portfólio + argumentário de vendas + suporte ao parceiro |

O `dossie_insumos.md` gerado por `analista-insumos` já traz as implicações práticas
do público escolhido — use-as como guia, não as re-derive do texto-base.

## Restrições

- Nunca invente especificação técnica, número ou claim fora do dossiê (REGRA 6).
- Nunca use cor/fonte no Markdown — isso é responsabilidade do template Typst
  (`scripts/parametros_projeto.py --pdf-vars`), não do conteúdo.
- O tom de voz vem de `brief_criativo.tom_de_voz` (escolha do operador, via
  `brand/publicos-alvo.json`) — nunca re-derive do texto-base.
- Handoff: `compilador-pdf` consome este Markdown.
