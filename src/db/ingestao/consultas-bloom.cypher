// =====================================================================
// CONSULTAS PARA O BLOOM — ver a ingestão de fontes públicas
//
// Cole uma por vez na barra de busca do Bloom (ela aceita Cypher direto).
// Conectar em: neo4j+s://0f36204d.databases.neo4j.io
//   user     0f36204d
//   database 0f36204d      <- NÃO é 'neo4j' nesta instância
//
// Se :EventoRegional não aparecer na paleta, a perspectiva está com o schema
// em cache: Perspective -> ⋮ -> Refresh, ou crie uma nova.
// =====================================================================


// ---------------------------------------------------------------------
// 1. TUDO o que o pipeline carregou, de uma vez
// Os 8 clientes reais com todo o entorno público: sócios do QSA, região do
// IBGE, imóvel embargado do IBAMA, eventos da CVM/QSA/IBAMA e os eventos
// regionais da Conab/PAM/DataJud que alcançam a região deles.
// ---------------------------------------------------------------------
MATCH (c:Cliente) WHERE c.id STARTS WITH 'TST'
OPTIONAL MATCH (c)-[ts:TEM_SOCIO]->(s:Socio)
OPTIONAL MATCH (c)-[oe:OPERA_EM]->(r:Regiao)
OPTIONAL MATCH (c)-[po:POSSUI]->(i:Imovel)
OPTIONAL MATCH (ev:Evento)-[sb:SOBRE]->(c)
OPTIONAL MATCH (er:EventoRegional)-[sr:SOBRE_REGIAO]->(r)
RETURN c, ts, s, oe, r, po, i, ev, sb, er, sr;


// ---------------------------------------------------------------------
// 2. O cenário da demo, real: a AgroGalaxy em RJ
// TST001 é revenda de insumos em Goiânia, em recuperação judicial desde
// 18/09/2024 segundo o cadastro da CVM. É o CLI001 do seed, verdadeiro.
// ---------------------------------------------------------------------
MATCH (c:Cliente {id:'TST001'})
OPTIONAL MATCH (c)-[ts:TEM_SOCIO]->(s:Socio)
OPTIONAL MATCH (ev:Evento)-[sb:SOBRE]->(c)
OPTIONAL MATCH (c)-[oe:OPERA_EM]->(r:Regiao)<-[sr:SOBRE_REGIAO]-(er:EventoRegional)
RETURN c, ts, s, ev, sb, oe, r, sr, er;


// ---------------------------------------------------------------------
// 3. Canal sistêmico medido, sem evento plantado
// Quais clientes estão em microrregião com choque confirmado por fonte.
// `granularidade` distingue o que foi medido por microrregião (PAM, DataJud)
// do que veio por UF (Conab, INMET) e portanto superestima a abrangência.
// ---------------------------------------------------------------------
MATCH (c:Cliente)-[oe:OPERA_EM]->(r:Regiao)<-[sr:SOBRE_REGIAO]-(er:EventoRegional)
RETURN c, oe, r, sr, er;


// ---------------------------------------------------------------------
// 4. Sócios em comum entre clientes reais — o vetor de peso 0,70
// Se esta consulta voltar vazia, é o resultado correto: são 8 companhias
// abertas sem sócios cruzados. Num recorte de carteira real da Krilltech é
// aqui que os vínculos apareceriam.
// Atenção: a identidade do sócio entre duas empresas é INFERIDA (CPF vem
// mascarado da Receita). Veja x.confianca = 0.85 na aresta.
// ---------------------------------------------------------------------
MATCH (a:Cliente)-[x:TEM_SOCIO]->(s:Socio)<-[y:TEM_SOCIO]-(b:Cliente)
WHERE a.id < b.id
RETURN a, x, s, y, b;


// ---------------------------------------------------------------------
// 5. Red flags reais, por fonte
// Cada bandeira com a procedência. É a Hard Rule #3: nunca mostrar risco
// sem dizer por qual vínculo e de qual fonte ele chegou.
// ---------------------------------------------------------------------
MATCH (e:Evento)-[sb:SOBRE]->(c:Cliente)
WHERE e.id =~ '(CVM|QSA|IBAMA|PGFN)-.*'
RETURN c, sb, e;


// ---------------------------------------------------------------------
// 6. Imóveis embargados pelo IBAMA, com a região
// ---------------------------------------------------------------------
MATCH (c:Cliente)-[po:POSSUI]->(i:Imovel)
WHERE i.id STARTS WITH 'IBAMA-'
OPTIONAL MATCH (i)-[le:LOCALIZADO_EM]->(r:Regiao)
RETURN c, po, i, le, r;


// ---------------------------------------------------------------------
// 7. Seed sintético vs ingestão real, lado a lado
// Os dois universos no mesmo grafo. CLI* é sintético e tem recebíveis;
// TST* é real e não tem — porque recebível privado não tem fonte pública.
// ---------------------------------------------------------------------
MATCH (c:Cliente)
OPTIONAL MATCH (rec:Recebivel)-[de:DE]->(c)
OPTIONAL MATCH (c)-[oe:OPERA_EM]->(r:Regiao)
RETURN c, rec, de, oe, r;


// ---------------------------------------------------------------------
// 8. Contagem por fonte — a tabela, não o grafo
// Útil para conferir a ingestão sem depender do layout visual.
// ---------------------------------------------------------------------
MATCH (n)
WHERE n.fonte IS NOT NULL
RETURN n.fonte AS fonte, labels(n)[0] AS rotulo, count(*) AS n
ORDER BY fonte, n DESC;
