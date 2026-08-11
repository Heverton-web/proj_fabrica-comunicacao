---
title: "Manual da Fábrica de Materiais de Comunicação"
subtitle: "Fluxo completo, comandos e entregáveis — Conexão"
date: "Agosto de 2026"
lang: pt-BR
---

# 1. Introdução

Este manual explica **como operar** a Fábrica de Materiais de Comunicação e **o que cada comando faz**. É dirigido a quem vai *usar* o sistema no dia a dia (marketing/operador), não a quem desenvolve o pipeline — para a arquitetura interna e as regras de engenharia, a fonte de verdade é `AGENTS.md`; para o procedimento técnico exato de cada comando, é `SPEC_COMANDOS.md`.

## O que a fábrica faz

A partir de **imagens + um texto-base** de um produto, a fábrica produz, de forma autônoma, um conjunto de materiais de comunicação com a marca Conexão:

- **PDF** (apostila/material de apoio)
- **Landing page** (HTML)
- **Apresentação** (HTML, tipo slide-deck)
- **Arte** para redes sociais em 3 formatos (1080×1080, 1080×1350, 1080×1920)
- **Textos** prontos para WhatsApp, Instagram e LinkedIn
- **Kit do Consultor** e **Kit Distribuidor** (10 artes + textos de WhatsApp cada)

A única etapa em que uma pessoa participa ativamente é a entrevista inicial (`/esbocar` ou um dos `/kit-completo-*`). Depois disso, o sistema produz, valida e corrige tudo sozinho.

## Pré-requisitos de ambiente

Quem for rodar a fábrica (ou dar suporte a quem roda) precisa ter instalado:

- **Pandoc** e **Typst** (CLI) — usados para gerar o PDF.
- **Playwright** (Python) — usado para renderizar HTML e "fotografar" as artes/kits em PNG.

O estado de cada projeto é sempre gravado em arquivos JSON dentro da pasta do projeto — nada fica só na memória da conversa.

---

# 2. Conceitos-chave

| Termo | Significado |
|---|---|
| **Slug** | Identificador único do projeto, em kebab-case (ex.: `kit-master-flex`). Vira o nome da pasta em `output/<slug>/`. |
| **Projeto** | Um produto/campanha em produção — tudo que se refere a ele vive em `output/<slug>/`. |
| **Insumos** | As imagens e o texto-base fornecidos pelo operador na entrevista. Fonte única de verdade de conteúdo — nada é inventado além do que está aqui. |
| **Dossiê de insumos** (`dossie_insumos.md`) | Fatos e claims extraídos dos insumos pelo `analista-insumos`. |
| **Brief criativo** (`brief_criativo.json`) | Mensagem central, hierarquia de conteúdo, tom, público e mapeamento de conteúdo por material, escrito pelo `diretor-de-arte`. |
| **Design system fixo** | Paleta, tipografia e componentes visuais da marca Conexão, definidos uma vez em `brand/design-system-conexao.json` e aplicados sempre da mesma forma pela skill `aplicador-marca-conexao` — não é reextraído a cada projeto. |
| **Material** | Cada um dos 9 tipos de entregável (pdf, landing-page, apresentacao, arte-01/02/03, textos, kit-consultor, kit-distribuidor). |
| **Lote (pool)** | A produção roda em paralelo, em lotes de até 4 materiais por vez, orquestrada por `pool-materiais.py`. |
| **Manifesto** (`manifesto_materiais.json`) | Relatório final de tudo que foi produzido: status, caminho, decisões de design, faltantes e sugestões de legenda/CTA por material. |

## Regras que todo operador deveria conhecer

1. **Fidelidade à fonte** — o sistema nunca inventa claim, número ou benefício que não esteja nos insumos. Se faltar informação, o material sai com uma nota de "faltante" em vez de um dado inventado.
2. **Autonomia após a entrevista** — depois de `/esbocar` (ou de um `/kit-completo-*`), não há mais perguntas; o sistema se autocorrige sozinho quando um validador aponta um problema.
3. **Nunca sobrescrever** — regenerar um material já entregue nunca apaga a versão anterior; cria `-v2`, `-v3`, etc. (ver seção 7).
4. **Scripts são o juiz** — toda validação (dimensão de imagem, peso de arquivo, ausência de erro de HTML etc.) é feita por script determinístico, nunca por "achismo" do agente.

