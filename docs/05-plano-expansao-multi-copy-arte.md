# 05 — Plano de Expansão: Multi-Copy nas Artes (1 Copy × 3 Formatos → 3 Copies × 3 Formatos)

**Status:** implementado nesta rodada · **Escopo:** `scripts/`, `.claude/skills/`, `.claude/agents/`, `.claude/commands/`, `SPEC*.md`, `templates/` (sem alteração), projeto `kit-inlego` (regeneração completa das artes).

## 1. Bug identificado

O pipeline de arte (`arte-01`/`arte-02`/`arte-03`) tratava **formato** (dimensão do
PNG) e **copy** (conceito criativo de headline/subcopy/CTA) como a mesma coisa: cada
`subagente-produtor-arte` invocava `redator-arte` de forma independente para a sua
própria variante, gerando **3 copies diferentes, cada uma presa a 1 formato**:

```
arte-01 (1080x1080)  ← copy A ("deserto anatômico")
arte-02 (1080x1350)  ← copy B ("elimine gambiarras")
arte-03 (1080x1920)  ← copy C ("mandíbula: deserto anatômico")
```

Isso está errado por dois motivos: (1) a mesma peça de comunicação não pode ter uma
mensagem diferente conforme o tamanho em que é publicada — WhatsApp (1080×1080),
Instagram retrato (1080×1350) e Stories (1080×1920) devem poder veicular a **mesma**
ideia; (2) o operador não tinha como escolher *qual* copy usar em qual canal, nem
comparar variações de mensagem lado a lado.

## 2. Modelo correto (aprovado pelo operador)

> 1 copy → 3 artes (mesma mensagem, 3 dimensões). Expandindo: **3 copies → cada copy
> nas 3 dimensões = 9 artes no total.**

```
                    1080x1080   1080x1350   1080x1920
copy-01 (problema)     ✅           ✅           ✅
copy-02 (diferencial)  ✅           ✅           ✅
copy-03 (versatilidade)✅           ✅           ✅
```

Formato (`arte-01`/`arte-02`/`arte-03`, i.e. a dimensão do PNG) e copy
(`copy-01`/`copy-02`/`copy-03`, i.e. o conceito criativo) passam a ser **eixos
ortogonais**. `materiais_selecionados` continua controlando **quais formatos** são
produzidos (o operador pode pedir só `arte-01`, por exemplo); as **3 copies são sempre
as mesmas**, compartilhadas entre todos os formatos selecionados.

## 3. Arquitetura da mudança

### 3.1 Novo artefato compartilhado: `output/<slug>/arte/copies.json`

```jsonc
{
  "copies": [
    {"id": "copy-01", "angulo": "problema", "headline": "...", "subcopy": "...", "cta": "..."},
    {"id": "copy-02", "angulo": "diferencial-tecnico", "headline": "...", "subcopy": "...", "cta": "..."},
    {"id": "copy-03", "angulo": "versatilidade", "headline": "...", "subcopy": "...", "cta": "..."}
  ]
}
```

Escrito **uma única vez** por `redator-arte`, independente de quantos formatos
(`arte-01/02/03`) estejam selecionados. Vive em `output/<slug>/arte/` — pasta auxiliar,
mesmo padrão de `insumos/` e `revisao/` (R12 do `SPEC.md` rege as pastas de material
final, não proíbe pastas auxiliares).

### 3.2 Novo fluxo de orquestração

Antes (bug): cada subagente de formato chamava `redator-arte` por conta própria →
3 chamadas paralelas e independentes → 3 copies divergentes por acidente.

Depois (corrigido): a geração de copy sai do subagente de formato e vira um passo
**compartilhado e único**, executado pelo orquestrador **antes** do fan-out de
qualquer subagente de arte:

```
/produzir-comunicacao-completa
  Passo 2.5 (NOVO) — se qualquer arte-0N estiver selecionado e
                      output/<slug>/arte/copies.json não existir:
                      invoca redator-arte UMA VEZ (inline, não subagente)
  Passo 3 — fan-out por lote
      subagente-produtor-arte (arte-01) → lê copies.json, renderiza 3 PNGs
      subagente-produtor-arte (arte-02) → lê copies.json, renderiza 3 PNGs
      subagente-produtor-arte (arte-03) → lê copies.json, renderiza 3 PNGs
```

Isso garante as 3 copies idênticas em todos os formatos, sem condição de corrida entre
subagentes paralelos (mesma classe de bug do `_pool_estado.json`, corrigida à parte
nesta sessão com file locking).

### 3.3 Nova convenção de nomenclatura

| Antes | Depois |
|---|---|
| `output/<slug>/arte-01/conteudo.json` (1 copy) | `output/<slug>/arte/copies.json` (3 copies, compartilhado) |
| `output/<slug>/arte-01/index.html` (1 arquivo) | `output/<slug>/arte-01/index.html` (copy-01, mantido para `validar-design-tokens.py`/`validar-logo.py`) + `index_copy02.html` + `index_copy03.html` |
| `output/<slug>/arte-01/arte_<slug>_01.png` (1 PNG) | `output/<slug>/arte-01/arte_<slug>_01_copy01.png` + `..._copy02.png` + `..._copy03.png` (3 PNGs) |

Cores/fontes/logo são idênticos entre as 3 copies de um mesmo formato (mesmo template,
mesmo design system) — só o texto varia — por isso basta 1 HTML canônico (`index.html`
= copy-01) para os validadores de marca; os outros 2 HTMLs ficam só para auditoria
manual/`revisor-marca`, sem exigir mudança nos scripts de token/logo.

