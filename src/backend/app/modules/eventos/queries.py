RADAR = """
MATCH (e:Evento)-[:SOBRE]->(c:Cliente)
WHERE e.data >= date() - duration({days:$dias})
RETURN e.id AS evento_id, e.tipo AS tipo, e.data AS data, e.fonte AS fonte,
       e.severidade AS severidade, e.descricao AS descricao,
       c.id AS cliente, c.nome AS cliente_nome, c.rating AS rating,
       c.exposicao_total AS exposicao_rs
ORDER BY e.data DESC, e.severidade DESC
"""

REGISTRAR = """
MERGE (e:Evento {id:$id})
  SET e.tipo=$tipo, e.data=date($data), e.fonte=$fonte,
      e.severidade=$severidade, e.descricao=$descricao,
      e.ingerido_em=datetime()
WITH e
MATCH (c:Cliente {id:$cliente})
MERGE (e)-[:SOBRE]->(c)
RETURN e.id AS evento_id, c.id AS cliente
"""
