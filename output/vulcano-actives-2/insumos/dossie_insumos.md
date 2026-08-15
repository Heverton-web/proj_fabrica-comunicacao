# Dossiê de Insumos — VULCANO ACTIVES 2

Projeto: `vulcano-actives-2` · Edição: "1ª Edição" · Gerado pelo skill `analista-insumos` (Fase 1 — Nó 0A).

## 1. Inventário de imagens

| # | Arquivo | Descrição | Status | Uso previsto |
|---|---------|-----------|--------|--------------|
| 1 | `insumos/flex_01.png` (1080×941, RGBA, ~508 KB) | Render 3D de dois implantes dentários de titânio sobre fundo preto (esq.: conexão interna; dir.: hexágono externo) — ver `insumos/imagem_descricao.md` | **DISPONÍVEL** (fornecida pelo operador na rodada 1) | Capa do PDF, hero da landing, imagem principal das artes e kits |

**Observação:** imagem fornecida pelo operador (caminho `F:/#PRODUTOS/.../flex_01.png`),
copiada e otimizada (1080px, 256 cores) para `output/vulcano-actives-2/insumos/`. Nunca
substituir por ilustração gerada (REGRA 6).

## 2. Fatos e claims verificáveis (fonte de verdade — REGRA 6)

Extraídos do texto-base `insumos/texto_base.md`, sem reformulação de sentido:

1. **Vulcano Actives** é uma superfície da **Conexão Sistemas de Prótese**, desenvolvida sob a **fundamentação científica do Dr. Carlos Nelson Elias**; apresentada como "estado da arte em bioengenharia".
2. **Previsibilidade em casos desafiadores:** eficácia superior validada em **fumantes, diabéticos** e **baixa densidade óssea (Tipo IV)**; **100% de sucesso em casos de osso tipo IV**; margem de segurança para reabilitações em **maxila posterior**.
3. **Bioatividade ativa:** processo de **oxidação por arco micro-elétrico (MAO)** incorpora íons de **Cálcio (Ca) e Fósforo (P)** diretamente na estrutura do **óxido de titânio**; concentração de fósforo **superior a 7%**; o organismo reconhece o implante como parte do tecido mineralizado; acelera a **deposição de apatita biológica**. Diferente de superfícies passivas.
4. **Carga precoce (redução da latência óssea):**
   - **60 dias:** taxa de sucesso de **97,7%**, suportando testes de **contra-torque de 25 N.cm**.
   - **45 dias:** índice de sucesso de **91,11%**, validando protocolos ultra-rápidos.
5. **Hidrofilia extrema:** indução da **fase cristalina anatase** no óxido de titânio (alta energia de superfície); sangue molha o implante **instantaneamente** após a instalação; estabilização imediata do coágulo; retenção da **rede de fibrina** ("andaime" para migração de **células osteogênicas**).
6. **Topografia ideal:** rugosidade média **Ra ≈ 1,26 µm**; "ponto ideal" para diferenciação de **células-tronco mesenquimais em osteoblastos**; matriz calcificada densa sobre o metal; essencial para a **manutenção do bordo alveolar**.
7. **Sinergia com a macrogeometria:** quando usada em implantes das linhas **Torq** (ápice ativo para altos torques) ou **Flash** (ressalto "Web" para compactação óssea), garante que a **estabilidade primária (mecânica)** seja rapidamente substituída pela **estabilidade secundária (biológica)**; minimiza risco de falhas na **janela crítica de cicatrização**.
8. **Resumo (fonte):** a superfície é uma ferramenta de alta tecnologia que permite tratamentos **mais rápidos, seguros e previsíveis**, mesmo nos cenários clínicos mais complexos.

## 3. Escolhas do operador (fonte de verdade — rodadas 2 e 3)

| Campo | Valor escolhido | Implicações práticas para os redatores |
|---|---|---|
| `publico_alvo` | **clientes** | Registro de `brand/publicos-alvo.json.clientes`: vocabulário **acessível, sem jargão sem explicação**; postura orientadora; benefício concreto; CTA padrão "Fale com um especialista". Ênfase: PDF = problema do paciente → como resolve → o que esperar; landing = hero com benefício de resultado; arte = headline de benefício. |
| `objetivo_tom` | **informacional_tecnico** | Objetivo `informacional` + tom `tecnico`. O texto-base é técnico e dirigido ao implantodontista — para **clientes**, traduzir cada conceito (MAO, anatase, Ra 1,26 µm, contra-torque, estabilidade primária/secundária) em benefício concreto (recuperação mais rápida, mais segurança em casos difíceis), mantendo precisão factual e sem superlativo sem evidência. |
| Combinação | clientes + informacional_tecnico | Explicar os conceitos em linguagem acessível sempre amarrando ao benefício (menos espera entre cirurgia e prótese, mais segurança em cenários desafiadores). Nunca listar spec solta. |

**Kits (exceção de público):** `kit-consultor` e `kit-distribuidor` selecionados usam
público fixo `dentista_implantodontista` (nunca o `publico_alvo` do projeto) e os 5 tons
fixos de `brand/tons-kit.json` — registro técnico-clínico em 2ª pessoa, 1 ideia por
peça; CTA/assinatura variam por kit via `brand/kits-conexao.json`.

## 4. Faltantes identificados (REGRA 6 — nunca preencher por suposição)

1. **Referências completas dos estudos clínicos:** nomes/datas/autores dos estudos citados (100% osso tipo IV; 97,7% em 60 dias; 91,11% em 45 dias) — não constam no texto-base.
2. **Dados comerciais:** preço, códigos de produto, condições — ausentes do texto-base.
3. **Detalhes das linhas Torq/Flash:** descrição das plataformas, torque de inserção, formatos — apenas menção nominal no texto-base.

## 5. Handoff

`diretor-de-arte` assume a partir deste dossiê para gerar `brief_criativo.json`.
