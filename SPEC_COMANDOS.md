# SPEC_COMANDOS.md — Contrato Universal dos Comandos da Fábrica

Este documento é a **fonte única de verdade** do procedimento completo de cada
comando da fábrica — `/esbocar`, `/produzir-comunicacao-completa`, `/gerar-pdf`,
`/gerar-landing`, `/gerar-apresentacao`, `/gerar-arte`. Funciona em **qualquer
harness** que leia os arquivos deste repositório (Claude Code, Antigravity,
OpenCode, Freebuff, MiMoCode, Gemini CLI, CodeBuddy, Qoder, ou qualquer outro
assistente de código) — não depende do mecanismo nativo de "slash command" de
nenhuma ferramenta específica.

## Como qualquer harness deve reconhecer e executar um comando

Um comando é reconhecido tanto pela string literal (`/esbocar <argumentos>`) quanto
por um pedido equivalente em linguagem natural do operador (ex.: "inicie a fábrica
para o Kit inLego", "produza a comunicação completa do kit-inlego", "regenere só o
PDF do projeto X"). Em ambos os casos, o agente deve:

1. Identificar a seção correspondente abaixo.
2. Ler essa seção **por completo** antes de agir (REGRA 7 do `AGENTS.md` — nunca
   truncar/grepar instrução de orquestração).
3. Executar exatamente o procedimento descrito, sem pular passos.

Em harnesses onde o Claude Code descobre comandos automaticamente via
`.claude/commands/*.md`, esses arquivos existem apenas como **ponteiros finos**
para este documento (evita duplicar e desalinhar a mesma instrução em 2 lugares —
mesma lição do bug histórico de `TIPOS_VALIDOS` duplicado entre
`parametros_projeto.py` e `auditar-projeto.py`, ver `docs/`). Este arquivo
(`SPEC_COMANDOS.md`) é sempre a versão canônica; se algum dia os dois divergirem,
este documento vence.

### Nota sobre `AskUserQuestion`

Onde o procedimento abaixo menciona `AskUserQuestion`, é a ferramenta nativa do
Claude Code para perguntas estruturadas com opções (usada nas rodadas de
`/esbocar`). Harnesses sem essa ferramenta devem fazer a **mesma pergunta em texto
simples**, listando as opções numeradas e aguardando a resposta do operador antes
de continuar. O que importa é o **conteúdo, a ordem e o número de rodadas** (R1 do
`SPEC.md` — exatamente 4 rodadas de interação humana), nunca o mecanismo de UI
usado para exibir a pergunta.

---

## `/esbocar`

Ponto de entrada da fábrica. Roda o Passo 1 do fluxo descrito em `SPEC.md` (a
entrevista em 4 rodadas) — a única interação humana real de todo o pipeline. Depois
disso, autonomia total (REGRA 3 do `AGENTS.md`).

`<argumentos>` pode conter um tema/nome de produto já dito pelo operador na mensagem
que disparou o comando — use-o como ponto de partida, mas as perguntas abaixo
continuam obrigatórias.

**Não pergunte sobre design system.** A marca é fixa (`brand/design-system-conexao.json`,
aplicada por `.claude/skills/aplicador-marca-conexao/SKILL.md`) para landing-page,
apresentação e arte — não é mais extraída por projeto. O PDF usa o mesmo arquivo fixo
como solução interina até que regras próprias de PDF ("Flex Gold") sejam desenhadas.

**Não derive tom de voz nem público-alvo do texto-base.** Desde a revisão da interação
humana, essas são **escolhas explícitas do operador** (rodadas 2 e 3) — a fonte de
verdade delas é o `config_projeto.json`, não a leitura do texto-base por
`analista-insumos` (ver `SPEC.md`).

### Passo 0 — slug

Derive um slug kebab-case a partir do nome do produto/projeto (se ainda não souber o
nome, pergunte isso como parte do Passo 1). Se `output/<slug>/` já existir, sufixe
`-v2`, `-v3`... automaticamente — nunca pergunte sobre isso (REGRA 3).

### Passo 1 — Entrevista de insumos (rodada 1)

Pergunte, numa única rodada, com até 3 perguntas:

1. **Nome do produto/projeto** — apenas se ainda não for conhecido (ver Passo 0).
2. **Imagens** — "Quais imagens você quer usar (produto, marca, logo)? Informe o
   caminho de cada arquivo ou anexe agora." (texto livre)
3. **Texto-base** — "Qual o texto-base com a informação a comunicar? Cole aqui ou
   informe o caminho de um arquivo." (texto livre)

Trate qualquer resposta livre/"Other" como válida — nunca pergunte de novo
(REGRA 3, mesma disciplina do `/esbocar` da Fábrica Agêntica de Livros).

### Passo 2 — Entrevista de público-alvo (rodada 2, seleção única)

Uma única pergunta, seleção única, com as 3 opções:

- Consultores
- Clientes
- Distribuidores

O valor escolhido é gravado em `config_projeto.publico_alvo` e vira fonte de verdade
para todos os `redator-*` — nunca o rederive do texto-base.

### Passo 3 — Entrevista de objetivo/tom de voz (rodada 3, seleção única)

Uma única pergunta, seleção única, com as 3 opções compostas (objetivo / tom):

- **Educacional / Comercial** → `educacional_comercial`
- **Informacional / Técnico** → `informacional_tecnico`
- **Comercial / Informacional técnico de parceria de venda** → `comercial_informacional_parceria`

O valor escolhido é gravado em `config_projeto.objetivo_tom` e orienta como o copy é
escrito em cada material — nunca o rederive do texto-base.

### Passo 4 — Entrevista de materiais (rodada 4, multiSelect)

9 opções no total. Se o mecanismo de pergunta do harness limitar quantas opções
cabem numa única pergunta (no Claude Code, `AskUserQuestion` permite até 4 opções
por pergunta e até 4 perguntas por chamada), divida em partes — ainda dentro da
**mesma rodada 4** (nunca conte como rodadas adicionais):

- Parte 1/3: PDF (apostila), Landing Page, Apresentação
- Parte 2/3: Arte 1080×1080 (WhatsApp/Instagram quadrado), Arte 1080×1350
  (Instagram/LinkedIn retrato), Arte 1080×1920 (Stories/Reels)
- Parte 3/3: Textos de Apoio (WhatsApp/Instagram/LinkedIn), Kit do Consultor (10
  artes 1080×1350 + copies + textos de WhatsApp, para Dentista/Implantodontista), Kit
  Distribuidor (mesmo conteúdo do Kit do Consultor, CTA/assinatura de distribuidor —
  ver `SPEC_KITS.md`)

Exija pelo menos 1 selecionado no total (soma das 3 partes) — se vier vazio, assuma
todos os 9 (nunca pare para confirmar, REGRA 3).

**Kit do Consultor e Kit Distribuidor não têm predefinições próprias a perguntar** —
público (Dentista/Implantodontista), produto (o do projeto atual), 5 tons de voz e
formato (1080×1350) são sempre fixos (`brand/tons-kit.json`, `brand/kits-conexao.json`,
`brand/publicos-alvo.json`). Selecionar qualquer um dos 2 já é suficiente para o
`/produzir-comunicacao-completa` gerar o kit completo (10 itens) sem nova pergunta.

**Se o material "PDF (apostila)" for selecionado:** pergunte adicionalmente na mesma
rodada (ou em uma pergunta subsequente) para o operador definir a **edição do
material** (ex.: "1ª Edição", "2ª Edição Revisada"). Esse valor deve ser gravado
obrigatoriamente no campo `edicao` de `config_projeto.json` para que os validadores e
templates o processem de forma correta.

### Passo 5 — Elementos gráficos decorativos (opcional, mesma rodada 4)

Se qualquer material de arte estiver selecionado (`arte-01`/`arte-02`/`arte-03`/
`kit-consultor`/`kit-distribuidor`), pergunte adicionalmente — mesma disciplina da
edição do PDF acima, dentro da rodada 4 ou como pergunta subsequente, **nunca como
uma 5ª rodada nova** (R1 do `SPEC.md` continua valendo: são sempre 4 rodadas de
interação estruturada) — se o operador quer ativar os elementos gráficos decorativos
de fundo (formas geométricas/waves com borda fina dourada e opacidade baixa, para dar
profundidade — ver `SPEC_ARTE.md`):

- Sim, ativar elementos decorativos (padrão recomendado)
- Não, manter fundo limpo (sem elementos decorativos)

Grave a escolha em `config_projeto.elementos_decorativos` (booleano). Se o operador
não selecionar nenhum material de arte, não pergunte isso (campo fica ausente do
JSON). Se pular a pergunta ou não especificar, assuma `true` (nunca trave por
ausência de resposta, REGRA 3) — `compilador-arte`/`compilador-kit` só omitem os
elementos decorativos quando o campo existir e for explicitamente `false`.

### Passo 6 — Gravar e preparar (sem nova pausa)

1. Crie `output/<slug>/insumos/` e copie/referencie os arquivos de imagem/texto-base
   informados.
2. Grave `output/<slug>/config_projeto.json` (schema em `SPEC.md` — sem campo
   `design_system`, ele não existe mais; com `publico_alvo` e `objetivo_tom` das
   rodadas 2 e 3; com `elementos_decorativos` se o Passo 5 se aplicou).
3. Rode `python scripts/parametros_projeto.py <slug> --validar` — se falhar, corrija o
   JSON você mesmo antes de seguir (REGRA 4), nunca devolva o erro bruto ao operador.
4. Invoque o skill `analista-insumos` → gera `dossie_insumos.md` (fatos do texto-base +
   inventário de imagens + as escolhas do operador registradas como fonte de verdade).
5. Invoque o skill `diretor-de-arte` → gera `brief_criativo.json` (decompõe
   `objetivo_tom` em `objetivo` + `tom_de_voz`; carrega `publico_alvo` do operador).

### Passo 7 — Relatório objetivo (REGRA 2 — sem preâmbulo)

Reporte, de forma telegráfica:
- Slug do projeto e onde ficou salvo.
- Público-alvo escolhido e objetivo/tom escolhido.
- Materiais selecionados.
- Qualquer faltante já identificado por `analista-insumos` (ex.: imagem citada no
  texto-base mas não localizada).
- Comando sugerido: `/produzir-comunicacao-completa <slug>`.

---

## `/produzir-comunicacao-completa`

`<argumentos>` = `<slug>`. Se `output/<slug>/config_projeto.json` não existir, rode
`/esbocar` primeiro (inline, sem novo comando do operador) e só então continue.

Este comando não pausa para nenhuma pergunta (REGRA 3). Ver `SPEC.md` para o contrato
completo do Passo 2.

### Passo 0 — Validação de pré-condições

```
python scripts/parametros_projeto.py <slug> --validar
```

Se `brief_criativo.json` ainda não existir (ex.: operador rodou `/esbocar` mas a sessão
foi interrompida antes do Passo 6 dele — gravação e preparação), invoque
`analista-insumos` e `diretor-de-arte` agora, sem perguntar nada ao operador.

### Passo 1 — Pre-flight de compatibilidade de slug

```
python scripts/preflight-compatibilidade-slug.py <slug> --estrito
```

Roda uma única vez, antes de qualquer fan-out, para detectar se algum
`scripts/compilar-*.py` compartilhado tem string de outro projeto hardcoded (mesma
causa raiz do bug de path de imagem já corrigido em `compilar-html.py`/
`compilar-arte.py`/`compilar-pdf.py`/`compilar-kit.py`). Se retornar não-conforme,
corrija o compilador apontado (REGRA 4) antes de prosseguir — evita que múltiplos
subagentes descubram o mesmo problema de forma redundante durante a produção real.

### Passo 2 — Plano de lotes

```
python scripts/pool-materiais.py <slug> --plano --lote 4
```

Imprime os materiais de `materiais_selecionados` divididos em lotes de até 4.

### Passo 2.5 — Copy compartilhada de arte (uma única vez, antes de qualquer fan-out de arte)

Se qualquer `arte-01`/`arte-02`/`arte-03` estiver em `materiais_selecionados` e
`output/<slug>/arte/copies.json` ainda não existir (ou não tiver exatamente 3 copies),
invoque o skill `redator-arte` **inline, agora, uma única vez** — nunca delegue isso a
um `subagente-produtor-arte`. Formato (dimensão do PNG) e copy (conceito criativo) são
eixos ortogonais: as mesmas 3 copies são compartilhadas por todos os formatos
selecionados (ver `docs/05-plano-expansao-multi-copy-arte.md`). Gerar a copy dentro de
cada subagente de formato reintroduz o bug original — 3 subagentes paralelos
descobrindo/escrevendo 3 copies divergentes em vez de reaproveitar as mesmas 3 em todos
os formatos.

Este passo precisa terminar **antes** de despachar o lote que contém qualquer
`arte-0N`, mesmo que esse lote não seja o primeiro.

### Passo 2.7 — Copy compartilhada de kit (uma única vez, antes de qualquer fan-out de kit)

Se qualquer `kit-consultor`/`kit-distribuidor` estiver em `materiais_selecionados` e
`output/<slug>/kits/copies.json` ainda não existir (ou não tiver exatamente 10
copies), invoque o skill `redator-kit-copy` **inline, agora, uma única vez** — nunca
delegue isso a um `subagente-produtor-kit`. Kit-variante (consultor/distribuidor) é
eixo ortogonal a copy: as mesmas 10 copies são compartilhadas pelos 2 kits, só o CTA
final muda (`brand/kits-conexao.json`, resolvido por `compilador-kit`, sem 2ª chamada
de LLM). Ver `SPEC_KITS.md`. Gerar copy dentro de cada subagente de kit reintroduziria
divergência de conteúdo entre `kit-consultor` e `kit-distribuidor`.

Este passo precisa terminar **antes** de despachar o lote que contém qualquer
`kit-consultor`/`kit-distribuidor`, mesmo que esse lote não seja o primeiro.

### Passo 3 — Fan-out em lote (disciplina de concorrência — nunca tudo de uma vez)

Para cada lote do plano, **nesta ordem, sem pular etapas**:

1. Despache, na mesma mensagem/rodada, um subagente por material do lote:
   - `pdf` → `subagente-produtor-pdf`
   - `landing-page` → `subagente-produtor-landing`
   - `apresentacao` → `subagente-produtor-apresentacao`
   - `arte-01`/`arte-02`/`arte-03` → `subagente-produtor-arte` (um por variante —
     requer que o Passo 2.5 já tenha gerado `arte/copies.json`)
   - `textos` → `subagente-produtor-textos`
   - `kit-consultor`/`kit-distribuidor` → `subagente-produtor-kit` (um por kit —
     requer que o Passo 2.7 já tenha gerado `kits/copies.json`)
2. Aguarde **todos** os subagentes do lote terminarem (cada um já auto-registra sucesso
   ou falha via `pool-materiais.py --registrar`).
3. Só então consulte `python scripts/pool-materiais.py <slug> --proximo-lote --lote 4`
   e despache o próximo lote.

Depois de todos os lotes planejados, drene pendentes:

```
python scripts/pool-materiais.py <slug> --pendentes --lote 4
```

Retentar com o backoff indicado (15s × 2^tentativas, máx. 240s), máximo 3 tentativas
por material — depois disso o material fica `esgotado` e é reportado, não bloqueia os
demais (R9 do `SPEC.md`).

### Passo 4 — Revisão de marca em lote

Se o total de materiais `concluido_autonomo` for **até 6**, despache **1 único**
`subagente-revisor-marca` cobrindo todos eles — reduz overhead de reconstrução de
contexto por subagente sem abrir mão da REGRA 7 (o subagente ainda lê tudo por
completo, só há menos subagentes no total). Se o total for **maior que 6**, divida em
lotes de até 6 (cada um só toca nos tipos do seu próprio lote, nunca todos de uma vez).

### Passo 5 — Auditoria final determinística

```
python scripts/auditar-projeto.py <slug> --estrito
```

Se retornar não-conforme, aplique as correções indicadas (REGRA 4) e rode de novo —
até 3 rodadas. Se ainda não-conforme na 3ª rodada, siga para o empacotamento mesmo
assim, reportando as não-conformidades residuais (nunca trave a entrega dos materiais
que já estão conformes).

### Passo 6 — Empacotamento final

```
python scripts/empacotar-projeto.py <slug>
```

Monta a estrutura final em
`output/<slug>/{pdf,landing-page,apresentacao,arte-01,arte-02,arte-03,textos,kit-consultor,kit-distribuidor}/`
e grava `manifesto_materiais.json`.

### Passo 7 — Relatório final (REGRA 2 — telegráfico, sem preâmbulo)

Reporte: materiais entregues (com path), materiais esgotados (com motivo), decisões de
design tomadas, informações faltantes, sugestões de legenda/CTA para compartilhamento
(REGRA 6/R11 do `SPEC.md`).

---

## `/gerar-pdf`

`<argumentos>` = `<slug>`. Regeneração pontual — nunca re-executa `/esbocar` nem
`analista-insumos`/`diretor-de-arte`.

**Pré-condição (falhe rápido se ausente):** confirme que `output/<slug>/brief_criativo.json`
existe. Se não existir, pare e informe: "Rode `/esbocar` (ou
`/produzir-comunicacao-completa <slug>`) primeiro — este projeto ainda não tem brief
criativo." Nunca invente um brief para contornar isso.

