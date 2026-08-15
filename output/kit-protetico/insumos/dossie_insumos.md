# Dossiê de Insumos — Kit Protético

## 1. Imagens fornecidas

| Arquivo | Descrição registrada | Conteúdo observado | Uso recomendado |
|---|---|---|---|
| `insumos/kit_protetico_01.png` | foto do produto Kit Protético | Foto oficial do estojo/case do Kit Protético Conexão Digital aberto, com a tampa exibindo "KIT PROTÉTICO" e logo Conexão; bandeja com chave catraca com referenciador de torque, chave digital, chave fricção, e as pontas/chaves organizadas e rotuladas: "Fenda Média", "Quadrada 1,3 Média", "Quadrada 1,3 Longa", "Hexagonal 1,2 Curta", "Hexagonal 1,2 Média", "Hexagonal 1,2 Longa", "Hexagonal 0,9 Média", "Hex. Int. 2,0", "Hex. Int. 2,5", "Hex. Int. 2,7", além de compartimentos "Extra" vazios | Imagem principal do produto — usar em destaque no PDF (seção de composição/kit) e como imagem central da arte-01. **Não gerar/ilustrar substituto** — esta é a única imagem oficial disponível. |

Nenhuma imagem citada no texto-base ficou sem correspondência no disco. Não há imagem de logo/marca separada fornecida — a aplicação de marca (cores, tipografia, componentes) é responsabilidade fixa de `brand/design-system-conexao.json` via `aplicador-marca-conexao`, fora do escopo deste dossiê.

## 2. Fatos e claims verificáveis extraídos do texto-base

Fonte única e literal: `insumos/texto-mae.txt` ("Inteligência Comercial: Kit Protético Conexão Digital", material voltado a Consultores de Vendas, foco tático/vendas/resultados B2B). Nenhum destes itens foi reformulado de forma a alterar o sentido; nenhum item fora desta lista deve ser usado pelos `redator-*`.

### Posicionamento
- O Kit Protético Conexão Digital é posicionado como a solução definitiva para organização e precisão no fluxo reabilitador.
- Em um mercado onde a falha protética pode comprometer a reputação do dentista, o kit entrega "a segurança do torque exato", essencial para a longevidade dos implantes.
- Não é apenas um conjunto de chaves — é descrito como "um sistema de garantia clínica" que assegura instalação de cada componente conforme as especificações da engenharia (fonte: Manual Kit Protético).

### Diferenciais técnicos
- Principal diferencial: a Chave Catraca com referenciador de torque.
- Todos os pilares e parafusos de fixação devem receber a carga exata recomendada pelo fabricante, para evitar solturas ou fraturas (Manual Kit Protético).
- O kit prioriza biossegurança: totalmente passível de esterilização em autoclave antes de cada procedimento (Manual Kit Protético).

### Componentes do kit
Inventário completo que atende às diversas geometrias do sistema Conexão Digital:
- **Controle de Torque:** 1 Chave catraca com referenciador + 1 Chave digital (Manual Kit Protético).
- **Chaves de Fenda e Fricção:** 1 Chave com encaixe fenda média + 1 Chave Fricção média (Manual Kit Protético).
- **Variedade Hexagonal e Quadrada:**
  - Hexagonal (0,9mm): 1 unidade média.
  - Quadrada (1,3mm): 3 unidades (curta, média, longa).
  - Hexagonal (1,2mm): 3 unidades (curta, média, longa).
- **Hexagonais Internas:** 3 unidades (2,0mm, 2,5mm e 2,7mm), todas no modelo médio (Manual Kit Protético).

### Versatilidade
- Disponibilidade de chaves em 3 tamanhos (curta, média, longa) permite procedimentos em pacientes com diferentes aberturas bucais ou em regiões posteriores de difícil acesso.
- Essa completude elimina a necessidade de o profissional improvisar ou adquirir peças avulsas de sistemas terceiros que podem não ter o ajuste perfeito.

### Script de vendas — Framework SPIN Selling (material de apoio ao consultor)
- Situação: pergunta sobre como é feita hoje a gestão das chaves protéticas no consultório (organizada ou dispersa).
- Problema: menção a dificuldade de alcançar dente posterior por falta de chave mais longa, ou soltura de parafuso por incerteza de torque.
- Implicação: prótese que solta por falta de torque preciso gera retrabalho (tempo de cadeira) e afeta a confiança do paciente no tratamento.
- Necessidade de Solução: proposta de um kit que unifica todas as chaves em 3 comprimentos + catraca torquímetro de alta precisão.

### Contorno de objeções (material de apoio ao consultor)
- Objeção de preço ("investimento parece alto") → resposta: o valor do kit se paga na primeira intercorrência evitada; torque inadequado é a principal causa de retorno de pacientes; kit é um "seguro" para a durabilidade do trabalho.
- Objeção de compatibilidade ("já tenho chaves de outras marcas") → resposta: chaves Conexão são usinadas especificamente para os parafusos da marca; chaves de terceiros podem gerar folgas microscópicas que levam a desgaste prematuro do componente e podem invalidar garantias técnicas de fábrica.

### Itens não verificáveis / não presentes no texto-base (registrar como faltante se solicitados)
- Não há preço, condições comerciais ou prazos de entrega no texto-base.
- Não há valor numérico exato de torque (N·cm) mencionado — o texto fala em "carga exata recomendada pelo fabricante" e "torque exato", sem especificar o número.
- Não há especificação de material de fabricação das chaves (ex.: tipo de aço) alem da menção genérica a "usinadas especificamente para nossos parafusos".

## 3. Escolhas do operador (fonte de verdade — não rederivar)

Lidas de `config_projeto.json`:

- **`publico_alvo`: `consultores`**
- **`objetivo_tom`: `educacional_comercial`**

### Implicações práticas para os `redator-*`

- **Público consultores:** o copy deve falar diretamente com quem vai apresentar/vender o produto ao dentista — pode e deve usar o vocabulário técnico-comercial já presente no texto-base (SPIN Selling, contorno de objeções, nomenclatura de torque/geometrias de chave) sem necessidade de simplificação para leigos. O consultor é o operador do argumento de venda, não o cliente final.
- **Tom educacional/comercial:** os materiais devem primeiro ensinar o consultor sobre o que é e como funciona o Kit Protético (diferenciais técnicos, composição do kit, versatilidade) e, a partir desse entendimento, municiá-lo com o argumento comercial (script SPIN, contorno de objeções) para vender com autoridade técnica — não é um tom puramente informativo/técnico neutro, nem puramente comercial agressivo. Materiais como PDF e apresentação devem reservar espaço explícito para a camada didática (o "porquê" técnico) antes de chegar ao "como vender".
- Esses dois valores são propagados sem alteração para `diretor-de-arte` → `brief_criativo.json` e devem se manter consistentes em todos os materiais selecionados (pdf, landing-page, apresentacao, arte-01/02/03, textos, kit-consultor, kit-distribuidor). Os kits têm público fixo próprio (`dentista_implantodontista`, independente de `publico_alvo`), conforme `SPEC_KITS.md`.

## 4. Handoff

Dossiê pronto para `diretor-de-arte` decompor `objetivo_tom` em `objetivo` (`educacional`) + `tom_de_voz` (`comercial`) e desenhar o `brief_criativo.json`.
