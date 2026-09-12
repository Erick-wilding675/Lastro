# Matching Model — Risco e Recuperação

**Status:** Reescrito em 11/09 para o case KRILLTECH. Substitui o matching pessoa↔projeto. **Este é o documento que o time de agentes/orquestração implementa primeiro.**

**Projeto:** Rizoma
**Versão:** 1.0 — Pivô de domínio
**Data:** 2026-09-11

---

## Princípio (preservado do original)

O modelo produz **recomendação, não decisão**. Todo score é decomposto por dimensão e rastreável até o dado que o gerou. Nenhuma ação de cobrança é disparada automaticamente: o comitê de crédito decide. Ver [../harness.md](../harness.md).

Num contexto de crédito isso deixa de ser preferência de design e vira requisito: decisão de crédito precisa ser auditável, defensável e reversível.

---

## Camada 0 — Motor de Contágio (novo, e é o diferencial)

Antes de qualquer matching, o grafo responde: **quem está em risco que ainda não apareceu no aging?**

Entrada: mudança de estado de um `Cliente` (entrou em RJ, estourou 90 dias, protestou).
Saída: arestas `EXPOSTO_A` com peso e caminho, para cada vizinho alcançado.

Implementação: **função determinística** (query Cypher multi-hop — ver
[data-model.md](data-model.md)). Não precisa de LLM: é propagação em grafo, não
interpretação.

O motor tem **dois canais distintos**, e a diferença entre eles é conceitual, não
cosmética:

- **Estrutural** — o risco de um contamina o outro por vínculo jurídico ou
  patrimonial: grupo econômico (0,90), avalista em comum (0,85), sócio em comum
  (0,70).
- **Sistêmico** — ninguém contamina ninguém; todos sofrem a mesma causa: mesma
  região e cultura (0,75), mesma revenda (0,65), mesma cultura (0,40). O peso
  cheio de região e cultura **só vale se houver evento regional confirmando o
  choque** (quebra de safra, alerta ZARC, queda de cotação nos últimos 365 dias);
  sem evento, cai para 0,30.

Essa condicional responde à objeção óbvia da banca — *"então a carteira inteira
acende?"* — com um não verificável: a microrregião só fica vermelha quando existe
causa comum documentada e com fonte.

O que precisa de LLM é **explicar o cluster em linguagem de negócio** — daí o `Contagion Narrative Agent` abaixo.

---

## Nível 1 — Adequação Devedor ↔ Estratégia

Para cada devedor, quão adequada é cada `EstrategiaRecuperacao` do catálogo.

| Dimensão | O que compara | Implementação | Peso (MVP) |
|---|---|---|---|
| **Capacidade de pagamento** | Histórico de pagamento, porte, safra corrente, cultura e região contra o saldo devedor | Função determinística | Uniforme |
| **Cobertura de garantia** | Garantia sobre exposição, com **haircut por tipo** (alienação fiduciária 1,00; aval 0,70; CPR 0,60; penhor de safra 0,50; nenhuma 0,00) — nem todo real de garantia vale um real no cenário de RJ | Função determinística | Uniforme |
| **Valor da relação comercial** | Tempo de casa, volume histórico, potencial de safras futuras — define se vale preservar o cliente | Função determinística | Uniforme |
| **Contexto qualitativo** | Relato do comercial, situação da lavoura, histórico de negociação, petição de RJ — texto livre | **Agente LLM** — `Strategy Fit Agent` | Uniforme |
| **Estágio jurídico** | `estagio_juridico` contra `estagios_elegiveis` da estratégia | Função determinística — **filtro de elegibilidade, não soma ao score** | — |

O estágio jurídico funciona como a disponibilidade funcionava no modelo original: filtro duro. Não se propõe cobrança amigável a quem já está habilitado em RJ.

---

## Nível 2 — Coerência da Carteira de Ações

Um plano de recuperação não é a soma das melhores ações individuais.

