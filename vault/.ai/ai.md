# Talent Graph — Índice de Contexto para IA

<!--
  PONTO DE ENTRADA ÚNICO para qualquer assistente de IA (IBM Bob, Claude, etc.)
  trabalhando neste repositório. AGENTS.md e CLAUDE.md, na raiz do repo, só
  redirecionam para cá. Leia este arquivo primeiro, depois navegue para o
  arquivo específico do tópico que precisar.
-->

> **Kickoff completo (11/09).** Todos os 5 steps de [workflows/project-kickoff.md](workflows/project-kickoff.md) aprovados: System Description, SRS, Use Cases, Data Model, Wireframes, Architecture + Matching Model, Design Doc + UI Guidelines. Únicas pendências: hospedagem (decide no dia do hackathon, conforme o que o ecossistema IBM disponibilizar) e o Task Tracker (`workflows/task-queue.md` + `tasks/`), que só é seedado quando o case oficial for revelado (11/09, 19h) — ver Hard Rule 9.

---

## O projeto, em uma olhada

**Sistema:** Talent Graph — um processo inteligente e contínuo de gestão de pessoas e projetos: aprendizado organizacional, melhoria processual e cultura, não só uma calculadora de squad. **A narrativa nunca deve reduzir isso a "recomendação de squad explicável"** — a recomendação é uma das saídas desse processo contínuo, não o produto em si (adendo de Erick, 10/09 — importante para o pitch).

**Contexto:** projeto para o Hackathon 2026 do Student Club PMI-DF (11–12/09/2026, presencial em Brasília, 12h de desenvolvimento). O case oficial só é revelado em 11/09 às 19h — ver [docs/edital-e-avaliacao.md](docs/edital-e-avaliacao.md) para as regras e os critérios de avaliação completos.

**Stack confirmada:** IBM watsonx Orchestrate (orquestra o Orchestrator Agent + 4 agentes LLM: Competency, Role, Interest, Annotation Normalizing) + IBM Bob (engenharia) + Neo4j AuraDB free tier (armazenamento — ver [docs/ARD.md](docs/ARD.md), ARD-01) + Python/FastAPI (backend — ARD-02, expõe o grafo como "tool" pro Orchestrate, ARD-04) + React (frontend — ARD-03). **Hospedagem ainda em aberto** — depende do que o ecossistema IBM disponibilizar no dia do hackathon (ver [architecture.md](architecture.md)).

**Fonte de verdade do projeto:** este vault, em modo **Local Markdown** (sem Notion). Os documentos originais de idealização — Tese e Resumo Técnico — ficam na raiz do repositório como material-fonte; este vault é onde a especificação evolui e vive.

---

## Mapa de Navegação — o que consultar para quê

| Tópico | Arquivo local |
|---|---|
| **Kickoff do projeto** (geração guiada de specs) | [workflows/project-kickoff.md](workflows/project-kickoff.md) |
| **Regras e critérios do hackathon** | [docs/edital-e-avaliacao.md](docs/edital-e-avaliacao.md) |
| **Harness de agentes — GIRO** (governança, interpretabilidade, rastreabilidade, observabilidade) | [harness.md](harness.md) |
| **Descrição do sistema** (visão geral, problema, atores) | [docs/system-description.md](docs/system-description.md) |
| **Arquitetura**, estrutura, data model, hosting | [architecture.md](architecture.md) |
| **Decisões de arquitetura** (ARDs) | [docs/ARD.md](docs/ARD.md) |
| **Requisitos** (SRS), user stories, NFRs, escopo | [docs/SRS.md](docs/SRS.md) |
| **Use cases & user flows** | [docs/use-cases.md](docs/use-cases.md) |
| **Data model** (Talent Model, Project Genome, entidades) | [docs/data-model.md](docs/data-model.md) |
| **Matching Model** (níveis 1–3, agentes especializados, pesos) | [docs/matching-model.md](docs/matching-model.md) |
| **Wireframes** | [docs/wireframes.md](docs/wireframes.md) |
| **UI / design system** | [ui_guidelines.md](ui_guidelines.md) + [docs/design-doc.md](docs/design-doc.md) |
| **Convenções de código** | [coding_conventions.md](coding_conventions.md) |
| **Papel e regras da IA** | [config/system.md](config/system.md) |
| **Índice de documentos** (Documents Hub) | [docs/documents-hub.md](docs/documents-hub.md) |
| **Fila de tarefas** | [workflows/task-queue.md](workflows/task-queue.md) |
| **Tarefas — schema e ciclo de status** | [workflows/local-workflow.md](workflows/local-workflow.md) |
| **Agentes em paralelo** (git worktree) | [workflows/parallel-agents.md](workflows/parallel-agents.md) |

