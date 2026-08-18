---
name: revisor-marca
description: Fase 2.5 da Fábrica de Materiais de Comunicação — roda depois que um material foi compilado e validado estruturalmente, antes do empacotamento final. Audita fidelidade à fonte (nunca inventar claim) e fidelidade à marca (cores/fontes/componentes do design system fixo brand/design-system-conexao.json), com evidência de scripts, não opinião. Use em todo material antes de marcá-lo concluido_autonomo.
---

# Skill: Revisor de Marca

Você é o peer review da fábrica — equivalente ao `revisor-tecnico` da Fábrica Agêntica
de Livros. Roda depois de cada material compilado, antes do empacotamento final.
Evidência antes de opinião: sempre rode os scripts de validação primeiro, e decida com
base no JSON deles, nunca por impressão própria do conteúdo.

## Entrada

- O(s) artefato(s) compilado(s) em `output/<slug>/<tipo>/`, onde `<tipo>` é o nome
  literal da pasta em disco — pode ser uma versão regenerada (ex.: `"pdf-v2"`) quando
  o material já foi entregue antes e o operador pediu uma nova geração via
  `/gerar-<material>` (REGRA 11 do `AGENTS.md`). Nunca normalize/reescreva `<tipo>` —
  use-o exatamente como recebido tanto para ler a pasta quanto para os comandos abaixo.
- `brand/design-system-conexao.json` (fixo), `output/<slug>/insumos/dossie_insumos.md`.

## Procedimento

### 1. Rodar as validações determinísticas primeiro

`<base>` abaixo é o tipo "puro" sem sufixo de versão (ex.: `<tipo>` = `"pdf-v2"` →
`<base>` = `"pdf"`) — só para escolher qual validador chamar; a pasta lida em disco
continua sendo sempre `<tipo>` (via `--pasta`, ou como argumento posicional em
`validar-design-tokens.py`, que já é genérico):

```
python scripts/validar-design-tokens.py <slug> <tipo>              # so se base in (landing-page, apresentacao)
python scripts/validar-pdf.py <slug> --pasta <tipo>                 # so se base == pdf
python scripts/validar-html.py <slug> <base> --pasta <tipo>         # so se base in (landing-page, apresentacao)
python scripts/validar-dimensoes.py <slug> <base> --pasta <tipo>    # so se base comeca com arte-
python scripts/validar-kit.py <slug> <base> --pasta <tipo>          # so se base in (kit-consultor, kit-distribuidor)
```

### 1.1. Checagens de endurecimento (determinísticas, novas)

- **PDF — capa (via `validar-pdf.py`):** título ≤ 2 linhas, sem linha com 1 palavra
  isolada, proporção de bloco, **não** contém "guia de treinamento" e **≥ 2 palavras
  significativas do título presentes no texto-mãe** (capa remete ao tema — REGRA 6);
  parágrafo da capa em bloco quadrado (proporção em `[0.12, 1.2]`), sem palavra
  isolada. O script já falha (exit 1) se qualquer critério falhar.
- **Artes e kits — 1 badge por peça (via `validar-dimensoes.py`/`validar-kit.py`):**
  cada `index*.html` persistido deve ter **0 badges de contexto** (`class="badge"`) e
  **exatamente 1 CTA pill** (`class="cta"`). O CTA é o único elemento tipo badge
  permitido em peça PNG (SPEC_ARTE.md/SPEC_KITS.md endurecidos).

### 2. Checar fidelidade à fonte (REGRA 6)

Para `<tipo>` com arquivos `.txt` (ex.: `textos`), rode primeiro o pré-filtro
determinístico — ele não substitui a checagem abaixo, só reduz o quanto você precisa
procurar do zero (achado real: esta etapa custou mais token do que a própria escrita do
material — ver `melhorias/plano-determinismo-reducao-custos.md`):

```
python scripts/extrair-claims-candidatos.py <slug> <tipo>
```

Use `output/<slug>/revisao/candidatos_verificacao.json` como checklist inicial: todo
candidato com `encontrado_no_dossie: false` precisa ser confirmado contra o dossiê antes
de aprovar (pode ser falso positivo — ex.: hashtag combinando 2 termos reais do dossiê
de forma legítima — ou pode ser o mesmo tipo de defeito real já visto em produção: uma
hashtag de outro nicho colada por engano). O script é assistivo, cobre só `.txt`
(ainda não cobre `copies.json` de arte/kit, HTML ou PDF) e **nunca** substitui a
comparação semântica linha a linha abaixo — uma paráfrase que muda o sentido não
aparece em regex.

Compare cada claim/dado presente no material com `dossie_insumos.md`. Qualquer
afirmação sem rastro no dossiê é um defeito — não é opinião, é checagem factual linha a
linha.

Para `arte-0N`: as 3 copies em `output/<slug>/arte/copies.json` são compartilhadas por
todos os formatos — audite as **3**, não só a primeira (`index.html`). Confirme também
que são 3 ângulos genuinamente distintos do dossiê, não 3 variações do mesmo ângulo
(ver `docs/05-plano-expansao-multi-copy-arte.md`).

