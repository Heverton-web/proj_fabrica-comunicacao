---
name: redator-apresentacao
description: Fase 2 da Fábrica de Materiais de Comunicação — escreve o conteúdo estruturado (JSON de slides) da apresentação HTML a partir do brief_criativo.json. Use quando "apresentacao" estiver em materiais_selecionados, antes de compilador-html.
---

# Skill: Redator de Apresentação

Você escreve o conteúdo dos slides — 1 conceito por slide, linguagem direta o
suficiente para leitura em tela durante uma reunião. Ver `SPEC_HTML.md`.

## Entrada

- `output/<slug>/brief_criativo.json` (seção `mapeamento_por_material.apresentacao`)
- `output/<slug>/insumos/dossie_insumos.md`

## Saída

- `output/<slug>/<pasta>/slides.json` — `<pasta>` é informada pelo subagente que te
  invoca (normalmente `"apresentacao"`, ou `"apresentacao-v2"` numa regeneração via
  `/gerar-apresentacao` — REGRA 11 do `AGENTS.md`: nunca escreva por cima de uma
  versão já entregue). Lista de slides, schema:
  `{slides: [{tipo: "capa"|"conteudo"|"cta", titulo, corpo?, imagem?, categoria?, componente?}]}`,
  consumido por `compilador-html`. No item de `corpo`, além da string legada
  `"**Titulo** — Texto"`, pode-se usar o objeto `{"texto": "...", "categoria": "<cat>"}`
  para marcar um card individual; `categoria` no slide aplica o ícone a todos os
  cards do slide. `categoria` é o vocabulário fechado da seção "Ícones" do
  `aplicador-marca-conexao` (8 valores) — nunca invente categoria.

## Procedimento

1. **Capa** — nome do material/produto + mensagem central do brief.
2. **1 slide por item da hierarquia de conteúdo** (problema, solução, cada destaque
   técnico relevante) — texto curto (headline + até 3 bullets), nunca parágrafo denso;
   um slide é lido em segundos, não estudado.
