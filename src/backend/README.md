# Lastro — Backend

API REST em Python + FastAPI. Único ponto do sistema que fala com o driver do
Neo4j (`app/core/neo4j.py`) — nem o frontend, nem o watsonx Orchestrate tocam
o banco diretamente (ARD-04, ver [`../../.ai/docs/ARD.md`](../../.ai/docs/ARD.md)).

## Rodar localmente

A partir da raiz do repositório (`.venv` único, compartilhado com a
ingestão — ver [`../README.md`](../../README.md)):

```bash
cp .env.example .env        # raiz — preencha NEO4J_URI/USER/PASSWORD com o AuraDB
make setup                  # cria .venv na raiz + instala requirements.txt deste módulo
make backend                # uvicorn --reload em :8000
```

Sem `make`:

```bash
python -m venv .venv && source .venv/Scripts/activate   # a partir da raiz
pip install -r src/backend/requirements.txt
cd src/backend && cp .env.example .env && cd ../..
uvicorn --app-dir src/backend app.main:app --reload
# http://localhost:8000/docs
```

`GET /health` diz se o driver conectou (`{"status":"ok","neo4j":"conectado"}`)
ou não (503, com o motivo). O boot nunca aborta por falha de conexão — ver o
comentário em `app/core/neo4j.py` sobre por que degradar é melhor que crashar
num PaaS.

## Módulos

Cada pasta em `app/modules/` é uma fronteira de responsabilidade de domínio,
não uma camada técnica — todas têm `router.py` (endpoints) e `queries.py`
(Cypher). Ordem em que `main.py` monta a app:

| Módulo | Prefixo | Responsabilidade |
|---|---|---|
| `carteira` | `/carteira` | clientes, KPIs, grafo completo da carteira |
| `contagio` | `/contagio` | motor de propagação de exposição pela rede |
| `scoring` | `/scoring` | score 0-1000, rating A-D, matriz de red flags |
| `recuperacao` | `/recuperacao` | estratégias de recuperação e fila priorizada por capacidade |
| `eventos` | `/eventos` | radar de eventos e registro de ocorrências (fonte pública ou ERP) |
| `motor` | `/motor` | encadeia contágio → scoring → recuperação na ordem obrigatória |
| `agentes` | `/agentes` | endpoints consumidos pelo watsonx Orchestrate como *tools* |

## Endpoints

```
GET  /health

GET  /carteira/kpis
GET  /carteira/grafo
GET  /carteira/cliente/{cliente_id}

POST /contagio/propagar/{origem}

POST /scoring/recalcular
GET  /scoring/red-flags

POST /recuperacao/recomendar/{cliente}
POST /recuperacao/recomendar-carteira
GET  /recuperacao/priorizar?capacidade=N
POST /recuperacao/executar/{cliente}

GET  /eventos/radar
POST /eventos/registrar

POST /motor/ciclo               (?origem=CLI001 para o cenário de demo)

GET  /agentes/contexto/{cliente}
GET  /agentes/dossie/{cliente}
```

## Ordem de execução do motor

O score usa o contágio como componente; a fila de recuperação usa a
recomendação. Chamar fora de ordem devolve número velho, **sem erro** — o
modo mais caro de errar. `POST /motor/ciclo` faz os três passos na ordem
certa e é o que o frontend chama ao abrir a tela inicial:

1. `POST /contagio/propagar/{origem}` — acende os vizinhos expostos
2. `POST /scoring/recalcular` — score e rating (usa o contágio como componente)
3. `POST /recuperacao/recomendar-carteira` — estratégias elegíveis
4. `GET /recuperacao/priorizar?capacidade=N` — fila do time
5. `GET /scoring/red-flags` — matriz de bandeiras

Ver [`../../.ai/docs/matching-model.md`](../../.ai/docs/matching-model.md) para os pesos e a lógica completa.

## Configuração (`app/core/config.py`)

Lida via `pydantic-settings` a partir de `.env` — nunca hardcode credencial:

| Variável | Default | Uso |
|---|---|---|
| `NEO4J_URI` | `bolt://localhost:7687` | endpoint do AuraDB/instância local |
| `NEO4J_USER` | `neo4j` | |
| `NEO4J_PASSWORD` | — | |
| `NEO4J_DATABASE` | `neo4j` | |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | origens explícitas |
| `CORS_ORIGIN_REGEX` | `https://.*\.vercel\.app` | cobre os previews da Vercel sem listar um a um |

## Integração com o watsonx Orchestrate

O módulo `agentes` expõe os endpoints que os 4 agentes de IA chamam como
*tools*. O FastAPI gera OpenAPI 3.1; o Orchestrate só aceita 3.0, por isso as
specs em `openapi/` foram escritas à mão em 3.0.3. Roteiro completo de
importação em [`../../.ai/docs/watsonx-orchestrate-setup.md`](../../.ai/docs/watsonx-orchestrate-setup.md).

## Docker / deploy

`Dockerfile` builda uma imagem de produção (Python 3.11-slim, porta via
`$PORT`). `../../render.yaml` é o blueprint usado no deploy real (Render,
plano free, `rootDir: src/backend`). `make docker-backend`, a partir da
raiz, builda a imagem localmente.

## Qualidade

`pyproject.toml` configura `ruff` (lint). `make lint`, a partir da raiz, roda
sobre `app/`. Não há suíte de testes automatizados hoje — ver a seção
"Roadmap" do README raiz.
