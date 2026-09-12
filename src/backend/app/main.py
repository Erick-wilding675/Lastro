"""Lastro — API do monólito modular.

Módulos (cada um é uma fronteira de responsabilidade, não uma camada):
  carteira     — clientes, recebíveis, exposição, KPIs
  contagio     — motor de propagação de risco pela rede
  scoring      — score 0-1000, rating A-D, matriz de red flags
  recuperacao  — estratégias, priorização, alocação de capacidade
  eventos      — radar de eventos e ingestão de fontes públicas
  agentes      — tools expostas ao watsonx Orchestrate
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.neo4j import lifespan
from app.modules.carteira.router import router as carteira
from app.modules.contagio.router import router as contagio
from app.modules.scoring.router import router as scoring
from app.modules.recuperacao.router import router as recuperacao
from app.modules.eventos.router import router as eventos
from app.modules.agentes.router import router as agentes

app = FastAPI(title="Lastro API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(carteira)
app.include_router(contagio)
app.include_router(scoring)
app.include_router(recuperacao)
app.include_router(eventos)
app.include_router(agentes)


@app.get("/health", tags=["infra"])
def health():
    from app.core.neo4j import run
    run("RETURN 1 AS ok")
    return {"status": "ok", "neo4j": "conectado"}
