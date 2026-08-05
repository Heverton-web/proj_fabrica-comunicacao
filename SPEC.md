# SPEC.md — Especificação Mestre da Fábrica de Materiais de Comunicação

Ver `PRD.md` para a visão de produto e `CLAUDE.md` para as REGRAs invioláveis. Este
documento é o contrato técnico de orquestração. Contratos técnicos por tipo de material
vivem em `SPEC_PDF.md`, `SPEC_HTML.md` e `SPEC_ARTE.md`.

## Requisitos contratuais (R1–R12) — não-negociáveis

| # | Requisito |
|---|---|
| R1 | Entrevista limitada a exatamente 4 rodadas de `AskUserQuestion` dentro de `/esbocar`: (1) imagens + texto-base, (2) público-alvo, (3) objetivo/tom de voz, (4) tipos de material. Nenhuma pergunta adicional depois disso — REGRA 3. |
| R2 | `config_projeto.json` é validado por `scripts/parametros_projeto.py --validar` antes de qualquer produção começar. |
| R3 | O design system é **fixo** (`brand/design-system-conexao.json`), não extraído por projeto — `analista-insumos` não pergunta nem gera tokens de marca, só processa texto-base/imagens e determina `tom_de_voz` (que vai para `brief_criativo.json`). O PDF usa o mesmo arquivo fixo como solução interina até que regras próprias ("Flex Gold") sejam definidas — ver `SPEC_PDF.md`. |
| R4 | Nenhum material contém claim, dado técnico ou benefício ausente do texto-base/imagens fornecidos — verificado por `revisor-marca` (REGRA 6). |
| R5 | Nenhum material usa cor fora de `brand/design-system-conexao.json` — verificado por `scripts/validar-design-tokens.py`. Botão/CTA primário sempre usa o gradiente de assinatura da marca, nunca cor chapada — ver `.claude/skills/aplicador-marca-conexao/SKILL.md`. |
| R6 | PDF (apostila): gerado via Pandoc→`.typ`→Typst, <5MB, texto vetorial extraível, contagem de páginas coerente com o conteúdo. Ver `SPEC_PDF.md`. |
| R7 | Landing page e apresentação: HTML estático autocontido, sem erro de console no Playwright, sem asset quebrado. Ver `SPEC_HTML.md`. |
| R8 | Arte PNG: dimensão pixel-perfect exata por variante (1080×1080 / 1080×1350 / 1080×1920), peso <1MB. Ver `SPEC_ARTE.md`. |
| R9 | Todo material selecionado em `config_projeto.json` termina `concluido_autonomo` ou `esgotado` — nunca fica silenciosamente ausente do relatório final. |
| R10 | Fan-out em lote de 4 (`pool-materiais.py`, `LOTE_PADRAO = 4`) — nunca despachar todos os subagentes de uma vez. |
| R11 | Toda entrega final produz: decisões de design tomadas, informações faltantes, sugestões de legenda/CTA (REGRA 6). `revisor-marca` acumula essas 3 listas em `revisao/parecer_revisao.json`; `empacotar-projeto.py` as consolida em `manifesto_materiais.json`. |
| R12 | `output/<slug>/` segue exatamente: `pdf/`, `landing-page/`, `apresentacao/`, `arte-01/`, `arte-02/`, `arte-03/`, `textos/` — nunca aninhado por marca/data. |

## Máquina de estados (por material)

```
pendente ──(subagente-produtor-<tipo> despachado)──► em_producao
em_producao ──(compilador-<tipo> + validar-*.py OK)──► aguardando_revisao
aguardando_revisao ──(revisor-marca aprova)──► concluido_autonomo
aguardando_revisao ──(revisor-marca reprova, REGRA 4 auto-correção)──► em_producao (retry, backoff)
em_producao ──(3 tentativas esgotadas)──► esgotado
```

Estado persistido em `output/<slug>/_pool_estado.json`, gerido por `scripts/pool-materiais.py`
(porte de `pool-capitulos.py` da referência — mesma interface CLI, unidade = 1 material).

