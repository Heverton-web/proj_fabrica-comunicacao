# Dossiê de Insumos — VULCANO ACTIVES

Projeto: `vulcano-actives` · Edição: "1ª Edição do Cliente" · Gerado pelo skill `analista-insumos` (Fase 1 — Nó 0A).

## 1. Inventário de imagens

| # | Arquivo | Descrição | Status | Uso previsto |
|---|---------|-----------|--------|--------------|
| 1 | `insumos/flex_01.png` (2560×2230, RGBA) | Render 3D de dois implantes dentários de titânio sobre fundo preto (esq.: conexão interna; dir.: hexágono externo) — ver `insumos/imagem_descricao.md` | **DISPONÍVEL** (fornecida pelo operador em 2026-08-14) | Capa do PDF, imagem principal das artes e materiais visuais |

**Observação:** a imagem foi fornecida pelo operador (caminho `F:/#PRODUTOS/.../flex_01.png`)
e copiada para `output/vulcano-actives/insumos/flex_01.png`. Nunca substituir por
ilustração gerada (REGRA 6).

## 2. Fatos e claims verificáveis (fonte de verdade — REGRA 6)

Extraídos do texto-base `insumos/texto_base.md`, sem reformulação de sentido:

1. Porous e Vulcano Actives são superfícies da **Conexão Sistemas de Prótese** — duas gerações distintas de bioengenharia, cada uma com indicações precisas.
2. **Porous = bioatividade passiva:** abordagem mecânico-subtrativa; a osseointegração depende da topografia de picos e vales para estabilizar o coágulo e permitir migração celular. Solução biomecanicamente estável e consagrada.
3. **Vulcano Actives = bioatividade ativa:** atua como biomaterial bioativo; processo de **oxidação por arco micro-elétrico (MAO)** incorpora íons de **Cálcio (Ca) e Fósforo (P)** diretamente na estrutura do titânio; concentração de fósforo **> 7%**; faz o organismo reconhecer o implante como parte do tecido mineralizado; acelera drasticamente a precipitação de apatita biológica.
4. **Hidrofilia Porous:** moderada; camada de óxido de titânio do tipo rutilo ou amorfa.
5. **Hidrofilia Vulcano Actives:** extrema; o tratamento induz a **fase cristalina anatase** (alta energia de superfície); o sangue molha toda a superfície instantaneamente após a instalação; facilita a retenção da rede de fibrina ("andaime" para formação óssea rápida).
6. **Rugosidade Porous:** homogênea entre **0,5 e 1,0 µm**; ideal para casos convencionais.
7. **Rugosidade Vulcano Actives:** média de **1,26 µm**; pesquisas do **Dr. Carlos Nelson Elias** confirmam ser o "ponto ideal" para diferenciação de células-tronco mesenquimais em **osteoblastos**, evitando formação de tecido fibroso e promovendo matriz calcificada densa diretamente sobre o metal.
8. **Desempenho Porous:** indicada para casos convencionais e ossos de maior densidade; taxa de sucesso longitudinal de **98,4%** (estudo de 6 anos).
9. **Desempenho Vulcano Actives:** ferramenta de eleição para **carga precoce (45 a 60 dias)** e situações desafiadoras — pacientes **fumantes, diabéticos** ou **ossos de baixa densidade (Tipo IV)**; **100% de sucesso em casos de osso tipo IV** e taxa geral de **97,7%** em protocolos de 60 dias em humanos.
10. **Resumo (fonte):** Porous = excelência da fixação mecânica comprovada por décadas; Vulcano Actives = sinalização química e física avançada que **elimina o período de latência óssea**, permitindo finalizar tratamentos com maior agilidade e segurança, mesmo em cenários biológicos adversos.

## 3. Escolhas do operador (fonte de verdade — rodadas 2 e 3)

| Campo | Valor escolhido | Implicações práticas para os redatores |
|---|---|---|
| `publico_alvo` | **clientes** | Registro de linguagem de `brand/publicos-alvo.json.clientes`: vocabulário **acessível, sem jargão sem explicação**; postura orientadora (explica, não impressiona com técnica); benefício concreto em linguagem cotidiana; evitar termos clínicos sem explicação e especificações numéricas isoladas sem contexto de benefício. CTA padrão: "Fale com um especialista". Ênfase por material: PDF = problema do paciente → como o produto resolve → o que esperar; arte = headline de resultado/benefício (não de spec). |
| `objetivo_tom` | **informacional_tecnico** | Objetivo `informacional` + tom `tecnico`. O texto-base é denso em especificação (MAO, anatase, µm, Ca/P) — para público **clientes**, traduzir cada conceito técnico em benefício concreto (previsibilidade, segurança, agilidade), mantendo precisão factual e sem superlativo sem evidência. |
| Combinação | clientes + informacional_tecnico | Explicar o que é osseointegração, MAO, fase anatase e rugosidade em linguagem acessível, sempre amarrando ao benefício (recuperação mais rápida, mais segurança em casos desafiadores). Nunca listar spec solta. |

**Kits (exceção de público):** `kit-consultor` selecionado usa público fixo `dentista_implantodontista` (nunca o `publico_alvo` do projeto) e os 5 tons fixos de `brand/tons-kit.json` — registro técnico-clínico em 2ª pessoa, 1 ideia por peça.

## 4. Faltantes identificados (REGRA 6 — nunca preencher por suposição)

1. ~~**Imagem do produto (render 3D):** sem arquivo físico em disco~~ — **RESOLVIDO** (flex_01.png fornecida em 2026-08-14).
2. **Dados comerciais:** preço, códigos de produto, condições — ausentes do texto-base.
3. **Referências dos estudos clínicos:** nomes/datas/autores dos estudos citados (98,4% em 6 anos; 97,7% em 60 dias; 100% osso tipo IV) — não constam no texto-base.
4. **"Kit do Cliente":** citado pelo operador na rodada 4, mas **não é um tipo de material suportado** pela fábrica (`TIPOS_VALIDOS` = pdf, landing-page, apresentacao, arte-01/02/03, textos, kit-consultor, kit-distribuidor) — registrado, não produzido.

## 5. Handoff

`diretor-de-arte` assume a partir deste dossiê para gerar `brief_criativo.json`.
