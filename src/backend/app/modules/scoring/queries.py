# Score 0-1000 e rating A-D, exigidos pela seção 7.1 do desafio.
# Score ALTO = risco BAIXO. A:800+ B:600+ C:400+ D:<400
# Cinco componentes com peso uniforme — hipótese declarada, não calibrada.
CALCULAR = """
MATCH (c:Cliente)
WITH c, CASE
      WHEN c.situacao = 'recuperacao_judicial' THEN 1.0
      WHEN c.dias_atraso_max >= 90 THEN 0.90
      WHEN c.dias_atraso_max >= 30 THEN 0.60
      WHEN c.dias_atraso_max > 0   THEN 0.30
      ELSE 0.0 END AS risco_pagamento
OPTIONAL MATCH (e:Evento)-[:SOBRE]->(c)
  WHERE e.data >= date() - duration({days:180})
    AND e.tipo IN ['pedido_rj','protesto','execucao_fiscal','alteracao_qsa']
WITH c, risco_pagamento, coalesce(max(e.severidade), 0.0) AS risco_juridico
OPTIONAL MATCH (r:Recebivel)-[:DE]->(c) WHERE r.status IN ['aberto','vencido','em_acordo']
WITH c, risco_pagamento, risco_juridico,
     coalesce(sum(r.valor_aberto), 0.0) AS exposicao,
     coalesce(sum(r.garantia_valor), 0.0) AS garantia
WITH c, risco_pagamento, risco_juridico, exposicao,
     CASE WHEN exposicao = 0 THEN 0.0
          ELSE 1.0 - (CASE WHEN garantia/exposicao > 1.0 THEN 1.0 ELSE garantia/exposicao END)
     END AS risco_garantia
OPTIONAL MATCH (:Cliente)-[x:EXPOSTO_A]->(c)
WITH c, risco_pagamento, risco_juridico, risco_garantia, exposicao,
     coalesce(max(x.peso), 0.0) AS risco_contagio
OPTIONAL MATCH (e2:Evento)-[:SOBRE]->(c)
  WHERE e2.tipo IN ['quebra_safra','embargo_ambiental']
WITH c, risco_pagamento, risco_juridico, risco_garantia, risco_contagio, exposicao,
     coalesce(max(e2.severidade), 0.0) AS risco_agro
WITH c, exposicao, risco_pagamento, risco_juridico, risco_garantia, risco_contagio, risco_agro,
     toInteger(round(1000 * (1.0 -
       (risco_pagamento + risco_juridico + risco_garantia + risco_contagio + risco_agro) / 5.0))) AS score
SET c.score = score,
    c.rating = CASE WHEN score >= 800 THEN 'A' WHEN score >= 600 THEN 'B'
                    WHEN score >= 400 THEN 'C' ELSE 'D' END,
    c.score_calculado_em = datetime(),
    c.score_decomposto = [risco_pagamento, risco_juridico, risco_garantia, risco_contagio, risco_agro]
RETURN c.id AS cliente, c.nome AS nome, c.score AS score, c.rating AS rating,
       exposicao AS exposicao_rs, risco_pagamento, risco_juridico,
       risco_garantia, risco_contagio, risco_agro
ORDER BY score ASC
"""

RED_FLAGS = """
MATCH (c:Cliente)
CALL {
    WITH c
    MATCH (e:Evento)-[:SOBRE]->(c) WHERE e.tipo='pedido_rj'
    RETURN 'RJ DISTRIBUÍDA — stay period ativo, execução bloqueada' AS flag, 1.0 AS gravidade
  UNION
    WITH c
    MATCH (e:Evento)-[:SOBRE]->(c) WHERE e.tipo='protesto'
    RETURN 'Protesto de título registrado' AS flag, 0.7 AS gravidade
  UNION
    WITH c
    MATCH (e:Evento)-[:SOBRE]->(c) WHERE e.tipo='execucao_fiscal'
    RETURN 'Execução fiscal / dívida ativa' AS flag, 0.6 AS gravidade
  UNION
    WITH c
    MATCH (e:Evento)-[:SOBRE]->(c) WHERE e.tipo='alteracao_qsa'
    RETURN 'Alteração societária recente (QSA)' AS flag, 0.4 AS gravidade
  UNION
    WITH c
    MATCH (c)-[:POSSUI]->(i:Imovel) WHERE i.embargo_ibama = true
    RETURN 'Embargo ambiental no imóvel (IBAMA)' AS flag, 0.55 AS gravidade
  UNION
    WITH c
    MATCH (e:Evento)-[:SOBRE]->(c) WHERE e.tipo='quebra_safra'
    RETURN 'Quebra de safra na região' AS flag, 0.5 AS gravidade
  UNION
    WITH c
    MATCH (:Cliente)-[x:EXPOSTO_A]->(c) WHERE x.peso >= 0.8
    RETURN 'Contágio forte: vínculo direto com devedor em crise' AS flag, x.peso AS gravidade
  UNION
    WITH c
    MATCH (r:Recebivel)-[:DE]->(c)
    WHERE r.status IN ['aberto','vencido'] AND r.garantia_tipo IN ['nenhuma','penhor_safra']
    RETURN 'Garantia frágil: sem alienação fiduciária (entra no concurso da RJ)' AS flag, 0.45 AS gravidade
}
WITH c, collect({flag:flag, gravidade:gravidade}) AS flags
WHERE size(flags) > 0
RETURN c.id AS cliente, c.nome AS nome, c.rating AS rating,
       c.exposicao_total AS exposicao_rs, size(flags) AS qtd_flags, flags
ORDER BY qtd_flags DESC, exposicao_rs DESC
"""
