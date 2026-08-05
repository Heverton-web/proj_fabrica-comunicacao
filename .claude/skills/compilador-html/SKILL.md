---
name: compilador-html
description: Fase 3 da Fábrica de Materiais de Comunicação — monta apresentacao/index.html e landing-page/index.html a partir do conteúdo estruturado (slides.json/conteudo.json), aplicando o design system fixo da Conexão. Use depois de redator-apresentacao/redator-landing, antes de validar-html.py/revisor-marca.
---

# Skill: Compilador de HTML

Você monta os dois materiais HTML (apresentação e landing page) — mesmo compilador para
ambos, templates diferentes. **Antes de gerar qualquer HTML/CSS, aplique
`.claude/skills/aplicador-marca-conexao/SKILL.md`** — ela é a única fonte de verdade de
cores, fontes e componentes (botão, badge, card). Não invente padrão visual aqui.

Para qualidade visual de HTML/CSS fora do que a marca já define, apoie-se nos skills
genéricos do catálogo (`frontend-design`, `web-artifacts-builder`, `high-end-visual-design`)
em vez de reinventar orientação de design do zero.

## Entrada

- `output/<slug>/apresentacao/slides.json` **ou** `output/<slug>/landing-page/conteudo.json`
- `brand/design-system-conexao.json` (fixo, mesmo para todo projeto)
- `templates/apresentacao.html` **ou** `templates/landing.html` — já vêm com o `:root`
  e os `@font-face` da marca embutidos; normalmente você não precisa tocar nisso, só
  nos placeholders de conteúdo.

## Procedimento

### 1. Executar a Compilação via `scripts/compilar-html.py`

Toda compilação de HTML do projeto foi centralizada de forma robusta e automatizada no script utilitário **`scripts/compilar-html.py`**. Ele gerencia cópias de fontes, logo horizontal de marca, imagem do produto e executa o processamento do conteúdo. Invoque o script informando o slug e o tipo do material:
```bash
python scripts/compilar-html.py <slug> apresentacao
python scripts/compilar-html.py <slug> landing-page
```

### 2. Auto-detecção de Layouts e Recursos Visuais (Apresentação)

O compilador lê o arquivo `slides.json` e monta os blocos correspondentes de forma inteligente a partir de palavras-chave do título:
- **Slide de Capa:** Cria um layout de duas colunas (Hero) com dados/badges à esquerda e imagem de alta qualidade do produto à direita.
- **Divisão em Duas Colunas (Respiro 32px):** Se um slide do tipo conteúdo tiver **4 ou mais marcadores**, o compilador os divide automaticamente em duas colunas paralelas (`.duas-colunas`) para que preencham a tela com excelente respiro lateral e tamanho de fonte perfeito. Os painéis (`.slide ul`) têm obrigatoriamente pelo menos **32px de padding** vertical.
- **Fluxograma Horizontal Animado (Layout `fluxo`):** Se o título tiver `"Script"`, `"SPIN"` ou `"Passos"`, converte os bullets em uma trilha de passos conectados horizontalmente por setas e com atrasos de animação stagger.
- **Tabela Técnica com Gauge SVG (Layout `torque`):** Se o título tiver `"Torque"`, renderiza uma tabela de especificações à esquerda e um indicador de torque seguro (SVG Gauge) à direita, cujas agulha e arco se movem de forma animada quando o slide recebe a classe `.ativo`.
- **Efeitos de Destaque Neon:** Realiza o parsing de marcas de markdown e aplica cores neon Conexão (Roxa, Azul, Verde, Vermelha) nas chaves e drivers, substituindo os asteriscos em tags HTML válidas.

### 3. Atenção — regra de ouro (bug já ocorrido, não repita)

Nos templates os placeholders de bloco vivem DENTRO de um comentário HTML (`<!-- {{HERO}} -- compilador-html substitui: ... -->`). Substitua o comentário INTEIRO pelo HTML gerado usando regex com a flag de quebra de linhas ativa (`flags=re.DOTALL`), senão o comentário permanece e os slides ficam invisíveis no navegador.

### 4. Handoff e Validação

Após a compilação, execute os validadores do projeto para atestar a conformidade técnica e fidelidade estrita das cores:
```bash
python scripts/validar-html.py <slug> <tipo>
python scripts/validar-design-tokens.py <slug> <tipo>
```

## Restrições

- **Sem Hexadecimais Não Homologados:** Para passar no validador `validar-design-tokens.py`, o arquivo final gerado não pode conter nenhum código hexadecimal de cor (`#RRGGBB`) que não esteja explícito no arquivo de tokens fixo. Para cores adicionais de destaque, luzes ou efeitos decorativos neon, utilize estritamente a notação funcional **`rgb()`** ou **`rgba()`** CSS.
- Botão/CTA primário sempre usa `var(--gradiente-assinatura)`, nunca `var(--accent)`
  chapado. No slide final (CTA), o botão deve ser translúcido e discreto, em total conformidade visual.
- HTML deve ser autocontido (sem CDN externo, inclusive de fonte).
  chapado — ver `aplicador-marca-conexao`.
- HTML deve ser autocontido (sem CDN externo, inclusive de fonte) — mesma disciplina de
  artifacts self-contained.
