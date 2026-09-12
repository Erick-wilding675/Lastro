// =============================================================================
// 03 — COMPLETAR LACUNAS
//
// Roda DEPOIS de 01-schema-e-seed.cypher e de `python -m ingestao all`.
// Fecha as lacunas que sobram quando as duas cargas convivem no mesmo grafo.
//
// Idempotente: só MERGE e SET. Rodar duas vezes não duplica nada.
//
// -----------------------------------------------------------------------------
// O QUE É CORREÇÃO E O QUE É SINTÉTICO — a distinção importa
//
// BLOCO A é CORREÇÃO de dado. O seed e a ingestão criaram dois nós para a MESMA
// microrregião do IBGE. Não se inventa nada aqui: se funde o duplicado.
//
// BLOCOS B a E são SINTÉTICOS, e seguem a mesma regra do módulo
// ingestao/fontes/sintetico.py — toda linha sai com `fonte:'SINTÉTICO — demo'`,
// `sintetico:true` e `confianca:0.0`. `MATCH (n) WHERE n.sintetico IS NULL`
// continua devolvendo só o que foi medido.
//
// A LINHA QUE NÃO SE CRUZA: os clientes TST são companhias abertas reais, de
// CNPJ público. Aqui não se cria NENHUM fato regulatório, jurídico ou ambiental
// sobre elas — nada de :Evento de pedido_rj, protesto, execução fiscal ou
// embargo, e nenhum sócio inventado (sócio é pessoa física com nome no QSA).
// O que se atribui a elas é quantitativo proprietário (lavoura, volume) e
// vínculo comercial, marcado como ficção. Ver o docstring de sintetico.py.
// =============================================================================


// -----------------------------------------------------------------------------
// BLOCO A — CORREÇÃO: microrregião duplicada
//
// `REG-GO-SUD` ("Sudoeste Goiano", do seed) e `REG-GO-52013` ("Sudoeste de
// Goiás", da malha do IBGE) são a MESMA microrregião — código 52013. O seed
// inventou um id antes de a malha real existir no grafo.
//
// Enquanto forem dois nós, o canal sistêmico não atravessa: CLI001 (em RJ),
// CLI002, CLI004 e CLI007 ficam de um lado e TST004 (Cerradinho, R$ 15,7 mi de
// exposição) do outro, mesmo os dois lados tendo evento de quebra de safra da
// Conab sobre a mesma terra. O vetor de peso 0,75 nunca dispara entre eles.
//
// Sobrevive o nó do IBGE, que tem código, mesorregião e procedência.
// -----------------------------------------------------------------------------

MATCH (antigo:Regiao {id:'REG-GO-SUD'}), (novo:Regiao {id:'REG-GO-52013'})
MATCH (c:Cliente)-[r:OPERA_EM]->(antigo)
MERGE (c)-[n:OPERA_EM]->(novo)
  SET n.remapeado_de = 'REG-GO-SUD', n.remapeado_em = date()
DELETE r
;

MATCH (antigo:Regiao {id:'REG-GO-SUD'}), (novo:Regiao {id:'REG-GO-52013'})
MATCH (i:Imovel)-[r:LOCALIZADO_EM]->(antigo)
MERGE (i)-[:LOCALIZADO_EM]->(novo)
DELETE r
;

MATCH (antigo:Regiao {id:'REG-GO-SUD'}), (novo:Regiao {id:'REG-GO-52013'})
MATCH (e)-[r:SOBRE_REGIAO]->(antigo)
MERGE (e)-[:SOBRE_REGIAO]->(novo)
DELETE r
;

// Só remove depois de ficar sem nenhuma aresta — se sobrou algo, o MATCH não
// casa e o nó fica, que é o comportamento desejado (falha visível, não perda).
MATCH (antigo:Regiao {id:'REG-GO-SUD'})
WHERE NOT (antigo)--()
DELETE antigo
;


// -----------------------------------------------------------------------------
// BLOCO B — SINTÉTICO: recebíveis de CLI006 e CLI007
//
// Eram os dois únicos clientes com exposição ZERO. Sem recebível o score sai
// 1000/A por vacuidade — não porque o cliente é bom, mas porque não há o que
// medir. Nos KPIs da carteira isso vira dois "rating A" falsos, e no ranking de
// priorização eles ocupam o topo da lista de saudáveis.
//
// CLI007 é REVENDA, e é por ela que CLI002 e CLI004 compram (COMPRA_VIA). Uma
// revenda em atraso é exatamente o que o vetor sistêmico de peso 0,65 existe
// para capturar, então os títulos dela entram vencidos.
// -----------------------------------------------------------------------------