---

# 3. Fluxo completo (visão geral)

```
Passo 1 — Entrevista (única interação humana)
  /esbocar  OU  /kit-completo-consultor|distribuidor|cliente
       │
       ├─► analista-insumos   → dossie_insumos.md
       └─► diretor-de-arte    → brief_criativo.json
       │
  config_projeto.json gravado

Passo 2 — Produção autônoma
  /produzir-comunicacao-completa <slug>
       │
       ├─ redator-arte (1x)      ─► arte/copies.json      (se houver arte selecionada)
       ├─ redator-kit-copy (1x)  ─► kits/copies.json       (se houver kit selecionado)
       │
       ├─ redator-apostila      ─► compilador-pdf     ─► output/<slug>/pdf/
       ├─ redator-landing       ─► compilador-html    ─► output/<slug>/landing-page/
       ├─ redator-apresentacao  ─► compilador-html    ─► output/<slug>/apresentacao/
       ├─ (copy compartilhada)  ─► compilador-arte    ─► output/<slug>/arte-01|02|03/
       ├─ redator-textos        ─► (grava .txt direto)─► output/<slug>/textos/
       └─ (copy compartilhada)  ─► compilador-kit     ─► output/<slug>/kit-consultor|distribuidor/
       │
       ▼
  revisor-marca  (fidelidade à fonte + fidelidade à marca)
       ▼
  auditar-projeto.py --estrito  (até 3 rodadas de autocorreção)
       ▼
  empacotar-projeto.py   → manifesto_materiais.json
       ▼
  empacotar-distribuicao.py → output/<slug>/distribuicao/ (finais + .zip + COPYRIGHT.txt)
```

Cada material tem seu próprio redator (fase 2), seu próprio compilador (fase 3) e seu próprio validador — mas todos passam pela mesma etapa final de revisão de marca e auditoria antes de serem empacotados.

**Nota:** a pasta `distribuicao/` é gerada por `empacotar-distribuicao.py` ao final do Passo 2. Se o pacote final não aparecer, verifique se essa etapa concluiu (pode ter sido pulada em execuções antigas do pipeline).

---

# 4. Como usar (passo a passo)

## 4.1 Iniciar um projeto novo — `/esbocar`

Rode `/esbocar` para começar. É uma entrevista guiada em 4 rodadas:

1. **Insumos** — nome do produto (se necessário), imagens e texto-base livre.
2. **Público-alvo** — escolha única entre `Consultores`, `Clientes` ou `Distribuidores`.
3. **Objetivo/tom** — escolha única entre `Educacional/Comercial`, `Informacional/Técnico` ou `Comercial/parceria de venda`.
4. **Materiais** — seleção múltipla entre os 9 materiais (se não escolher nenhum, o sistema assume todos). Se PDF for escolhido, pergunta a edição (ex.: "1ª Edição"). Se arte ou kit forem escolhidos, pergunta se quer os elementos gráficos decorativos (ativado por padrão).

Ao final, o sistema grava `config_projeto.json`, roda `analista-insumos` e `diretor-de-arte`, e devolve um resumo com o comando sugerido para o próximo passo.

## 4.2 Produzir tudo de uma vez — `/produzir-comunicacao-completa <slug>`

Depois do `/esbocar`, rode este comando para gerar todos os materiais selecionados, sem mais perguntas. O sistema:

- monta o plano de lotes e produz em paralelo (até 4 materiais por vez);
- tenta de novo automaticamente materiais que falharem (até 3 tentativas com espera crescente);
- revisa a marca, audita e empacota tudo ao final;
- devolve um relatório com o que foi entregue, o que ficou "esgotado" (falhou 3x) e o que está faltando por falta de insumo.

## 4.3 Atalhos por público — `/kit-completo-consultor` | `-distribuidor` | `-cliente`

Se você já sabe para quem é o material, use um desses três comandos: eles combinam `/esbocar` + `/produzir-comunicacao-completa` com o público e os materiais **já pré-definidos**, pulando a pergunta de seleção de materiais (ver tabela completa na seção 5).

## 4.4 Regenerar um material específico — `/gerar-<material>`

