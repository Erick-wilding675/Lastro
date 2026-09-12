KPIS = """
MATCH (c:Cliente)
OPTIONAL MATCH (r:Recebivel)-[:DE]->(c)
WITH c,
     sum(CASE WHEN r.status IN ['aberto','vencido','em_acordo'] THEN r.valor_aberto ELSE 0 END) AS exp_cli,
     sum(CASE WHEN r.status = 'vencido' THEN r.valor_aberto ELSE 0 END) AS venc_cli,
     sum(CASE WHEN r.status = 'recuperado' THEN r.valor ELSE 0 END) AS rec_cli
RETURN count(c) AS clientes,
       round(sum(exp_cli)) AS exposicao_total_rs,
       round(sum(venc_cli)) AS vencido_rs,
       round(sum(rec_cli)) AS recuperado_rs,
       round(100.0 * sum(venc_cli) / (CASE WHEN sum(exp_cli)=0 THEN 1 ELSE sum(exp_cli) END)) AS pct_carteira_vencida,
       sum(CASE WHEN c.rating='D' THEN 1 ELSE 0 END) AS clientes_rating_D,
       round(sum(CASE WHEN c.rating='D' THEN exp_cli ELSE 0 END)) AS exposicao_risco_critico_rs
"""

GRAFO = """
MATCH (c:Cliente)
OPTIONAL MATCH (c)-[x:EXPOSTO_A]->(v:Cliente)
WITH collect(DISTINCT {id:c.id, nome:c.nome, tipo:c.tipo, situacao:c.situacao,
                        rating:c.rating, score:c.score, exposicao:c.exposicao_total}) AS nodes,
     collect(DISTINCT CASE WHEN v IS NULL THEN NULL
             ELSE {source:c.id, target:v.id, peso:x.peso, caminho:x.caminho, tipo:'contagio'} END) AS links
RETURN nodes, [l IN links WHERE l IS NOT NULL] AS links
"""

CLIENTE = """
MATCH (c:Cliente {id:$cliente_id})
OPTIONAL MATCH (r:Recebivel)-[:DE]->(c)
OPTIONAL MATCH (c)-[:OPERA_EM]->(reg:Regiao)
OPTIONAL MATCH (c)-[:PLANTA]->(cul:Cultura)
RETURN c AS cliente,
       collect(DISTINCT r{.*}) AS recebiveis,
       collect(DISTINCT reg.nome) AS regioes,
       collect(DISTINCT cul.nome) AS culturas
"""
