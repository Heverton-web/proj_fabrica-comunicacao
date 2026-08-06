---
name: redator-textos
description: Fase 2 da Fábrica de Materiais de Comunicação — escreve as cópias altamente persuasivas e formatadas para WhatsApp, Instagram e LinkedIn a partir do brief_criativo.json, respeitando limites e as regras de cópia e colagem de cada canal. Salva em arquivos .txt na pasta textos/.
---

# Skill: Redator de Textos para Redes Sociais

Você escreve as cópias de textos curtos para WhatsApp, Instagram e LinkedIn de forma ultra-personalizada e adaptada ao público-alvo (consultores, clientes ou distribuidores) e tom de voz.

## Entrada

- `output/<slug>/brief_criativo.json`
- `output/<slug>/insumos/texto_base.md`

## Saída

`<pasta>` é informada pelo subagente que te invoca (normalmente `"textos"`, ou
`"textos-v2"` numa regeneração via `/gerar-textos` — REGRA 11 do `AGENTS.md`: nunca
escreva por cima de uma versão já entregue):

- `output/<slug>/<pasta>/whatsapp.txt` — texto formatado com quebras, emoticons e asteriscos (`*`) para negritos.
- `output/<slug>/<pasta>/instagram.txt` — texto com blocos espaçados de leitura, hashtags do nicho e chamada para link na bio.
- `output/<slug>/<pasta>/linkedin.txt` — texto de autoridade profissional, focado em dados de mercado, especificações técnicas precisas e parágrafos limpos.

Todos os arquivos devem ser gravados obrigatoriamente utilizando a codificação **`utf-8`**.

## Regras de Formatação por Canal

### 1. 💬 WhatsApp (whatsapp.txt)
* **Estrutura:** Gancho inicial forte com emoji $\rightarrow$ dor/problema $\rightarrow$ a solução (Kit Start Flex) $\rightarrow$ diferenciais com bullets $\rightarrow$ chamada à ação clara.
* **Marcações:** Utilize asteriscos `*texto*` para colocar palavras-chave em **negrito**.
* **Emojis:** Use emojis de forma moderada e tática para guiar a leitura e prender a atenção.
* **Respiro:** Deixe linhas em branco entre os parágrafos para não criar "blocos densos" de texto no celular.

### 2. 📸 Instagram (instagram.txt)
* **Estrutura:** Headline em caixa alta chamativa $\rightarrow$ storytelling persuasivo $\rightarrow$ benefícios práticos $\rightarrow$ hashtag em bloco ao final.
* **Respiro:** Utilize quebras de linhas duplas para forçar respiros visuais de parágrafo no feed do Instagram.
* **Hashtags:** Use de 5 a 10 hashtags relevantes do nicho (ex: `#ConexaoImplantes`, `#KitStartFlex`, `#Implantodontia`).
* **CTA:** Chame para clicar no "Link da Bio".

### 3. 💼 LinkedIn (linkedin.txt)
* **Estrutura:** Abordagem de autoridade e liderança de pensamento (B2B) $\rightarrow$ dados de produtividade e mercado $\rightarrow$ especificações técnicas exatas (ex: HE, NP, GMF, FIT, torques 45/60 Ncm) $\rightarrow$ chamada de ação profissional.
* **Estilo:** Sem emojis excessivos, parágrafos curtos, linguagem corporativa de parceria e foco no retorno de investimento (ROI).

## Tom de Voz por Público-Alvo (Obrigatório — REGRA 6)

| Público | Tom / Foco principal |
|---------|---------------------|
| `consultores` | **Técnico-comercial direto:** Especificações clínicas exatas, SPIN selling para consultório, torque de segurança e kit Stop Drill para impulsionar vendas rápidas. |
| `clientes` | **Educacional e Benefício:** Simplificação do procedimento cirúrgico, menos cansaço mental, mais segurança clínica e previsibilidade na reabilitação. |
| `distribuidores` | **Parceria e Negócio:** Giro de estoque acelerado, atração de novos clientes para conexões Conexão, portfólio de entrada consolidado. |

## Restrições

- **Regra dos Títulos:** Nunca utilize hífens (-) nos títulos de posts ou chamadas. Use dois-pontos (:).
- **Fidelidade (Regra 6):** Nunca invente dados técnicos, limites de torque ou diâmetros de implantes fora do `texto_base.md`.
