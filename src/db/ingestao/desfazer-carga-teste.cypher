// =====================================================================
// DESFAZER a carga de teste do pipeline de ingestão
//
// Remove SOMENTE o que o pipeline criou com a carteira de companhias
// abertas (TST001..TST008) e os nós de fonte pública que vieram com ela.
// O seed sintético (CLI001..CLI010, EVT001..EVT007, recebíveis, avais,
// estratégias, :EXPOSTO_A e :RECOMENDADA) NÃO é tocado.
//
// Rode no Neo4j Browser, bloco por bloco, na ordem. Confira a contagem de
// cada passo antes de seguir — DETACH DELETE não tem volta.
// =====================================================================


// --- 0. CONFERIR antes de apagar (não apaga nada) --------------------
MATCH (c:Cliente) WHERE c.id STARTS WITH 'TST'
RETURN count(c) AS clientes_teste;

MATCH (s:Socio) WHERE s.fonte STARTS WITH 'Receita Federal'
RETURN count(s) AS socios_do_pipeline;

MATCH (e:EventoRegional) RETURN count(e) AS eventos_regionais;

MATCH (e:Evento) WHERE e.id =~ '(CVM|QSA|IBAMA|PGFN)-.*'
RETURN count(e) AS eventos_de_fonte_publica;


// --- 1. Clientes de teste e suas arestas -----------------------------
MATCH (c:Cliente) WHERE c.id STARTS WITH 'TST' DETACH DELETE c;

// --- 2. Imóveis que vieram do IBAMA ----------------------------------
MATCH (i:Imovel) WHERE i.id STARTS WITH 'IBAMA-TAD-' DETACH DELETE i;

// --- 3. Eventos de fonte pública (sobre cliente) ---------------------
MATCH (e:Evento) WHERE e.id =~ '(CVM|QSA|IBAMA|PGFN)-.*' DETACH DELETE e;

// --- 4. Eventos regionais — o rótulo é exclusivo do pipeline ---------
MATCH (e:EventoRegional) DETACH DELETE e;

// --- 5. Sócios órfãos ------------------------------------------------
// Só os que ficaram sem nenhum cliente. Os 4 sócios do seed (SOC001..004)
// continuam ligados aos CLI*, então esta query não os alcança.
MATCH (s:Socio) WHERE NOT (s)<-[:TEM_SOCIO]-() DETACH DELETE s;

// --- 6. Regiões órfãs ------------------------------------------------
// As do seed (REG-GO-SUD, REG-MT-MED, REG-BA-OES, REG-MS-SUL) seguem
// ligadas aos CLI* por OPERA_EM. As do IBGE (REG-GO-52013 etc.) ficam
// sem nenhuma aresta depois dos passos acima.
MATCH (r:Regiao) WHERE NOT (r)--() DETACH DELETE r;

// --- 7. Safras que o pipeline criou e o seed não tinha ---------------
// O seed tem SAF-2526 e SAF-2425. As outras vieram da série da Conab.
MATCH (s:Safra) WHERE NOT (s)--() AND NOT s.id IN ['SAF-2526','SAF-2425']
DETACH DELETE s;

// --- 8. Limpar as propriedades que a ingestão acrescentou ao seed -----
// CUL-SOJA/MILHO/ALGODAO e SAF-2526/2425 têm os mesmos ids do seed, então
// o MERGE adicionou `fonte`, `produto_conab`, `coletado_em`, `confianca` e
// `ingerido_em` NELES. Os valores originais (nome, ciclo_dias, status) não
// foram alterados, mas estas propriedades extras não existiam.
MATCH (k:Cultura)
REMOVE k.fonte, k.produto_conab, k.coletado_em, k.confianca, k.ingerido_em;

MATCH (s:Safra)
REMOVE s.fonte, s.coletado_em, s.confianca, s.ingerido_em, s.ano_agricola;

// --- 9. CONFERIR o resultado ----------------------------------------
// Esperado: 10 :Cliente, 4 :Socio, 4 :Regiao, 3 :Imovel, 7 :Evento,
// 0 :EventoRegional, 10 :Recebivel, 3 :Avalista, 2 :GrupoEconomico,
// 3 :Cultura, 2 :Safra, 8 :EstrategiaRecuperacao
MATCH (n) WITH labels(n)[0] AS rotulo, count(*) AS n
RETURN rotulo, n ORDER BY n DESC;

// A exposição materializada precisa ser recalculada: o passo 1 removeu
// clientes, e o valor em :Cliente.exposicao_total é materializado.
MATCH (c:Cliente)
OPTIONAL MATCH (r:Recebivel)-[:DE]->(c)
  WHERE r.status IN ['aberto','vencido','em_acordo']
WITH c, coalesce(sum(r.valor_aberto), 0.0) AS exp
SET c.exposicao_total = exp
RETURN count(c) AS clientes, round(sum(exp)) AS exposicao_total;
