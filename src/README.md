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
│           ├── recuperacao/ estratégias de recuperação e fila priorizada por capacidade
│           ├── eventos/     radar e ingestão de fontes públicas
│           ├── motor/       encadeia os módulos na ordem obrigatória
│           └── agentes/     tools expostas ao watsonx Orchestrate
├── db/cypher/               schema, seed e as queries do motor
└── frontend/                React + react-force-graph-2d
```

## Subir

Via `make` (ver [`Makefile`](../Makefile) na raiz — `.venv` único fica na
raiz do repositório, não dentro de `src/backend`):

```bash
cp .env.example .env        # raiz do repo — preencha as credenciais do AuraDB
make setup                  # cria .venv na raiz + instala backend/ingestão/frontend
make seed                   # aplica 01-schema-e-seed.cypher no AuraDB via driver
make backend                # terminal 1 — http://localhost:8000/docs
make frontend                # terminal 2 — http://localhost:5173
```

Sem `make`, o equivalente manual:

```bash
# 1. banco — cole src/db/cypher/01-schema-e-seed.cypher no AuraDB (bloco A, depois B)
#    ou rode: python src/db/seed.py

# 2. backend (venv na raiz do repo, não dentro de src/backend)
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
pip install -r src/backend/requirements.txt
cd src/backend && cp .env.example .env && cd ../..   # preencha as credenciais do AuraDB
uvicorn --app-dir src/backend app.main:app --reload
# http://localhost:8000/docs

# 3. frontend
cd src/frontend
npm install
cp .env.example .env        # VITE_API_URL aponta para o backend
npm run dev                 # http://localhost:5173
```

O frontend usa a API real por padrão. Se ela não responder, a tela cai nos
dados sintéticos do case e **avisa** — o indicador no topo passa de "Motor
conectado" para "Modo demonstração". Rede de hackathon cai; o pitch não pode
cair junto, mas a tela também não pode mentir sobre a origem do número.
`VITE_DEMO_MODE=true` força o modo sintético, ignorando o backend.

## Ordem de execução do motor

Os módulos têm ordem obrigatória entre si: o score usa o contágio como
componente e a fila usa a recomendação. Chamar fora de ordem devolve número
velho, **sem erro** — que é o modo mais caro de errar.

`POST /motor/ciclo` faz os três na ordem, e é o que o frontend chama ao abrir:

1. `POST /contagio/propagar/CLI001` — acende os vizinhos expostos
2. `POST /scoring/recalcular` — score e rating (usa o contágio como componente)
3. `POST /recuperacao/recomendar-carteira` — estratégias elegíveis da carteira
4. `GET /recuperacao/priorizar?capacidade=5` — fila do time
5. `GET /scoring/red-flags` — matriz de bandeiras

`POST /motor/ciclo?origem=CLI001` roda o ciclo a partir de um gatilho só — é a
cena da demo: um cliente pede RJ e a rede reage.

Quando o time marca uma ação como feita, `POST /recuperacao/executar/{cliente}`
grava quem decidiu e quando, e tira o cliente da fila do período. O sistema não
executa nada sozinho (Hard Rule #1); ele registra a decisão de uma pessoa.

## Regra que não se quebra

O watsonx Orchestrate nunca fala com o driver do Neo4j. Ele chama esta API
(ARD-04). Se aparecer credencial do banco dentro de um agente, está errado.
