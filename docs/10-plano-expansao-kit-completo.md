# Plano de Expansão: Kits Completos por Público-Alvo (`/kit-completo-*`)

> **Status:** aprovado para implementação
> **Decisões de design registradas:** abordagem paramétrica (A); dados comerciais
> exclusivamente do texto-base (REGRA 6); versões numeradas sem sobrescrita (REGRA 11).
> **Documentos relacionados:** `SPEC.md`, `SPEC_COMANDOS.md`, `SPEC_PDF.md`,
> `SPEC_HTML.md`, `SPEC_KITS.md`, `AGENTS.md`.

---

## 1. Visão geral

Criar **3 novos comandos universais** que produzem um **kit completo de comunicação
focado em um público-alvo específico**, combinando materiais já existentes na fábrica
com **estruturas de conteúdo especializadas por público**:

| Comando | Público fixo | Materiais fixos |
|---|---|---|
| `/kit-completo-consultor` | `consultores` | `pdf` + `kit-consultor` + `landing-page` + `apresentacao` |
| `/kit-completo-distribuidor` | `distribuidores` | `pdf` + `kit-distribuidor` + `landing-page` + `apresentacao` |
| `/kit-completo-cliente` | `clientes` | `pdf` + `landing-page` + `apresentacao` |

**Impacto técnico baixo:** os comandos reutilizam 100% dos compiladores
(`compilar-pdf`/`compilar-html`/`compilar-kit`), dos subagentes produtores
(`subagente-produtor-pdf`/`-landing`/`-apresentacao`/`-kit`), do `revisor-marca`, do
`pool-materiais.py` e do `empacotar-projeto.py`. Não há MCP novo, hook novo, compilador
novo, subagente novo nem pasta de saída nova. O que muda é: (1) a **entrevista de
entrada** (público e materiais pré-fixos pelo preset), (2) o **mapeamento de conteúdo**
no `brief_criativo.json` (estruturas por público), e (3) a **validação determinística**
do novo campo `preset_kit_completo`.

**Por que "kit completo" não é apenas um atalho de seleção:** além de pré-fixar
público/materiais, o preset **altera a estrutura de conteúdo** — o PDF e a apresentação
ganham seções que hoje não existem na estrutura default (`SPEC_PDF.md`, 7 seções), como
"Como vender: SPIN + contorno de objeções", "Rentabilidade para o seu negócio" e
"Diferenciais para a prática clínica". É isso que justifica comandos próprios.

---

## 2. Decisões de design já tomadas

| # | Decisão | Fundamento |
|---|---|---|
| D1 | **Abordagem paramétrica (A):** 1 seção canônica em `SPEC_COMANDOS.md` (`/kit-completo-<publico>` com tabela de presets) + 3 ponteiros finos por harness | Segue o padrão do `/gerar-arte` guarda-chuva; evita triplicar a instrução (disciplina de não duplicar lógica, REGRA 10) |
| D2 | **Dados comerciais (margem, preço, objeções reais, benefícios clínicos) vêm exclusivamente do texto-base** fornecido pelo operador na entrevista | REGRA 6 — nunca inventar claim; ausência vira "faltante" no relatório final |
| D3 | **Nenhuma sobrescrita:** materiais já entregues por outros comandos (`/esbocar`+`/produzir-comunicacao-completa`, `/gerar-*`) geram pastas versionadas `-v2`/`-v3` via `pool-materiais.py --proxima-pasta` | REGRA 11 |
| D4 | **O preset define público e materiais; objetivo/tom continua escolha do operador** (3 opções atuais) | Mesma fonte de verdade de `config_projeto.json`; público e tom nunca derivados do texto-base |
| D5 | **Kit do Consultor/Distribuidor dentro do preset permanece com as predefinições fixas atuais** (público `dentista_implantodontista`, 5 tons, 1080×1350) | `SPEC_KITS.md` — o kit é material que o consultor/distribuidor usa; eixo ortogonal ao público do preset |
| D6 | `/kit-completo-cliente` **não inclui kits** (kits existem apenas para consultor/distribuidor) | Tabela de módulos do `AGENTS.md` e `SPEC_KITS.md` |
| D7 | Comando roda a **própria entrevista curta** (adaptação das 4 rodadas) e depois executa o fluxo padrão do Passo 2 (`/produzir-comunicacao-completa`) | REGRA 3 (autonomia) — mesma disciplina das exceções `/gerar-<material>` |

