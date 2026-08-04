# PRD — Fábrica de Materiais de Comunicação

## Problema

Times de marketing/comercial que atendem múltiplas marcas ou lançam múltiplos produtos
precisam gerar, para cada lançamento, um conjunto repetitivo de materiais — um PDF
explicativo, uma landing page, uma apresentação e artes para redes sociais — sempre
respeitando a identidade visual da marca e sem inventar informação técnica que não
esteja documentada. Hoje isso é feito manualmente peça por peça (como no exemplo real
que originou este projeto: uma peça Conexão/Kit Master Flex produzida via Claude
Design), o que é lento e depende de um designer disponível a cada novo produto.

## Objetivo

Dado (1) imagens do produto/marca, (2) um texto-base com a informação a comunicar e as
escolhas do operador de público-alvo e objetivo/tom (o design system é **fixo** —
`brand/design-system-conexao.json`), gerar de forma autônoma o subconjunto de
materiais que o operador escolher — PDF apostila, landing page, apresentação, e/ou
artes PNG em 3 formatos — todos fiéis à fonte e à marca.

## Usuário-alvo

Consultor comercial, analista de marketing ou operador de conteúdo que não é designer,
mas precisa produzir material de divulgação consistente com a marca em minutos, não
dias — o mesmo perfil do colaborador que usou o Claude Design manualmente no exemplo
Conexão/Kit Master Flex.

## Jobs-to-be-done

1. "Quero descrever meu produto uma vez e receber todos os formatos de material que
   minha equipe usa para divulgar — sem re-explicar a marca a cada peça."
2. "Quero ter certeza de que o material gerado não inventa nenhum dado técnico que eu
   não forneci, e que respeita as cores/fontes da minha marca."
3. "Quero poder gerar só uma parte (ex.: só as artes de Instagram) sem refazer todo o
   processo."

## Fora de escopo (v1)

- Distribuição automática (postar direto no Instagram/LinkedIn/WhatsApp) — a fábrica
  entrega os arquivos prontos, o operador distribui.
- Múltiplas variações de copy por material (A/B) — v1 gera 1 versão por material.
- Vídeo/motion.
- Tradução automática para outros idiomas do texto-base.

## Métricas de sucesso

- Tempo do briefing (entrevista do `/esbocar`) até `output/<slug>/` completo, sem
  intervenção humana.
- Taxa de conformidade na primeira passada de `auditar-projeto.py --estrito` (sem
  necessidade de retrabalho manual pós-entrega).
- Zero claims não rastreáveis ao texto-base/imagens fornecidos (REGRA 6 do `CLAUDE.md`).

## Fluxo de produto (ver `SPEC.md` para o contrato técnico completo)

**Rodada 1 — Entrevista de insumos** (`/esbocar`): quais imagens, qual texto-base. O
design system é fixo — não é mais perguntado.

**Rodada 2 — Entrevista de público-alvo** (`/esbocar`): seleção única entre
Consultores, Clientes e Distribuidores.

**Rodada 3 — Entrevista de objetivo/tom de voz** (`/esbocar`): seleção única entre
Educacional/Comercial, Informacional/Técnico e Comercial/Informacional técnico de
parceria de venda.

**Rodada 4 — Entrevista de materiais** (`/esbocar`): quais dos 6 tipos de material
gerar.

**Fábrica autônoma** (`/produzir-comunicacao-completa <slug>`): geração paralela em
lote, revisão de marca, compilação por tipo, empacotamento final.
