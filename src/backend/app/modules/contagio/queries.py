# Motor de contágio. Os pesos são hipótese declarada e auditável
# (ver vault/.ai/docs/matching-model.md).
PROPAGAR = """
MATCH (origem:Cliente {id:$origem})
CALL {
    WITH origem
    MATCH (origem)-[:PERTENCE_A]->(g:GrupoEconomico)<-[:PERTENCE_A]-(v:Cliente)
    WHERE v <> origem
    RETURN v AS vizinho, 0.90 AS peso, 'Mesmo grupo econômico: ' + g.nome AS via
  UNION
    WITH origem
    MATCH (origem)<-[:DE]-(:Recebivel)-[:GARANTIDO_POR]->(a:Avalista)
          <-[:GARANTIDO_POR]-(:Recebivel)-[:DE]->(v:Cliente)
    WHERE v <> origem
    RETURN v AS vizinho, 0.85 AS peso, 'Avalista em comum: ' + a.nome AS via
  UNION
    WITH origem
    MATCH (origem)-[:TEM_SOCIO]->(s:Socio)<-[:TEM_SOCIO]-(v:Cliente)
    WHERE v <> origem
    RETURN v AS vizinho, 0.80 AS peso, 'Sócio em comum (QSA): ' + s.nome AS via
  UNION
    WITH origem
    MATCH (origem)-[:COMPRA_VIA]->(rev:Cliente)<-[:COMPRA_VIA]-(v:Cliente)
    WHERE v <> origem
    RETURN v AS vizinho, 0.50 AS peso, 'Mesmo canal de revenda: ' + rev.nome AS via
  UNION
    WITH origem
    MATCH (origem)-[:OPERA_EM]->(r:Regiao)<-[:OPERA_EM]-(v:Cliente),
          (origem)-[:PLANTA]->(cu:Cultura)<-[:PLANTA]-(v)
    WHERE v <> origem
    RETURN v AS vizinho, 0.45 AS peso,
           'Mesma região e cultura: ' + r.nome + ' / ' + cu.nome AS via
}
WITH vizinho, max(peso) AS risco, collect(via) AS caminhos
MERGE (o:Cliente {id:$origem})-[x:EXPOSTO_A]->(vizinho)
  SET x.peso = risco, x.caminho = caminhos, x.calculado_em = datetime()
RETURN vizinho.id AS cliente, vizinho.nome AS nome, vizinho.situacao AS situacao,
       vizinho.exposicao_total AS exposicao_rs, risco AS risco_contagio, caminhos
ORDER BY risco DESC, exposicao_rs DESC
"""
