# 11 — Plano de Expansão: Variação de Layout nas Artes (disposição dos elementos)

**Status:** proposto — análise + exemplo de aplicação implementado em
`exemplos/expansao-layout/` · **Escopo futuro:** `templates/`, `scripts/`,
`.claude/skills/`, `SPEC*.md`, `brand/`.

Fonte de autoridade: **Manual de Identidade Visual Conexão Implantes** (Seção 11 —
Peças de campanha, Templates A/B/C; Seção 12 — Organização das artes digitais,
regra dos terços + 6 esqueletos). O manual define a **disposição** dos elementos;
o design system fixo (`brand/design-system-conexao.json`) define **cor/fonte/
componente**. A expansão casa os dois: layout passa a ser um eixo ortogonal da arte,
exatamente como `docs/05-plano-expansao-multi-copy-arte.md` fez com copy.

## Resumo executivo — a explicação em 4 pontos

**1. A expansão é viável? Sim.** Layout vira um 3º eixo ortogonal
(formato × copy × layout), mesmo padrão da expansão de copy de `docs/05`. Os
templates de arte já têm contrato de placeholders (`{{LOGO}}`, `{{IMAGEM_PRODUTO}}`,
`{{HEADLINE}}`, `{{SUBCOPY}}`, `{{CTA}}`, `{{FORMA_DECORATIVA}}`,
`{{BADGE_CONTEXTO}}`) e `preencher_template()` em `scripts/_arte_common.py` funciona
com qualquer HTML que respeite esse contrato — novo layout = novo arquivo de template,
sem mudar a lógica de substituição. O Manual fornece o vocabulário pronto (Seção 11:
Templates A/B/C; Seção 12: 6 esqueletos + regra dos terços + alternância
esquerda/direita). O mesmo mecanismo beneficia `arte-01/02/03` e os kits (que
compartilham template e helper). Riscos conhecidos: drift da posição do logo nos
templates atuais (corrigir, §1.2) e cores estendidas de campanha que exigem
homologação para os Templates A/C (§6.2).

**2. Como funciona no fluxo?** Layout é atributo da copy: `redator-arte` grava
`layout` por copy em `arte/copies.json` (catálogo fixo `brand/layouts-arte.json`,
formatos aplicáveis + alternância do manual); `compilador-arte`/`compilador-kit`
resolvem `templates/arte-<dimensao>-layout-<NN>.html` por copy; `validar-layout.py`
confere o marcador `class="layout-<NN>"` no HTML persistido, a aplicabilidade do
layout e 1 layout por peça (sem hibridizar). Total de PNGs não muda (9 arte + 20
kits) — nenhum script de contagem (pool, empacotar, validar-dimensoes/kit) é afetado.

**3. O que atualizar/corrigir/acrescentar?** **Acrescentar:** `brand/layouts-arte.json`,
templates `arte-<dimensao>-layout-<NN>.html`, `scripts/validar-layout.py`.
**Atualizar:** `compilar-arte.py` + `compilar-kit.py`, `_arte_common.py`, skills
`redator-arte`/`redator-kit-copy`/`compilador-arte`/`aplicador-marca-conexao`/
`diretor-de-arte`, agentes `subagente-produtor-arte`/`-kit`, `SPEC_ARTE.md`,
`SPEC_KITS.md`, `SPEC_COMANDOS.md`, `SPEC.md`, `AGENTS.md`. **Corrigir:** posição do
logo nos templates (drift vs design system) e comentário obsoleto em
`validar-logo.py`. `verificar-consistencia-pipeline.py` não muda (não enumera
templates).

**4. Exemplo de aplicação:** implementado em `exemplos/expansao-layout/` — 3
templates 1080×1350 (layout-01 central, layout-02 split foto à esquerda, layout-03
split foto à direita), 3 copies reais do kit-master-flex-02 com eixo layout,
renderizados via `scripts/_arte_common.py` sem tocar em `output/` (REGRA 11).
Verificação determinística: 3 PNGs pixel-perfect < 1 MB, título em 2 linhas sem
overflow, logo topo-esquerda (DS), produto sangrando a base sem sombra (Manual
Seção 11), espelhamento provado por pixels (produto×produto = 2.35 vs produto×fundo
≈ 112).