Use quando só precisa refazer **um** material (ex.: só o PDF mudou de conteúdo). Cada `/gerar-*` roda uma entrevista curta de confirmação (manter ou trocar imagem, texto-base, público, tom, edição) e **nunca sobrescreve** a versão anterior — cria `pdf-v2`, `landing-page-v2`, etc.

## 4.5 Onde encontrar os arquivos gerados

Tudo fica em `output/<slug>/`:

```
output/<slug>/
├── config_projeto.json          config gravada na entrevista
├── brief_criativo.json          brief do diretor-de-arte
├── manifesto_materiais.json     relatório final (status/faltantes/sugestões)
├── insumos/                     imagens + texto-base
├── pdf/                         apostila_<slug>.pdf + .md fonte
├── landing-page/                index.html
├── apresentacao/                index.html
├── arte-01/ arte-02/ arte-03/   3 PNGs cada (1 por copy)
├── kit-consultor/ kit-distribuidor/   10 PNGs + textos WhatsApp cada
├── textos/                      whatsapp.txt, instagram.txt, linkedin.txt
├── revisao/                     relatorio_auditoria.json
└── distribuicao/                pacote final: .zip + COPYRIGHT.txt
```

---

# 5. Catálogo de comandos

Para cada comando: **o que é / o que faz / pré-requisitos / o que entrega / quando usar**. Fonte canônica: `SPEC_COMANDOS.md`.

## `/esbocar`

- **O que é:** ponto de entrada da fábrica — a única interação humana de verdade do fluxo principal.
- **O que faz:** entrevista de 4 rodadas (insumos → público → objetivo/tom → materiais), grava `config_projeto.json`, roda `analista-insumos` e `diretor-de-arte`.
- **Pré-requisitos:** nenhum.
- **O que entrega:** `config_projeto.json`, `brief_criativo.json`, `dossie_insumos.md`, insumos copiados para a pasta do projeto, e o comando sugerido para o próximo passo.
- **Quando usar:** para começar um projeto do zero.

## `/produzir-comunicacao-completa <slug>`

- **O que é:** produção 100% autônoma de todos os materiais selecionados na entrevista.
- **O que faz:** valida pré-condições → gera copies compartilhadas de arte/kit (uma vez cada) → produz em lotes paralelos de até 4 → revisa marca → audita → empacota (`empacotar-projeto.py` + `empacotar-distribuicao.py`).
- **Pré-requisitos:** `/esbocar` já ter rodado para o slug (se não tiver, o próprio comando roda `/esbocar` primeiro).
- **O que entrega:** todos os materiais selecionados + `manifesto_materiais.json` + pacote de distribuição em `output/<slug>/distribuicao/`.
- **Quando usar:** logo depois de `/esbocar`, para gerar tudo de uma vez.

## `/gerar-pdf <slug>`

- **O que é:** regeneração pontual só do PDF (apostila).
- **O que faz:** entrevista curta de confirmação (manter/trocar imagem, texto-base, público, tom, edição) → resolve pasta de destino sem sobrescrever (`pdf`, `pdf-v2`...) → `redator-apostila` → `compilador-pdf` → `validar-pdf.py` → revisão de marca → auditoria só das pastas afetadas → reempacotamento.
- **Pré-requisitos:** `output/<slug>/brief_criativo.json` já existir (ou seja, `/esbocar` já rodou).
- **O que entrega:** um novo PDF (nova pasta versionada se já havia um).
- **Quando usar:** quando só o conteúdo/edição do PDF precisa mudar.

### Contrato técnico do PDF (Mosaico Conexão Premium)