### Procedimento

1. Se `pdf` não estiver em `config_projeto.materiais_selecionados`, adicione-o (o
   operador está pedindo explicitamente este material agora).
2. Despache `subagente-produtor-pdf` para `<slug>`.
3. Despache `subagente-revisor-marca` só para o tipo `pdf`.
4. Rode `python scripts/auditar-projeto.py <slug> --estrito --apenas pdf`.
5. Rode `python scripts/empacotar-projeto.py <slug>` (reempacota o manifesto sem tocar
   nos outros materiais já entregues).
6. Reporte (REGRA 2): path do PDF final, decisões de design, faltantes, sugestão de
   legenda de compartilhamento.

---

## `/gerar-landing`

`<argumentos>` = `<slug>`. Regeneração pontual — nunca re-executa `/esbocar` nem
`analista-insumos`/`diretor-de-arte`.

**Pré-condição:** mesma checagem de `brief_criativo.json` de `/gerar-pdf` acima.

### Procedimento

1. Se `landing-page` não estiver em `config_projeto.materiais_selecionados`, adicione-o.
2. Despache `subagente-produtor-landing` para `<slug>`.
3. Despache `subagente-revisor-marca` só para o tipo `landing-page`.
4. Rode `python scripts/auditar-projeto.py <slug> --estrito --apenas landing-page`.
5. Rode `python scripts/empacotar-projeto.py <slug>`.
6. Reporte (REGRA 2): path do `index.html`, decisões de design, faltantes.