## Fluxo de 2 passos

### Passo 1 — `/esbocar` (única interação humana — exatamente 4 rodadas)

**Rodada 1 — Insumos** (`AskUserQuestion`, até 2 perguntas em 1 chamada):
1. **Imagens** — paths/descrições das imagens do produto/marca a usar.
2. **Texto-base** — path ou conteúdo colado com a informação a comunicar (fonte de verdade de todo claim — REGRA 6).

**Rodada 2 — Público-alvo** (`AskUserQuestion`, seleção única):
- **Consultores** / **Clientes** / **Distribuidores** → gravado em `publico_alvo`.

**Rodada 3 — Objetivo/tom de voz** (`AskUserQuestion`, selection única, opções compostas):
- **Educacional / Comercial** → `educacional_comercial`
- **Informacional / Técnico** → `informacional_tecnico`
- **Comercial / Informacional técnico de parceria de venda** → `comercial_informacional_parceria`

O valor escolhido é gravado em `objetivo_tom` e orienta como o copy é escrito em cada
material. Público-alvo e objetivo/tom são **decisões do operador, fonte de verdade** —
nunca derivadas do texto-base por `analista-insumos`/`diretor-de-arte` (REGRA 6).

**Rodada 4 — Materiais** (`AskUserQuestion`, multiSelect): PDF apostila / Landing Page /
Apresentação / Arte 1080×1080 / Arte 1080×1350 / Arte 1080×1920 / Textos de Apoio (1 a 7 selecionados).

Não há pergunta de design system — é fixo (R3).

Ao final da rodada 4, `/esbocar`:
1. Grava `config_projeto.json` (schema em `## Contratos de dados` abaixo).
2. Roda `analista-insumos` (→ `dossie_insumos.md`, registrando as escolhas do operador como fonte de verdade) e `diretor-de-arte` (→ `brief_criativo.json`, decompõe `objetivo_tom` em `objetivo` + `tom_de_voz`) inline, sem nova pausa.
3. Termina com relatório objetivo + comando sugerido: `/produzir-comunicacao-completa <slug>`.

### Passo 2 — `/produzir-comunicacao-completa <slug>` (autônomo)

1. `parametros_projeto.py --validar` (R2).
2. `pool-materiais.py <slug> --plano --lote 4` → plano de lotes.
3. Para cada lote: despachar `subagente-produtor-<tipo>` de todos os materiais do lote em paralelo, aguardar todos terminarem, cada um roda seu `redator-*` → `compilador-*` → `validar-*.py` → auto-registra via `pool-materiais.py --registrar <tipo> --sucesso|--falha`.
4. Drenar pendentes com backoff exponencial (15s×2^n, máx. 240s, máx. 3 tentativas).
5. `revisor-marca` audita o lote de materiais concluídos (fidelidade de fonte + marca).
6. `auditar-projeto.py <slug> --estrito` — gate determinístico final (R4, R5, R9).
7. `empacotar-projeto.py <slug>` → monta `output/<slug>/` final + `manifesto_materiais.json`.
8. Relatório final consolidado (telegráfico, REGRA 2): materiais entregues, esgotados, decisões de design, faltantes, sugestões de legenda.

## Contratos de dados (JSON)

```jsonc
// output/<slug>/config_projeto.json
{
  "slug": "kit-master-flex",
  "texto_base": "insumos/texto_base.md",
  "imagens": [{"path": "insumos/produto.png", "descricao": "foto oficial do kit"}],
  // Rodada 2 — escolha única do operador:
  "publico_alvo": "consultores",   // consultores | clientes | distribuidores
  // Rodada 3 — escolha única do operador (objetivo/tom compostos):
  "objetivo_tom": "informacional_tecnico",
  //   educacional_comercial | informacional_tecnico | comercial_informacional_parceria
  "materiais_selecionados": ["pdf", "landing-page", "arte-01", "arte-02", "arte-03", "textos"],
  "edicao": "1ª Edição"           // Obrigatório se 'pdf' estiver em materiais_selecionados
}
```