## 4. Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `scripts/compilar-arte.py` | Lê `arte/copies.json` (não mais `<variante>/conteudo.json`); loop de 3 renders por variante; nomenclatura `_copy0N`. |
| `scripts/validar-dimensoes.py` | Exige exatamente 3 PNGs por variante (antes aceitava ≥ 1). |
| `scripts/pool-materiais.py` | `material_entregue()` para `arte-0N` passa a exigir 3 PNGs no disco (gate de disco), não mais 1. Também corrigido nesta sessão: lock de arquivo em `_pool_estado.json` e suporte ao tipo `textos`. |
| `scripts/empacotar-projeto.py` | Resolver de `arte-0N` no manifesto passa a exigir 3 PNGs válidos e referenciar a pasta (mesmo padrão já usado para `textos`). |
| `.claude/skills/redator-arte/SKILL.md` | Saída muda de "1 copy por variante" para "3 copies compartilhadas" em `output/<slug>/arte/copies.json`; escrito uma única vez. |
| `.claude/skills/compilador-arte/SKILL.md` | Documenta leitura do `copies.json` compartilhado e o loop de 3 renders por variante. |
| `.claude/skills/diretor-de-arte/SKILL.md` | `mapeamento_por_material.arte` passa a ter `angulos_criativos` (3 ângulos, não mais 1 "variação" por formato). |
| `.claude/agents/subagente-produtor-arte.md` | Remove a chamada a `redator-arte` do subagente (agora é passo compartilhado do orquestrador); subagente passa a falhar alto se `copies.json` não existir. |
| `.claude/commands/produzir-comunicacao-completa.md` | Novo Passo 2.5 — geração de copy compartilhada antes do fan-out de arte. |
| `.claude/commands/gerar-arte.md` | Garante `copies.json` antes de despachar subagentes (mesma race que o pipeline completo). |
| `SPEC.md` | Schema de `brief_criativo.mapeamento_por_material.arte` atualizado (`angulos_criativos`, não mais por formato). |
| `SPEC_ARTE.md` | Pipeline, nomenclatura e critério de validação (3 PNGs por variante = 9 no total) reescritos. |
| `.claude/skills/revisor-marca/SKILL.md` | Nota explícita: checar fidelidade de fonte nas 3 copies, não só na primeira. |

Templates (`templates/arte-*.html`) **não mudam** — são reaproveitados 3× por
variante, um render por copy.

## 5. Migração do projeto `kit-inlego`

As 3 copies existentes (uma por formato, incorretamente) são reaproveitadas como ponto
de partida dos 3 ângulos criativos, reescritas para serem format-agnósticas e
cobrindo 3 ângulos distintos do dossiê (nenhum deles usado antes desta forma):

1. **copy-01 — Problema:** "deserto anatômico" / eliminação de gambiarras (elástico,
   resina).
2. **copy-02 — Diferencial técnico:** hastes PEEK lidas como dente natural, sem
   parafuso passante, assentamento passivo.
3. **copy-03 — Versatilidade/eficiência:** Conexão Dupla (2 hastes por pilar) +
   economia de tempo de cadeira ("pela metade") — ângulo ainda não coberto por
   nenhuma arte anterior.

Cada uma das 3 copies é renderizada nos 3 formatos já selecionados em
`config_projeto.materiais_selecionados` (`arte-01`, `arte-02`, `arte-03`), totalizando
**9 PNGs**. Os artefatos antigos (1 copy por formato, 3 PNGs no total) são substituídos
por completo.

## 6. Critérios de aceite

- `output/kit-inlego/arte/copies.json` existe com exatamente 3 copies, cada uma citável
  linha a linha em `dossie_insumos.md` (REGRA 6 — nenhum claim inventado).
- `output/kit-inlego/arte-0N/` (N = 1, 2, 3) contém exatamente 3 PNGs cada
  (`_copy01`, `_copy02`, `_copy03`), pixel-perfect na dimensão da variante, abaixo do
  teto de 1 MB — 9 arquivos no total.
- `scripts/validar-dimensoes.py kit-inlego arte-0N` retorna OK para as 3 variantes.
- `scripts/pool-materiais.py kit-inlego --status` reporta os 3 materiais de arte como
  `concluido_autonomo`.
- `scripts/auditar-projeto.py kit-inlego --estrito` retorna CONFORME.
- `manifesto_materiais.json` referencia as 3 pastas de arte com as 9 peças.

## 7. Riscos e mitigação

- **Risco:** subagentes de formato paralelos gerando copies divergentes de novo no
  futuro (regressão do bug original). **Mitigação:** `compilar-arte.py` falha alto
  (`exit 1`) se `arte/copies.json` não existir ou não tiver exatamente 3 entradas — não
  há caminho silencioso para gerar arte sem o passo de copy compartilhado ter rodado
  antes.
- **Risco:** custo de renderização triplica (9 screenshots Playwright em vez de 3).
  **Mitigação:** aceito — é o comportamento pedido; cada render é leve (HTML/CSS
  local, sem chamada de API).
- **Risco:** confusão entre "formato" (`arte-01/02/03`) e "copy" (`copy-01/02/03`) por
  usarem a mesma numeração `01/02/03`. **Mitigação:** nomenclatura de arquivo sempre
  explicita os dois eixos juntos (`arte_<slug>_<formato>_copy<NN>.png`), nunca um
  número solto.
