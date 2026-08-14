# Dossiê de Insumos — Kit inLego

## 1. Imagens fornecidas

| Arquivo | Descrição registrada | Conteúdo observado | Uso recomendado |
|---|---|---|---|
| `insumos/kit-inlego.png` | foto do produto Kit inLego | Foto oficial do estojo/case do Kit inLego aberto, mostrando a organização física dos componentes (Scan inL / SC / TS / Clipe Scan / hastes de escaneamento em alturas 5/10/15) sobre a tampa transparente com o logo "inLegO system" e o claim "Multiple/Unitary — Precision and Agility"; case com identificação "Conexão - Abutment/inL", "Conexão - implant/Transfer Scan", QR code de "Biblioteca Digital / Soluções digitais principais sistemas de implantes" | Imagem principal do produto — usar em destaque no PDF (seção de composição/kit). **Não gerar/ilustrar substituto** — esta é a única imagem oficial disponível. |

Nenhuma imagem citada no texto-base ficou sem correspondência no disco. Não há imagem de logo/marca separada fornecida — a aplicação de marca (cores, tipografia, componentes) é responsabilidade fixa de `brand/design-system-conexao.json` via `aplicador-marca-conexao`, fora do escopo deste dossiê.

## 2. Fatos e claims verificáveis extraídos do texto-base

Fonte única e literal: `insumos/texto-mae-03.txt` (novo texto-base informado na entrevista de regeneração `/gerar-pdf` — substitui `texto-mae-02.txt` nesta regeneração). Nenhum destes itens foi reformulado de forma a alterar o sentido; nenhum item fora desta lista deve ser usado pelos `redator-*`.

**Observação sobre a natureza do texto-base:** este arquivo é um **posicionamento comercial B2B dirigido ao Distribuidor** ("Como seu Especialista Estratégico, apresento o posicionamento de mercado que fará a sua distribuição dominar o setor de implantodontia digital") — argumentário de revenda: escalabilidade de faturamento, fidelização de contas estratégicas, giro de estoque, recorrência, margem. Diferente do `texto-mae-02.txt` anterior (guia técnico dirigido diretamente ao Doutor) e do `texto-mae.txt` original (guia tático de vendas para consultor). O leitor final dos materiais desta regeneração é o **distribuidor**, não o clínico.

### Posicionamento estratégico para o distribuidor
- O Kit inLego é apresentado como ferramenta de **escalabilidade de faturamento** e **fidelização de contas estratégicas** para o distribuidor.
- O inLego é a "melhor arma" do distribuidor para converter dentistas do fluxo analógico para o digital "de forma segura e altamente lucrativa".

### 1. Solução de "Gargalos Invisíveis" e Redução de Churn
- Na implantodontia analógica ou com *scanbodies* convencionais, o dentista perde tempo com "gambiarras" (elásticos e resinas) e o laboratório sofre para dar o *match* digital.
- Vender o inLego entrega **previsibilidade clínica** → reduz suporte técnico pós-venda → aumenta a confiança do dentista na curadoria de produtos do distribuidor → parceria de longo prazo e crescimento mútuo.

### 2. Superioridade Técnica como Barreira de Entrada para a Concorrência
- A concorrência entrega componentes "grossos" que exigem múltiplas etapas de escaneamento; o inLego possui USPs (Propostas Únicas de Valor) que "esmagam" os sistemas comuns:
  - **Hastes de Escaneamento em Etapa Única:** devido à altura estratégica das hastes, o dentista escaneia gengiva e componente de uma só vez → argumento de **ganho de produtividade** para o dono da clínica.
  - **Exclusividade das Hastes Duplas:** o pilar inLego permite duas hastes simultâneas, facilitando o escaneamento de áreas posteriores (distais) onde outros sistemas falham.
  - **Zero Parafuso Passante:** o rosqueamento é manual; resolve o problema de falta de espaço posterior — dor que concorrentes que vendem sistemas com chaves longas não conseguem resolver.

### 3. Modelo de Negócio Baseado em Fluxo e Recorrência
- O Kit inLego é a porta de entrada para o ecossistema **Conexão Digital Implant**.
- **Giro de Estoque:** o sistema é otimizado para os pilares **Micro Unit (MU)** e **Multi Base (MB)**; a venda do kit inLego "puxa" automaticamente a demanda por componentes protéticos e bibliotecas digitais associadas.
- **Diferencial Regional:** tecnologia que resolve a "confusão do escâner" na mandíbula — algo que nem os grandes players globais resolvem com a mesma simplicidade — dá ao distribuidor um diferencial competitivo regional agressivo.

