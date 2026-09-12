// =====================================================================
// QUERIES DO MOTOR — Case KRILLTECH
// Estas 5 queries SÃO o produto. O backend só as embrulha em API.
// Rode na ordem. Q1 e Q2 alimentam Q3.
// =====================================================================


// ---------------------------------------------------------------------
// Q1 — MOTOR DE CONTÁGIO (dois canais)
//
// ESTRUTURAL: o risco de um contamina o outro por vínculo jurídico ou
//   patrimonial. Grupo econômico, avalista compartilhado, sócio em comum.
// SISTÊMICO: ninguém contamina ninguém, todos sofrem a MESMA causa (seca,
//   praga, queda de cotação). Só entra com peso cheio se houver evento
//   regional confirmando o choque — senão, um vizinho que quebrou por motivo
//   próprio acenderia a microrregião inteira sem razão.
//
// O "via" é a explicação: nunca mostrar risco sem dizer de onde veio.
// Parâmetro: $origem  (ex.: 'CLI001')
// ---------------------------------------------------------------------

MATCH (origem:Cliente {id: $origem})
CALL {
    // ---------- canal estrutural ----------
    WITH origem
    MATCH (origem)-[:PERTENCE_A]->(g:GrupoEconomico)<-[:PERTENCE_A]-(v:Cliente)
    WHERE v <> origem
    RETURN v AS vizinho, 0.90 AS peso, 'estrutural' AS canal,
           'Mesmo grupo econômico: ' + g.nome AS via
  UNION
    WITH origem
    MATCH (origem)<-[:DE]-(:Recebivel)-[:GARANTIDO_POR]->(a:Avalista)
          <-[:GARANTIDO_POR]-(:Recebivel)-[:DE]->(v:Cliente)
    WHERE v <> origem
    RETURN v AS vizinho, 0.85 AS peso, 'estrutural' AS canal,
           'Avalista em comum: ' + a.nome AS via
  UNION
    WITH origem
    MATCH (origem)-[:TEM_SOCIO]->(s:Socio)<-[:TEM_SOCIO]-(v:Cliente)
    WHERE v <> origem
    RETURN v AS vizinho, 0.70 AS peso, 'estrutural' AS canal,
           'Sócio em comum (QSA): ' + s.nome AS via
  UNION
    // ---------- canal sistêmico ----------
    WITH origem
    MATCH (origem)-[:OPERA_EM]->(r:Regiao)<-[:OPERA_EM]-(v:Cliente),
          (origem)-[:PLANTA]->(cu:Cultura)<-[:PLANTA]-(v)
    WHERE v <> origem
    OPTIONAL MATCH (ev:Evento)-[:SOBRE]->(:Cliente)-[:OPERA_EM]->(r)
      WHERE ev.tipo IN ['quebra_safra','alerta_zarc','queda_preco']
        AND ev.data >= date() - duration({days: 365})
    WITH v, r, cu, count(ev) > 0 AS choque
    RETURN v AS vizinho,
           CASE WHEN choque THEN 0.75 ELSE 0.30 END AS peso,
           'sistemico' AS canal,
           'Mesma região e cultura: ' + r.nome + ' / ' + cu.nome +
             CASE WHEN choque THEN ' — choque regional confirmado por evento'
                  ELSE ' — sem evento regional no período' END AS via
  UNION
    WITH origem
    MATCH (origem)-[:COMPRA_VIA]->(rev:Cliente)<-[:COMPRA_VIA]-(v:Cliente)
    WHERE v <> origem
    RETURN v AS vizinho, 0.65 AS peso, 'sistemico' AS canal,
           'Mesmo canal de revenda: ' + rev.nome AS via
  UNION
    WITH origem
    MATCH (origem)-[:PLANTA]->(cu:Cultura)<-[:PLANTA]-(v:Cliente)
    WHERE v <> origem
    RETURN v AS vizinho, 0.40 AS peso, 'sistemico' AS canal,
           'Mesma cultura: ' + cu.nome AS via
}
WITH origem, vizinho, max(peso) AS risco_exposicao, collect(via) AS caminhos,
     collect(DISTINCT canal) AS canais
// FIX (12/09): MERGE (o:Cliente {id:$origem})-[x:EXPOSTO_A]->(vizinho) num único
// padrão fazia o Neo4j tentar recriar o nó Cliente do zero (pattern não existia
// inteiro ainda) e batia na constraint de unicidade (index entry conflict).
// Reaproveitando "origem", já casado no MATCH inicial, o MERGE só resolve a relação.
MERGE (origem)-[x:EXPOSTO_A]->(vizinho)
  SET x.peso = risco_exposicao,
      x.caminho = caminhos,
      x.canais = canais,
      x.calculado_em = datetime()
RETURN vizinho.id              AS cliente,
       vizinho.nome            AS nome,
       vizinho.situacao        AS situacao_atual,
       vizinho.exposicao_total AS exposicao_rs,
       risco_exposicao,
       canais,
       caminhos
