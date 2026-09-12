"""Cypher da carga. Um constante por alvo, no mesmo estilo de modules/*/queries.py.

TRÊS REGRAS QUE VALEM PARA TODAS AS QUERIES AQUI:

1. `SET x += l.props` em vez de `SET x.campo = l.campo`. O loader já removeu as
   chaves vazias, então um campo sem fonte pública (OPERA_EM.hectares, por
   exemplo) simplesmente não é escrito — em vez de virar 0 ou '' no grafo e ser
   lido depois como se fosse medição. Ausência visível é melhor que zero falso.

2. Toda aresta e todo nó recebem `fonte`, `coletado_em` e `confianca`. É o que
   permite a um dossiê dizer "sócio em comum, confiança 0,85, fonte QSA" em vez
   de "risco 0,70". Hard Rule #3.

3. MERGE sempre pela chave de negócio, nunca pelo padrão inteiro. Foi o bug
   corrigido na Q1 em 12/09: `MERGE (a {id:$x})-[r]->(b)` tenta recriar `a` e
   bate na constraint de unicidade. Casa-se primeiro, faz-se MERGE só da aresta.
"""

# --------------------------------------------------------------------------
# Constraints adicionais. O 01-schema-e-seed.cypher cria as do seed; estas
# cobrem o que o pipeline introduz e não existia lá.
# --------------------------------------------------------------------------
CONSTRAINTS = [
    "CREATE CONSTRAINT evento_regional_id IF NOT EXISTS "
    "FOR (e:EventoRegional) REQUIRE e.id IS UNIQUE",
    "CREATE INDEX evento_regional_tipo IF NOT EXISTS "
    "FOR (e:EventoRegional) ON (e.tipo)",
    "CREATE INDEX cliente_documento IF NOT EXISTS "
    "FOR (c:Cliente) ON (c.documento)",
    "CREATE INDEX regiao_uf IF NOT EXISTS FOR (r:Regiao) ON (r.uf)",
]

REGIOES = """
UNWIND $linhas AS l
MERGE (r:Regiao {id: l.id})
  SET r += l.props, r.ingerido_em = datetime()
"""

CULTURAS = """
UNWIND $linhas AS l
MERGE (k:Cultura {id: l.id})
  SET k += l.props, k.ingerido_em = datetime()
"""

SAFRAS = """
UNWIND $linhas AS l
MERGE (s:Safra {id: l.id})
  SET s += l.props, s.ingerido_em = datetime()
"""

CLIENTES = """
UNWIND $linhas AS l
MERGE (c:Cliente {id: l.id})
  SET c += l.props, c.ingerido_em = datetime()
"""

# A CVM manda na situação de insolvência, mas só quando ela É de insolvência:
# uma linha histórica de 'FASE OPERACIONAL' não pode apagar um 'EM RECUPERAÇÃO
# JUDICIAL' gravado por outra linha do mesmo CNPJ. Por isso o loader já filtra
# para as linhas com situação preenchida, e aqui a escrita é direta.
SITUACAO_CVM = """
UNWIND $linhas AS l
MATCH (c:Cliente {id: l.cliente})
  SET c += l.props, c.situacao_fonte = 'CVM — cadastro de companhias abertas'
"""

# Atributos que só o ERP teria (atraso, situação, porte, cliente_desde). Roda
# DEPOIS de SITUACAO_CVM; o gerador deixa `situacao` vazia para a AgroGalaxy
# justamente para não sobrescrever a RJ real da CVM com uma derivada de atraso
# inventado — e campo vazio o loader não escreve.
ATRIBUTOS_SINTETICOS = """
UNWIND $linhas AS l
MATCH (c:Cliente {id: l.cliente})
  SET c += l.props, c.sintetico = null, c.atributos_sinteticos = true
"""

# Canal de revenda: vetor sistêmico de peso 0,65 do motor.
COMPRA_VIA = """
UNWIND $linhas AS l
MATCH (c:Cliente {id: l.cliente}), (rev:Cliente {id: l.revenda})
MERGE (c)-[x:COMPRA_VIA]->(rev)
  SET x += l.props
"""

GRUPOS = """
UNWIND $linhas AS l
MERGE (g:GrupoEconomico {id: l.grupo_id})
  SET g.nome = coalesce(l.grupo_nome, g.nome), g += l.props_no
WITH l, g
MATCH (c:Cliente {id: l.cliente})
MERGE (c)-[p:PERTENCE_A]->(g)
  SET p += l.props
"""

SOCIOS = """
UNWIND $linhas AS l
MERGE (s:Socio {id: l.socio_id})
  SET s.nome = l.socio_nome, s += l.props_socio, s.ingerido_em = datetime()
WITH l, s
MATCH (c:Cliente {id: l.cliente})
MERGE (c)-[t:TEM_SOCIO]->(s)
  SET t += l.props_aresta
"""

# Participação vem de contrato (interno) e sobrescreve só esse campo, sem
# mexer no resto da aresta que a QSA montou.
PARTICIPACOES = """
UNWIND $linhas AS l
MATCH (c:Cliente {id: l.cliente})-[t:TEM_SOCIO]->(:Socio {id: l.socio_id})
  SET t.participacao = toFloat(l.participacao),
      t.fonte_participacao = l.fonte
"""

