# ARD — Registros de Decisão de Arquitetura

**Status:** revisado pós-pivô. Registra as decisões de arquitetura do **Lastro**, tal como implementado — não mais do produto anterior ao pivô de domínio de 11/09 ("Talent Graph").

**Projeto:** Lastro
**Versão:** 1.0
**Data:** 2026-09-13

---

## Resumo de Decisões

| ARD | Tópico | Decisão |
|---|---|---|
| ARD-01 | Armazenamento do grafo | Neo4j (AuraDB, tier gratuito) — banco de grafos nativo |
| ARD-02 | Backend | Python + FastAPI, monólito modular por domínio (não por camada) |
| ARD-03 | Frontend | React + Vite + `react-force-graph-2d`, com fallback automático para dados sintéticos |
| ARD-04 | Integração watsonx Orchestrate ↔ Neo4j | API REST própria (FastAPI) exposta como "tools" via OpenAPI 3.0.3 — sem conexão direta driver-a-driver |
| ARD-05 | Persistência de exposição e score | Materializados como propriedades no grafo (`Cliente.score`, `EXPOSTO_A.peso/caminho`), não recalculados a cada leitura |
| ARD-06 | Ordem de execução do motor | Sequência obrigatória contágio → scoring → recuperação, encadeada em `POST /motor/ciclo` |
| ARD-07 | Hospedagem | Backend em container Docker no Render; frontend estático no Vercel |
| ARD-08 | Autenticação no MVP | Nenhuma — usuário único (área de crédito/comitê), decisão consciente de escopo |
| ARD-09 | Fronteira agente LLM × função determinística | Contágio, score e haircut são sempre Cypher/Python; LLM só entra onde há texto livre ou ambiguidade |

---

## ARD-01 — Armazenamento do grafo

**Decisão:** Representar clientes, recebíveis, sócios, avalistas, grupos econômicos, região/cultura/safra e eventos em **Neo4j (AuraDB, tier gratuito)** — banco de grafos nativo, consultado via Cypher.

**Racional:** o diferencial do Lastro é justamente a leitura de vínculos multi-hop entre clientes (mesmo grupo econômico, mesmo avalista, mesmo sócio, mesma região/cultura/safra) — o tipo de consulta que em SQL vira junção recursiva ilegível e em Cypher é uma travessia direta. Um banco de grafos nativo representa fisicamente a tese do produto ("produtor rural não quebra sozinho"), não só logicamente.

**Verificado:** AuraDB Free tier suporta até 200k nós e 400k relacionamentos, sem cartão de crédito — folga ampla para o seed sintético de demonstração (dezenas de nós). Instâncias sem atividade por 30 dias são apagadas.

**Consequências:** o schema (`src/db/cypher/01-schema-e-seed.cypher`) e as queries do motor (`src/db/cypher/02-queries-motor.cypher`) são a fonte de verdade estrutural — ver [`data-model.md`](data-model.md). O driver oficial `neo4j` (Python) é o único ponto de acesso ao banco, isolado em `src/backend/app/core/neo4j.py`.

**Status:** Decidido, implementado.

---

## ARD-02 — Backend

**Decisão:** Python + FastAPI, organizado como **monólito modular por domínio** — um deployable, módulos com fronteira de responsabilidade clara, não camadas anêmicas.

**Racional:** FastAPI dá tipagem, docs automáticas (`/docs`) e uma API REST rápida de expor como "tool" para o watsonx Orchestrate (ver ARD-04). O driver oficial do Neo4j em Python é maduro. A modularização por domínio (`carteira`, `contagio`, `scoring`, `recuperacao`, `eventos`, `motor`, `agentes` — cada um com `router.py` + `queries.py`) reflete os limites reais do negócio (exposição, score, recuperação, eventos são processos distintos), não uma separação técnica arbitrária tipo controller/service/repository.

**Consequências:** cada módulo só fala com o Neo4j através de `app/core/neo4j.py`; nenhum módulo importa Cypher de outro. `app/modules/motor/` é o único módulo que orquestra os demais (ver ARD-06).

**Status:** Decidido, implementado.

## ARD-03 — Frontend

**Decisão:** React + Vite, com `react-force-graph-2d` para o grafo de força da carteira, e **fallback automático para dados sintéticos** (`src/frontend/src/lib/demoData.js`) quando a API real não responde.