---

## 3. Presets — estrutura de conteúdo por público (canônico)

As estruturas abaixo são a **nova tabela canônica** que viverá em `SPEC_COMANDOS.md`
(seção `/kit-completo-<publico>`), referenciada por `SPEC_PDF.md`/`SPEC_HTML.md` e
materializada por `diretor-de-arte` em `brief_criativo.mapeamento_por_material`.

### 3.1 `/kit-completo-consultor`

| Material | Estrutura |
|---|---|
| **pdf** | 1. O que é · 2. Para que serve · 3. Diferenciais técnicos/comerciais · 4. Como vender: SPIN (S=Situação, P=Problema, I=Implicação, N=Necessidade de solução) · 5. Contorno de objeções (objeções reais + resposta) · 6. Fechamento/CTA |
| **kit-consultor** | Fluxo atual inalterado (`SPEC_KITS.md`) — 10 artes 1080×1350, público `dentista_implantodontista` |
| **landing-page** | Fluxo atual inalterado (estrutura default de `SPEC_HTML.md`) |
| **apresentacao** | Foco em: O que é · Para que serve · Diferenciais técnicos (1 conceito por slide) |

### 3.2 `/kit-completo-distribuidor`

| Material | Estrutura |
|---|---|
| **pdf** | 1. O que é · 2. Para que serve · 3. Diferenciais técnicos/comerciais · 4. Rentabilidade para o seu negócio · 5. Como vender: SPIN · 6. Contorno de objeções · 7. Fechamento/CTA |
| **kit-distribuidor** | Fluxo atual inalterado (`SPEC_KITS.md`) |
| **landing-page** | Fluxo atual inalterado |
| **apresentacao** | Foco em: O que é · Para que serve · Diferenciais técnicos · Rentabilidade para o seu negócio |

### 3.3 `/kit-completo-cliente`

| Material | Estrutura |
|---|---|
| **pdf** | 1. O que é · 2. Para que serve · 3. Diferenciais técnicos · 4. Diferenciais para a prática clínica · 5. Por que utilizar este produto · 6. Fechamento/CTA |
| **landing-page** | Foco em: O que é · Para que serve · Diferenciais técnicos · Diferenciais para a prática clínica · Por que utilizar este produto |
| **apresentacao** | Foco em: O que é · Para que serve · Diferenciais técnicos · Diferenciais para a prática clínica · Por que utilizar este produto |

### 3.4 Regras de conteúdo transversais

- **SPIN e contorno de objeções:** a técnica (S/P/I/N e a estrutura pergunta→resposta)
  é fixa e canônica; o **conteúdo** (perguntas reais do consultor, objeções reais do
  cliente, respostas com base no dossiê) é extraído do texto-base — nunca inventado.
- **Rentabilidade:** margens, preços, condições e benefícios comerciais exatamente como
  constam no texto-base. Ausência de dados → seção sinalizada como "faltante" no
  relatório (REGRA 6), nunca preenchida por suposição.
- **Diferenciais para a prática clínica / Por que utilizar:** benefícios clínicos e
  motivos de escolha presentes no texto-base, redigidos no registro de linguagem de
  `brand/publicos-alvo.json` para o público do preset.
- **Landing e apresentação** seguem o design system fixo (`aplicador-marca-conexao`);
  o PDF segue `SPEC_PDF.md` (capa Flex Gold + 7 seções default, agora com variantes por
  público no `mapeamento_por_material`).
- Registro de linguagem e `cta_padrao` por público: já existem em
  `brand/publicos-alvo.json` (`consultores`, `distribuidores`, `clientes`) — as novas
  seções herdam esses registros, sem duplicar definição.

---

## 4. Arquivos a criar e alterar (gap completo)

### 4.1 Camada canônica (única fonte de verdade)