| Dimensão | O que avalia | Implementação | Peso (MVP) |
|---|---|---|---|
| **Cobertura de exposição** | Quanto do R$ total em risco está de fato endereçado por alguma ação | Função determinística | Uniforme |
| **Capacidade operacional** | Quantos casos o time consegue tocar no período — ação recomendada que ninguém executa é ação inexistente | Função determinística | Uniforme |
| **Concentração de risco** | Se o esforço está todo num cluster e o resto da carteira está descoberto | Função determinística | Uniforme |
| **Janela de safra** | Se a cobrança está casada com o momento de caixa do produtor — cobrar na entressafra é queimar relação sem recuperar | Função determinística | Uniforme |
| **Coerência de contágio** | Se as ações vizinhas dentro de um mesmo cluster se contradizem (executar um e renegociar outro do mesmo grupo) | Função determinística sobre `EXPOSTO_A` | Uniforme |

---

## Nível 3 — Otimização de Portfólio (agora **dentro** do escopo)

> No projeto original este nível foi cortado por "muito trabalho para pouco ganho". No case real ele é o núcleo: o problema declarado da Krilltech é **recuperação lenta de capital**, e isso é exatamente um problema de alocação de capacidade escassa.

**Objetivo:** maximizar capital recuperado por unidade de esforço, dentro das restrições reais (capacidade do time, custo por estratégia, prazo desejado de retorno).

**Implementação no MVP:** heurística gulosa determinística — ordena por `valor_recuperavel_estimado / (custo × prazo)`, respeitando capacidade e concentração. **Não** um solver de otimização: cabe no tempo, é explicável linha a linha e resolve o problema. Solver fica como evolução declarada.

---

## Corte agente LLM vs. função determinística

Mantém a lógica do corte original (interpretação semântica vira agente; cálculo vira função):

**Agentes LLM (watsonx Orchestrate) — 4:**

| Agente | Responsabilidade |
|---|---|
| `Strategy Fit Agent` | Lê contexto qualitativo do devedor (relato comercial, histórico de negociação) e pontua adequação de estratégia com justificativa |
| `Contagion Narrative Agent` | Traduz o cluster de risco calculado em explicação de negócio: por que estes clientes acenderam juntos, o que os une |
| `Document Extraction Agent` | Lê petição de RJ, contrato, CPR ou e-mail e extrai dados estruturados (valores, prazos, garantias) com fonte e confiança. Herdeiro direto da "extração assistida" da Tese |
| `Annotation Normalizing Agent` | Anotações livres do gestor (impedimento, acordo verbal, promessa de pagamento) viram atualização estruturada nas dimensões |

**Funções determinísticas (backend FastAPI):** motor de contágio, capacidade de pagamento, cobertura de garantia, valor da relação, filtro de estágio jurídico, todas as cinco dimensões do Nível 2, e a heurística do Nível 3.

**Orchestrator:** watsonx Orchestrate coordena a sequência e chama o backend como tool (ARD-04, preservado).

---

## Pesos

Uniformes dentro de cada nível no MVP — auditável e honesto no pitch: *"não calibramos com dados históricos reais porque ainda não os temos; cada dimensão pesa igual até existir base para ajustar"*. A `EXECUTADA` (memória de recuperação) é o mecanismo pelo qual esses pesos passariam a ser calibrados com dado real.

---

## Persistência da explicação

A recomendação é **materializada** como `RECOMENDADA {score_decomposto, valor_recuperavel_estimado, prazo_estimado, calculado_em}` (ARD-05, preservado). A explicação não é recalculada a cada abertura de tela: fica gravada, datada e auditável — que é o que sustenta o R de GIRO num contexto de crédito.

---

## Open Questions

| # | Questão | Owner | Status |
|---|---|---|---|
| 1 | Catálogo real de estratégias que a Krilltech usa hoje (o nosso é o padrão do mercado — pode não bater) | Erick / empresa | Open |
| 2 | Capacidade operacional real do time de cobrança — insumo direto do Nível 3 | Erick / empresa | Open |
| 3 | Pesos de contágio: manter uniformes/hipótese ou calibrar com conhecimento de domínio | Erick | Open |
| 4 | `Document Extraction Agent` entra no build das 12h ou fica como demonstração conceitual no pitch? | Erick | Open — decidir antes das 9h |