---

## `/gerar-apresentacao`

`<argumentos>` = `<slug>`. Regeneração pontual — nunca re-executa `/esbocar` nem
`analista-insumos`/`diretor-de-arte`.

**Pré-condição:** mesma checagem de `brief_criativo.json` de `/gerar-pdf` acima.

### Procedimento

1. Se `apresentacao` não estiver em `config_projeto.materiais_selecionados`, adicione-o.
2. Despache `subagente-produtor-apresentacao` para `<slug>`.
3. Despache `subagente-revisor-marca` só para o tipo `apresentacao`.
4. Rode `python scripts/auditar-projeto.py <slug> --estrito --apenas apresentacao`.
5. Rode `python scripts/empacotar-projeto.py <slug>`.
6. Reporte (REGRA 2): path do `index.html`, decisões de design, faltantes.

---

## `/gerar-arte`

`<argumentos>` = `<slug> [--tamanho 1080x1080|1080x1350|1080x1920 ...]`. Sem
`--tamanho`, regenera todas as 3 variantes. Regeneração pontual — nunca re-executa
`/esbocar` nem `analista-insumos`/`diretor-de-arte`.

**Pré-condição:** mesma checagem de `brief_criativo.json` de `/gerar-pdf` acima.

### Mapeamento de `--tamanho` para tipo de material