| Arquivo | Ação | Conteúdo |
|---|---|---|
| `SPEC_COMANDOS.md` | Alterar | Nova seção `## /kit-completo-<publico>` com: tabela de presets (seção 3), entrevista adaptada (seção 5), fluxo de execução (seção 6), resolução de pastas (REGRA 11) |
| `SPEC_PDF.md` | Alterar | Variantes de estrutura por público (seção 3) referenciadas pelo mapeamento do brief |
| `SPEC_HTML.md` | Alterar | Variantes de apresentação/landing por público (seção 3) |
| `SPEC.md` | Alterar | R1 (rodadas pré-preenchíveis por preset — o preset não conta como rodada nova), schema de `config_projeto.json` (novo campo `preset_kit_completo`), edge cases (nota de escopo de landing interna, dados comerciais ausentes) |
| `AGENTS.md` | Alterar | Lista de comandos universais + tabela de módulos (3 novas linhas de comando) + menção dos presets na REGRA 3/11 se necessário |
| `brand/publicos-alvo.json` | Alterar | Blocos novos por público: `spin_objetivo`, `objetivos_de_venda` (consultor), `rentabilidade` (distribuidor), `pratica_clinica`, `por_que_utilizar` (cliente) — descrições de foco, nunca conteúdo |
| `docs/10-plano-expansao-kit-completo.md` | Criar | Este documento |

### 4.2 Skills (estágios do pipeline)

| Skill | Ação | Conteúdo |
|---|---|---|
| `diretor-de-arte` | Alterar | Quando `config_projeto.preset_kit_completo` existir, montar `mapeamento_por_material` com as estruturas por público da seção 3 (em vez da estrutura default) |
| `redator-apostila` | Alterar | Consumir `mapeamento_por_material.pdf.secoes` com as novas seções (SPIN/objeções/rentabilidade/prática clínica) e aplicar as regras de conteúdo transversais (3.4) |
| `redator-apresentacao` | Alterar | Consumir as variantes de foco por público |
| `redator-landing` | Alterar | Consumir as variantes de foco por público (aplicável ao preset cliente) |

Sem skill nova de orquestração: o procedimento canônico vive em `SPEC_COMANDOS.md`
(filosofia: SPEC = procedimento, skills = estágios).

### 4.3 Adaptadores de descoberta por harness (ponteiros finos)

| Arquivos | Ação |
|---|---|
| `.claude/commands/kit-completo-consultor.md` + `-distribuidor.md` + `-cliente.md` | Criar (3 ponteiros finos para a seção canônica) |
| `.opencode/commands/kit-completo-consultor.md` + `-distribuidor.md` + `-cliente.md` | Criar (3 ponteiros finos) |

Cada ponteiro segue o formato de 5 linhas de `esbocar.md`/`gerar-kit-consultor.md`
(frontmatter `description` + 2 parágrafos apontando para `SPEC_COMANDOS.md`).

### 4.4 Scripts determinísticos (árbitros — gate obrigatório)

| Script | Ação | Regra nova |
|---|---|---|
| `parametros_projeto.py` | Alterar | Validar `preset_kit_completo ∈ {consultor, distribuidor, cliente}` e **coerência com `materiais_selecionados`**: consultor ⇒ `kit-consultor` presente; distribuidor ⇒ `kit-distribuidor` presente; cliente ⇒ nenhum kit presente |
| `auditar-projeto.py` | Alterar | Mesma coerência preset↔materiais no gate final (`--estrito`) |
| `verificar-consistencia-pipeline.py` | Alterar | Tabela de módulos com os 3 comandos novos |
| `verificar-universalidade.py` | Alterar | Conhecer os 3 adaptadores novos (`.claude/commands/` + `.opencode/commands/`) |

Opcional (fase 2, endurecer depois): `validar-pdf.py`/`validar-html.py` ganham checagem
de presença das seções-chave por público (ex.: "Rentabilidade" no preset distribuidor).

**Sem alteração:** `pool-materiais.py` (tipos de pasta são os mesmos),
`empacotar-projeto.py` (manifesto já lista versões), compiladores, subagentes, MCPs,
hooks, `.mcp.json`, `opencode.jsonc`.

---

## 5. Entrevista do comando (adaptação das 4 rodadas — sem rodada nova)