- Formato A4, retrato, **texto 100% vetorial** (nunca imagem de texto), arquivo **abaixo de 5 MB**.
- Capa escura com vinheta e blobs de luz azul, faixas douradas finas (0.3cm), logo horizontal, bloco central único (imagem + título + parágrafo, 11.5cm de largura).
- Título da capa: máx. 34 caracteres/6 palavras, sem hífen, remete ao tema do texto-base (nunca o nome cru do produto nem clichês banidos, ex. "guia de treinamento").
- Cabeçalho interno dinâmico: título à esquerda, edição + data à direita.
- Páginas internas em fundo branco, título nível 1 em dourado, níveis 2/3 em azul/cinza escuro.
- Estrutura padrão de 7 seções: Abertura → Problema → Solução → Destaques → Composição/especificações → Aplicação → Fechamento.
- **Estrutura por público** (quando gerado via `/kit-completo-*`): consultor e distribuidor recebem seções extras de técnica de venda (SPIN — Situação/Problema/Implicação/Necessidade — e contorno de objeções); distribuidor ainda ganha "Rentabilidade para o seu negócio"; cliente foca em diferenciais para a prática clínica, sem técnica de venda.
- Validação (`validar-pdf.py`): arquivo não vazio, < 5 MB, texto extraível, contagem de páginas coerente, título/parágrafo da capa dentro dos limites de linha e sem clichês banidos.

## `/gerar-landing <slug>`

- **O que é:** regeneração pontual só da landing page.
- **O que faz:** mesmo procedimento de `/gerar-pdf`, trocando o material principal para `landing-page`.
- **Pré-requisitos:** mesmos de `/gerar-pdf`.
- **O que entrega:** novo `index.html` da landing page (versionado se já existia).
- **Quando usar:** quando só o copy/estrutura da landing precisa mudar.

### Contrato técnico da landing page

- HTML autocontido (CSS embutido, sem CDN externa), responsivo, sem erro de console, sem asset quebrado.
- Cores/fontes só via variáveis CSS do design system fixo (nunca cor/fonte hardcoded).
- Estrutura: Hero → problema→solução → destaques → prova/composição técnica e comercial → CTA final.
- Títulos em caixa alta, peso 900, com gradiente de assinatura da marca; faixas douradas finas no topo/rodapé.
- Validação (`validar-html.py`, via Playwright): abre a página, falha se houver erro de console, asset quebrado ou overflow horizontal.

## `/gerar-apresentacao <slug>`

- **O que é:** regeneração pontual só da apresentação (slide-deck HTML).
- **O que faz:** mesmo procedimento de `/gerar-pdf`, trocando o material principal para `apresentacao`.
- **Pré-requisitos:** mesmos de `/gerar-pdf`.
- **O que entrega:** novo `index.html` da apresentação.
- **Quando usar:** quando só o conteúdo/ordem dos slides precisa mudar.

### Contrato técnico da apresentação

- Estrutura de slides: capa → diferenciais → composição → especificações → scripts/SPIN → objeções → fechamento/CTA.
- Navegação por setas, barra de espaço e clique; títulos em caixa alta com gradiente da marca.
- Listas com 4+ itens dividem automaticamente em 2 colunas; painéis com respiro mínimo de 32px.
- Slide de torque cirúrgico (quando aplicável) tem um medidor visual (gauge) animado.
- Mesma validação técnica (`validar-html.py`) da landing page.

## `/gerar-textos <slug>`

- **O que é:** regeneração pontual só dos textos de apoio (WhatsApp/Instagram/LinkedIn).
- **O que faz:** mesmo procedimento de `/gerar-pdf`, trocando o material principal para `textos`; grava `.txt` direto, sem etapa de compilação HTML/PNG.
- **Pré-requisitos:** mesmos de `/gerar-pdf`.
- **O que entrega:** `whatsapp.txt`, `instagram.txt`, `linkedin.txt` em `output/<slug>/textos/`.
- **Quando usar:** quando só o copy de redes sociais precisa mudar.

## `/gerar-arte <slug> [--tamanho 1080x1080|1080x1350|1080x1920 ...]`

- **O que é:** comando guarda-chuva para regenerar 1, 2 ou as 3 variantes de arte de uma vez.
- **O que faz:** roda a entrevista de confirmação **uma única vez** (não repete por variante), resolve a pasta de destino de cada variante e dispara o procedimento específico de cada uma. Sem `--tamanho`, regenera as 3.
- **Pré-requisitos:** mesmos de `/gerar-pdf`.
- **O que entrega:** até 9 PNGs (3 copies × 3 variantes) se todas forem regeneradas.
- **Quando usar:** para regenerar mais de uma variante de arte de uma vez, sem repetir a entrevista.

## `/gerar-arte-1080x1080` · `/gerar-arte-1080x1350` · `/gerar-arte-1080x1920`