Para `kit-consultor`/`kit-distribuidor`: as 10 copies em `output/<slug>/kits/copies.json`
são compartilhadas pelos 2 kits — audite as **10**, cobrindo os 5 tons de
`brand/tons-kit.json`, 2 ângulos genuinamente distintos por tom (ver `SPEC_KITS.md`).
Compare também `kit-consultor/` e `kit-distribuidor/` item a item: headline e subcopy
devem ser **idênticos** entre os 2 kits — só CTA e assinatura podem diferir (vindos de
`brand/kits-conexao.json`). Qualquer outra divergência de conteúdo entre os 2 kits é
defeito, não variação aceitável.

### 2.1. Checar aderência às escolhas do operador

O dossiê registra `publico_alvo` e `objetivo_tom` escolhidos pelo operador (rodadas 2 e
3 do `/esbocar`). O material deve refletir esse público e esse objetivo/tom — copy
escrito para `clientes` não pode soar como texto para `distribuidores`, e o registro de
linguagem precisa corresponder ao `objetivo_tom` do brief. Desvio aqui é defeito,
corrigível pela mesma via da REGRA 4.

### 3. Checar fidelidade à marca

- Cores usadas no HTML devem ser exatamente as de `brand/design-system-conexao.json`
  (o script `validar-design-tokens.py` já faz o grep — confirme que não há hex "solto"
  fora das variáveis).
- Botão/CTA primário usa o gradiente de assinatura (nunca `accent` chapado) — ver
  `.claude/skills/aplicador-marca-conexao/SKILL.md`.
- Fontes Poppins/Inter carregadas de verdade via `assets/fonts/*.woff2` (confirme que
  não caiu silenciosamente em Roboto/sistema — `document.fonts` no Playwright deve
  mostrar `status: loaded` para os pesos usados).
- Logo presente e legível onde o template prevê (quando disponível).

### 2.2. Julgamento de design (embutido — funciona em qualquer harness)

Orientação escrita aqui, não referenciada de skill externa, para valer igual em
Claude Code, Antigravity, OpenCode, Freebuff, MiMoCode ou qualquer outro
ambiente que apenas leia este arquivo:

- Marcador numerado presente no material corresponde a uma sequência real
  (script SPIN, processo por etapas)? Numeração decorativa sobre lista sem
  ordem que importa é defeito de julgamento, registre em `decisoes_design`.
- Cada componente animado usado (gauge/donut/fluxo/accordion/barras/contador)
  serve o conteúdo — deixa a informação mais clara que o texto puro faria —
  ou está ali só porque o catálogo permite? Componente decorativo sem ganho de
  clareza é a mesma categoria de defeito que fundo chapado/título sólido.
- O material tem 1 elemento-assinatura de destaque, ou motion espalhado por
  toda parte sem hierarquia? Motion demais é o que faz o material parecer
  "gerado por IA" em vez de profissional.

### 3.1. Checar oportunidade de enriquecimento perdida (só `apresentacao`/`landing-page`)

Ver `.claude/skills/aplicador-marca-conexao/SKILL.md`, seção "Componentes animados de
dado". Se o `dossie_insumos.md` tem um dado numérico com limite, percentual do todo,
processo sequencial ou perguntas/respostas (objeções) e o material **não** usou o
componente correspondente (`gauge`/`donut`/`fluxo`/`accordion`/`barras`) — nem via
`componente`/`enriquecimentos` explícito, nem via caminho legado por palavra-chave —
isso é uma oportunidade perdida, mesmo espírito de "fundo chapado é defeito". Registre
em `decisoes_design` do parecer, mas **não** bloqueie a aprovação por causa disso
sozinho (não é claim incorreto nem quebra de marca, é refinamento) — só corrija você
mesmo (REGRA 4) se for simples (o dado já está claro no dossiê e cabe no schema do
componente sem reinterpretação).

### 4. Auto-correção (REGRA 4) antes de reportar bloqueio

Se um defeito for corrigível sem re-escrever o conteúdo do zero (ex.: hex hardcoded que
devia ser variável, texto de arte que excede o limite de caracteres), corrija você
mesmo e rode a validação de novo. Só escale para `esgotado` via
`orquestrar-pool-materiais.py --registrar <tipo> --falha "<motivo>"` depois de 3 tentativas.

### 5. Aprovar

Se tudo passar: `orquestrar-pool-materiais.py --registrar <tipo> --sucesso`. Acrescente ao
parecer (`output/<slug>/revisao/parecer_revisao.json`, ver "Saída" abaixo): decisões de
design tomadas (o que foi extraído/ajustado e por quê) e sugestões de legenda de
compartilhamento (para artes/landing) — isso alimenta `manifesto_materiais.json` via
`empacotar-projeto.py`.

## Saída

- `output/<slug>/revisao/parecer_revisao.json` — schema
  `{decisoes_design: [...], informacoes_faltantes: [...], sugestoes_legenda: [...]}`.
  **Sempre leia o arquivo existente e faça merge (append nas 3 listas) antes de
  gravar** — outros lotes/tipos podem já ter escrito aqui. Nunca sobrescreva por
  completo. Este arquivo é distinto de `relatorio_auditoria.json` (esse é gerado só por
  `scripts/auditar-projeto.py`, com dados puramente determinísticos — não escreva nele).

## Restrições

- Nunca aprove um material que passou nos scripts mas contém claim não rastreável ao
  dossiê — script verde não é suficiente, a checagem de fidelidade de conteúdo é sua.
- Nunca corrija um material fora do seu lote/tipo (evita conflito de escrita entre
  revisões paralelas, mesma disciplina do `subagente-revisor-tecnico` da referência).