O preset **pré-preenche** a rodada 2 (público) e a rodada 4 (materiais) do `/esbocar`
— o que sobra é a entrevista curta abaixo, na ordem, sempre mostrando o valor atual
como referência de "manter" quando aplicável:

1. **Insumos** (texto livre): "Informe o caminho das imagens e o **texto-base** da
   informação a comunicar." — para `distribuidor`, reforçar que o texto-base deve
   conter dados de rentabilidade (margem/preço/condições) se existirem; para
   `consultor`, objeções reais de clientes e perguntas de venda se existirem. Ausência
   nunca é bloqueio — vira "faltante" (REGRA 6).
2. **Objetivo/tom de voz** (seleção única): mesmas 3 opções compostas atuais
   (educacional/comercial, informacional/técnico, comercial/parceria). O preset
   sugere a opção compatível com o público (via `brand/publicos-alvo.json`), mas o
   operador decide.
3. **Edição** (texto livre): obrigatória (o preset sempre inclui `pdf`) — ex.:
   "1ª Edição".
4. **Elementos decorativos** (sim/não): obrigatória quando o preset inclui kit
   (consultor/distribuidor), pois os kits têm artes (mesma disciplina do Passo 5 de
   `/esbocar`). Default `true`.

Qualquer resposta livre/"Other" é válida (REGRA 3). Sem pergunta de público, sem
pergunta de materiais, sem pergunta de design system.

---

## 6. Fluxo de execução (autônomo, sem pausas)

1. **Pré-condições:** se `output/<slug>/config_projeto.json` não existir, cria o
   projeto do zero (slug derivado do nome do produto; se existir, sufixo `-v2`...);
   se existir, reaproveita e atualiza.
2. **Gravar configuração:** `config_projeto.json` com `publico_alvo` fixo do preset,
   `materiais_selecionados` fixos (adicionando aos já existentes, nunca removendo),
   `preset_kit_completo: <publico>`, `edicao`, `elementos_decorativos`.
3. **`parametros_projeto.py <slug> --validar`** — corrigir internamente (REGRA 4).
4. **`analista-insumos`** → `dossie_insumos.md` (fatos + registro das escolhas;
   detecta dados comerciais ausentes → lista de faltantes).
5. **`diretor-de-arte`** → `brief_criativo.json` com `mapeamento_por_material`
   usando as estruturas por público da seção 3 (quando o preset existir).
6. **Passo 2 padrão** (idêntico a `/produzir-comunicacao-completa`): pre-flight de
   compatibilidade de slug → plano de lotes (`--lote 4`) → copy compartilhada de kit
   (Passo 2.7, se `kit-consultor`/`kit-distribuidor` no preset) → fan-out por lote →
   drenar pendentes → `revisor-marca` → `auditar-projeto.py <slug> --estrito` →
   `empacotar-projeto.py <slug>` → relatório final telegráfico (REGRA 2) com decisões
   de design, faltantes e sugestões de legenda por pasta/versão.

---

## 7. Interação com materiais já existentes (REGRA 11)

O comando nunca decide sobrescrita por julgamento — para **cada** material do preset,
resolve a pasta via `pool-materiais.py <slug> --proxima-pasta <tipo>`:

| Situação em disco | Resolução |
|---|---|
| `output/<slug>/<tipo>/` não existe | cria `<tipo>/` (1ª geração) |
| `output/<slug>/<tipo>/` existe (qualquer comando anterior) | cria `<tipo>-v2/`, `-v3/`... — anterior intocado |

Regras complementares:

- **`config_projeto.json`/`brief_criativo.json` são atualizados para o estado mais
  recente** (público do preset, materiais somados, brief regravado por
  `diretor-de-arte`) — mesmo comportamento de `/gerar-pdf` quando o público muda na
  entrevista de regeneração. Os materiais antigos permanecem em disco.
- **Copy compartilhada** `kits/copies.json`: reaproveita se os insumos não mudaram;
  `redator-kit-copy` regrava se mudaram (regra existente).
- **Materiais fora do preset não são tocados** (ex.: `textos/`, `arte-01/` ficam como
  estão).
- **`manifesto_materiais.json` lista todas as versões** lado a lado (comportamento já
  implementado em `empacotar-projeto.py`).
