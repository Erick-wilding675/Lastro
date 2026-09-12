"""Tools expostas ao IBM watsonx Orchestrate.

O Orchestrate NÃO fala com o Neo4j (ARD-04). Ele chama estes endpoints,
que são a superfície de ferramenta dos agentes:

  Agente Coletor & Parser     -> POST /eventos/registrar
  Agente de Risco Agro        -> GET  /agentes/contexto/{cliente}
  Motor de Decisão & Scoring  -> POST /scoring/recalcular
  Agente Sintetizador         -> GET  /agentes/dossie/{cliente}
"""
from fastapi import APIRouter, HTTPException

from app.core.neo4j import run

router = APIRouter(prefix="/agentes", tags=["agentes"])

CONTEXTO = """
MATCH (c:Cliente {id:$cliente})
OPTIONAL MATCH (c)-[:OPERA_EM]->(r:Regiao)
OPTIONAL MATCH (c)-[:PLANTA]->(cu:Cultura)
OPTIONAL MATCH (c)-[:POSSUI]->(i:Imovel)
OPTIONAL MATCH (e:Evento)-[:SOBRE]->(c)
RETURN c{.id,.nome,.situacao,.rating,.score,.exposicao_total,.dias_atraso_max} AS cliente,
       collect(DISTINCT r.nome) AS regioes,
       collect(DISTINCT cu.nome) AS culturas,
       collect(DISTINCT i{.id,.area_ha,.embargo_ibama}) AS imoveis,
       collect(DISTINCT e{.tipo,.data,.fonte,.severidade,.descricao}) AS eventos
"""

DOSSIE = """
MATCH (c:Cliente {id:$cliente})
OPTIONAL MATCH (origem:Cliente)-[x:EXPOSTO_A]->(c)
OPTIONAL MATCH (c)-[rec:RECOMENDADA]->(est:EstrategiaRecuperacao)
OPTIONAL MATCH (r:Recebivel)-[:DE]->(c) WHERE r.status IN ['aberto','vencido']
RETURN c{.id,.nome,.situacao,.rating,.score,.score_decomposto,.exposicao_total} AS cliente,
       collect(DISTINCT {de:origem.nome, peso:x.peso, caminho:x.caminho}) AS contagio,
       collect(DISTINCT {estrategia:est.nome, recuperavel:rec.valor_recuperavel_estimado,
                         prazo:rec.prazo_estimado, indice:rec.indice}) AS recomendacoes,
       collect(DISTINCT r{.id,.valor_aberto,.dias_atraso,.garantia_tipo,.estagio_juridico}) AS recebiveis
"""


@router.get("/contexto/{cliente}")
def contexto(cliente: str):
    """Contexto bruto do cliente para o agente raciocinar em cima."""
    rows = run(CONTEXTO, cliente=cliente)
    if not rows:
        raise HTTPException(404, f"Cliente {cliente} não existe no grafo")
    return rows[0]


@router.get("/dossie/{cliente}")
def dossie(cliente: str):
    """Tudo que o Agente Sintetizador precisa para redigir o relatório
    padronizado de risco: score decomposto, contágio com caminho,
    recomendações e recebíveis em aberto."""
    rows = run(DOSSIE, cliente=cliente)
    if not rows:
        raise HTTPException(404, f"Cliente {cliente} não existe no grafo")
    return rows[0]
