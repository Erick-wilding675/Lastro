"""Motor — a ordem de execução, executável.

Os módulos carteira/contagio/scoring/recuperacao são fronteiras de
responsabilidade e cada um resolve o seu pedaço. Mas eles têm uma ordem
obrigatória entre si (README de `src/`): o score usa o contágio como
componente, e a fila usa a recomendação. Chamar fora de ordem devolve número
velho — silenciosamente.

Este módulo não tem regra de negócio própria: ele só encadeia os outros na
ordem certa, para que o frontend tenha uma chamada única ao abrir a tela.
"""
from fastapi import APIRouter

from app.core.neo4j import run
from app.modules.contagio import queries as q_contagio
from app.modules.motor import queries as q_motor
from app.modules.recuperacao import queries as q_recuperacao
from app.modules.scoring import queries as q_scoring

router = APIRouter(prefix="/motor", tags=["motor"])


@router.post("/ciclo")
def ciclo(origem: str | None = None):
    """Roda o ciclo completo e devolve o que mudou.

    1. contágio   — propaga a partir de quem deteriorou (ou só de `origem`)
    2. scoring    — recalcula score e rating já com o contágio dentro
    3. recuperação— regenera as recomendações da carteira
    """
    if origem:
        # Buscar o nome, e não repetir o id, porque a tela de propagação
        # mostra o gatilho pelo nome: sem isto o cabeçalho da cena da demo
        # vira "CLI001 — CLI001".
        origens = run(q_motor.UMA_ORIGEM, id=origem) or [
            {"id": origem, "nome": origem, "situacao": "desconhecida"}]
    else:
        origens = run(q_motor.ORIGENS)

    propagacoes = []
    for o in origens:
        expostos = run(q_contagio.PROPAGAR, origem=o["id"])
        if expostos:
            propagacoes.append({"origem": o["id"], "nome": o["nome"],
                                "expostos": expostos})

    scores = run(q_scoring.CALCULAR)
    recomendacoes = run(q_recuperacao.RECOMENDAR_CARTEIRA)[0]
    resumo = run(q_motor.RESUMO)[0]

    return {
        "origens_processadas": [o["id"] for o in origens],
        "propagacoes": propagacoes,
        "clientes_reavaliados": len(scores),
        "recomendacoes_geradas": recomendacoes["recomendacoes"],
        "resumo": resumo,
    }
