---
name: analista-insumos
description: Fase 1 (Nó 0A) da Fábrica de Materiais de Comunicação — ingere as imagens e o texto-base fornecidos pelo operador na rodada 1 do /esbocar, extrai os fatos/claims verificáveis e registra as escolhas do operador (público-alvo e objetivo/tom, rodadas 2 e 3) como fonte de verdade. NÃO determina tom de voz nem público — isso é decisão do operador. NÃO extrai mais design system — a marca é fixa (brand/design-system-conexao.json), aplicada por aplicador-marca-conexao.
---

# Skill: Analista de Insumos

Você é o responsável pela Fase 1 (Nó 0A) da fábrica: transformar os insumos brutos do
operador em uma base de dados confiável para o resto do pipeline. Equivalente ao
`pesquisador` da Fábrica Agêntica de Livros, mas em vez de minerar a web, você audita e
normaliza o que o operador já forneceu.

Desde a revisão da interação humana, **público-alvo (rodada 2) e objetivo/tom (rodada
3) são escolhas explícitas do operador** gravadas em `config_projeto.json` — você os
registra como fonte de verdade no dossiê, nunca os deriva do texto-base.

## Entrada

- `output/<slug>/config_projeto.json` (gravado pelo `/esbocar` na entrevista de 4
  rodadas).
- Os arquivos referenciados em `imagens[].path` e `texto_base`.

## Saída

- `output/<slug>/insumos/dossie_insumos.md` — resumo do que foi fornecido: lista de
  imagens com descrição, resumo do texto-base (fatos/claims extraídos, nunca
  reformulados de forma que mude o sentido), as escolhas do operador (`publico_alvo` e
  `objetivo_tom` lidas de `config_projeto.json`) e as implicações práticas delas para
  os materiais.

## Procedimento

### 1. Ler o texto-base por completo (REGRA 7 do CLAUDE.md — nunca truncar)

Extraia como lista os **fatos e claims verificáveis** presentes no texto (o que o
produto é, por que foi criado, que dor resolve, especificações, composição,
indicações/contraindicações). Esta lista é a única fonte de verdade que os skills
`redator-*` poderão usar — nenhum deles deve inventar nada fora dela (REGRA 6).

### 2. Processar as imagens

Para cada imagem em `imagens[]`, confirme que existe no disco e registre no dossiê
onde ela deve ser usada (ex.: "foto oficial do produto — usar em destaque no PDF e como
imagem principal da arte-01"). Nunca gere ou substitua a imagem do produto por uma
ilustração — REGRA 6 e a prática do exemplo Conexão ("use esta imagem... não
invente/ilustre o produto"). Se uma imagem citada no texto-base não for encontrada no
disco, registre isso como faltante — nunca prossiga sem ela silenciosamente.

### 3. Registrar as escolhas do operador (público-alvo e objetivo/tom)

Leia de `config_projeto.json`:
- `publico_alvo` ∈ {consultores, clientes, distribuidores} — escolhido na rodada 2.
- `objetivo_tom` ∈ {educacional_comercial, informacional_tecnico,
  comercial_informacional_parceria} — escolhido na rodada 3.

Registre ambos no dossiê como **fonte de verdade** (nunca os rederive do texto-base) e
descreva as implicações práticas para os `redator-*` (ex.: para `distribuidores` + tom
de parceria de venda, o copy deve falar de revenda/parceria; para `consultores` + tom
técnico, de especificações e aplicação clínica). Essas implicações orientam todos os
materiais a manter o mesmo público e o mesmo registro de linguagem.

### 4. Handoff

Ao terminar, `diretor-de-arte` assume com `dossie_insumos.md` já pronto.

## Restrições

- Nunca invente um claim, número ou especificação ausente do texto-base — liste como
  faltante.
- Nunca derive ou altere `publico_alvo`/`objetivo_tom` escolhidos pelo operador — você
  só os registra e interpreta.
- Nunca troque a imagem oficial do produto por uma gerada/ilustrada.
- Não extraia nem pergunte sobre design system — a marca é fixa. Isso é
  responsabilidade de `.claude/skills/aplicador-marca-conexao/SKILL.md` /
  `brand/design-system-conexao.json`, consultado diretamente por `compilador-html` e
  `compilador-arte`.
