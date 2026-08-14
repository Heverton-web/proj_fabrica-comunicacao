# SPEC_COMANDOS.md — Contrato Universal dos Comandos da Fábrica

Este documento é a **fonte única de verdade** do procedimento completo de cada
comando da fábrica — `/esbocar`, `/produzir-comunicacao-completa`, `/gerar-pdf`,
`/gerar-landing`, `/gerar-apresentacao`, `/gerar-arte` (guarda-chuva),
`/gerar-arte-1080x1080`, `/gerar-arte-1080x1350`, `/gerar-arte-1080x1920`,
`/gerar-textos`, `/gerar-kit-consultor`, `/gerar-kit-distribuidor` e
`/kit-completo-<publico>` (`/kit-completo-consultor`, `/kit-completo-distribuidor`,
`/kit-completo-cliente`). Funciona em
**qualquer harness** que leia os arquivos deste repositório (Claude Code, Antigravity,
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

### Guardas determinísticos — passo manual obrigatório (qualquer harness)

Hooks e automações nativas de harness (ex.: `.claude/settings.json`) são
**conveniência, nunca requisito** (REGRA 10 do `AGENTS.md`). Em **qualquer
harness**, sempre que um comando, skill, rule ou qualquer personalização deste
repositório for **criada, alterada ou removida**, o operador ou agente deve rodar,
antes de considerar o trabalho concluído:

```
python scripts/verificar-universalidade.py --estrito
python scripts/verificar-consistencia-pipeline.py --estrito
```

Exit code 0 = universal/consistente. Exit code 1 = lacuna — corrija internamente
(REGRA 4) e rode de novo, nunca entregue com guarda vermelho. O
`verificar-universalidade.py` é o árbitro da arquitetura de 3 camadas: canônico
único, adaptadores finos por harness (`.claude/commands/` + `.opencode/commands/` +
MCPs) e rules finas (`CLAUDE.md`/`GEMINI.md`/`CODEBUDDY.md`/`QODER.md`).

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
e grava `manifesto_materiais.json`. Em seguida rode **sempre**:

```
python scripts/empacotar-distribuicao.py <slug>
```

Gera o **pacote de distribuição** (se auto-atualiza a cada ciclo/finalização): pasta
`output/<slug>/distribuicao/` contendo os **resultados finais** dos materiais
`concluido_autonomo` — sem insumos, briefs, JSONs de trabalho ou `revisao/`
(REGRA 2) — com `COPYRIGHT.txt` e o zip `distribuicao_<slug>.zip` **dentro da
pasta**. Empacota a **versão mais recente** de cada material (maior sufixo `-vN` da
REGRA 11); as versões antigas permanecem em `output/<slug>/`, o pacote é derivado e
regenerado do zero, nunca apaga origem.

**REGRA INTOCÁVEL:** `kit-consultor` e `kit-distribuidor`, tanto na pasta
`distribuicao/` quanto dentro do `.zip`, contêm **somente `.png` e `.txt`** de cada
arte — nunca `index.html`, `assets/` (fontes/logos/imagem de produto) ou
`conteudo.json`. Esses arquivos de trabalho continuam existindo normalmente em
`output/<slug>/kit-*/` para fins de auditoria/revisão; simplesmente não entram no
pacote entregue ao cliente.

### Passo 7 — Relatório final (REGRA 2 — telegráfico, sem preâmbulo)

Reporte: materiais entregues (com path), materiais esgotados (com motivo), decisões de
design tomadas, informações faltantes, sugestões de legenda/CTA para compartilhamento
(REGRA 6/R11 do `SPEC.md`).

---

## `/gerar-pdf`

`<argumentos>` = `<slug>`. Regeneração pontual de um projeto já esboçado — nunca
re-executa as 4 rodadas de `/esbocar` do zero, mas **sempre** roda a entrevista de
regeneração abaixo antes de iniciar qualquer criação. Isso vale para **todo**
`/gerar-<material>` (esta seção é a definição canônica da entrevista; as demais
seções abaixo só referenciam esta, nunca duplicam o texto).

**Pré-condição (falhe rápido se ausente):** confirme que `output/<slug>/brief_criativo.json`
existe. Se não existir, pare e informe: "Rode `/esbocar` (ou
`/produzir-comunicacao-completa <slug>`) primeiro — este projeto ainda não tem brief
criativo." Nunca invente um brief para contornar isso.

