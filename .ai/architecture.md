# Arquitetura

**Status:** revisado pós-pivô e pós-hackathon — descreve o Lastro como ele
foi construído, não mais um rascunho de decisão em aberto. Ver
[`docs/ARD.md`](docs/ARD.md) para os Architecture Decision Records
individuais por trás de cada escolha abaixo.

## Visão Geral do Sistema

```
┌───────────────────────┐        ┌──────────────────────────────┐
│  Frontend (React)      │◀─────▶│  Backend (FastAPI)             │
│  grafo de força,       │  REST │  API REST + camada de acesso    │
│  drawer do cliente,    │       │  ao Neo4j (único ponto que fala │
│  fila de recuperação   │       │  com o driver — ARD-04)         │
└───────────────────────┘        └──────────────┬─────────────────┘
                                                  │
                                                  ▼
                                     ┌──────────────────────────────┐
                                     │  Neo4j AuraDB (free tier)      │
                                     │  Carteira como rede: clientes,  │
                                     │  recebíveis, sócios, avalistas, │
                                     │  região, cultura, safra, eventos│
                                     └──────────────────────────────┘
                                                  ▲
                                                  │ chamada como "tool" (OpenAPI)
                                     ┌──────────────────────────────┐
                                     │  IBM watsonx Orchestrate        │
                                     │  4 agentes: Coletor & Parser,    │
                                     │  Risco Agro & Climático,         │
                                     │  Decisão & Scoring, Sintetizador │
                                     └──────────────────────────────┘
```

**O fato arquitetural mais importante:** o watsonx Orchestrate nunca fala
diretamente com o driver do Neo4j. Toda leitura/escrita no grafo passa pela
API REST do backend, que expõe endpoints como *tools* que os agentes
acionam — a separação entre orquestração (raciocínio, texto livre) e cálculo
(determinístico, auditável) é garantida fisicamente pela própria
arquitetura, não só por convenção de código. Ver
[`docs/agentes.md`](docs/agentes.md), princípio "agente onde há ambiguidade,
função onde há conta".

---

## Serviços & Hosting

| Serviço | Plataforma | Responsabilidade |
|---|---|---|
| watsonx Orchestrate | IBM | Orquestração dos 4 agentes de IA |
| Neo4j AuraDB | Neo4j (free tier) | Armazenamento do grafo da carteira |
| Backend | Python + FastAPI, container Docker | Render (`lastro-api`, `render.yaml`) |
| Frontend | React + Vite | Vercel, apontando para `src/frontend` (`vercel.json`) |

---

## Estrutura de Código

```
Hackathon/                          (raiz do repositório)
├── AGENTS.md / CLAUDE.md           redirecionam para .ai/ai.md
├── Makefile
├── .env.example
├── .ai/                            este vault de documentação
├── tasks/                          task tracker (Local Markdown)
├── pitch/                          Project Canvas, pitch deck, roteiro
└── src/                            monólito modular — ver src/README.md
    ├── backend/
    │   └── app/
    │       ├── main.py             wiring dos módulos
    │       ├── core/                config e driver Neo4j (único ponto que fala com o banco)
    │       └── modules/
    │           ├── carteira/        clientes, recebíveis, exposição, KPIs, grafo
    │           ├── contagio/        motor de propagação de risco pela rede
    │           ├── scoring/         score 0-1000, rating A-D, matriz de red flags
    │           ├── recuperacao/     estratégias e fila priorizada por capacidade
    │           ├── eventos/         radar e ingestão de fontes públicas
    │           ├── motor/           encadeia os módulos na ordem obrigatória
    │           └── agentes/         tools expostas ao watsonx Orchestrate
    ├── db/
    │   ├── cypher/                  schema, seed e as 5 queries do motor
    │   ├── seed.py                  aplica o schema via driver (alternativa ao console)
    │   └── ingestao/                pipeline extract → transform → load de fontes públicas reais
    └── frontend/                    React + react-force-graph-2d
```

