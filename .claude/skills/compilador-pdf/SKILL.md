---
name: compilador-pdf
description: Fase 3 da Fábrica de Materiais de Comunicação — compila apostila_<slug>.md em PDF via Pandoc + Typst, usando templates/template_apostila.typ de padrão premium (Mosaico Conexão Premium / Flex Gold) de forma totalmente automatizada. Use depois de redator-apostila, antes de validar-pdf.py/revisor-marca.
---

# Skill: Compilador de PDF

Você compila o Markdown da apostila em PDF final aplicando as regras premium de diagramação (Mosaico Conexão Premium / Flex Gold).

O PDF ganhou regras visuais definitivas (estilo "Flex Gold"): capa com fundo escuro e blobs, faixas douradas em gradiente metálico, bloco único de 11.5cm (imagem do produto em evidência 8cm + título + parágrafo), título temático em caixa alta com Inter 900 (Black) em no máximo 2 linhas sem palavra isolada, logotipo horizontal de marca e imagem do produto perfeitamente centralizados, cabeçalho dinâmico (título à esquerda, edição e data à direita), contracapa com o mesmo logo em tamanho discreto, e conteúdo interno com fundo branco para leitura confortável de alta definição.

A **capa remete ao tema do material**: `scripts/compilar-pdf.py` extrai da seção
`## Abertura` do Markdown o `capa_titulo` (primeiro H1, nunca o próprio rótulo
estrutural da seção como "Abertura") e o `capa_paragrafo` (primeiro parágrafo após
o H1) e os passa como `-V capa_titulo=...` / `-V capa_paragrafo=...` ao template —
o título da capa nunca usa o rótulo genérico "Guia de Treinamento" (SPEC_PDF
endurecido). Se a seção "## Abertura" não existir ou não tiver um H1 temático
válido, `capa_titulo`/`capa_paragrafo` caem no fallback genérico (título/mensagem
central do brief) — sinal de que `redator-apostila` precisa ser rodado de novo
para essa seção.

**Enforcement determinístico do título (não depende só do redator acertar de
primeira):** antes de montar as flags, `compilar-pdf.py` insere um espaço
inseparável (NBSP) entre as 2 últimas palavras de `capa_titulo`/`capa_paragrafo`
(evita palavra isolada na última linha) e compila em loop, reduzindo a variável
`capa_titulo_size` do template (24pt → piso de 18pt, nunca menos — ver
`SPEC_PDF.md`) até o título medir ≤ 2 linhas sem linha órfã, usando
`scripts/validar-pdf.py::medir_titulo_capa` como árbitro (REGRA 8). Mesmo papel do
ajuste de font-size via JS nos templates de arte (`SPEC_ARTE.md`), só que resolvido
recompilando no lado Python em vez de medir no navegador.

**Duas variantes de capa (`capa_variante`):** o padrão (`capa_variante` ausente) mostra
a foto do produto em evidência — sempre usado para apostilas de kit, nunca troque isso,
é o que permite identificar de relance qual material é aquele num catálogo com vários
kits. A variante `capa_variante=institucional` troca a foto do produto pelo logo da
marca (`logo_imagem_hero`, normalmente `Logo_Conexão_vertical_texto_branco.png`) no
mesmo bloco de destaque e omite o logo pequeno do topo — reservada para materiais que
falam da marca/da Fábrica em si, sem produto específico (ex.: `manuais/MANUAL_EXECUTIVO.pdf`,
compilado à parte, fora do pipeline de `compilar-pdf.py`, com `pandoc ... --template
templates/template_apostila.typ -V capa_variante=institucional -V logo_imagem_hero=...`).
Ver `SPEC_PDF.md` para o contrato completo de cada variante.

Se precisar de técnicas auxiliares de manipulação de PDF fora do que Pandoc+Typst cobre, consulte o skill genérico `pdf` do catálogo.

## Entrada

- `output/<slug>/<pasta>/apostila_<slug>.md` (`<pasta>` normalmente `"pdf"`, ou uma
  versão regenerada como `"pdf-v2"` — informada pelo subagente que te invoca; ver
  REGRA 11 do `AGENTS.md`)
- `brand/design-system-conexao.json`
- `templates/template_apostila.typ`

## Procedimento

### 1. Executar a Compilação via `scripts/compilar-pdf.py`

Toda compilação de PDF do projeto foi centralizada de forma robusta e automatizada no script utilitário **`scripts/compilar-pdf.py`**. Ele gerencia o carregamento de variáveis do design system, metadados do projeto, edição de escolha do operador, imagem do produto e executa o processamento. Invoque o script informando o slug (e a `--pasta`, se for diferente do padrão `"pdf"`):
```bash
python scripts/compilar-pdf.py <slug>
python scripts/compilar-pdf.py <slug> --pasta pdf-v2   # regeneracao pontual (REGRA 11)
```

O script lê `brand/design-system-conexao.json` diretamente (cores/tipografia), resgata a edição do `config_projeto.json` e repassa para o Pandoc e Typst as flags `-V` de forma perfeitamente separada e argv-normalizada (evitando bugs de leitura silenciosa de variáveis), compilando o arquivo final com integridade máxima de design e cores. Internamente ele recompila em loop (ver acima) só para resolver o `capa_titulo_size` — isso é transparente para quem invoca o script, que só vê o `[OK]`/`[FALHA]` final.

### 2. Handoff e Validação

`scripts/validar-pdf.py <slug> --pasta <pasta>` confirma tamanho/páginas/texto vetorial **e as checagens
determinísticas de capa e contracapa** (título ≤ 2 linhas sem palavra isolada remetendo
ao tema do texto-mãe; parágrafo da capa em bloco quadrado sem palavra isolada; logo da
marca presente na última página — via spans/imagens PyMuPDF); `revisor-marca` faz a
checagem de fidelidade de conteúdo e de marca.

## Restrições

- Nunca hardcode cor/fonte no comando ou no template — tudo vem de `brand/design-system-conexao.json`, lido por `scripts/compilar-pdf.py` e repassado via `-V`.
- Nunca duplique a lógica de "quantas linhas o título ocupa" — ela vive em `scripts/validar-pdf.py::medir_titulo_capa` e é importada por `compilar-pdf.py`, nunca reimplementada.
- Se a compilação falhar (Pandoc ou Typst com erro), tente uma correção estrutural óbvia no Markdown (ex.: tabela mal fechada) antes de escalar como falha — REGRA 4.