MATCH (c:Cliente {id:'CLI006'})
MATCH (s:Safra {id:'SAF-2526'})
UNWIND [
  {id:'SINT-CLI006-01', valor:185000.0, garantia_tipo:'cpr',
   garantia_valor:120000.0, dias:0, emissao:'2026-04-20', venc:'2026-12-16'},
  {id:'SINT-CLI006-02', valor:96000.0, garantia_tipo:'alienacao_fiduciaria',
   garantia_valor:96000.0, dias:0, emissao:'2026-05-11', venc:'2027-01-06'}
] AS t
MERGE (r:Recebivel {id:t.id})
  SET r.valor = t.valor, r.valor_aberto = t.valor, r.status = 'aberto',
      r.garantia_tipo = t.garantia_tipo, r.garantia_valor = t.garantia_valor,
      r.estagio_juridico = 'nenhum', r.dias_atraso = t.dias,
      r.data_emissao = date(t.emissao), r.data_vencimento = date(t.venc),
      r.fonte = 'SINTÉTICO — demo', r.sintetico = true, r.confianca = 0.0,
      r.coletado_em = date(),
      r.base_real = 'dimensionado por 1.400 ha de algodao no Oeste Baiano x R$/ha de insumo biologico'
MERGE (r)-[:DE]->(c)
MERGE (r)-[:REFERENTE_A]->(s)
;

MATCH (c:Cliente {id:'CLI007'})
MATCH (s:Safra {id:'SAF-2526'})
UNWIND [
  {id:'SINT-CLI007-01', valor:640000.0, garantia_tipo:'aval',
   garantia_valor:420000.0, dias:52, emissao:'2025-11-28', venc:'2026-07-22'},
  {id:'SINT-CLI007-02', valor:310000.0, garantia_tipo:'nenhuma',
   garantia_valor:0.0, dias:52, emissao:'2025-11-28', venc:'2026-07-22'}
] AS t
MERGE (r:Recebivel {id:t.id})
  SET r.valor = t.valor, r.valor_aberto = t.valor, r.status = 'vencido',
      r.garantia_tipo = t.garantia_tipo, r.garantia_valor = t.garantia_valor,
      r.estagio_juridico = 'notificado', r.dias_atraso = t.dias,
      r.data_emissao = date(t.emissao), r.data_vencimento = date(t.venc),
      r.fonte = 'SINTÉTICO — demo', r.sintetico = true, r.confianca = 0.0,
      r.coletado_em = date(),
      r.base_real = 'volume de revenda de insumo a produtores do Sudoeste de Goias'
MERGE (r)-[:DE]->(c)
MERGE (r)-[:REFERENTE_A]->(s)
;

// O avalista de CLI007 é o mesmo de CLI002 — as duas pontas são clientes
// fictícios do seed, então o vínculo pode ser nominal sem ressalva.
MATCH (r:Recebivel {id:'SINT-CLI007-01'})
MATCH (a:Avalista {nome:'Agropecuária Cruzeiro Ltda'})
MERGE (r)-[:GARANTIDO_POR]->(a)
;

// exposicao_total, situacao e dias_atraso_max são derivados — o motor lê os três.
MATCH (c:Cliente) WHERE c.id IN ['CLI006','CLI007']
OPTIONAL MATCH (r:Recebivel)-[:DE]->(c)
  WHERE r.status IN ['aberto','vencido','em_acordo']
WITH c, sum(r.valor_aberto) AS exposicao, max(r.dias_atraso) AS atraso
SET c.exposicao_total = exposicao,
    c.dias_atraso_max = atraso,
    c.situacao = CASE WHEN atraso >= 90 THEN 'inadimplente'
                      WHEN atraso > 0   THEN 'atraso'
                      ELSE 'adimplente' END
;


// -----------------------------------------------------------------------------
// BLOCO C — SINTÉTICO: lavoura de TST006 e TST007
//
// Os dois estavam sem :PLANTA e por isso fora do canal sistêmico inteiro — os
// vetores de 0,75 (mesma região e cultura com choque) e 0,40 (mesma cultura)
// não têm por onde passar.
//
// O pipeline os deixou sem cultura por um motivo correto: ele atribui lavoura
// pela PAM do município da SEDE, e a sede das duas é São Paulo capital, que não
// tem um hectare de soja. Mas as duas plantam — longe da sede. A atribuição
// abaixo é sintética justamente porque a fonte pública não liga a empresa à
// lavoura dela.
// -----------------------------------------------------------------------------

