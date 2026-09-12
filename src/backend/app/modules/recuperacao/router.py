from fastapi import APIRouter

from app.core.neo4j import run
from app.modules.recuperacao import queries

router = APIRouter(prefix="/recuperacao", tags=["recuperacao"])


@router.post("/recomendar/{cliente}")
def recomendar(cliente: str):
    """Nível 1 — qual estratégia cabe neste devedor, e por quê."""
    return {"cliente": cliente, "estrategias": run(queries.RECOMENDAR, cliente=cliente)}


@router.get("/priorizar")
def priorizar(capacidade: int = 5):
    """Nível 3 — onde o time deve gastar a capacidade que tem.

    `capacidade` = quantos casos o time consegue tocar no período.
    Ação recomendada que ninguém executa é ação inexistente.
    """
    return {"capacidade": capacidade,
            "fila": run(queries.PRIORIZAR_CARTEIRA, capacidade=capacidade)}
