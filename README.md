# Talent Graph

Repositório do projeto **Talent Graph**, construído para o Hackathon 2026 do Student Club PMI-DF (11–12/09/2026, Brasília).

Toda a documentação de idealização, especificação e decisões do projeto vive em [`vault/`](vault/) — um vault do Obsidian, versionado neste repositório.

- **Para ler/editar a documentação:** abra a pasta `vault/` no Obsidian.
- **Para qualquer assistente de IA** (IBM Bob, Claude, etc.) trabalhando neste repositório: comece por [`AGENTS.md`](AGENTS.md), que aponta para [`vault/.ai/ai.md`](vault/.ai/ai.md) — o ponto de entrada único.

## Documentos-fonte

- `Tese-Talent_Graph_IBM.pdf` — a idealização completa: o problema, o Talent Model, o Project Model e o Matching Model.
- `Resumo-Tecnico-Talent_Graph_IBM.pdf` — a arquitetura multiagente (IBM Bob + watsonx Orchestrate).
- `Edital_01_2026_HackathonPMIDF_VF.pdf` — o edital oficial do hackathon, resumido e transformado em checklist em [`vault/.ai/docs/edital-e-avaliacao.md`](vault/.ai/docs/edital-e-avaliacao.md).

## Estado atual

**Kickoff completo (11/09/2026).** Todos os 5 steps de [`vault/.ai/workflows/project-kickoff.md`](vault/.ai/workflows/project-kickoff.md) foram percorridos e aprovados: System Description, SRS, Use Cases & User Flows, Data Model, Wireframes, Architecture + Matching Model, Design Doc + UI Guidelines. Status de cada documento em [`vault/.ai/docs/documents-hub.md`](vault/.ai/docs/documents-hub.md).

O motor do produto (Talent Model, Project Model, Matching Model, schema Neo4j, arquitetura watsonx Orchestrate + Neo4j + backend/frontend) e o **sistema de design estão prontos, mas ainda genéricos por decisão deliberada**: o Diagnóstico do Problema & Impacto e qualquer narrativa/UI específica de domínio ficam em stand-by até o case oficial do hackathon ser revelado (11/09, 19h — ver [`vault/.ai/docs/edital-e-avaliacao.md`](vault/.ai/docs/edital-e-avaliacao.md)). O sistema de design em [`vault/.ai/docs/design-doc.md`](vault/.ai/docs/design-doc.md) e [`vault/.ai/ui_guidelines.md`](vault/.ai/ui_guidelines.md) — Carbon (IBM) híbrido, tema escuro padrão, paleta da Síntese Labs, wordmark em Sora, tokens de cor/tipografia/componentes — é intencionalmente domain-agnostic: assim que o case chegar, é só escopar (cores/estados já resolvidos, falta encaixar a narrativa e os dados do caso real).

**Pendências conhecidas:**
- Hospedagem de backend/frontend — decide no dia do hackathon, dependendo do que o ecossistema IBM disponibilizar.
- Task Tracker (`vault/tasks/` + [`vault/.ai/workflows/task-queue.md`](vault/.ai/workflows/task-queue.md)) — deliberadamente não seedado ainda; só é montado quando o case real for revelado.