### 4. Valor Agregado e Autoridade "Dark & Tech"
- A percepção de valor do inLego é potencializada pela identidade visual da marca.
- **Estética High-End:** uso de **PEEK de grau médico** e **titânio**, apresentados sob a estética **Dark & Tech (Azul Noturno e Dourado)** → transmite ao cliente do distribuidor sensação de estabilidade industrial e confiança tecnológica → permite **margem de lucro superior** comparada a componentes brutos e sem valor agregado de marca.

### Resumo para Negociação B2B (Distribuidor vs. Clínica)
- Argumento-chave cotado: *"Doutor, enquanto seus concorrentes estão perdendo tempo e dinheiro refazendo protocolos que não têm assentamento passivo, o Kit inLego garante que sua barra chegue perfeita de primeira, liberando sua cadeira para novos pacientes e escalando seu lucro"*.

### Itens não verificáveis / não presentes no texto-base (registrar como faltante se solicitados)
- Não há preço, condições comerciais, margens percentuais ou prazos de entrega no texto-base.
- Não há dados numéricos de redução de tempo/churn além das afirmações qualitativas (ex.: "tempo de trabalho pela metade" não é citado neste texto — a economia aparece como produtividade de etapa única).
- Não há especificações dimensionais de componentes neste texto (SC=10mm / TS=13mm não são citados aqui — vieram de texto-base anterior e **não devem ser usados como claim desta regeneração** sem confirmação; a imagem do produto sugere alturas 5/10/15, não confirmadas por este texto).
- Não há composição enumerada do kit (Scan inL / SC / TS) neste texto — apenas menção ao pilar inLego, hastes de escaneamento e otimização para MU e MB.
- Não há menção a "MU in lab" nem à "Ciência da Continuidade" neste texto — esses claims vieram de texto-base anterior e **não pertencem a esta regeneração**.

## 3. Escolhas do operador (fonte de verdade — não rederivar)

Lidas de `config_projeto.json` na regeneração pontual `/gerar-pdf kit-inlego` (entrevista de regeneração):

- **`publico_alvo`: `distribuidores`** (atualizado na entrevista de regeneração — era `clientes`)
- **`objetivo_tom`: `comercial_informacional_parceria`** (atualizado na entrevista de regeneração — era `informacional_tecnico`)
- **`edicao`: `1ª Edição do Distribuidor`** (atualizada na entrevista de regeneração — era `1ª Edição do Dentista`)
- **Imagem:** mantida (`insumos/kit-inlego.png`)
- **Texto-base:** novo — `texto-mae-03.txt` copiado de `C:\Users\trcnologia\Desktop\02_Conexao_Implantes\Kits\Kit inLego\texto-mae -03.txt`
- **Materiais desta regeneração:** apenas `pdf`

### Implicações práticas para os `redator-*`

- **`texto-mae-03.txt` se dirige diretamente ao Distribuidor** em 2ª pessoa ("sua distribuição", "para você"), com voz de Especialista Estratégico apresentando posicionamento de mercado — alinhado com `publico_alvo = distribuidores`. O argumento B2B aparece como citação do distribuidor falando com o Doutor — voz de negociação, para o próprio distribuidor usar.
- **Público distribuidores (o revendedor como leitor final):** copy comercial de parceria — escalabilidade de faturamento, fidelização de contas estratégicas, redução de churn/suporte pós-venda, giro de estoque e recorrência (MU/MB), diferencial regional, margem superior por valor agregado de marca.
- **Tom comercial/informacional de parceria de venda (`comercial_informacional_parceria`):** registro persuasivo de parceria B2B, com fundamentos técnicos servindo de argumento de venda — cada diferencial técnico é apresentado como vantagem comercial (produtividade do dono da clínica, barreira de entrada da concorrência, fluxo de recorrência). Não é didática técnica pura nem pitch frio: é o distribuidor como parceiro estratégico.
- **Título do PDF:** cunhar título **sóbrio, novo e técnico-comercial**, sem "gambiarra"/"gambiarras" nem "guia de treinamento" (lista `TITULOS_BANIDOS` de `validar-pdf.py`). Eixo preferencial: escalabilidade da distribuição / fluxo digital lucrativo / conversão de dentistas ao digital. Máx. 34 caracteres / 6 palavras, sem hífens.
- Esses valores são propagados sem alteração para `diretor-de-arte` → `brief_criativo.json`.

## 4. Handoff

Dossiê pronto para `diretor-de-arte` decompor `objetivo_tom` em `objetivo` (`comercial`) + `tom_de_voz` (`informacional_parceria`) e regravar o `brief_criativo.json`.
