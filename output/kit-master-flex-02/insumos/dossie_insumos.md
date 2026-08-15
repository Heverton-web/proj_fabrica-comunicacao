# Dossiê de Insumos — KIT MASTERFLEX (regeneração 2ª Edição)

Projeto: `kit-master-flex-02` · Edição: "2ª Edição" · Gerado pelo skill `analista-insumos` (Fase 1 — Nó 0A).
Texto-base atual: `insumos/texto-mae-02.txt` (novo, trocado na regeneração `/gerar-pdf`).

## 1. Inventário de imagens

| # | Arquivo | Descrição | Status | Uso previsto |
|---|---------|-----------|--------|--------------|
| 1 | `insumos/kit-master-flex.png` | Foto oficial do Kit MasterFlex (mantida da geração anterior) | **DISPONÍVEL** | Capa do PDF, hero da landing, artes e kits |

O texto-base faz referência ao logotipo Conexão (`logo%20conexao.png`) com sugestões
visuais de animação (animate-float/animate-shimmer) — isso é orientação de material
HTML, não claim; o logotipo oficial da marca é aplicado pelos templates a partir de
`assets/logos-marca/` (design system fixo), nunca de um arquivo de insumo.

## 2. Fatos e claims verificáveis (fonte de verdade — REGRA 6)

Extraídos de `insumos/texto-mae-02.txt`, sem reformulação de sentido:

1. **Kit MasterFlex** é um "**Single Kit**" que unifica a prática clínica com rigor científico; posiciona-se como **padrão-ouro** no mercado; da **Conexão Implantes**; pensado para o **Dentista (Implantodontista)** com foco em segurança biológica e eficiência operacional.
2. **Sistema exclusivo de Stop Drills:** o MasterFlex é o **único sistema no mercado** a integrar a **Fresa Start (Lança)** com um dispositivo de **Stop Drill** dedicado.
   - **Controle de profundidade:** garante que o planejamento digital ou tomográfico seja executado com fidelidade desde o primeiro contato ósseo, mitigando riscos de acidentes em estruturas nobres.
   - **Sistema completo:** todas as fresas helicoidais (**do número 1 ao 9**) possuem seus respectivos limitadores de profundidade, assegurando cavidade cirúrgica exata para o comprimento do implante selecionado.
3. **Flex - Bone Drill Protocol:** protocolo de fresagem por **densidade óssea (Soft III-IV e Hard I-II)** estampado diretamente na **tampa da caixa organizadora**; elimina hesitação no transoperatório.
   - **Otimização do preparo:** sequência exata de fresagem para estabilidade primária em ossos medulares de maxila ou corticais densas de mandíbula.
   - **Identificação dual:** fresas com marcações duplas — número em **negrito** (sequência) e diâmetro em *itálico* — facilitando comunicação com a equipe auxiliar e reduzindo o tempo de cadeira.
4. **Versatilidade universal (uma plataforma):** compatível com:
   - **Conexões Cônicas (Morse):** NP (24°), GMF (16°) e FIT (11,5°).
   - **Hexágono Externo:** HE-RD (Regular), HE-SD (Small) e a linha HI.
   - **Amplitude de diâmetros:** instrumentação completa do **Slim (2.9mm)** — espaços protéticos estreitos — ao diâmetro largo de **5.0mm** — alvéolos de extração imediata.
5. **Eficiência na captura e finalização protética:**
   - **Drivers de Captura Ativa:** capturam o implante diretamente da embalagem e o transportam com segurança até o alvéolo; identificados por **anéis coloridos (Azul = NP, Verde = GMF/FIT/HE-RD, Vermelho = SL/HE-SD)**.
   - **Sistema Extension Fitness:** adaptadores transformam chaves de transporte em **chaves sólidas de finalização**, permitindo o uso da **catraca de torque** para assentamento preciso.
   - **Acessórios de precisão:** **4 pinos de paralelismo** (casos múltiplos) e o ***Extension Drill*** (extensor de fresa) para acesso em áreas interdentais com dentes vizinhos altos.
6. **Conclusão (fonte):** o MasterFlex materializa a engenharia da Conexão Implantes em prol da **redução do erro humano** e do **aumento do sucesso clínico**, respeitando limites biológicos e estéticos do paciente.

## 3. Escolhas do operador (fonte de verdade — rodadas 2 e 3 + regeneração)

| Campo | Valor atual | Implicações práticas |
|---|---|---|
| `publico_alvo` | **clientes** (mantido na regeneração) | Registro acessível/orientador (`brand/publicos-alvo.json.clientes`): vocabulário sem jargão sem explicação, benefício concreto, CTA "Fale com um especialista". |
| `objetivo_tom` | **informacional_tecnico** (trocado na regeneração) | Objetivo `informacional` + tom `tecnico`: explicar os diferenciais (Stop Drill, protocolo de fresagem, conexões, drivers) em linguagem acessível, sempre amarrando ao benefício (previsibilidade, segurança, menos tempo de cadeira), sem superlativo sem evidência. |
| `edicao` | **2ª Edição** (nova na regeneração) | Capa e cabeçalhos usam "2ª Edição". |

**Kits (exceção de público):** `kit-consultor` e `kit-distribuidor` usam público fixo
`dentista_implantodontista` (registro técnico-clínico em 2ª pessoa) e os 5 tons fixos de
`brand/tons-kit.json`; CTA/assinatura por kit via `brand/kits-conexao.json`.

## 4. Faltantes identificados (REGRA 6)

1. **Torque da catraca em N.cm** — o texto cita a catraca de torque mas não informa o valor.
2. **Dimensão do Extension Drill** (comprimento) — apenas menção de uso.
3. **Dados comerciais** — preço, códigos de produto, condições — ausentes.
4. **Referências de estudos/taxas de sucesso** — este texto não cita números de sucesso clínico.

## 5. Handoff

`diretor-de-arte` assume para regravar `brief_criativo.json` com o novo tom e conteúdo.