### Entrevista de regeneração (obrigatória, comum a todo `/gerar-<material>`)

Antes de despachar qualquer subagente produtor, faça esta entrevista com o operador,
na ordem abaixo, sempre mostrando o valor atualmente gravado como referência de
"manter" (mesma disciplina de `AskUserQuestion`/texto simples numerado descrita na
Nota sobre `AskUserQuestion` no topo deste documento):

1. **Imagem** — "Deseja utilizar a imagem atual do produto (`<caminho em
   output/<slug>/insumos/>`) ou informar uma nova?" Se nova, colete o caminho/anexo e
   copie/referencie em `output/<slug>/insumos/`; marque que os insumos mudaram.
2. **Texto-base** — "Deseja utilizar o texto-base atual ou informar um novo?" Se
   novo, colete (cole aqui ou caminho de arquivo); marque que os insumos mudaram.
3. **Público-alvo** — mostre o valor atual de `config_projeto.publico_alvo` e
   pergunte se mantém ou troca, com as mesmas 3 opções do Passo 2 de `/esbocar`
   (Consultores / Clientes / Distribuidores).
4. **Objetivo/tom de voz** — mostre o valor atual de `config_projeto.objetivo_tom` e
   pergunte se mantém ou troca, com as mesmas 3 opções do Passo 3 de `/esbocar`.
5. **Edição** — só se o material principal desta regeneração for `pdf`, ou se
   `config_projeto.edicao` já existir de uma geração anterior: mostre o valor atual
   e pergunte se mantém ou define um novo (ex.: "1ª Edição", "2ª Edição Revisada").
   Se nenhuma das duas condições se aplicar, pule esta pergunta.
6. **Outros materiais** — "Deseja gerar apenas `pdf` ou também outros tipos de
   material?" Se "também outros", apresente as 9 opções da rodada 4 de `/esbocar`
   (multiSelect, mesma divisão em partes 1/3, 2/3, 3/3 se o mecanismo do harness
   limitar) e registre as escolhas.

Trate qualquer resposta livre/"Other" como válida — nunca pare para confirmar de novo
(REGRA 3). Só depois de coletar as 6 respostas, siga para "Aplicar resultado" abaixo.

### Aplicar resultado da entrevista (sem nova pausa)

1. Se a imagem e/ou o texto-base mudaram (perguntas 1-2), atualize
   `output/<slug>/insumos/` e reinvoque `analista-insumos` para regravar
   `dossie_insumos.md`.
2. Se público-alvo, objetivo/tom mudaram (perguntas 3-4), OU se os insumos mudaram
   no passo 1 acima, grave os novos valores em `config_projeto.publico_alvo`/
   `config_projeto.objetivo_tom` (o que se aplicar) e reinvoque `diretor-de-arte`
   para regravar `brief_criativo.json`.
3. Se a edição mudou (pergunta 5), grave em `config_projeto.edicao`.
4. Monte o conjunto final de materiais a (re)gerar: o material principal desta
   regeneração (`pdf`) mais qualquer material adicional escolhido na pergunta 6.
   Adicione todos os que ainda não estiverem em
   `config_projeto.materiais_selecionados`.
5. Rode `python scripts/parametros_projeto.py <slug> --validar` — corrija
   internamente qualquer erro (REGRA 4) antes de seguir.

### Resolver pasta de destino — nunca sobrescrever (REGRA 11 do `AGENTS.md`)

Para **cada material** do conjunto final montado no passo 4 acima, resolva a pasta
real de destino em disco **antes de despachar qualquer subagente**:

```
python scripts/pool-materiais.py <slug> --proxima-pasta <tipo>
```

Isso imprime `<tipo>` sem sufixo se `output/<slug>/<tipo>/` ainda não existir (1ª
geração), ou `<tipo>-v2`, `-v3`... se já existir uma entrega anterior (regeneração
pontual — nunca escreva por cima). Guarde o par `(tipo, pasta)` resolvido para cada
material — `pasta` é o valor usado em todos os passos de despacho/validação/registro
abaixo; `tipo` continua sendo a string base (define qual validador/dimensão/CTA
aplica). **Nunca decida "sobrescrever ou não" por julgamento do agente — a resolução
é sempre feita por este script determinístico.**

### Procedimento (despacho)

1. Para cada par `(tipo, pasta)` resolvido acima, despache o subagente produtor
   correspondente **informando `<pasta>`** — mapeamento e ordem de dependências (copy
   compartilhada de arte/kit antes do fan-out) iguais aos Passos 2.5, 2.7 e 3 de
   `/produzir-comunicacao-completa`. O subagente lê/escreve exclusivamente em
   `output/<slug>/<pasta>/**` e nunca toca em `output/<slug>/<tipo>/` se `pasta !=
   tipo` (essa é a versão anterior, intocável).
2. Despache `subagente-revisor-marca` cobrindo todas as `<pasta>` despachadas no
   passo 1 (a lista do lote é de pastas, não de tipos-base).
3. Rode `python scripts/auditar-projeto.py <slug> --estrito --apenas <lista das
   pastas despachadas, separadas por vírgula>`.
4. Rode `python scripts/empacotar-projeto.py <slug>` (reempacota o manifesto;
   `manifesto_materiais.json` passa a listar automaticamente toda pasta versionada
   encontrada em disco — nunca só a 1ª geração — sem afetar as demais já entregues).
   Em seguida rode `python scripts/empacotar-distribuicao.py <slug>` — o pacote de
   distribuição (pasta `distribuicao/` com `distribuicao_<slug>.zip` e
   `COPYRIGHT.txt` dentro) se auto-atualiza a cada ciclo, empacotando a versão mais
   recente de cada material.
5. Reporte (REGRA 2): path de cada material entregue **por pasta/versão** (deixando
   claro quando um material é uma nova versão e qual pasta anterior permanece
   intocada), decisões de design, faltantes, sugestão de legenda de compartilhamento.

---

## `/gerar-landing`

`<argumentos>` = `<slug>`. Regeneração pontual — nunca re-executa `/esbocar` nem
`analista-insumos`/`diretor-de-arte` do zero.

**Pré-condição:** mesma checagem de `brief_criativo.json` de `/gerar-pdf` acima.

### Procedimento

Mesma **entrevista de regeneração**, "Aplicar resultado", "Resolver pasta de destino"
e "Procedimento (despacho)" de `/gerar-pdf` acima, trocando o material principal
`pdf` por `landing-page` (a pergunta 5 sobre edição só se aplica se
`config_projeto.edicao` já existir de uma geração anterior).

---

## `/gerar-apresentacao`

`<argumentos>` = `<slug>`. Regeneração pontual — nunca re-executa `/esbocar` nem
`analista-insumos`/`diretor-de-arte` do zero.

**Pré-condição:** mesma checagem de `brief_criativo.json` de `/gerar-pdf` acima.

### Procedimento

Mesma **entrevista de regeneração**, "Aplicar resultado", "Resolver pasta de destino"
e "Procedimento (despacho)" de `/gerar-pdf` acima, trocando o material principal
`pdf` por `apresentacao` (a pergunta 5 sobre edição só se aplica se
`config_projeto.edicao` já existir de uma geração anterior).

---

## `/gerar-arte`

`<argumentos>` = `<slug> [--tamanho 1080x1080|1080x1350|1080x1920 ...]`. Sem
`--tamanho`, regenera todas as 3 variantes. Regeneração pontual — nunca re-executa
`/esbocar` nem `analista-insumos`/`diretor-de-arte` do zero.

**Pré-condição:** mesma checagem de `brief_criativo.json` de `/gerar-pdf` acima.

### Procedimento

1. Resolva a lista de variantes a partir de `--tamanho` (ou as 3, se omitido).
2. Rode a **entrevista de regeneração** de `/gerar-pdf` acima **uma única vez**
   (nunca repita por variante), tratando o material principal como "arte" (a
   soma das variantes resolvidas no passo 1) — na pergunta 6 ("outros materiais"),
   as variantes de arte ainda não resolvidas não contam como "outros materiais",
   já fazem parte do pedido atual. Aplique o resultado (mesmos passos de "Aplicar
   resultado da entrevista" de `/gerar-pdf`).
3. Para cada variante resolvida no passo 1, resolva a pasta de destino (**"Resolver
   pasta de destino" de `/gerar-pdf` acima — REGRA 11 do `AGENTS.md`, nunca
   sobrescrever**): `python scripts/pool-materiais.py <slug> --proxima-pasta
   <variante>`. Guarde o par `(variante, pasta)` de cada uma.
4. Para cada par `(variante, pasta)`, execute o "Procedimento (despacho)" do comando
   específico correspondente abaixo (`/gerar-arte-1080x1080`,
   `/gerar-arte-1080x1350`, `/gerar-arte-1080x1920`) **sem repetir a entrevista nem a
   resolução de pasta**, já feitas nos passos 2-3 — este comando é o guarda-chuva,
   nunca uma segunda cópia do passo a passo. Passe a `<pasta>` já resolvida adiante.
5. Reporte (REGRA 2): path de cada PNG **por pasta/versão** (até 9 se as 3 variantes
   forem regeneradas), decisões de design, faltantes, sugestões de legenda por
   copy×variante.

---

## `/gerar-arte-1080x1080`

`<argumentos>` = `<slug>`. Regeneração pontual de uma única variante de arte —
nunca re-executa `/esbocar` nem `analista-insumos`/`diretor-de-arte` do zero.

**Pré-condição:** mesma checagem de `brief_criativo.json` de `/gerar-pdf` acima.

### Mapeamento de variantes

- `/gerar-arte-1080x1080` → `arte-01` (WhatsApp/Instagram quadrado)
- `/gerar-arte-1080x1350` → `arte-02` (Instagram/LinkedIn retrato)
- `/gerar-arte-1080x1920` → `arte-03` (Stories/Reels)

### Procedimento

Se chamado **diretamente** pelo operador (não via `/gerar-arte` guarda-chuva), rode
primeiro a **entrevista de regeneração** e "Aplicar resultado da entrevista" de
`/gerar-pdf` acima, trocando o material principal `pdf` por `arte-01` (a pergunta 5
sobre edição só se aplica se `config_projeto.edicao` já existir); em seguida resolva a
pasta de destino (**"Resolver pasta de destino" de `/gerar-pdf` acima — REGRA 11 do
`AGENTS.md`**): `python scripts/pool-materiais.py <slug> --proxima-pasta arte-01`. Se
chamado **pelo guarda-chuva** `/gerar-arte`, a entrevista e a pasta já foram
resolvidas — pule direto para o despacho abaixo usando a `<pasta>` recebida.

1. Se `arte-01` não estiver em `config_projeto.materiais_selecionados`, adicione-o.
2. Se `output/<slug>/arte/copies.json` não existir (ou não tiver exatamente 3
   copies), invoque `redator-arte` inline, uma única vez, ANTES do fan-out — formato
   e copy são eixos ortogonais (ver `docs/05-plano-expansao-multi-copy-arte.md`);
   as mesmas 3 copies são compartilhadas por todas as variantes. Se já existir e a
   entrevista não mudou público/tom, reaproveite sem regravar (se mudou, `redator-arte`
   regrava — ver seu `SKILL.md`).
3. Despache `subagente-produtor-arte` para `<slug>` na variante `arte-01`,
   **informando `<pasta>`** — ele lê `arte/copies.json` e renderiza as 3 copies em
   1080×1080 (3 PNGs) em `output/<slug>/<pasta>/`, nunca em `output/<slug>/arte-01/`
   se `pasta != arte-01`. Se a entrevista (quando aplicável) tiver escolhido "outros
   materiais" adicionais, resolva a pasta de cada um (mesmo passo de "Resolver pasta
   de destino") e despache também os subagentes correspondentes (mesmo mapeamento do
   Passo 3 de `/produzir-comunicacao-completa`).
4. Despache `subagente-revisor-marca` cobrindo todas as pastas despachadas.
5. Rode `python scripts/auditar-projeto.py <slug> --estrito --apenas <lista das
   pastas despachadas, separadas por vírgula>`.
6. Rode `python scripts/empacotar-projeto.py <slug>`, depois
   `python scripts/empacotar-distribuicao.py <slug>` (pacote de distribuição
   auto-atualizado: pasta `distribuicao/` com `distribuicao_<slug>.zip` e
   `COPYRIGHT.txt` dentro — ver Passo 6 de
   `/produzir-comunicacao-completa`).
7. Reporte (REGRA 2): path de cada PNG **por pasta/versão** (3 nesta variante, mais os
   demais materiais despachados), decisões de design, faltantes, sugestões de legenda
   por copy.

---

## `/gerar-arte-1080x1350`

`<argumentos>` = `<slug>`. Regeneração pontual de uma única variante de arte —
nunca re-executa `/esbocar` nem `analista-insumos`/`diretor-de-arte` do zero.

**Pré-condição:** mesma checagem de `brief_criativo.json` de `/gerar-pdf` acima.

### Procedimento

Mesmo procedimento de `/gerar-arte-1080x1080` acima (incluindo a mesma regra de
"entrevista e resolução de pasta só quando chamado diretamente, puladas quando vem do
guarda-chuva"), trocando `arte-01` por `arte-02` (subagente renderiza as 3 copies em
1080×1350).

---

## `/gerar-arte-1080x1920`

`<argumentos>` = `<slug>`. Regeneração pontual de uma única variante de arte —
nunca re-executa `/esbocar` nem `analista-insumos`/`diretor-de-arte` do zero.

**Pré-condição:** mesma checagem de `brief_criativo.json` de `/gerar-pdf` acima.

### Procedimento

Mesmo procedimento de `/gerar-arte-1080x1080` acima (incluindo a mesma regra de
"entrevista e resolução de pasta só quando chamado diretamente, puladas quando vem do
guarda-chuva"), trocando `arte-01` por `arte-03` (subagente renderiza as 3 copies em
1080×1920).

---

## `/gerar-textos`

`<argumentos>` = `<slug>`. Regeneração pontual — nunca re-executa `/esbocar` nem
`analista-insumos`/`diretor-de-arte` do zero.

**Pré-condição:** mesma checagem de `brief_criativo.json` de `/gerar-pdf` acima.

### Procedimento

Mesma **entrevista de regeneração**, "Aplicar resultado", "Resolver pasta de destino"
e "Procedimento (despacho)" de `/gerar-pdf` acima, trocando o material principal
`pdf` por `textos` (a pergunta 5 sobre edição só se aplica se
`config_projeto.edicao` já existir de uma geração anterior).

---

## `/gerar-kit-consultor`

`<argumentos>` = `<slug>`. Regeneração pontual — nunca re-executa `/esbocar` nem
`analista-insumos`/`diretor-de-arte` do zero.

**Pré-condição:** mesma checagem de `brief_criativo.json` de `/gerar-pdf` acima.

### Procedimento

1. Rode a mesma **entrevista de regeneração** e "Aplicar resultado da entrevista"
   de `/gerar-pdf` acima, trocando o material principal `pdf` por `kit-consultor`
   (a pergunta 5 sobre edição só se aplica se `config_projeto.edicao` já existir).
2. Resolva a pasta de destino (**"Resolver pasta de destino" de `/gerar-pdf` acima —
   REGRA 11 do `AGENTS.md`**): `python scripts/pool-materiais.py <slug>
   --proxima-pasta kit-consultor`.
3. Se `kit-consultor` não estiver em `config_projeto.materiais_selecionados`,
   adicione-o.
4. Se `output/<slug>/kits/copies.json` não existir (ou não tiver exatamente 10
   copies), invoque `redator-kit-copy` inline, uma única vez, ANTES do fan-out —
   copy é compartilhada entre os 2 kits (eixo ortogonal a variante, ver
   `SPEC_KITS.md`); só o CTA final muda (`brand/kits-conexao.json`, resolvido por
   `compilador-kit`). Se já existir e a regeneração não trocou imagem/texto-base,
   reaproveite sem regravar (se trocou, `redator-kit-copy` regrava — ver seu
   `SKILL.md`).
5. Despache `subagente-produtor-kit` para `<slug>` na variante `kit-consultor`,
   **informando `<pasta>`** — ele lê `kits/copies.json` e renderiza as 10 copies em
   1080×1350 com CTA de consultor em `output/<slug>/<pasta>/`, nunca em
   `output/<slug>/kit-consultor/` se `pasta != kit-consultor`. Se a entrevista
   escolheu "outros materiais" adicionais, resolva a pasta de cada um e despache
   também os subagentes correspondentes (mesmo mapeamento do Passo 3 de
   `/produzir-comunicacao-completa`).
6. Despache `subagente-revisor-marca` cobrindo todas as pastas despachadas.
7. Rode `python scripts/auditar-projeto.py <slug> --estrito --apenas <lista das
   pastas despachadas, separadas por vírgula>`.
8. Rode `python scripts/empacotar-projeto.py <slug>`, depois
   `python scripts/empacotar-distribuicao.py <slug>` (pacote de distribuição
   auto-atualizado: pasta `distribuicao/` com `distribuicao_<slug>.zip` e
   `COPYRIGHT.txt` dentro — ver Passo 6 de
   `/produzir-comunicacao-completa`).
9. Reporte (REGRA 2): path de cada PNG **por pasta/versão** (10, mais os demais
   materiais despachados), decisões de design, faltantes, sugestões de legenda/CTA.

---

## `/gerar-kit-distribuidor`

`<argumentos>` = `<slug>`. Regeneração pontual — nunca re-executa `/esbocar` nem
`analista-insumos`/`diretor-de-arte` do zero.

**Pré-condição:** mesma checagem de `brief_criativo.json` de `/gerar-pdf` acima.

### Procedimento

Mesmo procedimento de `/gerar-kit-consultor` acima, trocando `kit-consultor` por
`kit-distribuidor` (subagente renderiza as 10 copies com CTA de distribuidor).

---

## `/kit-completo-consultor`

Canônico completo dos 3 comandos universais de **kit completo de comunicação focado
em um público-alvo fixo** — combinação de materiais já existentes com **estruturas de
conteúdo especializadas por público** (ver "Presets" abaixo). As variantes
`/kit-completo-distribuidor` e `/kit-completo-cliente` (seções próprias abaixo)
referenciam esta seção, trocando apenas o preset — nunca duplicam o procedimento
(REGRA 10).

São comandos de entrada de projeto: rodam num projeto novo (equivalem a `/esbocar` +
`/produzir-comunicacao-completa` com público e materiais pré-fixos) ou num projeto já
existente (regeneração parcial — ver "Resolver pasta de destino", REGRA 11 do
`AGENTS.md`).

| Comando | Público fixo (`config_projeto.publico_alvo`) | Materiais fixos (`config_projeto.materiais_selecionados`) |
|---|---|---|
| `/kit-completo-consultor` | `consultores` | `pdf` + `kit-consultor` + `landing-page` + `apresentacao` |
| `/kit-completo-distribuidor` | `distribuidores` | `pdf` + `kit-distribuidor` + `landing-page` + `apresentacao` |
| `/kit-completo-cliente` | `clientes` | `pdf` + `landing-page` + `apresentacao` |

`<argumentos>` = `<slug>` (se `output/<slug>/` já existir) ou o nome/tema do produto
(se novo — slug derivado como no Passo 0 de `/esbocar`, com sufixo `-v2` se
`output/<slug>/` já existir).

O preset **pré-preenche** a rodada 2 (público-alvo) e a rodada 4 (materiais) do
`/esbocar` — nunca é uma 5ª rodada nova (R1 do `SPEC.md`).

### Presets — estrutura de conteúdo por público (canônico)

Estas estruturas alimentam `diretor-de-arte` (→
`brief_criativo.mapeamento_por_material`) quando `config_projeto.preset_kit_completo`
existir. São também as variantes referenciadas por `SPEC_PDF.md`/`SPEC_HTML.md`.

#### `/kit-completo-consultor`

| Material | Estrutura |
|---|---|
| `pdf` | O que é · Para que serve · Diferenciais técnicos/comerciais · Como vender: SPIN (Situação, Problema, Implicação, Necessidade de solução) · Contorno de objeções (objeções reais + resposta) · Fechamento/CTA |
| `kit-consultor` | Fluxo atual inalterado (`SPEC_KITS.md`) — 10 artes 1080×1350, público `dentista_implantodontista` |
| `landing-page` | Fluxo atual inalterado (`SPEC_HTML.md`) |
| `apresentacao` | Foco: O que é · Para que serve · Diferenciais técnicos |

#### `/kit-completo-distribuidor`

| Material | Estrutura |
|---|---|
| `pdf` | O que é · Para que serve · Diferenciais técnicos/comerciais · Rentabilidade para o seu negócio · Como vender: SPIN · Contorno de objeções · Fechamento/CTA |
| `kit-distribuidor` | Fluxo atual inalterado (`SPEC_KITS.md`) |
| `landing-page` | Fluxo atual inalterado (`SPEC_HTML.md`) |
| `apresentacao` | Foco: O que é · Para que serve · Diferenciais técnicos · Rentabilidade para o seu negócio |

#### `/kit-completo-cliente`

| Material | Estrutura |
|---|---|
| `pdf` | O que é · Para que serve · Diferenciais técnicos · Diferenciais para a prática clínica · Por que utilizar este produto · Fechamento/CTA |
| `landing-page` | Foco: O que é · Para que serve · Diferenciais técnicos · Diferenciais para a prática clínica · Por que utilizar este produto |
| `apresentacao` | Foco: O que é · Para que serve · Diferenciais técnicos · Diferenciais para a prática clínica · Por que utilizar este produto |

#### Regras de conteúdo transversais (fidelidade à fonte — REGRA 6)

- **SPIN e contorno de objeções:** a técnica (S/P/I/N; pergunta→resposta) é fixa; o
  **conteúdo** (perguntas reais de venda, objeções reais, respostas baseadas no dossiê)
  é extraído do texto-base — nunca inventado.
- **Rentabilidade:** margens, preços, condições e benefícios comerciais exatamente
  como constam no texto-base. Ausência de dados → a seção entra como "faltante" no
  relatório final, nunca preenchida por suposição.
- **Diferenciais para a prática clínica / Por que utilizar:** benefícios clínicos e
  motivos de escolha presentes no texto-base, redigidos no registro de linguagem de
  `brand/publicos-alvo.json` para o público do preset.
- Design system, capa do PDF, componentes e validações: inalterados — só o conteúdo
  muda de estrutura.

### Entrevista (adaptação das rodadas — sem rodada nova)

Público (rodada 2) e materiais (rodada 4) vêm do preset — não são perguntados. As
perguntas abaixo são feitas na ordem, sempre mostrando o valor atual como referência
de "manter" quando o projeto já existir (mesma disciplina de `/gerar-pdf`):

1. **Insumos** (texto livre): "Informe o caminho das imagens e o texto-base da
   informação a comunicar." — para `/kit-completo-distribuidor`, reforçar que o
   texto-base deve conter dados de rentabilidade (margem/preço/condições) se
   existirem; para `/kit-completo-consultor`, objeções reais e perguntas de venda se
   existirem. Ausência nunca é bloqueio — vira "faltante" (REGRA 6).
2. **Objetivo/tom de voz** (seleção única): mesmas 3 opções compostas do Passo 3 de
   `/esbocar`. O preset sugere a opção compatível com o público (via
   `brand/publicos-alvo.json`), mas o operador decide.
3. **Edição** (texto livre): obrigatória (o preset sempre inclui `pdf`) — ex.:
   "1ª Edição". Gravada em `config_projeto.edicao`.
4. **Elementos decorativos** (sim/não): obrigatória nos presets consultor/distribuidor
   (os kits têm artes — mesma disciplina do Passo 5 de `/esbocar`); no preset cliente
   (sem kits, sem artes) não perguntar. Default `true`. Gravada em
   `config_projeto.elementos_decorativos`.

Trate qualquer resposta livre/"Other" como válida (REGRA 3). Não pergunte sobre
design system (é fixo, REGRA 10/`aplicador-marca-conexao`).

### Aplicar resultado (sem nova pausa)

1. Se `output/<slug>/` não existir, crie a estrutura (mesma disciplina do Passo 6 de
   `/esbocar`): copie/referencie os insumos em `output/<slug>/insumos/`.
2. Grave/atualize `config_projeto.json`: `publico_alvo` = público do preset,
   `materiais_selecionados` = materiais do preset **somados aos já existentes** (nunca
   remova um material já listado), `preset_kit_completo` = `<publico>`, `edicao`,
   `elementos_decorativos` (schema em `SPEC.md`).
3. Se os insumos mudaram (ou o projeto é novo), invoque `analista-insumos` → regrava
   `dossie_insumos.md`.
4. Invoque `diretor-de-arte` → regrava `brief_criativo.json` com o
   `mapeamento_por_material` das estruturas por público da tabela de presets acima (o
   preset é detectado por `config_projeto.preset_kit_completo`).
5. Rode `python scripts/parametros_projeto.py <slug> --validar` — corrija internamente
   (REGRA 4) antes de seguir.

### Resolver pasta de destino — nunca sobrescrever (REGRA 11 do `AGENTS.md`)

Para **cada material** do preset, resolva a pasta real de destino **antes de
despachar qualquer subagente**:

```
python scripts/pool-materiais.py <slug> --proxima-pasta <tipo>
```

`<tipo>` ∈ {`pdf`, `landing-page`, `apresentacao`, `kit-consultor` (preset consultor),
`kit-distribuidor` (preset distribuidor)}. O script imprime `<tipo>` sem sufixo se a
pasta ainda não existir (1ª geração) ou `<tipo>-v2`, `-v3`... se já existir (material
entregue por qualquer comando anterior — `/esbocar`+`/produzir-comunicacao-completa`,
`/gerar-*` ou um kit-completo anterior). Nunca decida sobrescrita por julgamento do
agente — a resolução é sempre feita por este script determinístico.

### Procedimento (despacho)

1. Para cada par `(tipo, pasta)` resolvido, despache o subagente produtor
   correspondente **informando `<pasta>`** — mapeamento e dependências (copy
   compartilhada de kit antes do fan-out) iguais aos Passos 2.7 e 3 de
   `/produzir-comunicacao-completa`:
   - `pdf` → `subagente-produtor-pdf`
   - `landing-page` → `subagente-produtor-landing`
   - `apresentacao` → `subagente-produtor-apresentacao`
   - `kit-consultor`/`kit-distribuidor` → `subagente-produtor-kit`
2. Se `kit-consultor`/`kit-distribuidor` estiver no preset e
   `output/<slug>/kits/copies.json` não existir (ou não tiver exatamente 10 copies),
   invoque `redator-kit-copy` inline, uma única vez, antes do fan-out (Passo 2.7) —
   copy compartilhada; reaproveitada se os insumos não mudaram, regravada se mudaram.
3. Despache `subagente-revisor-marca` cobrindo todas as `<pasta>` despachadas.
4. Rode `python scripts/auditar-projeto.py <slug> --estrito --apenas <lista das pastas
   despachadas, separadas por vírgula>`.
5. Rode `python scripts/empacotar-projeto.py <slug>` (o manifesto lista todas as
   versões encontradas em disco, nunca só a mais recente — REGRA 11), depois
   `python scripts/empacotar-distribuicao.py <slug>` (pacote de distribuição
   auto-atualizado: pasta `distribuicao/` com `distribuicao_<slug>.zip` e
   `COPYRIGHT.txt` dentro — ver Passo 6 de
   `/produzir-comunicacao-completa`).
6. Reporte (REGRA 2): path de cada material **por pasta/versão** (deixando claro
   quando um material é uma nova versão e qual pasta anterior permanece intocada),
   decisões de design, faltantes (incluindo dados comerciais/clínicos ausentes do
   texto-base), sugestões de legenda/CTA para compartilhamento.

---

## `/kit-completo-distribuidor`

Variante do preset **distribuidores** — mesmo procedimento de
`/kit-completo-consultor` acima, trocando apenas o preset:

- `config_projeto.publico_alvo` = `distribuidores`;
- `config_projeto.materiais_selecionados` = `pdf` + `kit-distribuidor` +
  `landing-page` + `apresentacao` (somados aos já existentes, nunca removendo);
- `config_projeto.preset_kit_completo` = `distribuidores`;
- estrutura de conteúdo por material na tabela de presets acima (PDF acrescenta
  "Rentabilidade para o seu negócio"; apresentação idem);
- entrevista: reforçar que o texto-base deve conter dados de rentabilidade
  (margem/preço/condições) se existirem — ausência vira "faltante" (REGRA 6);
- `pool-materiais.py --proxima-pasta` para `kit-distribuidor` (nunca sobrescrever,
  REGRA 11).

---

## `/kit-completo-cliente`

Variante do preset **clientes** — mesmo procedimento de `/kit-completo-consultor`
acima, trocando apenas o preset:

- `config_projeto.publico_alvo` = `clientes`;
- `config_projeto.materiais_selecionados` = `pdf` + `landing-page` +
  `apresentacao` (somados aos já existentes, nunca removendo) — **sem kits**, sem
  artes;
- `config_projeto.preset_kit_completo` = `clientes`;
- estrutura de conteúdo por material na tabela de presets acima (PDF, landing e
  apresentação focam em "Diferenciais para a prática clínica" e "Por que utilizar
  este produto");
- entrevista: **não perguntar** elementos decorativos (sem kits, sem artes) —
  gravar `config_projeto.elementos_decorativos` = `true` por default;
- `pool-materiais.py --proxima-pasta` para `pdf`, `landing-page` e `apresentacao`
  (nunca sobrescrever, REGRA 11).