- **Relatório e auditoria por versão:** `auditar-projeto.py --estrito --apenas
  <pastas>` e relatório final com path por pasta/versão (padrão do
  `/gerar-kit-consultor`).

---

## 8. Validação e gates

| Gate | Quando | Exit 1 se... |
|---|---|---|
| `parametros_projeto.py <slug> --validar` | antes de produzir | `preset_kit_completo` inválido ou incoerente com `materiais_selecionados` |
| `auditar-projeto.py <slug> --estrito` | após produção | mesma incoerência + regras atuais (R4, R5, R9) |
| `verificar-consistencia-pipeline.py --estrito` | após implementação | tabela de módulos desalinhada |
| `verificar-universalidade.py --estrito` | após implementação | adaptadores por harness ausentes/divergentes |
| `validar-pdf.py`/`validar-html.py`/`validar-kit.py` | por material | critérios atuais (estrutura, dimensão, peso, capa) |

---

## 9. Fases de implementação

| Fase | Escopo | Entregável |
|---|---|---|
| 1 | **Canônicos** — `SPEC_COMANDOS.md` (seção paramétrica + tabela de presets), `SPEC_PDF.md`, `SPEC_HTML.md`, `SPEC.md` (R1, schema, edge cases), `AGENTS.md` (comandos + tabela), `brand/publicos-alvo.json` (blocos de foco por público) | Specs atualizadas |
| 2 | **Skills** — `diretor-de-arte` (mapeamento por preset), `redator-apostila`, `redator-apresentacao`, `redator-landing` (novas seções) | Skills atualizados |
| 3 | **Scripts** — `parametros_projeto.py` (preset + coerência), `auditar-projeto.py` (gate), tabelas de consistência/universalidade | Gate determinístico verde |
| 4 | **Adaptadores** — 3 ponteiros em `.claude/commands/` + 3 em `.opencode/commands/` | 6 arquivos novos |
| 5 | **Verificação final** — `verificar-consistencia-pipeline.py --estrito` + `verificar-universalidade.py --estrito` + teste ponta-a-ponta com um projeto real (ex.: `kit-start-flex`) | Planos aprovados |

---

## 10. Riscos e mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| Texto-base sem dados de rentabilidade/objeções | Seções saem vazias ou inventadas | Regra de conteúdo 3.4: ausência → "faltante" no relatório, nunca suposição (REGRA 6); entrevista reforça o pedido dos dados |
| Material já entregue com outro público (ex.: `pdf/` de clientes + `kit-completo-consultor`) | Duplicação de versões | REGRA 11 + manifesto lista tudo; relatório por pasta/versão deixa explícito qual é qual |
| Landing interna para consultor (escopo interno vs. externo) | Material fora de escopo | Edge case existente de `SPEC.md` (`nota_de_escopo`): se o texto-base indicar material interno, registrar a decisão, não produzir por suposição |
| Entrevista confundida com 4 rodadas novas | Regressão da R1 | Preset pré-preenche rodadas 2 e 4 — não cria rodadas novas; documentado em `SPEC.md`/`SPEC_COMANDOS.md` |
| Harness sem mecanismo de comando | Comando indisponível | REGRA 10: reconhecimento por linguagem natural equivalente + adaptadores finos |

---

## 11. Critérios de aceitação

1. `/kit-completo-consultor`, `/kit-completo-distribuidor` e `/kit-completo-cliente`
   funcionam em qualquer harness (string literal ou linguagem natural).
2. Produção 100% autônoma após a entrevista curta — nenhuma pausa no meio.
3. Estruturas por público aplicadas (SPIN/objeções, rentabilidade, prática clínica,
   por que utilizar) conforme a seção 3, com conteúdo exclusivamente do texto-base.
4. Nenhuma sobrescrita de material entregue; versões numeradas lado a lado no
   manifesto.
5. Gates determinísticos verdes: `parametros_projeto.py`, `auditar-projeto.py`,
   `verificar-consistencia-pipeline.py`, `verificar-universalidade.py` (todos
   `--estrito`).
6. Kit do Consultor/Distribuidor dentro do preset com as 10 copies idênticas entre
   variantes (exceto CTA) — sem regressão do `SPEC_KITS.md`.