---

## Decisões-chave (resumo ultra-curto)

- O Matching Model **recomenda, não decide**: todo score é explicável e decomposto por dimensão, nunca uma caixa-preta.
- A "decisão humana final" **não é um gate síncrono dentro do pipeline**. O sistema não trava esperando um humano aprovar um squad para continuar funcionando — é uma capacidade contínua de apoio à gestão (armazenamento de informação, evolução do conhecimento sobre pessoas/projetos/organização). A decisão humana é sobre formar o time no mundo real, não sobre destravar uma etapa do software. Ver [harness.md](harness.md).
- Talent Model e Project Model usam a **mesma taxonomia** de competências e papéis, para permitir comparação direta.
- MVP prioriza **regras explícitas e pesos auditáveis** (Nível 1 e 2 do Matching Model) antes de similaridade semântica, análise de grafo e aprendizado histórico.
- Toda informação (competência, requisito, score) carrega **fonte e nível de confiança** — sugestão de IA nunca vira fato consolidado sem essa rastreabilidade.
- Documentação em **Local Markdown**, neste vault, versionada no repositório GitHub privado `talent-graph`.
- Entry point para agentes: `AGENTS.md` (raiz do repo) → `vault/.ai/ai.md` (este arquivo).

---

## Hard Rules

1. **O Matching Model recomenda, nunca decide sozinho.** Nenhuma implementação forma um squad e age automaticamente sem expor a explicação decomposta por dimensão a quem decide.
2. **GIRO não é opcional.** Governança, Interpretabilidade, Rastreabilidade e Observabilidade — ver [harness.md](harness.md) — se aplicam a todo agente que constrói ou opera este projeto.
3. **Talent Model e Project Model nunca duplicam dado.** Participação e colaboração vivem só no histórico de colaboração da pessoa (Talent Model); o Project Model não registra quem já trabalhou no projeto.
4. `architecture.md` e `docs/ARD.md` são a fonte de verdade para decisões estruturais; atualize-os quando uma decisão mudar.
5. **Kickoff de novo projeto é interativo.** Ao rodar [workflows/project-kickoff.md](workflows/project-kickoff.md), um passo por vez, aguardando resposta antes de rascunhar — nunca inventar ou escolher stack/framework/arquitetura sozinho.
6. **Agentes em paralelo trabalham em worktrees git separados.** Nunca dois agentes escrevendo no mesmo diretório — ver [workflows/parallel-agents.md](workflows/parallel-agents.md).
7. **Meça antes de afirmar; corrija-se em voz alta quando a medição contradisser você.** Nunca declare uma causa, um tamanho ou uma melhoria que não verificou.
8. **Prefira falha ruidosa a degradação silenciosa.** Um estado inesperado deve falhar com uma mensagem que nomeia o que falta, nunca cair em um default silencioso.
9. **O case oficial só é revelado em 11/09 às 19h.** O Talent Graph é a solução que a equipe leva pronta; quando o case for revelado, adaptar a narrativa/escopo sem perder os pilares (Talent Model, Project Model, Matching Model, GIRO).
10. **Nunca descreva o Talent Graph como "só" uma recomendação de squad explicável.** É um processo de gestão, aprendizado, melhoria processual e cultura organizacional contínuo — a recomendação de squad é uma saída, não a identidade do produto.
