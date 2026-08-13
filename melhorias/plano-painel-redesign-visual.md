# Plano de Ação — Redesign Visual do Painel de Controle

**Status:** confirmado via `/interview-me` (ver seção 5), pendente de implementação
**Data:** 2026-08-13
**Escopo:** só `painel/static/index.html` e `painel/static/app.js` — nenhuma mudança de
API, comportamento de backend ou funcionalidade já existente.

---

## 1. Contexto

O painel (`painel/static/index.html` + `app.js`) ganhou várias correções funcionais
numa mesma sessão (ícones, barra de progresso, proteção do workspace raiz, novos
harnesses, reordenação de passos — ver histórico de commits em
`feature/painel-controle-multi-harness`). Depois de usar o resultado, o operador
identificou um incômodo que nenhuma dessas correções resolveu: o visual da página
está "feio" — seis `<section>` com estilo idêntico, empilhadas num scroll único.

A primeira hipótese levantada foi trocar o scroll por um formulário multipasso
(wizard com Próximo/Voltar). A entrevista (`/interview-me painel` → `wizard
multipasso`) mostrou que essa não é a solução certa — ver seção 4.

## 2. Padrão de uso real (o que a entrevista revelou)

- **Setup (workspace + harness/credenciais) é raro** — configurado uma vez por
  workspace, raramente revisitado.
- **Iteração (projetos existentes + novo projeto + disparar + acompanhar jobs) é
  frequente** — o operador repete disparos de materiais diferentes no mesmo
  workspace várias vezes seguidas.
- O incômodo real é visual ("feio"), não de navegação — o operador considera o
  scroll atual **melhor que um wizard** em termos de visibilidade (consegue ver o
  painel de jobs rodando enquanto configura o próximo disparo).

## 3. Decisão

**Não construir um wizard sequencial (Próximo/Voltar) que esconde passos.** Um
wizard resolveria "página longa" escondendo conteúdo, mas pioraria exatamente o que
o operador já valoriza (ver tudo ao mesmo tempo durante a iteração) — e não
resolveria o "feio" sozinho, já que um wizard com o mesmo CSS plano continuaria
parecendo plano, só que um passo de cada vez.

Em vez disso, redesign do **mesmo layout de scroll único**, em 3 frentes:

1. **Colapsar o setup depois de configurado.** Assim que workspace + harness
   estiverem escolhidos, os passos 1 (Workspace) e 2 (Harness/credenciais) encolhem
   para um resumo de uma linha (ex.: `Workspace: output/ · Harness: claude-code ✓
   — editar`), expansível sob demanda. Isso é responsável pela maior parte do
   scroll hoje durante a fase de iteração (a mais frequente) e some sem esconder
   nada que o operador precisaria checar no meio do fluxo.
2. **Hierarquia visual real nos passos 3-6** (Projetos existentes, Novo projeto,
   Disparar produção, Jobs do workspace) — hoje são seis cards com peso visual
   idêntico independente da frequência de uso; a leitura de "feio" vem
   provavelmente disso, não da quantidade de scroll em si.
3. **Painel de jobs (passo 6) nunca colapsa nem esconde** — é a única coisa que o
   operador ativamente observa enquanto itera, constraint inegociável.

## 4. Por que não o wizard (registro da entrevista)

| Hipótese testada | Resultado |
|---|---|
| Wizard resolve "página feia" | Não — o mesmo CSS plano, só que um card por vez, continua plano. O problema é visual, não de quantidade de passos visíveis. |
| Wizard resolve a fricção de repetição | Não — o padrão de uso real é "configurar uma vez, iterar muito" sobre os passos 3-6; forçar Próximo/Voltar nesses passos atrapalharia a repetição em vez de ajudar. |
| Scroll atual é o problema | Parcialmente — o scroll incomoda especificamente na fase de iteração por causa dos passos 1-2 (setup) permanecerem sempre expandidos ocupando espaço, não pelos passos 3-6 em si. |

## 5. Confirmação

Plano fechado e confirmado explicitamente pelo operador em `/interview-me` nesta
sessão (3 pontos da seção 3, como bloco único). Escopo institucional: **este tipo de
documento de intenção/plano passa a ser sempre salvo em `docs/melhorias/`** (não em
`docs/intent/`), a partir desta decisão.

## 6. Fora de escopo

- Wizard de verdade com Próximo/Voltar escondendo passos.
- Qualquer mudança de API, comportamento de job runner, adaptadores de harness ou
  regras de negócio já implementadas nesta sessão.
- Reescrita em framework (React/Vue/etc.) — continua HTML/CSS/JS puro, página
  estática única servida por `StaticFiles`.
