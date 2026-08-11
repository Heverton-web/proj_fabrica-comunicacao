---
name: redator-apostila
description: Fase 2 da Fábrica de Materiais de Comunicação — escreve o conteúdo Markdown da apostila (PDF) a partir do brief_criativo.json e do dossiê de insumos, seguindo a estrutura de 7 seções de SPEC_PDF.md. Use quando "pdf" estiver em materiais_selecionados, antes de compilador-pdf.
---

# Skill: Redator de Apostila

Você escreve o conteúdo final (Markdown) do material PDF — o mais longo e didático dos
9 tipos. Ver `SPEC_PDF.md` para o contrato técnico completo.

## Entrada

- `output/<slug>/brief_criativo.json` (seção `mapeamento_por_material.pdf`, e o
  `tom_de_voz`/`publico_alvo` gerais do brief)
- `output/<slug>/insumos/dossie_insumos.md`

## Saída

- `output/<slug>/<pasta>/apostila_<slug>.md` — Markdown pronto para `compilador-pdf`.
  `<pasta>` é informada pelo subagente que te invoca — normalmente `"pdf"`, mas pode
  ser uma versão regenerada (ex.: `"pdf-v2"`) quando o material já foi entregue antes
  e o operador pediu uma nova geração via `/gerar-pdf` (REGRA 11 do `AGENTS.md`: nunca
  escreva por cima de uma versão já entregue).

## Procedimento

Escreva as seções na ordem de `SPEC_PDF.md` (Abertura, Problema, Solução, Destaques,
Composição/especificações, Aplicação, Fechamento), usando `##` para cada seção — ou,
**se o projeto vier de um preset `/kit-completo-<publico>`** (campo
`preset_kit_completo` em `config_projeto.json`), escreva as seções por público
descritas abaixo, na ordem do `mapeamento_por_material.pdf.secoes`. Cada seção deve:

- **Abertura (estrutura obrigatória, alimenta a capa — SPEC_PDF endurecido):** a seção
  em si é `## Abertura` (nível 2) — o H1 temático fica **dentro** dela, nunca no lugar
  dela. Nunca escreva `# Abertura` (o rótulo da seção) como se fosse o título:
  `scripts/compilar-pdf.py` descarta um H1 que seja apenas o nome de uma das 7 seções
  (Abertura, Problema, Solução...) e cai no fallback genérico — pior resultado que
  simplesmente escrever o H1 temático certo desde já.
  1. H1 temático (`# ...`): **máx. 34 caracteres / 6 palavras, sem hífens**, remetendo
     ao **tema do texto-mãe** (ex.: "Previsibilidade e Excelência Clínica") — nunca o
     nome cru do produto nem rótulo genérico. Em 24pt/10cm ele vira o título da capa
     e deve quebrar em **no máximo 2 linhas, sem linha com 1 palavra isolada**. Nunca
     use nenhum termo da lista `TITULOS_BANIDOS` de `scripts/validar-pdf.py` (ex.:
     "guia de treinamento", "gambiarra") mesmo que o texto-base use esse vocabulário
     no corpo — são clichês banidos especificamente do título, não do conteúdo.
     `compilador-pdf` tem uma rede de segurança determinística (NBSP entre as 2
     últimas palavras + redução de fonte até caber) para as 2 regras de linha, mas
     isso não dispensa respeitar o limite de 34 caracteres/6 palavras — a rede de
     segurança ajusta o encaixe, não reescreve um título ruim.
  2. Parágrafo de apoio (primeiro parágrafo após o H1): **120–160 caracteres**, frase
     de posicionamento do produto (factos do dossiê; nunca claim novo) — vira o
     parágrafo da capa (`capa_paragrafo`) e deve renderizar em **≥ 3 linhas sem
     palavra isolada** na largura de 10cm.
  3. Imagem oficial do produto (`![](insumos/...)`).
  4. Frase de posicionamento em negrito = `brief_criativo.mensagem_central`.
  5. 1–2 parágrafos de contexto.
- Usar exclusivamente fatos presentes em `dossie_insumos.md` — se uma seção não tiver
  evidência suficiente (ex.: sem dados de "Aplicação"), escreva o que houver e registre
  a lacuna em um comentário `<!-- FALTANTE: ... -->` no fim da seção (removido antes da
  entrega final, mas primeiro repassado para `manifesto_materiais.informacoes_faltantes`
  por `revisor-marca`).
- Manter `objetivo` e `tom_de_voz` de `brief_criativo.json` (escolhas do operador nas
  rodadas 2 e 3 — fonte de verdade, nunca re-derivar do texto-base).
- Se o texto-base trouxer itens/códigos/dimensões, formatar a seção "Composição" como
  tabela Markdown — mais escaneável que prosa.
- Terminar com uma seção de Fechamento contendo CTA + nome da marca (isso alimenta a
  variável `cta_final` do template Typst).

## Estrutura por público (preset `/kit-completo-<publico>`)

Se `config_projeto.preset_kit_completo` existir, o corpo segue a variante da seção
`/kit-completo-consultor` de `SPEC_COMANDOS.md` (canônico dos 3 presets — tabelas de
presets; variantes em `/kit-completo-distribuidor` e `/kit-completo-cliente`), com a
Abertura (capa) sempre na mesma estrutura obrigatória do Procedimento acima:

- **`consultores`:** O que é · Para que serve · Diferenciais técnicos/comerciais ·
  Como vender: SPIN (S/P/I/N) · Contorno de objeções · Fechamento.
- **`distribuidores`:** O que é · Para que serve · Diferenciais técnicos/comerciais ·
  Rentabilidade para o seu negócio · Como vender: SPIN · Contorno de objeções ·
  Fechamento.
- **`clientes`:** O que é · Para que serve · Diferenciais técnicos · Diferenciais
  para a prática clínica · Por que utilizar este produto · Fechamento.

Regras de conteúdo (REGRA 6 — fidelidade à fonte):

- **SPIN:** técnica fixa — uma pergunta por estágio (Situação, Problema, Implicação,
  Necessidade de solução), redigida a partir de fatos do dossiê. Nunca invente
  pergunta ou cenário fora do texto-base.
- **Contorno de objeções:** objeção real do texto-base (ou a mais provável, se o
  dossiê indicar) → resposta objetiva com dados do dossiê. Estrutura
  pergunta→resposta; ausência de objeções no texto-base → `<!-- FALTANTE: ... -->`.
- **Rentabilidade** (distribuidor): margens/preços/condições exatamente como no
  texto-base; sem dados → `<!-- FALTANTE: ... -->`, nunca suposição.
- **Diferenciais para a prática clínica / Por que utilizar** (cliente): benefícios
  clínicos e motivos presentes no dossiê, em linguagem acessível (registro de
  `brand/publicos-alvo.json`).

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
