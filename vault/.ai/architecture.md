# Arquitetura

<!--
  Como o sistema é construído. Este arquivo + docs/ARD.md são a fonte de
  verdade estrutural no repositório. Preenchido no Step 4 do kickoff
  (workflows/project-kickoff.md), depois do Data Model e Use Cases aprovados.
-->

**Status:** Rascunho — Step 4 respondido por Erick em 11/09 (itens 1, 2, 4, 5 aprovados diretamente; item 3, hosting, em aberto — depende do que o ecossistema IBM disponibilizar no dia do hackathon). Aguardando aprovação final condicionada a essa definição.

> **Já sabemos:** IBM watsonx Orchestrate (orquestração de agentes) + IBM Bob (engenharia) fazem parte da stack — ver [ai.md](ai.md). Neo4j AuraDB free tier é o armazenamento (ver [docs/ARD.md](docs/ARD.md), ARD-01).

## Visão Geral do Sistema

```
┌─────────────────────┐        ┌──────────────────────────┐
│  Frontend (React)     │◀─────▶│  Backend (FastAPI)         │
│  grafo de força,       │  REST │  API REST + camada de      │
│  painel lateral,       │       │  acesso ao Neo4j (Cypher)  │
│  memória organizacional│       └──────────────┬─────────────┘
└─────────────────────┘                        │
                                                 ▼
                                    ┌──────────────────────────┐
                                    │  Neo4j AuraDB (free tier)  │
                                    │  Talent Graph + Project    │
                                    │  Genome (ver data-model.md)│
                                    └──────────────────────────┘
                                                 ▲
                                                 │ chamada como "tool"
                                    ┌──────────────────────────┐
                                    │  IBM watsonx Orchestrate    │
                                    │  Orchestrator Agent +      │
                                    │  agentes LLM (Competency,  │
                                    │  Role, Interest, Annotation│
                                    │  Normalizing)              │
                                    └──────────────────────────┘
```

**O fato arquitetural mais importante:** watsonx Orchestrate nunca fala diretamente com o driver do Neo4j. Toda leitura/escrita no grafo passa pela API REST do backend, que expõe endpoints como "tools" que o Orchestrator aciona — a mesma separação entre orquestração e cálculo que a Tese exige (Talent Model, item 17; Project Model, item 16) fica fisicamente garantida pela própria arquitetura, não só como uma convenção de código.

---

## Serviços & Hosting

| Serviço | Plataforma | Responsabilidade |
|---|---|---|
| watsonx Orchestrate | IBM | Orquestração do Orchestrator Agent e dos agentes LLM (Competency, Role, Interest, Annotation Normalizing) |
| IBM Bob | IBM | Ambiente de engenharia — build, docs, testes |
| Neo4j AuraDB | Neo4j (free tier) | Armazenamento do Talent Graph + Project Genome |
| Backend | Python + FastAPI | API REST; camada de acesso ao Neo4j; funções determinísticas dos agentes de Nível 1/2 que não exigem LLM (Availability, Contextual Experience, Coverage, Complementarity, Experience Distribution, Aggregated Availability, Collaboration) |
| Frontend | React | Grafo de força (tela inicial), painel lateral, Memória Organizacional |
| Hospedagem backend/frontend | **Em aberto** | Ver Questões de Arquitetura em Aberto, item 1 |

---

## Estrutura de Código

```
talent-graph/
├── AGENTS.md / CLAUDE.md        # redirecionam para vault/.ai/ai.md
├── vault/                        # este vault de documentação (Obsidian)
├── backend/
│   ├── api/                      # rotas REST — projetos, squads, matching, memória organizacional
│   ├── graph/                    # camada de acesso ao Neo4j (queries Cypher)
│   ├── matching/                 # funções determinísticas (Nível 1: Availability, Contextual
│   │                              #   Experience; Nível 2: Coverage, Complementarity,
│   │                              #   Experience Distribution, Aggregated Availability, Collaboration)
│   └── seed/                     # scripts de geração do dataset seed artificial enriquecido
└── frontend/
    └── src/
        ├── graph/                # componente do grafo de força — tela inicial
        ├── panels/                # painel lateral (abas Genoma / Squad / Anotações)
        └── memoria/               # tela de Memória Organizacional
```