**Racional:** `react-force-graph-2d` é a biblioteca mais madura para prototipagem rápida de grafo de força em React. O fallback sintético existe por uma razão operacional concreta: a rede do hackathon podia cair, mas o pitch não pode cair junto — e a tela também não pode **mentir** sobre a origem do número. Por isso, ao invés de simplesmente travar, o frontend detecta a falha de conexão (`src/frontend/src/lib/conexao.js`) e alterna para o modo sintético com aviso visível no indicador de status ("Motor conectado" → "Modo demonstração"). `VITE_DEMO_MODE=true` força esse modo, ignorando o backend.

**Consequências:** todo componente que exibe dado numérico precisa saber se está em modo real ou demo (via `StatusConexao.jsx`) — não é permitido um componente que finja que um número sintético é um número real.

**Status:** Decidido, implementado.

## ARD-04 — Integração watsonx Orchestrate ↔ Neo4j

**Decisão:** o watsonx Orchestrate **nunca** se conecta diretamente ao driver do Neo4j. Toda leitura/escrita passa pela API REST do backend (ARD-02), importada no Orchestrate como "tools" a partir de specs OpenAPI **3.0.3** escritos à mão em `src/backend/openapi/` (o FastAPI gera OpenAPI 3.1, que o Orchestrate não aceita — ver [`watsonx-orchestrate-setup.md`](watsonx-orchestrate-setup.md)).

**Racional:** é a regra de arquitetura mais importante do sistema. Mantém fisicamente a separação entre orquestração (LLM, onde há ambiguidade) e cálculo (determinístico, onde há conta) — não depende de disciplina de código para não ser violada, é a própria topologia do sistema. Se uma credencial do Neo4j aparecer dentro de um agente, é erro de arquitetura, não atalho.

**Consequências:** no MVP do hackathon, a importação das tools no Orchestrate é **manual** (upload dos specs OpenAPI via UI ou ADK, backend exposto por túnel público temporário — Cloudflare/ngrok) — não há chamada programática do Orchestrate para o backend fora desse fluxo de configuração. Ver ARD suplementar sobre produção real nas Decisões em Aberto.

**Status:** Decidido, implementado (fluxo manual via OpenAPI + túnel).

## ARD-05 — Persistência de exposição e score

**Decisão:** o resultado do motor de contágio e do scoring é **materializado no próprio grafo** — `POST /contagio/propagar/{origem}` grava peso, caminho e canais na relação `EXPOSTO_A`; `POST /scoring/recalcular` grava `score`, `rating`, `score_decomposto` e `score_calculado_em` como propriedades do nó `Cliente` — em vez de recalculado em tempo real a cada leitura.