- **O que é:** regeneração pontual de uma única variante de arte. `1080x1080` = `arte-01` (WhatsApp/post quadrado), `1080x1350` = `arte-02` (post retrato Instagram/LinkedIn), `1080x1920` = `arte-03` (Stories/Reels).
- **O que faz:** entrevista de confirmação (se chamado direto) → se a copy compartilhada (`arte/copies.json`) ainda não existir, gera as 3 copies uma única vez → renderiza as 3 copies nessa variante via Playwright.
- **Pré-requisitos:** mesmos de `/gerar-pdf`.
- **O que entrega:** 3 PNGs (1 por copy) na variante regenerada.
- **Quando usar:** para ajustar só um formato específico de arte.

### Contrato técnico da arte (as 3 variantes)

- **Formato × copy são eixos independentes:** existem sempre 3 copies (ângulos criativos distintos, ex. problema / diferencial técnico / versatilidade) e cada uma é renderizada em todos os formatos selecionados — nunca uma copy por formato.
- Dimensão pixel-perfect exata por formato; teto de peso 1 MB por PNG.
- Limites de texto (mesmos nos 3 formatos, já que a copy é compartilhada): headline ≤ 60 caracteres, subcopy ≤ 120, CTA ≤ 30.
- Imagem do produto sempre em evidência (ocupa a maior parte do bloco de conteúdo); nunca reduzida para caber texto — o texto é que se ajusta.
- Título em no máximo 2 linhas, nunca uma palavra isolada sozinha na linha.
- Exatamente **1 badge por peça** (o CTA) — nenhum badge de contexto adicional.
- Elementos decorativos de fundo (formas geométricas finas e discretas) ativados por padrão; pode ser desligado na entrevista (`elementos_decorativos: false`).
- Nome do arquivo sempre com os dois eixos juntos: `arte_<slug>_<formato>_copy<NN>.png`.
- Validação (`validar-dimensoes.py`): dimensão exata, exatamente 3 PNGs por formato, peso abaixo do teto.

## `/gerar-kit-consultor <slug>` · `/gerar-kit-distribuidor <slug>`

- **O que é:** regeneração pontual de um dos dois kits (10 artes + textos de WhatsApp cada).
- **O que faz:** entrevista de confirmação → se a copy compartilhada (`kits/copies.json`, 10 copies) ainda não existir, gera uma única vez → renderiza as 10 copies com o CTA/assinatura da variante (consultor ou distribuidor).
- **Pré-requisitos:** mesmos de `/gerar-pdf`.
- **O que entrega:** 10 PNGs 1080×1350 + 10 `texto_whatsapp.txt` + 10 `conteudo.json`.
- **Quando usar:** para regenerar só um dos dois kits sem tocar no outro.

### Contrato técnico dos kits

- Público, produto, formato (1080×1350) e os **5 tons de voz** fixos (`informativa`, `contra-intuitiva`, `tecnica`, `efeito-uau`, `educativa`) — não fazem parte da entrevista.
- `kit-consultor` e `kit-distribuidor` **compartilham as mesmas 10 copies** (2 por tom); só mudam CTA final e assinatura de rodapé — qualquer outra divergência entre os dois kits é tratada como defeito.
- Cada item = 1 PNG 1080×1350 + 1 `texto_whatsapp.txt` (mensagem pronta com gancho por tom, headline em negrito, bullet de subcopy, CTA em destaque) + 1 `conteudo.json`.
- Mesmas regras de imagem/título/badge/decoração da arte (herdadas de `SPEC_ARTE.md`).
- Validação (`validar-kit.py`): as 5 pastas de tom existem, cada uma com 2 subpastas (`arte-01`/`arte-02`), cada uma com 1 PNG + 1 `conteudo.json` + 1 `texto_whatsapp.txt` — total de 10 + 10 + 10 por kit.

## `/kit-completo-consultor` · `/kit-completo-distribuidor` · `/kit-completo-cliente`

- **O que é:** atalhos "tudo-em-um" — equivalem a `/esbocar` + `/produzir-comunicacao-completa`, mas com **público e materiais pré-definidos**, pulando a pergunta de seleção.
- **O que fazem:** entrevista reduzida (só insumos, objetivo/tom, edição do PDF e, para consultor/distribuidor, elementos decorativos) → produção autônoma completa do preset.
- **Pré-requisitos:** nenhum (podem iniciar projeto novo) — também servem para regenerar parcialmente um projeto existente do mesmo preset.
- **Presets:**