ORDER BY risco_exposicao DESC, exposicao_rs DESC;


// ---------------------------------------------------------------------
// Q2 — SCORE 0–1000 E RATING A–D
// Exigido explicitamente pela seção 7.1 do desafio.
// Convenção: score ALTO = risco BAIXO (igual mercado).
//   A  800–1000  Baixo risco
//   B  600–799   Risco moderado
//   C  400–599   Risco alto
//   D    0–399   Risco crítico / Alerta de RJ
// Pesos uniformes (0.2 cada) — hipótese declarada e auditável.
// ---------------------------------------------------------------------

MATCH (c:Cliente)

// componente 1: comportamento de pagamento
WITH c, CASE
      WHEN c.situacao = 'recuperacao_judicial' THEN 1.0
      WHEN c.dias_atraso_max >= 90 THEN 0.90
      WHEN c.dias_atraso_max >= 30 THEN 0.60
      WHEN c.dias_atraso_max > 0   THEN 0.30
      ELSE 0.0 END AS risco_pagamento

// componente 2: eventos jurídicos/fiscais recentes (180 dias)
OPTIONAL MATCH (e:Evento)-[:SOBRE]->(c)
WHERE e.data >= date() - duration({days: 180})
  AND e.tipo IN ['pedido_rj','protesto','execucao_fiscal','alteracao_qsa']
WITH c, risco_pagamento, coalesce(max(e.severidade), 0.0) AS risco_juridico

// componente 3: cobertura de garantia
OPTIONAL MATCH (r:Recebivel)-[:DE]->(c) WHERE r.status IN ['aberto','vencido','em_acordo']
WITH c, risco_pagamento, risco_juridico,
     coalesce(sum(r.valor_aberto), 0.0) AS exposicao,
     // Haircut por tipo: nem todo real de garantia vale um real.
     // Penhor de safra evapora com a seca e entra no concurso da RJ;
     // alienacao fiduciaria e extraconcursal e sobrevive.
     coalesce(sum(r.garantia_valor * CASE r.garantia_tipo
        WHEN 'alienacao_fiduciaria' THEN 1.0
        WHEN 'aval'                 THEN 0.7
        WHEN 'cpr'                  THEN 0.6
        WHEN 'penhor_safra'         THEN 0.5
        ELSE 0.0 END), 0.0) AS garantia_ajustada
WITH c, risco_pagamento, risco_juridico, exposicao,
     CASE WHEN exposicao = 0 THEN 0.0
          ELSE 1.0 - (CASE WHEN garantia_ajustada/exposicao > 1.0 THEN 1.0
                           ELSE garantia_ajustada/exposicao END)
     END AS risco_garantia

// componente 4: contágio herdado da rede
OPTIONAL MATCH (:Cliente)-[x:EXPOSTO_A]->(c)
WITH c, risco_pagamento, risco_juridico, risco_garantia, exposicao,
     coalesce(max(x.peso), 0.0) AS risco_contagio

// componente 5: risco agro/ambiental
OPTIONAL MATCH (e2:Evento)-[:SOBRE]->(c)
WHERE e2.tipo IN ['quebra_safra','embargo_ambiental']
WITH c, risco_pagamento, risco_juridico, risco_garantia, risco_contagio, exposicao,
     coalesce(max(e2.severidade), 0.0) AS risco_agro

WITH c, exposicao, risco_pagamento, risco_juridico, risco_garantia, risco_contagio, risco_agro,
     (risco_pagamento + risco_juridico + risco_garantia + risco_contagio + risco_agro) / 5.0 AS risco_medio

WITH c, exposicao, risco_pagamento, risco_juridico, risco_garantia, risco_contagio, risco_agro,
     toInteger(round(1000 * (1.0 - risco_medio))) AS score

SET c.score = score,
    c.rating = CASE WHEN score >= 800 THEN 'A'
                    WHEN score >= 600 THEN 'B'
                    WHEN score >= 400 THEN 'C'
                    ELSE 'D' END,
    c.score_calculado_em = datetime(),
    c.score_decomposto = [risco_pagamento, risco_juridico, risco_garantia, risco_contagio, risco_agro]

RETURN c.id AS cliente, c.nome AS nome, c.score AS score, c.rating AS rating,
       exposicao AS exposicao_rs,
       risco_pagamento, risco_juridico, risco_garantia, risco_contagio, risco_agro
ORDER BY score ASC;


// ---------------------------------------------------------------------
// Q3 — MATRIZ DE RED FLAGS
// Também exigida explicitamente pela seção 7.1.
// Uma linha por cliente, com a lista de bandeiras acesas.
// ---------------------------------------------------------------------

