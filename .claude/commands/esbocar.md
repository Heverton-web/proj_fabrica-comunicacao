---
description: Passo 1 da Fábrica de Materiais de Comunicação — entrevista em 4 rodadas (insumos, público-alvo, objetivo/tom de voz e tipos de material), grava config_projeto.json e prepara o brief criativo. Único ponto de interação humana (REGRA 3).
---

# /esbocar

Ponto de entrada da fábrica. Roda o Passo 1 do fluxo descrito em `SPEC.md` (a
entrevista em 4 rodadas) — a única interação humana real de todo o pipeline. Depois
disso, autonomia total (REGRA 3 do `CLAUDE.md`).

`$ARGUMENTS` pode conter um tema/nome de produto já dito pelo operador na mensagem que
disparou o comando — use-o como ponto de partida, mas as perguntas abaixo continuam
obrigatórias.

**Não pergunte sobre design system.** A marca é fixa (`brand/design-system-conexao.json`,
aplicada por `.claude/skills/aplicador-marca-conexao/SKILL.md`) para landing-page,
apresentação e arte — não é mais extraída por projeto. O PDF usa o mesmo arquivo fixo
como solução interina até que regras próprias de PDF ("Flex Gold") sejam desenhadas.

**Não derive tom de voz nem público-alvo do texto-base.** Desde a revisão da interação
humana, essas são **escolhas explícitas do operador** (rodadas 2 e 3) — a fonte de
verdade delas é o `config_projeto.json`, não a leitura do texto-base por
`analista-insumos` (ver `SPEC.md`).

## Passo 0 — slug

Derive um slug kebab-case a partir do nome do produto/projeto (se ainda não souber o
nome, pergunte isso como parte do Passo 1). Se `output/<slug>/` já existir, sufixe
`-v2`, `-v3`... automaticamente — nunca pergunte sobre isso (REGRA 3).

## Passo 1 — Entrevista de insumos (`AskUserQuestion`, rodada 1)

Pergunte, em uma única chamada de `AskUserQuestion` com até 3 perguntas:

1. **Nome do produto/projeto** — apenas se ainda não for conhecido (ver Passo 0).
2. **Imagens** — "Quais imagens você quer usar (produto, marca, logo)? Informe o
   caminho de cada arquivo ou anexe agora." (texto livre / "Other")
3. **Texto-base** — "Qual o texto-base com a informação a comunicar? Cole aqui ou
   informe o caminho de um arquivo." (texto livre / "Other")

Trate qualquer resposta "Other" como texto livre válido — nunca pergunte de novo
(REGRA 3, mesma disciplina do `/esbocar` da Fábrica Agêntica de Livros).

## Passo 2 — Entrevista de público-alvo (`AskUserQuestion`, rodada 2, seleção única)

Uma única pergunta, single select, com as 3 opções:

- Consultores
- Clientes
- Distribuidores

O valor escolhido é gravado em `config_projeto.publico_alvo` e vira fonte de verdade
para todos os `redator-*` — nunca o rederive do texto-base.

## Passo 3 — Entrevista de objetivo/tom de voz (`AskUserQuestion`, rodada 3, seleção única)

Uma única pergunta, single select, com as 3 opções compostas (objetivo / tom):

- **Educacional / Comercial** → `educacional_comercial`
- **Informacional / Técnico** → `informacional_tecnico`
- **Comercial / Informacional técnico de parceria de venda** → `comercial_informacional_parceria`

O valor escolhido é gravado em `config_projeto.objetivo_tom` e orienta como o copy é
escrito em cada material — nunca o rederive do texto-base.

## Passo 4 — Entrevista de materiais (`AskUserQuestion`, rodada 4, multiSelect)

9 opções no total — acima do limite de 4 opções por pergunta de `AskUserQuestion` — por
isso a rodada 4 é **1 única chamada de `AskUserQuestion`, com 3 perguntas multiSelect**
(máx. 4 perguntas por chamada, dentro do limite):

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

**Se o material 'PDF (apostila)' for selecionado:** pergunte adicionalmente na mesma rodada (ou em uma pergunta subsequente) para o operador definir a **edição do material** (ex: '1ª Edição', '2ª Edição Revisada'). Esse valor deve ser gravado obrigatoriamente no campo `edicao` de `config_projeto.json` para que os validadores e templates o processem de forma correta.

## Passo 5 — Elementos gráficos decorativos (opcional, mesma rodada 4)

Se qualquer material de arte estiver selecionado (`arte-01`/`arte-02`/`arte-03`/
`kit-consultor`/`kit-distribuidor`), pergunte adicionalmente — mesma disciplina da
edição do PDF acima, dentro da rodada 4 ou como pergunta subsequente, **nunca como
uma 5ª rodada nova** (R1 do `SPEC.md` continua valendo: são sempre 4 rodadas de
`AskUserQuestion`) — se o operador quer ativar os elementos gráficos decorativos de
fundo (formas geométricas/waves com borda fina dourada e opacidade baixa, para dar
profundidade — ver `SPEC_ARTE.md`):

- Sim, ativar elementos decorativos (padrão recomendado)
- Não, manter fundo limpo (sem elementos decorativos)

Grave a escolha em `config_projeto.elementos_decorativos` (booleano). Se o operador
não selecionar nenhum material de arte, não pergunte isso (campo fica ausente do
JSON). Se pular a pergunta ou não especificar, assuma `true` (nunca trave por
ausência de resposta, REGRA 3) — `compilador-arte`/`compilador-kit` só omitem os
elementos decorativos quando o campo existir e for explicitamente `false`.

## Passo 6 — Gravar e preparar (sem nova pausa)

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

## Passo 7 — Relatório objetivo (REGRA 2 — sem preâmbulo)

Reporte, de forma telegráfica:
- Slug do projeto e onde ficou salvo.
- Público-alvo escolhido e objetivo/tom escolhido.
- Materiais selecionados.
- Qualquer faltante já identificado por `analista-insumos` (ex.: imagem citada no
  texto-base mas não localizada).
- Comando sugerido: `/produzir-comunicacao-completa <slug>`.