| Comando | Público fixo | Materiais fixos |
|---|---|---|
| `/kit-completo-consultor` | Consultores | PDF + Kit do Consultor + Landing page + Apresentação |
| `/kit-completo-distribuidor` | Distribuidores | PDF + Kit Distribuidor + Landing page + Apresentação |
| `/kit-completo-cliente` | Clientes | PDF + Landing page + Apresentação (sem kits/artes) |

- **Conteúdo por público:**
  - **Consultor:** foco em técnica de venda (SPIN) + contorno de objeções + fechamento.
  - **Distribuidor:** igual ao consultor, mais "Rentabilidade para o seu negócio".
  - **Cliente:** foco em diferenciais para a prática clínica e "por que utilizar este produto" — sem técnica de venda.
- **O que entrega:** os materiais do preset, já revisados, auditados e empacotados.
- **Quando usar:** quando o público já é conhecido de antemão e você quer pular a etapa de escolher materiais manualmente.

---

# 6. Materiais entregues — visão de uso

| Material | Para que serve na prática |
|---|---|
| **PDF (apostila)** | Material de apoio completo, compartilhável por e-mail/WhatsApp, para leitura detalhada (técnica, comercial ou clínica conforme o público). |
| **Landing page** | Página única para campanha digital (link em bio, anúncio, e-mail marketing). |
| **Apresentação** | Slide-deck HTML para reunião comercial, treinamento ou pitch ao vivo. |
| **Arte (3 formatos)** | Peças visuais para redes sociais — quadrado (feed), retrato (feed/carrossel) e vertical (Stories/Reels). |
| **Textos** | Copy pronto para colar em WhatsApp, Instagram e LinkedIn, sem precisar redigir do zero. |
| **Kit do Consultor** | 10 peças + textos de WhatsApp para o consultor usar em prospecção/relacionamento com dentistas. |
| **Kit Distribuidor** | Mesmo conteúdo do Kit do Consultor, com CTA/assinatura voltados para o distribuidor. |

## 6.1 Pacote de Distribuição — a entrega final

O **Pacote de Distribuição** não é um material novo: é o **invólucro final** que reúne
a versão mais recente de cada material já `concluido_autonomo`, pronto para ser
enviado ao cliente/time comercial sem nenhum arquivo interno de trabalho.

**Quando é gerado:** automaticamente, ao final de **todo** ciclo de produção ou
regeneração — nunca é um passo manual separado:

- ao final de `/produzir-comunicacao-completa` (Passo 6, depois de `empacotar-projeto.py`);
- ao final de qualquer `/gerar-<material>` (reempacotamento só das pastas afetadas);
- ao final de qualquer `/kit-completo-consultor|-distribuidor|-cliente`.

Ou seja, o pacote **se auto-atualiza a cada ciclo**: sempre reflete o estado mais
recente do projeto, nunca precisa ser pedido separadamente.

**Onde fica:** `output/<slug>/distribuicao/` (gerado por `scripts/empacotar-distribuicao.py <slug>`).

**Do que é composto:**

- 1 subpasta por material com status `concluido_autonomo`, contendo **só o
  resultado final** (a versão mais recente em disco, maior sufixo `-vN`):
  - `pdf/` → apenas o `.pdf` (sem o `.md` fonte);
  - `landing-page/`, `apresentacao/` → a pasta HTML inteira (com assets);
  - `arte-01/`, `arte-02/`, `arte-03/` → os PNGs da variante;
  - `textos/` → os `.txt` de WhatsApp/Instagram/LinkedIn;
  - `kit-consultor/`, `kit-distribuidor/` → os 10 PNGs + 10 `texto_whatsapp.txt` (+ `conteudo.json`);
- `COPYRIGHT.txt` na raiz do pacote (direitos autorais da marca Conexão);
- `distribuicao_<slug>.zip` — o pacote inteiro compactado, dentro da própria pasta `distribuicao/`.

