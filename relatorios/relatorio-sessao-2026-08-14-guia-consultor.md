# Relatório de Sessão — 2026-08-14 (Guia do Consultor no pacote de distribuição)

**Status:** entregue e em produção (commit `c183c45`, pushado para `main`); planejamento de
etapa seguinte (ícones SVG + animações em apresentação/landing-page) feito, não implementado.
**Data:** 2026-08-14
**Branch:** `main` (commit direto, sem branch de feature)

---

## 1. O que foi pedido

Criar um HTML com a identidade visual da marca Conexão explicando, em linguagem simples e
não técnica, o conteúdo dos pacotes de distribuição e como os Consultores Conexão devem usar
cada material no canal certo — com o objetivo de causar um efeito "uau" no consultor. Em
seguida, verificar se esse material poderia ser gerado automaticamente como parte do fluxo da
fábrica e incluído no pacote de distribuição de todo projeto.

## 2. O que foi feito

### 2.1 Levantamento de dados reais (sem inventar nada — REGRA 6)

Antes de escrever qualquer linha do guia, foram lidos diretamente do repositório:

- `brand/design-system-conexao.json` — paleta (`bg #0f172a`, `surface #1e293b`, `accent
  #c9a655`, gradiente de assinatura `#c9a655→#e8d48b→#a8873a`), tipografia (Inter 300–900,
  fallback Roboto), componentes (botão pill, badge, card) e regra de logo obrigatório.
