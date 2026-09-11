# ARD — Registros de Decisão de Arquitetura

**Status:** ARD-01 registrado em 10/09. ARD-02 a ARD-05 registrados em 11/09, Step 4.

**Projeto:** Talent Graph
**Versão:** 0.4 — Rascunho
**Data:** 2026-09-11

---

## Resumo de Decisões

| ARD | Tópico | Decisão |
|---|---|---|
| ARD-01 | Armazenamento do Talent Graph e do Project Genome | Neo4j (AuraDB, tier gratuito) — banco de grafos nativo |
| ARD-02 | Backend | Python + FastAPI |
| ARD-03 | Frontend | React |
| ARD-04 | Integração watsonx Orchestrate ↔ Neo4j | API REST própria (FastAPI) exposta como "tool" — sem conexão direta driver-a-driver |
| ARD-05 | Persistência da explicação decomposta do Matching | Materializada como relação `RECOMENDADO_PARA {score_decomposto}` no grafo, não recalculada em tempo real |

---

## ARD-01 — Armazenamento do Talent Graph e do Project Genome

**Decisão:** Representar o Talent Graph e o Project Genome em **Neo4j (AuraDB, tier gratuito)** — banco de grafos nativo, consultado via Cypher.

**Racional:** Toda a equipe já tem domínio prático de Cypher e Neo4j — a objeção original (ferramenta/linguagem nova sob pressão de 10h) não se aplica. Um banco de grafos nativo também representa "fisicamente" o Talent Graph de forma mais direta do que tabelas relacionais, e favorece exatamente os traversals que o Matching Model Nível 2 precisa (complementaridade, colaboração entre pares via caminhos multi-hop) — Cypher expressa isso de forma mais natural do que joins recursivos. Reforça ainda a narrativa técnica do pitch (Viabilidade Técnica & Execução, 25% da nota): um banco de grafos real por trás do nome "Talent Graph" é mais convincente para a banca do que uma simulação relacional.

**Verificado em 10/09:** AuraDB Free tier suporta até 200k nós e 400k relacionamentos, sem cartão de crédito — folga enorme para um dataset seed de demonstração (dezenas a poucas centenas de nós). Instâncias sem atividade por 30 dias são apagadas — não é risco dentro da janela de 2 dias do hackathon. Fonte: FAQ oficial da Neo4j ([neo4j.com/cloud/platform/aura-graph-database/faq](https://neo4j.com/cloud/platform/aura-graph-database/faq/)).

**Alternativa considerada:** PostgreSQL relacional — era a recomendação original, pelo risco de a equipe não conhecer Cypher. Descartada porque a premissa não se confirmou: toda a equipe já trabalha com Neo4j.

**Consequências:**
- Criar a instância AuraDB Free **antes** do hackathon começar (hoje, 10/09), para não gastar tempo de build com provisionamento e credenciais.
- Decidir cedo, no Step 4, como o watsonx Orchestrate chama o Neo4j — driver oficial, API HTTP, ou uma tool/function intermediária — isso vira uma sub-decisão de arquitetura própria.
- [docs/data-model.md](data-model.md) deve ser desenhado em termos de **nós, relacionamentos e propriedades** (não tabelas) quando chegarmos ao Step 3b.

**Status:** Decidido em 10/09.

---

## ARD-02 — Backend

**Decisão:** Python + FastAPI.

**Racional:** os 2 analistas de sistemas responsáveis por agentes/orquestração já trabalham em Python no lado do watsonx Orchestrate; usar Python no backend reduz troca de contexto entre quem cuida dos agentes e quem cuida da API. O driver oficial do Neo4j em Python é maduro. FastAPI dá tipagem e uma API REST rápida de expor como "tool" para o Orchestrator (ver ARD-04).

**Status:** Decidido em 11/09.

## ARD-03 — Frontend

**Decisão:** React.

**Racional:** ecossistema mais direto para `react-force-graph` — a família de bibliotecas de grafo de força mais madura para prototipagem rápida (ver [docs/wireframes.md](wireframes.md), Questão 2, biblioteca exata ainda em aberto). Time fullstack aprovou diretamente.

**Status:** Decidido em 11/09.

## ARD-04 — Integração watsonx Orchestrate ↔ Neo4j

**Decisão:** o watsonx Orchestrate nunca se conecta diretamente ao driver do Neo4j. Toda leitura/escrita passa por uma API REST própria (o backend FastAPI de ARD-02), exposta ao Orchestrator como "tool".

**Racional:** mantém fisicamente a separação entre orquestração e cálculo que a Tese exige (Talent Model item 17, Project Model item 16) — não depende de disciplina de código para não ser violada, é a própria topologia do sistema. Também evita duplicar lógica de acesso ao grafo entre o ambiente do Orchestrate e o backend.

**Consequências:** o backend precisa nascer cedo no build — os agentes LLM do watsonx Orchestrate dependem dele existir para terem o que chamar.

**Status:** Decidido em 11/09.

## ARD-05 — Persistência da explicação decomposta do Matching

**Decisão:** o resultado do matching (score decomposto por dimensão) é **materializado** no grafo como uma relação `RECOMENDADO_PARA {score_decomposto}` entre `Pessoa` e `Projeto`, em vez de recalculado em tempo real a cada consulta via Cypher.

**Racional:** reforça a Rastreabilidade (Hard Rule 2 do [ai.md](../ai.md)) e é o que viabiliza a Memória Organizacional (UC-05) — "olhar pra trás" para squads já formados sem precisar re-rodar o pipeline de matching inteiro. Também é consistente com ARD-01: aproveitar que o próprio banco é um grafo para guardar o histórico de decisões como parte do grafo, não como um log externo desacoplado.

**Consequências:** [docs/data-model.md](data-model.md) e [docs/matching-model.md](matching-model.md) precisam registrar essa relação nova. Resolve a Open Question 3 de data-model.md e alimenta parcialmente a Open Question 2 de [../harness.md](../harness.md) (onde ficam os registros de rastreabilidade).

**Status:** Decidido em 11/09.

---

## Decisões em Aberto

1. Hospedagem de backend e frontend — depende do que o ecossistema IBM disponibilizar no dia do hackathon (ver [../architecture.md](../architecture.md), Questões de Arquitetura em Aberto, item 1).