## 1. Diagnóstico do estado atual

### 1.1 O que existe hoje

- **Eixos:** formato (`arte-01`/`02`/`03` = dimensão do PNG) × copy (3 copies
  compartilhadas em `output/<slug>/arte/copies.json`). Ver `SPEC_ARTE.md`.
- **Layout: único por dimensão.** `templates/arte-1080x1080.html`,
  `arte-1080x1350.html`, `arte-1080x1920.html` são 3 variações de escala do MESMO
  esqueleto: logo no topo, imagem do produto, headline/subcopy/CTA em eixo central.
- **Compartilhamento crítico:** `compilar-kit.py` reusa exatamente
  `templates/arte-1080x1350.html` para as 10 artes dos kits (SPEC_KITS.md) — qualquer
  mudança de layout no template afeta kits também, e hoje as 10 artes de um kit são
  visualmente idênticas na disposição (só texto muda).
- **Resultado:** 9 PNGs de arte (3 copies × 3 formatos) + 20 PNGs de kits (2 kits ×
  10) com a MESMA composição — o operador não tem variação de disposição, e o manual
  recomenda explicitamente alternar (Seção 12: "Alternar foto à esquerda e à direita
  em posts consecutivos"; "Nunca centralizar tudo no eixo horizontal médio").

### 1.2 Drift já existente (corrigir na mesma rodada)

O template atual **contradiz o design system documentado** quanto à posição do logo:

| Fonte | Regra documentada | Template atual (1080×1350) |
|---|---|---|
| `brand/design-system-conexao.json` → `logos.posicao_por_tipo.arte-0N` | "canto superior esquerdo, margem 48px, altura 28px" | centralizado no topo (`left:50%`, `top:83px`, altura 70px) |
| `.claude/skills/aplicador-marca-conexao/SKILL.md` → seção Logo | "canto superior esquerdo do canvas, margem de 48px, altura 28–32px. **Nunca centrado**" | idem (drift) |

Também há drift de comentário em `scripts/validar-logo.py` (`checar_arte`: "o HTML
temporário é apagado após a geração do PNG" — falso desde a rodada multi-copy: os
`index*.html` são persistidos). A rodada de layouts é o momento natural de
re-homologar: cada layout passa a declarar sua própria posição de logo no catálogo, e
o JSON/skill/templates são corrigidos juntos (contrato de sincronização do
aplicador-marca-conexao).

## 2. Modelo proposto: formato × copy × layout

Terceiro eixo ortogonal, mesmo padrão de `docs/05`:

```
                    arte-01         arte-02         arte-03
                  (1080x1080)     (1080x1350)     (1080x1920)
copy-01 layout-02     ✅              ✅              ✅
copy-02 layout-01     ✅              ✅              ✅
copy-03 layout-03     ✅              ✅              ✅
```

**Opção B (recomendada, padrão): layout é atributo da copy.** Cada copy de
`copies.json` declara `layout` (um id do catálogo, restrito aos formatos aplicáveis).
O total de PNGs **não muda** (3 copies × formatos = 9 em arte; 10 por kit) — nenhum
script de contagem (pool, empacotar, validar-dimensoes, validar-kit) precisa mudar.
A regra do manual de alternar esquerda/direita em posts consecutivos é cumprida
atribuindo layouts alternados às copies 1/2/3.

**Opção C (v2, opcional): multiplicador por formato.** `/esbocar` Passo 4 ganha
"quantos layouts por formato?" (1 ou 2). Com 2, cada copy renderiza em 2 layouts →
6 PNGs por formato (18 no total), nomenclatura com 3º eixo
(`..._copy<MM>_lay<NN>.png`) e contagens atualizadas em 5 scripts. Só vale quando o
operador pedir volume; não é o padrão.

### Catálogo de layouts (proposto — `brand/layouts-arte.json`)

Derivado das Seções 11/12 do manual. Cada layout = 1 arquivo de template +
entrada de catálogo (id, nome, origem no manual, formatos aplicáveis, posição do
logo, regras de cor específicas).

| id | Nome | Origem (manual) | Formatos | Notas |
|---|---|---|---|---|
| `layout-01` | Eixo central | Template B (institucional) + esqueleto "eixo central" | 01, 02, 03 | É o template atual. Logo centralizado no topo **ou** corrigido p/ topo-esquerda — re-homologar |
| `layout-02` | Split foto à esquerda | Esqueleto "foto à esquerda" + regras do Template A | 01, 02 | Produto à esquerda sangrando a base, sem sombra; texto à direita. Logo topo-esquerda |
| `layout-03` | Split foto à direita | Esqueleto "foto à direita" (espelho) | 01, 02 | Espelho do 02 — alternância no feed |
| `layout-04` | Triângulo | Esqueleto "triângulo" (kits e conjuntos) | 01, 02 | Massa do produto na base central, título acima |
| `layout-05` | Comercial Template A | Template A (coluna 35% + filete tricolor) | 02 (4:5) | **Exige homologação das cores estendidas de campanha** (marinho `#0B1B3A`, azul story `#12377F`, verde petróleo `#0E5C46`, amarelo faixa `#F5C400`) + lado claro — ver §6.2 |
| `layout-06` | Story parceria Template C | Template C (selo "exclusivo", card de oferta) | 03 | Selo/lettering é elemento fixo nunca redesenhado; reservado a oferta com parceiro |

Regras transversais do manual aplicadas em TODOS os layouts: margem mínima de 6% da
largura; preço/validade nos cruzamentos baixos da regra dos terços (quando houver
preço); 1 esqueleto por peça, sem hibridizar; render do produto recortado, sem fundo
e sem sombra projetada (Template A) — **nunca** texto sobre a área de maior detalhe
do produto.

## 3. Como a expansão funciona no fluxo (passo a passo)

1. **`/esbocar`** — sem mudança obrigatória (Opção B): público/tom/materiais
   continuam as únicas escolhas do operador (REGRA 3). A seleção de layouts é decisão
   de design, feita pelo pipeline. (Opção C adicionaria 1 pergunta no Passo 4/5.)
2. **`diretor-de-arte`** — escreve `brief_criativo.mapeamento_por_material.arte.
   angulos_criativos` como hoje, e passa a poder sugerir `layout_sugerido` por ângulo
   (orientação, não vínculo — o redator valida contra o catálogo e os formatos
   aplicáveis).
3. **`redator-arte`** (1× por projeto) — além de headline/subcopy/CTA, atribui
   `layout` a cada copy: lê o catálogo `brand/layouts-arte.json`, respeita os
   `formatos` aplicáveis do layout escolhido, e aplica a regra de alternância do
   manual (copies consecutivas com disposições diferentes; split-esquerda/direita
   alternados). Grava `output/<slug>/arte/copies.json` com o campo novo.
4. **`compilador-arte`** — para cada formato, para cada copy: resolve o template
   pelo id de layout da copy (`templates/arte-<dimensao>-layout-<NN>.html`) em vez
   de um template fixo por dimensão. O restante (assets, placeholders, render
   Playwright, persistência de `index*.html`) não muda — o contrato de placeholders
   de `preencher_template()` é o mesmo para todo template de arte.
5. **`compilador-kit`** — idem para as 10 copies dos kits: `kits/copies.json` ganha
   `layout` por copy (catálogo restrito a 1080×1350), o que quebra a uniformidade
   visual das 10 artes de um kit.
6. **Validação (REGRA 8)** — `validar-dimensoes.py` (dimensão/peso/contagem)
   permanece; novo `validar-layout.py` (determinístico) confere: (a) o HTML
   persistido de cada copy contém o marcador `class="layout-<NN>"` no `<body>`
   correspondente ao layout atribuído em `copies.json`; (b) o layout pertence aos
   `formatos` aplicáveis do catálogo; (c) 0 hibridização (um único marcador de
   layout por arquivo). Falha → auto-correção (REGRA 4) pelo `compilador-*`.
7. **`revisor-marca` / `auditar-projeto.py` / `empacotar-projeto.py`** — sem mudança
   de contrato: os validadores existentes seguem cobrindo logo/tokens/1 badge; o
   manifesto continua listando pastas `arte-0N` com seus 3 PNGs (Opção B).

## 4. Nomenclatura

Arquivo de template (novo padrão canônico, com renomeação limpa dos atuais):
`templates/arte-<dimensao>-layout-<NN>.html` — ex.: `arte-1080x1350-layout-02.html`.
Os 3 arquivos atuais são renomeados para `-layout-01` (sem alias/legado; cutover
limpo nos 2 compiladores via catálogo).

PNG (Opção B, 2 eixos como hoje): `arte_<slug>_<NN>_copy<MM>.png` — o layout não
entra no nome porque é derivado de `copies.json`; o HTML persistido carrega o
marcador para auditoria. (Opção C acrescentaria `_lay<NN>`.)

## 5. Validação determinística nova

`scripts/validar-layout.py <slug> <variante> --pasta <pasta>`:

1. Lê `output/<slug>/arte/copies.json` (ou `kits/copies.json`) e `brand/layouts-arte.json`.
2. Para cada `index*.html` persistido: extrai `class="layout-<NN>"` do `<body>`.
3. Confere que o marcador bate com o `layout` da copy correspondente (ordem:
   `index.html`=copy-01, `index_copy02.html`=copy-02, ...).
4. Confere `layout ∈ formatos_aplicaveis(dimensao)` do catálogo.
5. Confere exatamente 1 marcador de layout por arquivo (sem hibridização).
6. Exit 0 conforme / 1 não conforme (gate `--estrito` de `auditar-projeto.py`).

## 6. O que ACRESCENTAR, ATUALIZAR e CORRIGIR

### ACRESCENTAR (novos arquivos)

| Arquivo | Conteúdo |
|---|---|
| `brand/layouts-arte.json` | Catálogo fixo de layouts (tabela §2) — id, nome, origem no manual, formatos aplicáveis, template, posição do logo, regras específicas. Fixo de marca, nunca por projeto (REGRA 6) |
| `templates/arte-<dimensao>-layout-<NN>.html` | Um template por layout/dimensão aplicável, com o MESMO contrato de placeholders (`{{LOGO}}`, `{{IMAGEM_PRODUTO}}`, `{{HEADLINE}}`, `{{SUBCOPY}}`, `{{CTA}}`, `{{FORMA_DECORATIVA}}`, `{{BADGE_CONTEXTO}}`, `{{TITULO}}`, `{{NOME_MARCA}}`) + script de ajuste de título + marcador `class="layout-<NN>"` no `<body>` |
| `scripts/validar-layout.py` | Validador determinístico (§5) |
| `docs/11-plano-expansao-variacao-layout-arte.md` | Este documento |
| `exemplos/expansao-layout/` | Prova de conceito funcional (§8) |

### ATUALIZAR (arquivos existentes)

| Arquivo | Mudança |
|---|---|
| `scripts/compilar-arte.py` | Lê `copy["layout"]`; resolve template via catálogo em vez de `arte-<dimensao>.html` fixo |
| `scripts/compilar-kit.py` | Idem para `kits/copies.json` (layouts aplicáveis a 1080×1350) |
| `scripts/_arte_common.py` | Helper `resolver_template_layout(variante, layout)` (lê `brand/layouts-arte.json` → path do template); `preencher_template` inalterado (contrato de placeholders já é genérico) |
| `.claude/skills/redator-arte/SKILL.md` | Escreve `layout` por copy; regras de escolha (catálogo, formatos aplicáveis, alternância do manual, REGRA 6 — nunca inventar layout fora do catálogo) |
| `.claude/skills/redator-kit-copy/SKILL.md` | Idem para as 10 copies dos kits |
| `.claude/skills/compilador-arte/SKILL.md` | Documenta resolução de template por copy/layout; placeholder `{{LAYOUT}}` ou marcador de classe |
| `.claude/skills/aplicador-marca-conexao/SKILL.md` | Seção nova "Layouts de arte" — posição de logo por layout, cores estendidas de campanha (quando homologadas), regras de cada layout (sem sombra, margem 6%, alternância) |
| `.claude/skills/diretor-de-arte/SKILL.md` | `layout_sugerido` opcional por ângulo (orientação) |
| `.claude/agents/subagente-produtor-arte.md` / `subagente-produtor-kit.md` | Passo 2: confirma `layout` válido nas copies antes de compilar; Passo 3: roda `validar-layout.py` junto com `validar-dimensoes.py`/`validar-kit.py` |
| `SPEC_ARTE.md` | Modelo vira "formato × copy × layout"; seção de requisitos ganha "disposição por layout"; validação ganha `validar-layout.py`; nomenclatura de template |
| `SPEC_KITS.md` | Idem (10 copies com layout por copy) |
| `SPEC_COMANDOS.md` | Passos 2.5/2.7: cópias ganham layout; `/gerar-arte*`: entrevista pode perguntar "manter layouts atuais?"; Opção C documentada para o Passo 4 do `/esbocar` |
| `SPEC.md` | Schema do brief: `layout_sugerido` opcional no mapeamento de arte |
| `AGENTS.md` | Diagrama "arquitetura em uma frase" e nota na tabela de módulos: eixo layout (sem novos tipos de material — tabela de módulos inalterada) |
| `scripts/verificar-consistencia-pipeline.py` | **Sem mudança** — o gate mapeia tipos de material, não enumera templates (verificado) |

### CORRIGIR (drifts já presentes, nesta rodada)

| Item | Evidência | Correção |
|---|---|---|
| Posição do logo nos templates de arte | JSON/skill dizem "canto superior esquerdo, margem 48px, altura 28–32px, nunca centrado"; templates centralizam (`left:50%`, `top:83px`, 64–80px) | Re-homologar: cada layout declara a posição no catálogo; `layout-01` decide (recomendação: manter centralizado como as peças entregues, atualizando DS/skill — ou corrigir para topo-esquerda e regenerar as artes, o que exige re-render de projetos existentes; decisão do operador) |
| Comentário obsoleto em `validar-logo.py` (`checar_arte`) | Diz "HTML temporário é apagado" — os `index*.html` são persistidos desde a rodada multi-copy | Atualizar comentário |
| Kits visualmente uniformes | 10 artes de um kit usam o mesmo layout central | Atribuir layout por copy (Opção B) — quebra a monotonia sem mudar contagem |

### Fora de escopo desta rodada (exigem decisão do operador)

- **Cores estendidas de campanha** (marinho `#0B1B3A`, azul story `#12377F`, verde
  petróleo `#0E5C46`, amarelo faixa `#F5C400` + filetes tricolores/gradientes do
  manual): são do Manual da Marca, mas NÃO estão no design system fixo. Para
  `layout-05` (Template A) e `layout-06` (Template C) elas precisam ser homologadas
  como bloco "campanha" do DS (o manual é a autoridade de marca — a homologação é
  legítima, mas é decisão do operador; ver REGRA 6).
- **Template A lado claro**: o DS é fundo escuro (`--bg: #0f172a`) e o logo claro é o
  padrão; o lado claro do Template A exigiria a variante `_texto_preto` + regra de
  não-aplicar dourado sobre o lado claro (manual, Seção 11). Só com homologação.
- **Opção C** (multiplicador de layouts por formato) — v2.
- **Regeneração visual das artes já entregues** — a migração de projetos existentes
  é decisão do operador (REGRA 11: nunca sobrescrever; seria `-v2`).

## 7. Critérios de aceite

- `brand/layouts-arte.json` existe, cobre `layout-01` a `layout-06` com `formatos`
  aplicáveis e `template` resolvível para cada combinação.
- `redator-arte` grava `layout` válido em cada copy de `copies.json`; copies
  consecutivas usam disposições diferentes (alternância do manual).
- `compilar-arte.py` renderiza cada copy no template do layout atribuído; os
  `index*.html` persistidos carregam `class="layout-<NN>"`.
- `validar-layout.py` passa para arte e kits; `validar-dimensoes.py` segue passando
  com exatamente 3 PNGs por formato (Opção B) / 10 por kit.
- `auditar-projeto.py <slug> --estrito` CONFORME; `verificar-consistencia-pipeline.py
  --estrito` CONFORME.
- Nenhum template `layout-01` regride: PNGs novos de um projeto regenerado com
  `layout-01` idênticos aos atuais (mesmo CSS).

## 8. Exemplo de aplicação (implementado)

`exemplos/expansao-layout/` — prova de conceito funcional, fora de `output/` (REGRA
11: não toca material entregue; lê `output/kit-master-flex-02` só como fonte de
insumo, read-only):

```
exemplos/expansao-layout/
├── copies.json                      ← 3 copies reais do kit-master-flex-02 + eixo layout
├── templates/
│   ├── arte-1080x1350-layout-01.html  ← eixo central (template atual, renomeado)
│   ├── arte-1080x1350-layout-02.html  ← split foto à esquerda (novo)
│   └── arte-1080x1350-layout-03.html  ← split foto à direita, espelho (novo)
├── gerar_exemplo.py                ← reusa scripts/_arte_common.py (mesmo helper do pipeline)
└── saida/
    ├── arte_kit-master-flex-02_02_copy01_layout02.png   ← copy-01 → layout-02
    ├── arte_kit-master-flex-02_02_copy02_layout01.png   ← copy-02 → layout-01
    ├── arte_kit-master-flex-02_02_copy03_layout03.png   ← copy-03 → layout-03
    └── index*.html                   ← persistidos com marcador class="layout-<NN>"
```

Decisões do exemplo (registradas para o revisor-marca):
- `layout-02`/`03`: produto à esquerda/direita sangrando a base (barra dourada cobre
  a borda inferior), **sem drop-shadow** (manual Seção 11: render recortado, sem
  sombra projetada); margem lateral de 65px (6% de 1080); logo topo-esquerda 48px
  (DS); headline menor que o central (coluna de texto mais estreita ~425px) — o
  script de ajuste de título segue ativo.
- alternância: copy-01 (problema) → split esquerda, copy-02 (diferencial) → central,
  copy-03 (versatilidade) → split direita — feed de 3 posts variados, regra do
  manual cumprida.
- CTA/assinatura e badge seguem o contrato atual (1 CTA pill, 0 badges de contexto).

## 9. Riscos e mitigação

- **Texto não cabe em coluna estreita (split).** Mitigação: fontes-base por layout
  no catálogo (headline ~2.3rem nos splits vs 3.2rem no central) + script de ajuste
  existente (mín. 55%); se ainda transbordar, REGRA 4: `redator-arte` encurta a copy
  — nunca fonte menor que a marca não usa.
- **Regressão silenciosa do layout atual.** Mitigação: `layout-01` = CSS idêntico ao
  template atual; critério de aceite explícito de paridade visual.
- **Confusão de eixos (formato/copy/layout).** Mitigação: marcador de classe no HTML
  + `validar-layout.py` + nomenclatura de template com os 3 eixos; catálogo é a
  fonte única.
- **Custo de render** — não cresce na Opção B (mesmo nº de PNGs). Opção C cresce
  proporcionalmente e é opt-in.
- **Homologação de cores de campanha pendente** — `layout-05/06` ficam fora até a
  decisão do operador; os layouts 01–04 usam apenas o DS fixo (zero risco de
  violar REGRA 6).
