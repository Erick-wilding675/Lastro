"""Motor de contágio — dois canais distintos.

CANAL ESTRUTURAL: o risco de um contamina o outro por vínculo jurídico ou
patrimonial. Grupo econômico, avalista compartilhado, sócio em comum.

CANAL SISTÊMICO: ninguém contamina ninguém — todos sofrem a MESMA causa
(seca, praga, queda de cotação). Região, cultura, safra, canal de revenda.
Este canal só entra com peso cheio quando existe um evento regional
confirmando o choque. Sem evento confirmado, entra reduzido: um vizinho que
quebrou por motivo próprio não é motivo para acender a microrregião inteira.

Pesos são hipótese declarada e auditável (ver vault/.ai/docs/matching-model.md).
"""

PROPAGAR = """
MATCH (origem:Cliente {id:$origem})
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
    // Peso cheio só com evento regional confirmando o choque.
    WITH origem
    MATCH (origem)-[:OPERA_EM]->(r:Regiao)<-[:OPERA_EM]-(v:Cliente),
          (origem)-[:PLANTA]->(cu:Cultura)<-[:PLANTA]-(v)
    WHERE v <> origem
    OPTIONAL MATCH (ev:Evento)-[:SOBRE]->(:Cliente)-[:OPERA_EM]->(r)
      WHERE ev.tipo IN ['quebra_safra','alerta_zarc','queda_preco']
        AND ev.data >= date() - duration({days:365})
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
WITH vizinho, max(peso) AS risco, collect(via) AS caminhos,
     collect(DISTINCT canal) AS canais
MERGE (o:Cliente {id:$origem})-[x:EXPOSTO_A]->(vizinho)
  SET x.peso = risco, x.caminho = caminhos, x.canais = canais,
      x.calculado_em = datetime()
RETURN vizinho.id AS cliente, vizinho.nome AS nome, vizinho.situacao AS situacao,
       vizinho.exposicao_total AS exposicao_rs, risco AS risco_exposicao,
       canais, caminhos
ORDER BY risco DESC, exposicao_rs DESC
"""
