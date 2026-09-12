from fastapi import APIRouter
from pydantic import BaseModel

from app.core.neo4j import run
from app.modules.eventos import queries

router = APIRouter(prefix="/eventos", tags=["eventos"])


class NovoEvento(BaseModel):
    id: str
    cliente: str
    tipo: str          # pedido_rj | protesto | execucao_fiscal | embargo_ambiental | quebra_safra | alteracao_qsa
    data: str          # YYYY-MM-DD
    fonte: str         # DJE | PGFN | IBAMA | Receita Federal | Conab/INMET
    severidade: float
    descricao: str


@router.get("/radar")
def radar(dias: int = 90):
    """Radar de eventos: o que apareceu nas fontes públicas na janela."""
    return {"janela_dias": dias, "eventos": run(queries.RADAR, dias=dias)}


@router.post("/registrar")
def registrar(evento: NovoEvento):
    """Porta de entrada do Agente Coletor & Parser.

    Todo evento carrega FONTE — inferência de IA nunca vira fato sem origem.
    """
    return run(queries.REGISTRAR, **evento.model_dump())[0]
