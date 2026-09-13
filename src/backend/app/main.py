"""Lastro — API do monólito modular.

Módulos (cada um é uma fronteira de responsabilidade, não uma camada):
  carteira     — clientes, recebíveis, exposição, KPIs
  contagio     — motor de propagação de risco pela rede
  scoring      — score 0-1000, rating A-D, matriz de red flags
  recuperacao  — estratégias, priorização, alocação de capacidade
  eventos      — radar de eventos e ingestão de fontes públicas
  motor        — encadeia contágio → scoring → recuperação na ordem obrigatória
  agentes      — tools expostas ao watsonx Orchestrate
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.neo4j import lifespan
from app.modules.agentes.router import router as agentes
from app.modules.carteira.router import router as carteira
from app.modules.contagio.router import router as contagio
from app.modules.eventos.router import router as eventos
from app.modules.motor.router import router as motor
from app.modules.recuperacao.router import router as recuperacao
from app.modules.scoring.router import router as scoring

app = FastAPI(title="Lastro API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_origin_regex=settings.cors_origin_regex or None,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(carteira)
app.include_router(contagio)
app.include_router(scoring)
app.include_router(recuperacao)
app.include_router(eventos)
app.include_router(motor)
app.include_router(agentes)


@app.get("/health", tags=["infra"])
def health():
    """Estado da conexão com o grafo.

    O frontend usa isto para dizer na tela se o motor está no ar. Por isso
    devolve corpo JSON mesmo quando falha (503): "sem conexão" é informação,
    não exceção — quem consome precisa saber o porquê, não só que deu ruim.
    """
    from app.core.neo4j import run
    try:
        run("RETURN 1 AS ok")
    except Exception as erro:
        return JSONResponse(
            status_code=503,
            content={"status": "sem_conexao", "neo4j": "indisponível",
                     "detalhe": f"{type(erro).__name__}: {erro}"},
        )
    return {"status": "ok", "neo4j": "conectado"}
