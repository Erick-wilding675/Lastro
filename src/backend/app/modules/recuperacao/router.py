from fastapi import APIRouter, HTTPException

from app.core.neo4j import run
from app.modules.recuperacao import queries

router = APIRouter(prefix="/recuperacao", tags=["recuperacao"])


@router.post("/recomendar/{cliente}")
def recomendar(cliente: str):
    """Nível 1 — qual estratégia cabe neste devedor, e por quê."""
    return {"cliente": cliente, "estrategias": run(queries.RECOMENDAR, cliente=cliente)}


@router.post("/recomendar-carteira")
def recomendar_carteira():
    """Nível 1 aplicado à carteira inteira.

    A fila do Nível 3 lê as arestas :RECOMENDADA. Sem passar por aqui uma vez,
    o frontend conecta na API e encontra fila vazia — não por erro, por ordem
    de execução do motor.
    """
    return run(queries.RECOMENDAR_CARTEIRA)[0]


@router.get("/priorizar")
def priorizar(capacidade: int = 5):
    """Nível 3 — onde o time deve gastar a capacidade que tem.

    `capacidade` = quantos casos o time consegue tocar no período.
    Ação recomendada que ninguém executa é ação inexistente.
    """
    return {"capacidade": capacidade,
            "fila": run(queries.PRIORIZAR_CARTEIRA, capacidade=capacidade)}


@router.post("/executar/{cliente}")
def executar(cliente: str, responsavel: str = "operador"):
    """Marca a estratégia recomendada como executada pelo time.

    O sistema não executa nada sozinho (Hard Rule #1). Este endpoint registra
    a decisão de uma pessoa e fecha a trilha de auditoria: quem marcou, quando,
    e sobre qual recomendação.
    """
    linhas = run(queries.EXECUTAR, cliente=cliente, responsavel=responsavel)
    if not linhas:
        raise HTTPException(
            404, f"Nenhuma recomendação pendente para {cliente} — "
                 "rode POST /recuperacao/recomendar-carteira antes.")
    return linhas[0]
