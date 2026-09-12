# Nível 1: adequação devedor x estratégia, com filtro de elegibilidade jurídica.
RECOMENDAR = """
MATCH (c:Cliente {id:$cliente})<-[:DE]-(r:Recebivel)
WHERE r.status IN ['aberto','vencido','em_acordo']
WITH c, sum(r.valor_aberto) AS exposicao, collect(DISTINCT r.estagio_juridico) AS estagios
MATCH (e:EstrategiaRecuperacao)
WHERE any(est IN estagios WHERE est IN e.estagios_elegiveis)
WITH c, e, exposicao,
     exposicao * e.taxa_sucesso_historica AS valor_esperado,
     exposicao * e.taxa_sucesso_historica - e.custo_medio AS valor_liquido,
     CASE WHEN c.cliente_desde <= date() - duration({years:3}) THEN 1.0 ELSE 0.5 END AS peso_relacao
WITH c, e, exposicao, valor_esperado, valor_liquido,
     valor_liquido / e.prazo_medio_dias
       * (CASE WHEN e.preserva_relacao THEN 1.0 + peso_relacao * 0.3 ELSE 1.0 END) AS indice
MERGE (c)-[rec:RECOMENDADA]->(e)
  SET rec.valor_recuperavel_estimado = round(valor_esperado),
      rec.prazo_estimado = e.prazo_medio_dias,
      rec.indice = indice,
      rec.calculado_em = datetime()
RETURN e.nome AS estrategia, round(valor_esperado) AS recuperavel_rs,
       e.prazo_medio_dias AS prazo_dias, e.custo_medio AS custo_rs,
       e.taxa_sucesso_historica AS taxa_sucesso, e.preserva_relacao AS preserva_relacao,
       round(indice) AS indice_prioridade
ORDER BY indice DESC
"""

# Nível 3: alocação de capacidade. Heurística gulosa, explicável linha a linha.
PRIORIZAR_CARTEIRA = """
MATCH (c:Cliente)-[rec:RECOMENDADA]->(e:EstrategiaRecuperacao)
WITH c, e, rec ORDER BY rec.indice DESC
WITH c, head(collect({estrategia:e.nome, indice:rec.indice,
                      recuperavel:rec.valor_recuperavel_estimado,
                      prazo:rec.prazo_estimado})) AS melhor
RETURN c.id AS cliente, c.nome AS nome, c.rating AS rating,
       c.exposicao_total AS exposicao_rs, melhor
ORDER BY melhor.indice DESC
LIMIT $capacidade
"""