UNWIND [
  {cliente:'TST006', cultura:'CUL-SOJA',  hectares:14800},
  {cliente:'TST006', cultura:'CUL-MILHO', hectares:6200},
  {cliente:'TST007', cultura:'CUL-SOJA',  hectares:9100},
  {cliente:'TST007', cultura:'CUL-MILHO', hectares:3400}
] AS t
MATCH (c:Cliente {id:t.cliente}), (cu:Cultura {id:t.cultura})
MERGE (c)-[p:PLANTA]->(cu)
  SET p.hectares = t.hectares,
      p.fonte = 'SINTÉTICO — demo', p.sintetico = true, p.confianca = 0.0,
      p.base_real = 'companhia com lavoura fora do municipio-sede; a PAM do municipio da sede (Sao Paulo) nao sustenta a atribuicao'
;


// -----------------------------------------------------------------------------
// BLOCO D — SINTÉTICO: canal de revenda
//
// O vetor de peso 0,65 ("mesmo canal de revenda") tinha 3 arestas no grafo
// inteiro, então nunca aparecia num dossiê. O vínculo comercial é inventado —
// mas é o vetor que explica contágio sem vínculo societário nenhum, que é
// metade da tese do produto.
//
// Duas revendas no grafo: CLI007 (fictícia, Sudoeste de Goiás) e TST001
// (AgroGalaxy, distribuidora de insumos, em RJ desde 18/09/2024 pela CVM).
// Produtores comprando da revenda que entrou em RJ é o caso da demo.
// -----------------------------------------------------------------------------

UNWIND [
  {cliente:'CLI001', revenda:'CLI007', volume:880000.0},
  {cliente:'CLI009', revenda:'CLI007', volume:240000.0},
  {cliente:'TST002', revenda:'TST001', volume:1950000.0},
  {cliente:'TST003', revenda:'TST001', volume:530000.0},
  {cliente:'TST004', revenda:'TST001', volume:2400000.0}
] AS t
MATCH (c:Cliente {id:t.cliente}), (rev:Cliente {id:t.revenda})
MERGE (c)-[x:COMPRA_VIA]->(rev)
  SET x.volume_safra = t.volume,
      x.fonte = 'SINTÉTICO — demo', x.sintetico = true, x.confianca = 0.0,
      x.base_real = 'vinculo comercial inventado; a revenda e real, a relacao de compra nao'
;


// -----------------------------------------------------------------------------
// BLOCO E — SINTÉTICO: quadro societário dos clientes do seed
//
// CLI004, CLI006, CLI007, CLI009 e CLI010 estavam sem :TEM_SOCIO, e o vetor de
// peso 0,70 (sócio em comum) só tinha dois pares no grafo inteiro.
//
// Isto é permitido aqui e NÃO seria nos TST: estes cinco são empresas fictícias
// do seed, então a pessoa física inventada não descreve ninguém. Nos clientes
// reais o QSA manda, e este arquivo não toca nele.
// -----------------------------------------------------------------------------

UNWIND [
  {id:'SOC-SINT-01', nome:'Marina Duarte Ribeiro (SINTETICO)', doc:'***.000.001-** (ficticio)'},
  {id:'SOC-SINT-02', nome:'Otavio Lemos Andrade (SINTETICO)',  doc:'***.000.002-** (ficticio)'},
  {id:'SOC-SINT-03', nome:'Clara Bittencourt Sa (SINTETICO)',  doc:'***.000.003-** (ficticio)'}
] AS s
MERGE (n:Socio {id:s.id})
  SET n.nome = s.nome, n.documento = s.doc,
      n.fonte = 'SINTÉTICO — demo', n.sintetico = true, n.confianca = 0.0
;

// Dois sócios compartilhados (é o que faz o vetor propagar) e um exclusivo.
UNWIND [
  {cliente:'CLI004', socio:'SOC-SINT-01', participacao:0.45},
  {cliente:'CLI009', socio:'SOC-SINT-01', participacao:0.30},
  {cliente:'CLI010', socio:'SOC-SINT-02', participacao:0.55},
  {cliente:'CLI006', socio:'SOC-SINT-02', participacao:0.40},
  {cliente:'CLI007', socio:'SOC-SINT-03', participacao:1.00}
] AS t
MATCH (c:Cliente {id:t.cliente}), (s:Socio {id:t.socio})
MERGE (c)-[x:TEM_SOCIO]->(s)
  SET x.participacao = t.participacao,
      x.fonte = 'SINTÉTICO — demo', x.sintetico = true, x.confianca = 0.0
;
