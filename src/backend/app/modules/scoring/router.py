from fastapi import APIRouter

from app.core.neo4j import run
from app.modules.scoring import queries

router = APIRouter(prefix="/scoring", tags=["scoring"])


@router.post("/recalcular")
def recalcular():
    """Recalcula score 0-1000 e rating A-D de toda a carteira.

    Rode DEPOIS do contágio: o risco herdado da rede é um dos componentes.
    """
    return {"clientes": run(queries.CALCULAR)}


@router.get("/red-flags")
def red_flags():
    """Matriz de red flags — entregável explícito da seção 7.1 do desafio."""
    return {"matriz": run(queries.RED_FLAGS)}