**Racional:** `GET /carteira/*` e o drawer do cliente no frontend só **leem** o que já foi calculado — não recalculam a cada requisição. Isso torna a explicação auditável e estável entre uma tela e outra, e é o que sustenta a trilha de auditoria (Hard Rule #2 de [`ai.md`](../ai.md)): o dado carrega o momento em que foi calculado (`calculado_em`), não é reconstituído silenciosamente.

**Consequências:** um evento novo sobre um cliente exige **repropagar** a exposição dos vizinhos, não só recalcular aquele cliente isoladamente — chamar os endpoints fora de ordem devolve número velho, sem erro (ver ARD-06). `data-model.md` documenta essas propriedades materializadas como parte do schema.

**Status:** Decidido, implementado.

## ARD-06 — Ordem de execução do motor

**Decisão:** os módulos `contagio`, `scoring` e `recuperacao` têm ordem obrigatória entre si — o score usa o contágio como componente, e a fila de recuperação usa a recomendação. `POST /motor/ciclo` encadeia os três na ordem certa (contágio → scoring → recuperação → priorização → red flags) e é o endpoint que o frontend chama ao abrir a tela inicial.

**Racional:** chamar os endpoints individuais fora de ordem não gera erro — gera **número desatualizado silencioso**, o modo mais caro de errar em um sistema de decisão de crédito (Hard Rule #7: "prefira falha ruidosa a degradação silenciosa"). Centralizar a ordem em um único endpoint de ciclo remove essa classe de erro do lado de quem consome a API.

**Consequências:** qualquer novo consumidor da API (frontend, agente do watsonx, script) que precise do estado consistente da carteira deve preferir `POST /motor/ciclo` a chamar os três endpoints manualmente.

**Status:** Decidido, implementado.

## ARD-07 — Hospedagem

**Decisão:** backend em container Docker no **Render** (`render.yaml`, serviço `lastro-api`, plano free, credenciais do Neo4j como secrets `sync: false`); frontend estático no **Vercel** (`vercel.json`, build a partir de `src/frontend`, output `src/frontend/dist`).

**Racional:** ambos sobem em minutos, sem custo, e resolvem o problema real de expor o backend numa URL pública HTTPS — necessário tanto para o frontend em produção quanto (durante a configuração) para a importação de tools no watsonx Orchestrate.

**Consequências:** `src/backend/Dockerfile` fixa Python 3.11 (não 3.14 — `pydantic-core` ainda não publica wheel para 3.14 no momento da decisão) e lê a porta de `$PORT`, que Render/Railway/Fly injetam em runtime.

**Status:** Decidido, implementado.

## ARD-08 — Autenticação no MVP

**Decisão:** nenhuma autenticação multi-papel. Um único usuário implícito (área de crédito/comitê da Krilltech).

**Racional:** decisão consciente de escopo, não uma lacuna esquecida — o MVP existe para provar a tese de exposição em rede, não para modelar RBAC. A API do MVP não exige `connection`/`app-id` no watsonx Orchestrate por causa disso.

**Consequências:** qualquer evolução pós-MVP que exponha o Lastro a múltiplos papéis (comercial, jurídico, diretoria) precisa endereçar autenticação e controle de acesso antes — não é um `TODO` interno, é um requisito de produção real.

**Status:** Decidido, implementado (ausência deliberada).

## ARD-09 — Fronteira entre agente LLM e função determinística

**Decisão:** propagação de exposição pelo grafo, score, rating, haircut de garantia e priorização de recuperação são **sempre** cálculo determinístico — Cypher (`queries.py` de cada módulo) ou Python no backend — e **nunca** gerados ou estimados por um LLM. Os quatro agentes do watsonx Orchestrate (Coletor & Parser, Risco Agro & Climático, Decisão & Scoring, Sintetizador — ver [`agentes.md`](agentes.md)) só atuam onde há texto livre, ambiguidade ou redação: ler um documento, interpretar contexto agroclimático, decidir *quando* disparar o recálculo, escrever o parecer final.

**Racional:** é a resposta direta a "e se o modelo errar o score?" — a resposta é que o score não é gerado por modelo, então não há alucinação possível na origem do número; o pior caso é rodar sobre dado desatualizado (mitigado por ARD-06), nunca um número inventado. Cada agente carrega esse guardrail em primeira pessoa no próprio prompt base (`agentes.md`): o de Decisão & Scoring "nunca produz score por conta própria — só dispara e lê"; o Sintetizador só cita números que já existem no dossiê recebido de `GET /agentes/dossie/{cliente}`. A garantia arquitetural (função vs. agente) só vira comportamento observável se o prompt também a reforçar — separar os módulos não impede um agente mal instruído de "chutar" um número em texto livre. Também é o que torna o resultado auditável (Hard Rule #2 de [`ai.md`](../ai.md)): todo score tem uma query que o gerou, reproduzível fora do contexto de um LLM.

**Consequências:** qualquer novo tipo de cálculo (nova dimensão de score, novo canal de exposição) entra como Cypher/Python em `queries.py`, nunca como prompt. A demo do pitch roda um agente ao vivo (Sintetizador, cliente CLI002) e mostra os outros três por print — o que importa provar é a fronteira, não os quatro agentes rodando simultaneamente (ver `agentes.md`, seção "Como demonstrar no pitch").

**Status:** Decidido, implementado nos módulos `contagio`, `scoring` e `recuperacao`; guardrails documentados em [`agentes.md`](agentes.md).

---

## Decisões em Aberto

1. **Integração programática watsonx Orchestrate → Lastro em produção real.** O MVP usa importação manual de OpenAPI (ARD-04). Uma operação real usaria a API/CLI (`ibm-watsonx-orchestrate` ADK) com credenciais de IBM Cloud (`WATSONX_APIKEY`, `IBM_CLOUD_API_KEY`) geridas como secrets — ver `.env.example` da raiz para os placeholders dessas variáveis, hoje não usadas pelo backend.
2. **Autenticação multi-papel** — ver ARD-08, fica para pós-MVP.
3. **Observabilidade dos agentes** — ver [`../harness.md`](../harness.md): usar a nativa do watsonx Orchestrate se cobrir a necessidade; fallback Langfuse.
