# SPEC_KITS.md — Contrato Técnico: Kit do Consultor e Kit Distribuidor

Ver `SPEC.md` para o fluxo geral, `SPEC_ARTE.md` para a técnica de renderização
reaproveitada, e `docs/06-plano-expansao-kits-consultor-distribuidor.md` para o
histórico da decisão. Este documento cobre os materiais `kit-consultor` e
`kit-distribuidor`.

## Modelo: predefinições fixas, kit-variante × tom × item

Os kits têm 4 predefinições **sempre fixas** (não fazem parte da entrevista do
`/esbocar`, exceto a seleção sim/não em `materiais_selecionados`):

| Predefinição | Valor fixo | Fonte |
|---|---|---|
| Público-alvo | `dentista_implantodontista` | `brand/publicos-alvo.json` |
| Produto | O produto foco do projeto atual | `dossie_insumos.md` / `config_projeto.imagens[0]` |
| Tons de voz | 5: `informativa`, `contra-intuitiva`, `tecnica`, `efeito-uau`, `educativa` | `brand/tons-kit.json` |
| Formato de arte | Único: 1080×1350 | `brand/kits-conexao.json` |

**`kit-consultor` e `kit-distribuidor` compartilham o mesmo conteúdo-base.** As 10
copies (2 por tom × 5 tons) são escritas **uma única vez** por projeto — o que muda
entre os 2 kits é **apenas o CTA final e a assinatura de rodapé**
(`brand/kits-conexao.json.variantes`), aplicados de forma determinística (sem 2ª
chamada de LLM) no momento da renderização. Formato (dimensão) já é único nos kits —
o eixo ortogonal aqui é **kit-variante** (consultor/distribuidor), análogo ao papel que
"formato" tem em `SPEC_ARTE.md` para as 3 copies de arte-01/02/03.

Cada kit contém **10 itens** (5 tons × 2 variações por tom), cada item = 1 copy + 1 PNG
1080×1350 + 1 texto de WhatsApp — 30 arquivos por kit, 60 no total quando os 2 kits são
selecionados.

## Pipeline

1. `redator-kit-copy` — roda **uma única vez por projeto**, nunca por kit. Lê
   `brief_criativo.mapeamento_por_material.kit.angulos_por_tom` (2 ângulos por tom,
   definidos por `diretor-de-arte`) + `brand/tons-kit.json` + `dossie_insumos.md`, e
   escreve `output/<slug>/kits/copies.json` com as 10 copies **sem CTA final**
   (kit-agnóstico — o CTA é responsabilidade de `compilador-kit`, não do redator).
2. `compilador-kit` — para cada kit-variante selecionado, lê `kits/copies.json` +
   `brand/kits-conexao.json.variantes.<kit>` e, para cada uma das 10 copies: renderiza
   o PNG 1080×1350 (reaproveitando `templates/arte-1080x1350.html` + a técnica
   Playwright de `SPEC_ARTE.md`, via helper compartilhado `scripts/_arte_common.py`) e
   escreve o `texto_whatsapp.txt` correspondente (copy + CTA/assinatura da variante).
3. `scripts/validar-kit.py` — confirma a estrutura completa (seção "Validação" abaixo).

**Disciplina de orquestração (crítica, mesma classe de bug já corrigida em
`SPEC_ARTE.md`):** a geração de copy é um passo compartilhado e único, executado pelo
orquestrador (`/produzir-comunicacao-completa`, Passo 2.7) **antes** de despachar
qualquer `subagente-produtor-kit`. Gerar copy dentro de cada subagente de kit
reintroduziria divergência entre `kit-consultor` e `kit-distribuidor` (que devem ter as
10 copies **idênticas**, exceto CTA).

## Estrutura de diretórios

```
output/<slug>/
├── kits/
│   └── copies.json                     ← 10 copies compartilhadas (pasta auxiliar,
│                                          mesmo papel de insumos/, revisao/, arte/)
├── kit-consultor/
│   ├── artes-informativas/{arte-01,arte-02}/
│   ├── artes-contra-intuitivas/{arte-01,arte-02}/
│   ├── artes-tecnicas/{arte-01,arte-02}/
│   ├── artes-efeito-uau/{arte-01,arte-02}/
│   └── artes-educativas/{arte-01,arte-02}/
└── kit-distribuidor/
    └── (estrutura idêntica — mesmas 10 copies, CTA/assinatura diferente)
```

Cada `arte-0N/` tem exatamente 3 **entregáveis**: `conteudo.json` (copy final, já com
CTA/assinatura da variante), `arte_<slug>_<kit-variante>_<tom>_<NN>.png` (1080×1350),
`texto_whatsapp.txt` — essa é a contagem que `validar-kit.py` verifica. Além deles, a
pasta também guarda `index.html` (renderização mantida, não temporária, mesma
disciplina de `SPEC_ARTE.md`, para permitir auditoria de marca) e `assets/`
(fontes/logo/produto copiados) — auxiliares de build, não contam na validação.