Não há mais `design_tokens.json` por projeto — o design system é fixo em
`brand/design-system-conexao.json` (ver `.claude/skills/aplicador-marca-conexao/SKILL.md`),
igual para todos os projetos, em landing-page/apresentacao/arte. O PDF usa o mesmo
arquivo como solução interina (ver `SPEC_PDF.md`).

```jsonc
// output/<slug>/brief_criativo.json
{
  "mensagem_central": "Um único kit para todos os implantes.",
  // Escolhas do operador (rodadas 2 e 3) — fonte de verdade, nunca derivadas:
  "publico_alvo": "consultores",
  "objetivo_tom": "informacional_tecnico",  // escolha bruta preservada
  "objetivo": "informacional",              // educacional | informacional | comercial
  "tom_de_voz": "tecnico",                  // comercial | tecnico | informacional_tecnico_de_parceria_de_venda
  "nota_de_escopo": "opcional — registrar aqui decisões de interpretação de escopo confirmadas com o operador (ex.: material interno vs. externo)",
  "hierarquia_de_conteudo": ["problema clínico", "solução", "destaques técnicos", "composição do kit", "aplicação clínica"],
  "mapeamento_por_material": {
    "pdf": {"secoes": ["abertura", "problema", "solução", "destaques", "composição", "aplicação", "fechamento"]},
    "landing-page": {"secoes": ["hero", "problema-solução", "destaques", "prova/composição", "cta"]},
    "apresentacao": {"slides": ["capa", "problema", "solução", "destaques (1 por slide)", "cta"]},
    // "arte" e compartilhado entre arte-01/02/03 selecionados — formato (dimensao)
    // e copy (conceito criativo) sao eixos ortogonais (ver
    // docs/05-plano-expansao-multi-copy-arte.md). Exatamente 3 angulos, cada um
    // renderizado depois em TODOS os formatos selecionados (nunca 1 angulo por
    // formato):
    "arte": {"angulos_criativos": ["problema (capa isca)", "diferencial técnico", "versatilidade/eficiência"]},
    "textos": {"canais": ["whatsapp", "instagram", "linkedin"]}
  }
}
```

```jsonc
// output/<slug>/manifesto_materiais.json
{
  "slug": "kit-master-flex",
  "materiais": [
    {"tipo": "pdf", "status": "concluido_autonomo", "path": "pdf/apostila_kit-master-flex.pdf"},
    {"tipo": "arte-01", "status": "concluido_autonomo", "path": "arte-01/"},  // pasta com 3 PNGs (1 por copy)
    {"tipo": "textos", "status": "concluido_autonomo", "path": "textos/"}
  ],
  "decisoes_design": ["Paleta extraída da peça de referência (navy + dourado metálico)."],
  "informacoes_faltantes": ["Torque recomendado para o modelo XL não estava no texto-base."],
  "sugestoes_legenda": ["Um único kit. Todas as plataformas. Conheça o Master Flex.", "..."]
}
```

## Edge cases

- **Texto-base insuficiente para preencher todas as seções do brief:** `redator-*` preenche o que tem evidência e lista o restante como faltante — nunca inventa (REGRA 6).
- **Material esgotado após 3 tentativas:** aparece em `manifesto_materiais.json` com `status: "esgotado"` e motivo; os demais materiais são entregues normalmente (R9).
- **Fonte da marca (Poppins/Inter) não instalada na máquina de build do PDF:** `scripts/parametros_projeto.py` detecta via `typst fonts` e cai para `Arial` com aviso — nunca falha silenciosamente. Registrar como faltante ("instalar fonte no ambiente de build") em vez de aceitar o fallback como definitivo.
- **Texto-base ambíguo sobre escopo interno vs. externo do material** (ex.: guia de vendas com script/objeções, mas materiais externos foram selecionados): não decidir sozinho — `/esbocar` deve confirmar com o operador antes de produzir (excepciona a autonomia da REGRA 3, é uma decisão de escopo, não de conteúdo/design) e registrar a decisão em `brief_criativo.nota_de_escopo`.