MATCH (c:Cliente)
CALL {
    WITH c
    MATCH (e:Evento)-[:SOBRE]->(c) WHERE e.tipo = 'pedido_rj'
    RETURN 'RJ DISTRIBUÍDA — stay period ativo, execução bloqueada' AS flag, 1.0 AS gravidade
  UNION
    WITH c
    MATCH (e:Evento)-[:SOBRE]->(c) WHERE e.tipo = 'protesto'
    RETURN 'Protesto de título registrado' AS flag, 0.7 AS gravidade
  UNION
    WITH c
    MATCH (e:Evento)-[:SOBRE]->(c) WHERE e.tipo = 'execucao_fiscal'
    RETURN 'Execução fiscal / dívida ativa' AS flag, 0.6 AS gravidade
  UNION
    WITH c
    MATCH (e:Evento)-[:SOBRE]->(c) WHERE e.tipo = 'alteracao_qsa'
    RETURN 'Alteração societária recente (QSA)' AS flag, 0.4 AS gravidade
  UNION
    WITH c
    MATCH (c)-[:POSSUI]->(i:Imovel) WHERE i.embargo_ibama = true
    RETURN 'Embargo ambiental no imóvel (IBAMA)' AS flag, 0.55 AS gravidade
  UNION
    WITH c
    MATCH (e:Evento)-[:SOBRE]->(c) WHERE e.tipo = 'quebra_safra'
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
WITH c, collect({flag: flag, gravidade: gravidade}) AS flags
WHERE size(flags) > 0
RETURN c.id AS cliente, c.nome AS nome, c.rating AS rating,
       c.exposicao_total AS exposicao_rs, size(flags) AS qtd_flags, flags
ORDER BY qtd_flags DESC, exposicao_rs DESC;


// ---------------------------------------------------------------------
// Q4 — RECOMENDAÇÃO DE ESTRATÉGIA (Nível 1)
// Filtra por elegibilidade jurídica e ordena por retorno esperado.
// Materializa em :RECOMENDADA (a explicação fica gravada, não recalculada).
//
// Parâmetro: $cliente
// ---------------------------------------------------------------------

MATCH (c:Cliente {id: $cliente})<-[:DE]-(r:Recebivel)
WHERE r.status IN ['aberto','vencido','em_acordo']
WITH c, sum(r.valor_aberto) AS exposicao, collect(DISTINCT r.estagio_juridico) AS estagios
MATCH (e:EstrategiaRecuperacao)
WHERE any(est IN estagios WHERE est IN e.estagios_elegiveis)

WITH c, e, exposicao,
     exposicao * e.taxa_sucesso_historica                          AS valor_esperado,
     exposicao * e.taxa_sucesso_historica - e.custo_medio          AS valor_liquido,
     CASE WHEN c.cliente_desde <= date() - duration({years: 3})
          THEN 1.0 ELSE 0.5 END                                     AS peso_relacao

WITH c, e, exposicao, valor_esperado, valor_liquido,
     valor_liquido / e.prazo_medio_dias
       * (CASE WHEN e.preserva_relacao THEN 1.0 + peso_relacao * 0.3 ELSE 1.0 END) AS indice

MERGE (c)-[rec:RECOMENDADA]->(e)
  SET rec.valor_recuperavel_estimado = round(valor_esperado),
      rec.prazo_estimado             = e.prazo_medio_dias,
      rec.indice                     = indice,
      rec.calculado_em               = datetime()

RETURN e.nome                       AS estrategia,
       round(valor_esperado)        AS recuperavel_rs,
       e.prazo_medio_dias           AS prazo_dias,
       e.custo_medio                AS custo_rs,
       e.taxa_sucesso_historica     AS taxa_sucesso,
       e.preserva_relacao           AS preserva_relacao,
       round(indice)                AS indice_prioridade
ORDER BY indice DESC;


// ---------------------------------------------------------------------
// Q5 — CARTEIRA: KPIs PARA A TELA
// Os números que o gestor vê de cara.
// ---------------------------------------------------------------------

MATCH (c:Cliente)
OPTIONAL MATCH (r:Recebivel)-[:DE]->(c)
WITH c,
     sum(CASE WHEN r.status IN ['aberto','vencido','em_acordo'] THEN r.valor_aberto ELSE 0 END) AS exp_cli,
     sum(CASE WHEN r.status = 'vencido' THEN r.valor_aberto ELSE 0 END)                          AS venc_cli,
     sum(CASE WHEN r.status = 'recuperado' THEN r.valor ELSE 0 END)                              AS rec_cli
RETURN
  count(c)                                                        AS clientes,
  round(sum(exp_cli))                                             AS exposicao_total_rs,
  round(sum(venc_cli))                                            AS vencido_rs,
  round(sum(rec_cli))                                             AS recuperado_rs,
  round(100.0 * sum(venc_cli) / (CASE WHEN sum(exp_cli) = 0 THEN 1 ELSE sum(exp_cli) END)) AS pct_carteira_vencida,
  sum(CASE WHEN c.rating = 'D' THEN 1 ELSE 0 END)                 AS clientes_rating_D,
  round(sum(CASE WHEN c.rating = 'D' THEN exp_cli ELSE 0 END))    AS exposicao_em_risco_critico_rs;