## Nomenclatura de arquivo

`arte_<slug>_<kit-variante>_<tom>_<NN>.png`, ex.:
`arte_kit-inlego_kit-consultor_informativa_01.png`. Os três eixos (kit, tom, item)
aparecem sempre juntos — nunca um número solto (mesma disciplina de
`arte_<slug>_<formato>_copy<NN>.png` em `SPEC_ARTE.md`).

## Artefato compartilhado: `output/<slug>/kits/copies.json`

```jsonc
{
  "copies": [
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
  ]
}
```

Sem campo `cta` — o CTA é sempre resolvido em tempo de renderização a partir de
`brand/kits-conexao.json.variantes.<kit>.cta_padrao`, nunca escrito pelo redator.

## Requisitos técnicos

- Dimensão **pixel-perfect exata** 1080×1350, viewport do Playwright fixado igual
  (mesma regra de `SPEC_ARTE.md`).
- Limites de caractere por copy: headline ≤ 60 caracteres, subcopy ≤ 120 caracteres
  (mesmos tetos de `SPEC_ARTE.md` — o CTA da variante já é fixo e curto por definição
  em `brand/kits-conexao.json`, não precisa de limite adicional).
- Teto de peso: 1 MB por PNG (mesmo de `SPEC_ARTE.md`).
- Título em no máximo 2 linhas, nunca 1 palavra sozinha numa linha, largura igual à
  do parágrafo (mesma regra e mesmo template `arte-1080x1350.html` de `SPEC_ARTE.md`
  — os kits reaproveitam o script de ajuste embutido no template, nada específico
  de kit a implementar aqui).
- **1 Badge por Peça (endurecimento):** mesma regra de `SPEC_ARTE.md` — cada PNG tem
  exatamente 1 elemento tipo badge (o CTA pill `class="cta"` da variante) e nenhum
  badge de contexto (`class="badge"`). Validado por `validar-kit.py` sobre os
  `index*.html` persistidos (0 badges de contexto, exatamente 1 CTA por arquivo).
- Elementos geométricos/wave decorativos de fundo: mesma regra de `SPEC_ARTE.md`,
  aqui o **bloco** é o par kit-variante×tom (as 2 artes de 1 tom de 1 kit
  compartilham forma/posição/tamanho/opacidade) — opt-out via
  `config_projeto.elementos_decorativos: false`, mesmo campo dos demais materiais
  de arte.
- `texto_whatsapp.txt`: mensagem curta pronta para envio, montada deterministicamente
  (sem 2ª chamada de LLM) a partir da copy + `brand/kits-conexao.json`, sempre com:
  gancho de abertura por tom em itálico (gera curiosidade — "causa", sem inventar
  claim novo, ver `TOM_GANCHO` em `scripts/compilar-kit.py`), headline em **negrito**,
  subcopy como bullet point (▪️), CTA comercial em destaque (negrito + emoji 👉) e
  assinatura da variante em itálico. UTF-8, não vazio.
- As 10 copies de um projeto devem cobrir os 5 tons de `brand/tons-kit.json`, 2 por
  tom, cada uma um ângulo genuinamente distinto do dossiê (nunca 2 variações do mesmo
  ângulo dentro do mesmo tom, nem ângulos repetidos entre tons).
- Nenhum claim/número fora de `dossie_insumos.md` (REGRA 6, AGENTS.md).

## Validação (`scripts/validar-kit.py`)

```
python scripts/validar-kit.py <slug> kit-consultor
python scripts/validar-kit.py <slug> kit-distribuidor
```

Critérios (exit 1 se qualquer falhar):
- As 5 pastas de tom existem: `artes-informativas`, `artes-contra-intuitivas`,
  `artes-tecnicas`, `artes-efeito-uau`, `artes-educativas`.
- Cada uma tem exatamente 2 subpastas `arte-01`/`arte-02`.
- Cada `arte-0N` tem exatamente 1 PNG 1080×1350 (pixel-perfect, < 1 MB), 1
  `conteudo.json` não vazio, 1 `texto_whatsapp.txt` não vazio em UTF-8.
- Total: 10 PNGs + 10 `conteudo.json` + 10 `texto_whatsapp.txt` por kit — contagem
  exata, mesma disciplina de `validar-dimensoes.py` para as 3 copies de arte-0N.

## Revisão de marca (`revisor-marca`)

Além dos critérios padrão (fidelidade de fonte + marca, ver `SKILL.md` de
`revisor-marca`), os kits têm um critério específico: as 10 copies de
`kit-consultor` e `kit-distribuidor` devem ser **idênticas** exceto pelo CTA final e
assinatura — qualquer outra divergência de headline/subcopy entre os 2 kits é defeito
(reintrodução do bug de conteúdo divergente que esta arquitetura existe para evitar).