**Princípio organizador:** separação por responsabilidade arquitetural (agentes LLM ficam no watsonx Orchestrate; cálculo determinístico e acesso a dados ficam no backend; apresentação fica no frontend) — não um monorepo "feature-first", porque as fronteiras aqui são as mesmas que a Tese já definiu entre orquestração, cálculo e representação de conhecimento.

---

## Data Model

<!-- Espelha docs/data-model.md, mas focado no schema implementado. -->

| Entidade | Descrição |
|---|---|
| `Pessoa` | Nó do Talent Model — ver [docs/data-model.md](docs/data-model.md) |
| `Projeto` | Nó do Project Model/Genome |
| `Competencia`, `Papel`, `Dominio` | Taxonomias compartilhadas |
| `TEM_COMPETENCIA`, `REQUER_COMPETENCIA`, `PARTICIPOU_DE`, `PREFERE_PAPEL`, `REQUER_PAPEL`, `TEM_INTERESSE`, `COLABOROU_COM`, `AVALIADO_EM` | Relações — ver [docs/data-model.md](docs/data-model.md) |
| `RECOMENDADO_PARA` | Relação nova do Step 4 — materializa a explicação decomposta por dimensão de cada recomendação de matching. Ver detalhe no [docs/matching-model.md](docs/matching-model.md) e adendo em [docs/data-model.md](docs/data-model.md). |

---

## Fluxos-chave

### Cadastro de Projeto → Matching → Explicação (UC-02)

1. Gestor preenche o modal de elicitação direta (frontend) → `POST /projetos` (backend).
2. Backend cria o nó `Projeto` no Neo4j com `fonte: "elicitação_direta"`.
3. Backend aciona o watsonx Orchestrate (Orchestrator Agent) para iniciar o matching.
4. Orchestrator chama, via tool/API, os agentes LLM (Competency, Role, Interest) e as funções determinísticas do backend (Availability, Contextual Experience) para o Nível 1; depois as funções determinísticas de Nível 2 (Coverage, Complementarity, Experience Distribution, Aggregated Availability, Collaboration).
5. Backend grava o resultado: cria as relações `PARTICIPOU_DE` (squad formado) **e** a relação `RECOMENDADO_PARA {score_decomposto}` (explicação materializada) — sem esperar aprovação humana síncrona (ver [harness.md](harness.md)).
6. Frontend consome o resultado via API e anima a "matching em movimento" a partir dos dados já persistidos (a animação é apresentação, não recálculo).
7. Gestor visualiza o squad; pode adicionar anotações (UC-03) → aciona o Annotation Normalizing Agent (LLM) → backend atualiza as dimensões correspondentes.

---

## Segurança

- Sem autenticação multi-papel no MVP — um único usuário autenticado (Gestor de Projetos), consistente com NFR-04 e com use-cases.md (Alta Gestão/Talento são só narrativa de pitch).
- `AVALIADO_EM` nunca é servida pela API fora do fluxo de decisão de formação de squad — restrição de apresentação, não uma ACL de banco (ver [docs/data-model.md](docs/data-model.md), Decisão de modelagem #2).
- Segredos (credenciais do AuraDB, chaves do watsonx Orchestrate) via variáveis de ambiente — sem gestão de secrets dedicada no MVP (verba/tempo não justificam para 12h).

---

## Questões de Arquitetura em Aberto

1. **Hospedagem de backend e frontend** — Erick não consegue confirmar agora se o hackathon disponibiliza mais infraestrutura do ecossistema IBM (ex.: Code Engine) para o deploy. Default caso nada seja oferecido: Vercel/Netlify (frontend) + Render/Railway/Fly.io (backend) — rápidos de subir em poucos minutos. **Decidir no dia do hackathon, assim que o ecossistema disponível for conhecido.**
2. Biblioteca exata de grafo de força (react-force-graph, vis-network, D3 puro) — ver [docs/wireframes.md](docs/wireframes.md), Questão 2.
3. Biblioteca de charts para a Memória Organizacional (mesma lib do grafo ou uma separada, ex. Chart.js) — ver [docs/wireframes.md](docs/wireframes.md), Questão 3.