3. **Componentes animados de dado (preferencial — ver
   `.claude/skills/aplicador-marca-conexao/SKILL.md`, seção "Componentes animados de
   dado"):** quando o dossiê tiver um dos gatilhos abaixo, acrescente o campo
   `componente` explícito ao slide — **nunca invente dado para caber num componente,
   REGRA 6**:
   - Dado numérico com limite/faixa de segurança → `componente: {"tipo": "gauge", ...}`.
   - Processo sequencial (script de vendas, "como funciona em N passos") →
     `componente: {"tipo": "fluxo", ...}`.
   - Estatística isolada de destaque ("50% menos tempo") → `componente: {"tipo": "contador", ...}`.
   - Percentual do todo (cobertura, redução, taxa) → `componente: {"tipo": "donut", ...}`.
   - Perguntas/respostas (objeções, dúvidas) → `componente: {"tipo": "accordion", ...}`
     — substitui a tabela plana de objeções.
   - Múltiplas specs do mesmo tipo comparadas lado a lado → `componente: {"tipo": "barras", ...}`.

   **Caminho legado (sem `componente`):** o compilador ainda auto-detecta pelo título
   ("Script"/"SPIN" → fluxo, "Torque" → gauge, "Objeções"/"Tabela" → tabela) para
   compatibilidade — mas usa valores fixos, não o dado real do seu projeto. Prefira
   sempre o campo `componente` explícito.
   - **Composição/Versatilidade/Diferenciais** sem gatilho de componente continuam como
     bullets em painel double-bezel — 4+ itens dividem automaticamente em duas colunas.
   - **Ícones da biblioteca fixa (opcional — ver
     `.claude/skills/aplicador-marca-conexao/SKILL.md`, seção "Ícones"):** para slides
     descritivos (Problema, Solução, Evidência, Processo, Check-list, Prazo, Contato),
     marque `categoria` no slide (aplica a todos os cards) ou por item de `corpo` via
     objeto. O ícone entra reusando `entradaSuave` — nunca invente categoria fora do
     vocabulário de 8, nem use emoji.
4. **Sem Hífens nos Títulos:** É expressamente proibido usar hífens (-) nos títulos de slides. Use sempre dois-pontos (:) para divisões ou subtítulos.
5. **Slide de fechamento** — CTA + assinatura de marca.

### Critério de julgamento de design (embutido — funciona em qualquer harness)

Esta orientação está escrita aqui, não referenciada de uma skill externa, para
funcionar igual em Claude Code, Antigravity, OpenCode, Freebuff, MiMoCode ou
qualquer outro ambiente que apenas leia este arquivo como instrução:

- **Marcador numerado (1/2/3...) só se a ordem carregar informação real**
  (`fluxo` do script SPIN, processo com etapas) — nunca aplique numeração a uma
  lista que não é sequência, só para "parecer mais dinâmico".
- **Cada componente animado precisa ganhar o slide por servir o conteúdo, não
  por estar disponível no catálogo.** Nem todo dado numérico do dossiê precisa
  virar gauge/donut/barras — se a visualização não adiciona clareza sobre o
  texto puro, bullets simples são a escolha certa (REGRA 6: enriquecer não é
  decorar).
- **Um elemento-assinatura por material, não animação espalhada por toda
  parte.** Motion demais é o que faz um material parecer "gerado por IA" em
  vez de profissional — prefira 1 momento de destaque real bem executado a
  vários efeitos medianos.

Cada slide deve caber sem scroll no template de apresentação (ver `SPEC_HTML.md`) —
prefira cortar conteúdo secundário a espremer texto. Se uma imagem fornecida pelo
operador ilustra bem um slide, referencie-a; nunca gere ilustração no lugar dela.

## Estrutura por público (preset `/kit-completo-<publico>`)

Se `config_projeto.preset_kit_completo` existir, monte os slides seguindo o **foco**
da tabela de presets da seção `/kit-completo-consultor` de `SPEC_COMANDOS.md`
(canônico dos 3 presets — variantes em `/kit-completo-distribuidor` e
`/kit-completo-cliente`), sempre 1 conceito por slide:

- **`consultores`:** O que é · Para que serve · Diferenciais técnicos.
- **`distribuidores`:** O que é · Para que serve · Diferenciais técnicos ·
  Rentabilidade para o seu negócio.
- **`clientes`:** O que é · Para que serve · Diferenciais técnicos · Diferenciais
  para a prática clínica · Por que utilizar este produto.

Regra (REGRA 6): rentabilidade/prática clínica/por que utilizar só entram como slide
com dados do dossiê — sem evidência, a seção não vira slide e a lacuna é registrada
como faltante (nunca suposição). Sem preset, vale o procedimento default acima.

## Tom de voz por público-alvo (obrigatório — REGRA 6)

Leia `brief_criativo.publico_alvo` e aplique o registro de linguagem definido em
`brand/publicos-alvo.json`. A apresentação é usada em reunião — o tom define se ela
funciona como pitch técnico, educação do paciente ou proposta de parceria.

| Público | Tom | Estrutura dos slides |
|---------|-----|----------------------|
| `consultores` | Técnico-clínico | 1 slide = 1 spec ou indicação clínica — sem bullet genérico |
| `clientes` | Acessível/orientador | Narrativa antes/depois, dor → alívio — nunca tabela de specs como slide principal |
| `distribuidores` | Comercial-parceiro | Pitch de parceria: mercado → produto → programa de distribuição → próximos passos |

O `dossie_insumos.md` gerado por `analista-insumos` já traz as implicações práticas
do público escolhido — use-as como guia, não as re-derive do texto-base.

## Restrições

- Nunca invente destaque/claim fora do dossiê de insumos (REGRA 6).
- Nunca inclua cor/fonte no `slides.json` — só conteúdo; estilo vem do design system
  fixo (`brand/design-system-conexao.json`) via `compilador-html`/`aplicador-marca-conexao`.
- O tom de voz vem de `brief_criativo.tom_de_voz` (escolha do operador, via
  `brand/publicos-alvo.json`) — nunca re-derive do texto-base.
- Handoff: `compilador-html` consome `slides.json` + `templates/apresentacao.html`.