**O que fica de fora (de propósito — REGRA 2, silenciamento estético):** insumos,
`brief_criativo.json`, `config_projeto.json`, `manifesto_materiais.json`,
`dossie_insumos.md` e a pasta `revisao/`. Isso é o que separa a pasta
`output/<slug>/` (área de trabalho completa) da pasta `distribuicao/` (só o produto final).

---

# 7. Versionamento e nunca-sobrescrever

Regra fixa do sistema: **nenhum comando `/gerar-<material>` sobrescreve um material já entregue.** Ao detectar que a pasta de destino já existe, o sistema cria a próxima versão disponível (`pdf-v2`, `landing-page-v3`, `arte-01-v2`...). Todas as versões ficam listadas em `manifesto_materiais.json`, com status e caminho de cada uma.

Na prática, isso significa que é seguro rodar `/gerar-pdf` várias vezes seguidas para testar variações — nada do que já foi aprovado é perdido.

---

# 8. Perguntas frequentes / solução de problemas

**Um material apareceu como "esgotado" no relatório final. O que aconteceu?**
O sistema tentou produzir aquele material até 3 vezes (com espera crescente entre tentativas) e não conseguiu passar na validação. Verifique o motivo no relatório e, se for algo pontual (ex.: insumo insuficiente), rode o `/gerar-<material>` correspondente depois de ajustar os insumos.

**O material saiu com uma nota de "informação faltante". É um bug?**
Não — é o sistema respeitando a regra de fidelidade à fonte: quando o texto-base não traz um dado necessário (ex.: preço, margem, especificação técnica), o material é entregue mesmo assim, com a lacuna sinalizada em vez de um dado inventado. Para resolver, complemente o texto-base e rode `/gerar-<material>` de novo.

**Preciso trocar só a imagem/texto-base de um material específico. Preciso rodar `/esbocar` de novo?**
Não. Use o `/gerar-<material>` correspondente — ele faz uma entrevista curta só para confirmar o que muda, sem repetir as 4 rodadas completas.

**Onde vejo o resultado final para entregar ao cliente/time comercial?**
Em `output/<slug>/distribuicao/` — pacote com os materiais finais, mais recentes de cada tipo, compactado em `.zip`, sem os arquivos internos de trabalho (insumos, briefs, JSONs).

**Rodei um `/kit-completo-*` mas quero adicionar um material que não está no preset.**
Use o `/gerar-<material>` do material que falta diretamente sobre o mesmo slug — ele funciona em projetos já existentes, preset ou não.

---

# 9. Glossário

- **`config_projeto.json`** — configuração gravada por `/esbocar`: slug, insumos, público, tom, materiais selecionados.
- **`brief_criativo.json`** — brief criativo gerado pelo `diretor-de-arte`: mensagem central, hierarquia, mapeamento de conteúdo por material.
- **`dossie_insumos.md`** — fatos/claims extraídos dos insumos pelo `analista-insumos`.
- **`manifesto_materiais.json`** — relatório final por material: status, caminho, decisões de design, faltantes, sugestões de legenda/CTA.
- **`copies.json`** (em `arte/` e `kits/`) — as copies (headline/subcopy/CTA) compartilhadas entre variantes de arte ou entre os dois kits.
- **Redator** — skill responsável por escrever o conteúdo de um material (`redator-apostila`, `redator-landing`, `redator-apresentacao`, `redator-arte`, `redator-kit-copy`, `redator-textos`).
- **Compilador** — skill responsável por transformar o conteúdo escrito no arquivo final (`compilador-pdf`, `compilador-html`, `compilador-arte`, `compilador-kit`).
- **Revisor de marca** (`revisor-marca`) — audita fidelidade à fonte e à marca depois da compilação, antes do empacotamento.
- **Auditoria** (`auditar-projeto.py`) — verificação final de conformidade do projeto inteiro, com até 3 rodadas de autocorreção.
- **Design system fixo** — `brand/design-system-conexao.json`, aplicado sempre da mesma forma pela skill `aplicador-marca-conexao`.
- **Pacote de distribuição** (`output/<slug>/distribuicao/`, gerado por `empacotar-distribuicao.py`) — entrega final: só os resultados mais recentes dos materiais concluídos, sem arquivos internos de trabalho, com `COPYRIGHT.txt` e `distribuicao_<slug>.zip` dentro. Ver seção 6.1.