- `1080x1080` → `arte-01`
- `1080x1350` → `arte-02`
- `1080x1920` → `arte-03`

### Procedimento

1. Resolva a lista de variantes a partir de `--tamanho` (ou as 3, se omitido). Para
   cada uma não presente em `config_projeto.materiais_selecionados`, adicione-a.
2. Se `output/<slug>/arte/copies.json` não existir (ou não tiver exatamente 3 copies),
   invoque `redator-arte` inline, uma única vez, ANTES do fan-out — formato e copy são
   eixos ortogonais (ver `docs/05-plano-expansao-multi-copy-arte.md`); as mesmas 3
   copies são compartilhadas por todas as variantes regeneradas nesta rodada. Se já
   existir, reaproveite sem regravar.
3. Despache um `subagente-produtor-arte` por variante, em paralelo — cada um lê
   `arte/copies.json` e renderiza as 3 copies na sua própria dimensão (3 PNGs por
   variante).
4. Despache `subagente-revisor-marca` só para as variantes desta rodada.
5. Rode `python scripts/auditar-projeto.py <slug> --estrito --apenas <variantes>`.
6. Rode `python scripts/empacotar-projeto.py <slug>`.
7. Reporte (REGRA 2): path de cada PNG (9 no total se as 3 variantes forem
   regeneradas), decisões de design, faltantes, sugestões de legenda por copy×variante.