**Princípio organizador:** o monólito é modular por domínio de negócio
(`carteira`, `contagio`, `scoring`, `recuperacao`, `eventos`), não por
camada técnica (não há pasta `services/`, `models/`, `controllers/`
genérica) — cada módulo tem sua própria fronteira de responsabilidade,
`router.py` e `queries.py`. `motor` é a exceção deliberada: não é domínio,
é o módulo que encadeia os outros na ordem que o negócio exige.

---

## Data Model

Ver [`docs/data-model.md`](docs/data-model.md) para o schema completo (nós,
relações, pesos dos dois canais de propagação, haircut de garantia). Resumo:

| Entidade | Descrição |
|---|---|
| `Cliente` | Produtor rural, PF ou PJ, cliente da Krilltech |
| `Recebivel` | Título a receber, com status e garantia |
| `Socio`, `Avalista`, `GrupoEconomico` | Vínculos do canal estrutural de exposição |
| `Regiao`, `Cultura`, `Safra` | Vínculos do canal sistêmico de exposição |
| `Evento` | Ocorrência com fonte e data — jurídica, fiscal, ambiental, climática, societária |
| `EstrategiaRecuperacao` | Catálogo de ações de recuperação, com custo/prazo/taxa de sucesso histórica |

---

## Fluxo-chave: cliente pede RJ → rede reage → comitê decide

1. Um evento `pedido_rj` é registrado sobre um cliente (`POST /eventos/registrar`,
   via Agente Coletor & Parser ou direto pela API).
2. `POST /motor/ciclo?origem={cliente}` (ou o frontend, ao abrir a tela)
   dispara, na ordem: `contagio/propagar` → `scoring/recalcular` →
   `recuperacao/recomendar-carteira`.
3. O motor de contágio acende os clientes vizinhos pelos dois canais
   (estrutural e sistêmico), gravando o **caminho** que gerou cada exposição
   — nunca só o número.
4. O score de cada vizinho é recalculado incorporando a exposição herdada
   como um dos cinco componentes; rating e matriz de red flags atualizam
   junto.
5. O frontend consome `/carteira/grafo` e `/scoring/red-flags` e anima a
   propagação a partir dos dados já persistidos — a animação é
   apresentação, não recálculo.
6. Ao abrir o drawer de um cliente afetado, o Agente Sintetizador
   (`GET /agentes/dossie/{cliente}`) redige o parecer de risco; a decisão de
   limite e condição de pagamento fica com o comitê de crédito
   (`POST /recuperacao/executar/{cliente}` registra quem decidiu e quando).

---

## Segurança

- Sem autenticação multi-papel no MVP — decisão consciente para o escopo do
  hackathon, não lacuna: um único perfil de usuário (área de
  crédito/comitê).
- Segredos (credenciais do AuraDB) via variáveis de ambiente — sem gestão de
  secrets dedicada no MVP.
- Nenhum dado real de produtor entra no repositório (Hard Rule #8) — o seed
  é sintético e mascarado; o que a ingestão baixa de verdade fica fora do
  git (`src/db/ingestao/.gitignore`).

---

## Evolução conhecida (pós-hackathon)

1. **Integração com o watsonx Orchestrate hoje é manual** (import de specs
   OpenAPI 3.0.3 pela interface, ver
   [`docs/watsonx-orchestrate-setup.md`](docs/watsonx-orchestrate-setup.md)).
   Uma operação real evoluiria para chamada programática via ADK/API, com as
   credenciais já mapeadas em `.env.example`.
2. **Autenticação multi-papel** — hoje um único perfil; produção real com
   mais de um usuário simultâneo precisa de login e escopo de acesso.
3. **Calibração dos pesos de contágio e do score** com o histórico real da
   Krilltech, em vez das hipóteses declaradas do MVP (ver
   [`docs/project-canvas.md`](docs/project-canvas.md), seção Próximos Passos).