IMOVEIS = """
UNWIND $linhas AS l
MERGE (i:Imovel {id: l.id})
  SET i += l.props, i.ingerido_em = datetime()
WITH l, i
MATCH (c:Cliente {id: l.cliente})
MERGE (c)-[:POSSUI]->(i)
WITH l, i WHERE l.regiao IS NOT NULL
// O imóvel herda a região do PRÓPRIO município, não a do cliente: fazenda em
// microrregião diferente da sede é o caso normal, não a exceção. O de-para
// município→microrregião é resolvido no loader (staging/municipio_regiao.csv),
// não aqui: é join de dados, não de grafo.
MATCH (r:Regiao {id: l.regiao})
MERGE (i)-[:LOCALIZADO_EM]->(r)
"""

OPERA_EM = """
UNWIND $linhas AS l
MATCH (c:Cliente {id: l.cliente}), (r:Regiao {id: l.regiao})
MERGE (c)-[o:OPERA_EM]->(r)
  SET o += l.props
"""

PLANTA = """
UNWIND $linhas AS l
MATCH (c:Cliente {id: l.cliente}), (k:Cultura {id: l.cultura})
MERGE (c)-[p:PLANTA]->(k)
  SET p += l.props
"""

RECEBIVEIS = """
UNWIND $linhas AS l
MERGE (r:Recebivel {id: l.id})
  SET r += l.props, r.ingerido_em = datetime()
WITH l, r
MATCH (c:Cliente {id: l.cliente})
MERGE (r)-[:DE]->(c)
WITH l, r WHERE l.safra IS NOT NULL
MATCH (s:Safra {id: l.safra})
MERGE (r)-[:REFERENTE_A]->(s)
"""

AVALISTAS = """
UNWIND $linhas AS l
MERGE (a:Avalista {id: l.avalista_id})
  SET a.nome = l.avalista_nome, a += l.props_avalista
WITH l, a
MATCH (r:Recebivel {id: l.recebivel})
MERGE (r)-[g:GARANTIDO_POR]->(a)
  SET g += l.props_aresta
"""

# Evento de CLIENTE: a fonte publica CPF/CNPJ, então a atribuição é direta.
EVENTOS_CLIENTE = """
UNWIND $linhas AS l
MERGE (e:Evento {id: l.id})
  SET e += l.props, e.data = date(l.data), e.ingerido_em = datetime()
WITH l, e
MATCH (c:Cliente {id: l.cliente})
MERGE (e)-[:SOBRE]->(c)
"""

# Evento de REGIÃO: rótulo :EventoRegional, separado de :Evento de propósito.
# Misturar os dois faria a Q2 (score) e a Q3 (red flags) contarem um choque
# regional como se fosse fato sobre o cliente — e a matriz de red flags passaria
# a acender a carteira inteira por causa de uma seca. A ligação com o cliente,
# quando o motor quiser, é travessia explícita (ver nota no README).
EVENTOS_REGIAO = """
UNWIND $linhas AS l
MERGE (e:EventoRegional {id: l.id})
  SET e += l.props, e.data = date(l.data), e.ingerido_em = datetime()
WITH l, e
MATCH (r:Regiao {id: l.regiao})
MERGE (e)-[:SOBRE_REGIAO]->(r)
WITH l, e WHERE l.cultura IS NOT NULL
MATCH (k:Cultura {id: l.cultura})
MERGE (e)-[:SOBRE_CULTURA]->(k)
"""

# Conab e INMET publicam por UF, não por microrregião: o evento se liga a TODAS
# as regiões daquela UF. A superestimação é real e está declarada na cobertura.
EVENTOS_UF = """
UNWIND $linhas AS l
MERGE (e:EventoRegional {id: l.id})
  SET e += l.props, e.data = date(l.data),
      e.granularidade = 'uf', e.ingerido_em = datetime()
WITH l, e
MATCH (r:Regiao {uf: l.uf})
MERGE (e)-[:SOBRE_REGIAO]->(r)
WITH l, e WHERE l.cultura IS NOT NULL
MATCH (k:Cultura {id: l.cultura})
MERGE (e)-[:SOBRE_CULTURA]->(k)
"""

# Mesma materialização do fim do seed: exposição por cliente. Roda depois dos
# recebíveis, senão grava zero em todo mundo.
EXPOSICAO = """
MATCH (c:Cliente)
OPTIONAL MATCH (r:Recebivel)-[:DE]->(c)
  WHERE r.status IN ['aberto','vencido','em_acordo']
WITH c, coalesce(sum(r.valor_aberto), 0.0) AS exp
SET c.exposicao_total = exp
RETURN count(c) AS clientes, round(sum(exp)) AS exposicao_total
"""

CONFERENCIA = """
MATCH (n) WITH labels(n)[0] AS rotulo, count(*) AS n
RETURN rotulo, n ORDER BY n DESC
"""

CONFERENCIA_ARESTAS = """
MATCH ()-[r]->() WITH type(r) AS tipo, count(*) AS n
RETURN tipo, n ORDER BY n DESC
"""
