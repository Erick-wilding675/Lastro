# Quem dispara contágio: cliente que já deteriorou. Não é a carteira inteira —
# propagar a partir de quem está saudável só produziria ruído com peso baixo.
ORIGENS = """
MATCH (c:Cliente)
WHERE c.situacao IN ['recuperacao_judicial','inadimplente','atraso']
   OR coalesce(c.dias_atraso_max, 0) > 0
RETURN c.id AS id, c.nome AS nome, c.situacao AS situacao
ORDER BY c.dias_atraso_max DESC
"""

# Fotografia do que o ciclo produziu, para o frontend mostrar sem outra volta.
RESUMO = """
MATCH (c:Cliente)
OPTIONAL MATCH (:Cliente)-[x:EXPOSTO_A]->(c)
RETURN count(DISTINCT c) AS clientes,
       count(x) AS vinculos_de_contagio,
       sum(CASE WHEN c.rating IN ['C','D'] THEN 1 ELSE 0 END) AS clientes_em_atencao
"""

UMA_ORIGEM = """
MATCH (c:Cliente {id:$id})
RETURN c.id AS id, c.nome AS nome, c.situacao AS situacao
"""
