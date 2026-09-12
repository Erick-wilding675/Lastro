from fastapi import APIRouter

from app.core.neo4j import run
from app.modules.contagio import queries

router = APIRouter(prefix="/contagio", tags=["contagio"])


@router.post("/propagar/{origem}")
def propagar(origem: str):
    """Dado um cliente que deteriorou, acende os vizinhos expostos.

    Devolve sempre o CAMINHO do vínculo — risco sem explicação é caixa-preta,
    e isso é proibido por regra do projeto (GIRO).
    """
    return {"origem": origem, "expostos": run(queries.PROPAGAR, origem=origem)}