- `brand/kits-conexao.json` — estrutura do Kit Consultor (CTA "Fale com seu consultor
  Conexão") vs. Kit Distribuidor (CTA "Peça ao seu distribuidor Conexão").
- `AGENTS.md` e `SPEC_COMANDOS.md` — tabela completa dos 9 tipos de material e o Passo 6
  (empacotamento final).
- `scripts/empacotar-distribuicao.py` e `scripts/empacotar-projeto.py` — lógica exata de
  como o pacote `distribuicao/` e o `.zip` são montados.
- Projeto real já processado (`output/vulcano-actives/`) — nomes de arquivo reais
  (`arte_vulcano-actives_01_copy01.png`, `texto_whatsapp.txt`, legendas por canal etc.) para
  o guia nunca citar um caminho hipotético.

### 2.2 `templates/guia-consultor-conexao.html`

Página única, autocontida (fontes Inter 400/600/700/900 e logo horizontal em base64 — sobrevive
sozinha mesmo isolada do resto do projeto, dentro do `.zip`), ~469 KB, fiel ao design system
(cores, gradiente, tipografia e componentes pill/card oficiais). Conteúdo:

- O que é o pacote de distribuição.
- Cada material explicado (o que é / para que serve / como usar no dia a dia / onde encontrar,
  com nomes de arquivo reais) — PDF, Apresentação, Landing Page, Arte 1080×1080/1350/1920, Kit
  do Consultor, Textos de Apoio.
- Tabela "qual material usar em cada situação" (visita, WhatsApp frio, LinkedIn, Stories...).
- Os 5 tons do Kit do Consultor explicados em linguagem simples.
- 6 boas práticas de ouro.

Validado visualmente com Playwright (screenshot da página completa) antes de ser considerado
pronto — não apenas leitura de código.

### 2.3 Integração no fluxo (decisão do operador: sim, aplicar)

`scripts/empacotar-distribuicao.py` passou a copiar o guia como `GUIA-DO-CONSULTOR.html` na
raiz de todo pacote (mesmo padrão já usado para `COPYRIGHT.txt`), tanto na pasta `distribuicao/`
quanto dentro do `.zip` — sem exigir nenhuma outra mudança, porque o zip já varre
`pacote.rglob("*")` automaticamente.

Documentação canônica atualizada para refletir o novo conteúdo do pacote (REGRA 10 —
nunca deixar o texto divergir do código): `AGENTS.md`, `SPEC_COMANDOS.md` (5 ocorrências) e
`manuais/MANUAL_FABRICA.md`.

## 3. Como foi validado (evidência, não opinião)

- `python scripts/verificar-consistencia-pipeline.py --estrito` → `[OK]`.
- `python scripts/empacotar-distribuicao.py <slug>` reexecutado nos **11 projetos** já
  existentes em `output/` (`kit-expertguide`, `kit-inlego`, `kit-inlego-v2`, `kit-master-flex`,
  `kit-master-flex-02`, `kit-protetico`, `kit-start-flex`, `kit-stop-drill`,
  `tratamento-de-superficie`, `vulcano-actives`, `vulcano-actives-2`) — todos reempacotados sem
  erro.
- Conferido por script (não por suposição) que `distribuicao/apresentacao/index.html` existe e
  tem conteúdo real (28–35 KB) nos 11 projetos, e que `GUIA-DO-CONSULTOR.html` e `COPYRIGHT.txt`
  aparecem dentro do `.zip` de teste (`vulcano-actives`).
- Suíte de testes do pre-commit: **17/17 passando** (`tests/test_extrair_claims_candidatos.py`,
  `tests/test_parametros_projeto.py`).

## 4. Esclarecimento dado ao operador durante a sessão

O operador perguntou se os pacotes reempacotados já tinham a apresentação ou se ela havia sido
criada nesta sessão. Resposta confirmada por script: **nenhuma apresentação foi criada agora**
— `empacotar-distribuicao.py` só copia artefatos que **já existiam em disco** de rodadas
anteriores de `/produzir-comunicacao-completa`; o reempacotamento serviu apenas para injetar o
novo guia dentro do `.zip` já existente de cada projeto.

## 5. Planejamento da próxima etapa (não implementado)

O operador aprovou o resultado do guia e pediu para avaliar aplicar o mesmo método (HTML
autoral, cuidado de marca) na **Apresentação** e na **Landing Page**, com uma ressalva: nada de
emoji como ícone — usar SVGs únicos (bespoke, não de biblioteca genérica) — e reaproveitar as
animações que já são regra no design system.

Diagnóstico feito antes de planejar: `templates/apresentacao.html` e `templates/landing.html`
**já não usam emoji hoje** (gauge/donut já são SVG animado). O gap real é outro: (1) não existe
uma biblioteca de ícones oficial documentada — hoje bullets/destaques são só texto; (2) as
regras de animação (`entradaSuave`, `entradaEscala`, `focoProgressivo`, `assentamento3D`,
`pulsoAnel`, `stroke-dashoffset` do gauge/donut, sempre com `var(--ease-premium)` + stagger +
fallback `prefers-reduced-motion`) existem só como CSS solto dentro dos dois templates, nunca
formalizadas em `aplicador-marca-conexao/SKILL.md` como fonte única de verdade (REGRA 6).

Decisão de escopo confirmada pelo operador: mexer nos **templates compartilhados**
(`templates/apresentacao.html` e `templates/landing.html`, usados por `compilador-html` em todo
projeto futuro) — não um caso pontual isolado do `kit-expertguide`.

Plano em 6 passos entregue ao operador (aguardando sinal para execução):

1. Desenhar 8 ícones SVG genéricos e bespoke (problema, solução, dado técnico, evidência,
   processo, checklist, tempo, contato) — reaproveitáveis por qualquer produto, não ilustração
   por produto.
2. Formalizar em `aplicador-marca-conexao/SKILL.md`: seção **Ícones** (biblioteca fixa) e seção
   **Animações** (consolidar as regras hoje dispersas nos templates).
3. Cablear os ícones nos dois templates, entrando com as animações já existentes (sem inventar
   nova).
4. Adicionar um campo determinístico (`categoria`, vocabulário fechado de 8 valores) no schema
   que `redator-apresentacao`/`redator-landing` já escrevem, para o compilador saber qual ícone
   usar sem "achismo" (REGRA 6).
5. Reforçar `scripts/validar-html.py` (REGRA 8, árbitro determinístico): falha `--estrito` se
   aparecer emoji no HTML renderizado, ou se um bullet/card marcado com `categoria` não tiver o
   SVG correspondente.
6. Validar num slug de teste (nunca direto num projeto real) com `validar-html.py --estrito`,
   `auditar-projeto.py --estrito` e screenshot Playwright confirmando que a animação dispara de
   verdade ao trocar `.ativo`/`.visivel` — só depois decidir com o operador se os 11 projetos já
   entregues são regenerados (sempre como nova versão `-vN`, REGRA 11, nunca sobrescrevendo).

## 6. Estado final do repositório

- `main` atualizada com o commit `c183c45` (5 arquivos, +544/−14), pushado para o remoto.
- Novo arquivo versionado: `templates/guia-consultor-conexao.html`.
- `scripts/empacotar-distribuicao.py` alterado (cópia do guia) e já validado contra os 11
  projetos reais existentes em `output/` (pastas `output/**/distribuicao/` não são versionadas
  por git — apenas regeneradas em disco).
- Nenhuma mudança pendente de commit relacionada a este trabalho; arquivos não relacionados
  (`.token-economy` modificado, `manuais/manual-submodulos-git.*` não versionados) foram
  deixados intocados por não fazerem parte do escopo desta sessão.
- Etapa de ícones SVG/animações em apresentação e landing-page: **planejada, não iniciada**.
