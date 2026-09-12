# Lastro — código

Monólito modular. Um deployable, módulos com fronteira de responsabilidade
clara (não camadas anêmicas).

```
src/
├── backend/                 Python + FastAPI
│   └── app/
│       ├── main.py          wiring dos módulos
│       ├── core/            config e driver Neo4j (único ponto que fala com o banco)
│       └── modules/
│           ├── carteira/    clientes, recebíveis, exposição, KPIs, grafo
│           ├── contagio/    motor de propagação de risco pela rede
│           ├── scoring/     score 0-1000, rating A-D, matriz de red flags
│           ├── recuperacao/ estratégias (N1) e alocação de capacidade (N3)
│           ├── eventos/     radar e ingestão de fontes públicas
│           └── agentes/     tools expostas ao watsonx Orchestrate
├── db/cypher/               schema, seed e as queries do motor
└── frontend/                React + react-force-graph-2d
```

## Subir

```bash
# 1. banco — cole 01-schema-e-seed.cypher no AuraDB (bloco A, depois bloco B)

# 2. backend
cd src/backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # preencha as credenciais do AuraDB
uvicorn app.main:app --reload
# http://localhost:8000/docs

# 3. frontend
cd src/frontend
npm install
cp .env.example .env
npm run dev                 # http://localhost:5173
```

## Ordem de execução do motor

1. `POST /contagio/propagar/CLI001` — acende os vizinhos expostos
2. `POST /scoring/recalcular` — score e rating (usa o contágio como componente)
3. `GET /scoring/red-flags` — matriz de bandeiras
4. `POST /recuperacao/recomendar/{cliente}` — estratégias elegíveis
5. `GET /recuperacao/priorizar?capacidade=5` — fila do time

## Regra que não se quebra

O watsonx Orchestrate nunca fala com o driver do Neo4j. Ele chama esta API
(ARD-04). Se aparecer credencial do banco dentro de um agente, está errado.
