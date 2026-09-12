from fastapi import APIRouter, HTTPException

from app.core.neo4j import run
from app.modules.carteira import queries

router = APIRouter(prefix="/carteira", tags=["carteira"])


@router.get("/kpis")
def kpis():
    """Os números da tela inicial."""
    return run(queries.KPIS)[0]


@router.get("/grafo")
def grafo():
    """Nós e arestas para o grafo de força do frontend."""
    return run(queries.GRAFO)[0]


@router.get("/cliente/{cliente_id}")
def cliente(cliente_id: str):
    rows = run(queries.CLIENTE, cliente_id=cliente_id)
    if not rows:
        raise HTTPException(404, f"Cliente {cliente_id} não existe no grafo")
    return rows[0]
