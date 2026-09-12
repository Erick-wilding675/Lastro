"""CNJ / DataJud — API pública de metadados processuais.

LEIA A LIMITAÇÃO PRIMEIRO, porque ela muda o que o Lastro pode prometer.

A tese do produto é: "quando o cliente pede RJ, começa um stay period de 180
dias e não há mais o que fazer; todo o valor está em saber antes". O evento
`pedido_rj` é o gatilho da demo inteira (EVT001 -> CLI001).

O DataJud público tem esse dado — e NÃO diz de quem é. Resposta real da API
(api_publica_tjgo, classe 129, verificado em 12/09/2026):

  {"id":"TJGO_G1_56550054920268090125","tribunal":"TJGO","grau":"G1",
   "numeroProcesso":"56550054920268090125","dataAjuizamento":"20260716134720",
   "nivelSigilo":0,
   "orgaoJulgador":{"codigo":11598,"nome":"Vara Judicial",
                    "codigoMunicipioIBGE":5217203},
   "classe":{"codigo":129,"nome":"Recuperação Judicial"},
   "movimentos":[...], "assuntos":[{"codigo":9559,"nome":"Classificação de créditos"}]}

Não há `partes`. Não há nome, não há CNPJ. A Portaria CNJ 160/2020 expõe
metadados e protege dados das partes — por desenho, não por falha.

CONSEQUÊNCIA PRÁTICA — COM UMA CORREÇÃO IMPORTANTE:
  Por ESTA fonte, `(:Evento{tipo:'pedido_rj'})-[:SOBRE]->(:Cliente)` não sai.
  Mas NÃO é verdade que nenhuma fonte pública o entregue: o cadastro de
  companhias abertas da CVM publica `SIT_EMISSOR='EM RECUPERAÇÃO JUDICIAL OU
  EQUIVALENTE'` com CNPJ e data, em CSV aberto — ver `cvm_cias.py`. A CVM cobre
  ~755 companhias registradas, o que exclui produtor rural PF e Ltda fechada,
  mas inclui a cauda de maior exposição individual (S.A. aberta, emissor de CRA).
  Para o RESTO da carteira o elo continua vindo de fora: (a) DJE/Diário Oficial,
  que publica o nome no edital mas é PDF por comarca, sem API; (b) API comercial
  paga (Escavador, Jusbrasil, Digesto); (c) a própria Krilltech, citada como
  credora e intimada no processo.

O QUE ESTA FONTE ENTREGA, e não é pouco: pressão judicial POR MICRORREGIÃO,
medida contra o histórico da própria microrregião. "A microrregião do seu
cliente teve 2,3x mais pedidos de RJ neste ano do que a média dos 4 anteriores"
é sinal sistêmico legítimo e que bureau de crédito não dá. Entra no grafo como
`:EventoRegional`, nunca como fato sobre o cliente.

---
POR QUE ESTE MÓDULO CONTA EM VEZ DE BAIXAR. A primeira versão paginava os
processos e contava em Python. Três problemas, todos observados ao vivo:

  1. Não existe campo de desempate ordenável. `id` e `numeroProcesso` são `text`
     ("Fielddata is disabled on [id]") e `_id` é barrado por configuração de
     cluster, então `search_after` com chave única é impossível. A paginação
     tinha de avançar pelo piso de `dataAjuizamento` e deduplicar.
  2. Quando 1.000 processos dividem o mesmo segundo — acontece em carga migrada
     em lote, visto no TJBA — a paginação empaca.
  3. Com teto de segurança de 50 páginas, RS e SP pararam em 49.945 e 49.950
     processos de execução fiscal: TRUNCADOS, em ordem cronológica, o que
     enviesa para baixo a contagem de qualquer microrregião cujos processos
     fiquem depois do corte. Contagem truncada silenciosamente é exatamente o
     tipo de degradação que não se aceita aqui.

A solução é não trazer processo nenhum: `size: 0` + `track_total_hits: true` +
agregação por `orgaoJulgador.codigoMunicipioIBGE`, filtrando já na query pelos
municípios da carteira. Uma requisição por tribunal e classe devolve a contagem
EXATA (`relation: 'eq'`) por município e por janela. Sem paginação, sem teto,
sem baixar 95 mil processos para descartar 95 mil.
"""
from collections import defaultdict
from datetime import date, timedelta

import httpx

from ingestao import config, http, staging
from ingestao.fontes.base import Cobertura, Fonte

API = "https://api-publica.datajud.cnj.jus.br/api_publica_{alias}/_search"
BRUTO = config.RAW / "datajud"

# Códigos verificados ao vivo contra o TJGO (12/09/2026): 129 = Recuperação
# Judicial, 1116 = Execução Fiscal. Outras classes de insolvência existem na
# Tabela Processual Unificada do CNJ, mas `classe.nome` não é campo pesquisável
# na API — então o código não se descobre por busca textual, tem de ser lido na
# tabela do CNJ e somado aqui.
#
# Agora que a contagem é por agregação, AS DUAS classes usam o mesmo método
# (desvio contra o histórico da própria microrregião). Na versão paginada a
# execução fiscal era forçada a uma régua de densidade porque seu volume não
# caberia na paginação — essa restrição deixou de existir.
CLASSES = {
    129: {"tipo": "pressao_rj_regional", "nome": "Recuperação Judicial",
          "severidade_min": 0.30, "severidade_max": 0.85},
    1116: {"tipo": "pressao_fiscal_regional", "nome": "Execução Fiscal",
           "severidade_min": 0.15, "severidade_max": 0.50},
}

JANELA_DIAS = 365
ANOS_BASELINE = 4

# Razão janela/baseline em que a severidade satura. 1,0 = igual à média
# histórica; 3,0 = o triplo do normal. Acima disso não sobe mais, porque o que
# importa já foi dito.
RAZAO_SATURACAO = 3.0


def _alias(uf: str) -> str:
    """UF -> alias do tribunal estadual. Só justiça estadual: RJ de produtor
    rural corre em vara cível/empresarial estadual, não em federal."""
    return f"tj{uf.lower()}"


def _carimbo(dias_atras: int) -> str:
    """`dataAjuizamento` é um LONG de 14 dígitos (20260716134720), não uma data.

    Um piso de 8 dígitos ('20250912') compara números e casa 19870616000000
    também — ou seja, não filtra nada e devolve a série inteira em silêncio. Foi
    um bug real da primeira versão. O piso tem de ter os 14 dígitos.
    """
    return (date.today() - timedelta(days=dias_atras)).strftime("%Y%m%d") + "000000"


def _consultar(alias: str, classe: int, municipios: list[int]) -> dict:
    """Uma requisição: contagem exata por município, nas janelas e por ano.

    As duas agregações servem a propósitos diferentes e ambas são necessárias:

    `janelas` dá o número que vai para a severidade — janela de 365 dias contra
    os 4 anos anteriores, em datas exatas.

    `por_ano` existe para DESCONFIAR de `janelas`. A carga do DataJud é feita
    pelos tribunais e é irregular por classe e por vara. Exemplo real (TJSP,
    classe 129, município 3550308): 2019:1 · 2022:13 · 2023:6 · 2024:0 ·
    2025:44 · 2026:118. Uma vara de recuperação judicial em São Paulo não teve
    ZERO pedidos em 2024 — aquele ano simplesmente não foi alimentado. Sem esse
    histograma, o pipeline leria "34x acima da média" e reportaria um surto que
    não existe. Com ele, detecta o ano vazio e se recusa a medir.
    """
    piso = _carimbo(JANELA_DIAS * (1 + ANOS_BASELINE))
    # Teto em 'hoje': a base tem `dataAjuizamento` corrompido, com anos 2206,
    # 4201 e 8007 (verificado nas agregações do TJSP e do TJRS). Sem o teto, um
    # processo datado de 2206 entra na janela dos últimos 365 dias.
    teto = _carimbo(0)
    payload = {
        "size": 0,
        # Sem isso o ES devolve {'value': 10000, 'relation': 'gte'} e a contagem
        # vira um teto, não um número.
        "track_total_hits": True,
        "query": {"bool": {"must": [
            {"term": {"classe.codigo": classe}},
            {"terms": {"orgaoJulgador.codigoMunicipioIBGE": municipios}},
            {"range": {"dataAjuizamento": {"gte": piso, "lte": teto}}},
        ]}},
        "aggs": {"por_municipio": {
            "terms": {"field": "orgaoJulgador.codigoMunicipioIBGE",
                      "size": max(10, len(municipios) * 2)},
            "aggs": {
                "janelas": {"range": {
                    "field": "dataAjuizamento",
                    "ranges": [
                        {"key": "baseline", "from": float(piso),
                         "to": float(_carimbo(JANELA_DIAS))},
                        {"key": "janela", "from": float(_carimbo(JANELA_DIAS)),
                         "to": float(teto)},
                    ]}},
                # interval 1e10 = um ano, porque dataAjuizamento é AAAAMMDDHHMMSS
                # como inteiro: o ano ocupa as 4 casas mais significativas.
                "por_ano": {"histogram": {"field": "dataAjuizamento",
                                          "interval": 10_000_000_000}},
            }}},
    }
    return http.json_post(API.format(alias=alias), payload,
                          {"Authorization": f"APIKey {config.DATAJUD_APIKEY}"})


def extract() -> None:
    import json
    from ingestao.fontes.ibge_regioes import _codigos

    carteira = staging.carregar_carteira()
    BRUTO.mkdir(parents=True, exist_ok=True)

    # UF por código de município: o tribunal vem da UF, e os municípios filtram
    # a query. Os dois primeiros dígitos do código do IBGE são a UF.
    UF_POR_CODIGO = {
        "52": "GO", "51": "MT", "50": "MS", "29": "BA", "43": "RS",
        "35": "SP", "41": "PR", "42": "SC", "31": "MG", "17": "TO",
        "21": "MA", "22": "PI", "53": "DF", "32": "ES", "33": "RJ",
        "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA",
        "16": "AP", "23": "CE", "24": "RN", "25": "PB", "26": "PE",
        "27": "AL", "28": "SE",
    }
    por_uf: dict[str, list[int]] = defaultdict(list)
    for codigo in sorted(_codigos(carteira)):
        uf = UF_POR_CODIGO.get(codigo[:2])
        if uf:
            por_uf[uf].append(int(codigo))
    if not por_uf:
        raise SystemExit(
            "Nenhum municipio resolvido — rode 'qsa' e 'ibge_regioes' antes.\n"
            "O DataJud e consultado por tribunal (da UF) e filtrado por\n"
            "municipio, entao sem o codigo do IBGE nao ha query a fazer."
        )

    for uf, municipios in sorted(por_uf.items()):
        for classe, cfg in CLASSES.items():
            destino = BRUTO / f"{_alias(uf)}-{classe}.json"
            if destino.exists() and destino.stat().st_size > 0:
                print(f"  cache: {destino.name}")
                continue
            try:
                resposta = _consultar(_alias(uf), classe, municipios)
            except httpx.HTTPStatusError as e:
                print(f"  {uf} classe {classe}: HTTP {e.response.status_code} — "
                      "alias do tribunal pode nao existir, ou a query foi recusada")
                continue
            total = resposta.get("hits", {}).get("total", {})
            if total.get("relation") != "eq":
                # Defesa contra regressão silenciosa: se um dia o servidor
                # ignorar track_total_hits, a contagem volta a ser um teto e
                # tudo o que se calcula a partir dela fica errado para baixo.
                print(f"  AVISO: {uf} classe {classe} devolveu total "
                      f"{total} — contagem pode estar limitada")
            destino.write_text(json.dumps(resposta, ensure_ascii=False),
                               encoding="utf-8")
            print(f"  ok: {uf} {cfg['nome']} — {total.get('value')} processo(s) "
                  f"em {len(municipios)} municipio(s) da carteira, "
                  f"{1 + ANOS_BASELINE} ano(s)")


def transform() -> None:
    import json
    municipio_regiao = {r["codigo_municipio_ibge"]: r["regiao"]
                        for r in staging.ler("municipio_regiao")}
    if not municipio_regiao:
        print("  AVISO: staging/municipio_regiao.csv ausente — rode "
              "ibge_regioes antes; sem ele nao da para situar o processo")
        return

    # (regiao, classe) -> {'janela': n, 'baseline': n}
    contagem: dict[tuple[str, int], dict[str, int]] = defaultdict(
        lambda: {"janela": 0, "baseline": 0})
    # (regiao, classe) -> {ano: n}, para checar buraco na carga do tribunal
    por_ano: dict[tuple[str, int], dict[int, int]] = defaultdict(
        lambda: defaultdict(int))

    for arquivo in sorted(BRUTO.glob("*.json")):
        classe = int(arquivo.stem.split("-")[-1])
        if classe not in CLASSES:
            continue
        dados = json.loads(arquivo.read_text(encoding="utf-8"))
        buckets = (dados.get("aggregations", {})
                        .get("por_municipio", {}).get("buckets", []))
        for b in buckets:
            regiao = municipio_regiao.get(str(b.get("key")))
            if not regiao:
                continue
            for janela in b.get("janelas", {}).get("buckets", []):
                chave = janela.get("key")
                if chave in ("janela", "baseline"):
                    contagem[(regiao, classe)][chave] += janela.get("doc_count", 0)
            for ano in b.get("por_ano", {}).get("buckets", []):
                rotulo = int(str(int(ano.get("key", 0)))[:4] or 0)
                if 2000 <= rotulo <= date.today().year:
                    por_ano[(regiao, classe)][rotulo] += ano.get("doc_count", 0)

    eventos, analises = [], []
    hoje = date.today().isoformat()
    for (regiao, classe), n in sorted(contagem.items()):
        cfg = CLASSES[classe]
        if n["janela"] == 0:
            continue
        media = n["baseline"] / ANOS_BASELINE

        # Anos do baseline que o tribunal deixou vazios. Um ano em branco no
        # meio de uma série com movimento não é "não houve processo": é carga
        # não feita. Tratá-lo como zero real divide a média e inventa surto.
        atual = date.today().year
        anos_esperados = range(atual - ANOS_BASELINE, atual)
        serie = por_ano.get((regiao, classe), {})
        vazios = [a for a in anos_esperados if serie.get(a, 0) == 0]
        intermitente = bool(vazios) and any(serie.get(a, 0) > 0
                                           for a in anos_esperados)

        def _registrar(motivo: str, razao=None, severidade=None, emitiu=False):
            analises.append({
                "regiao": regiao, "classe": classe, "classe_nome": cfg["nome"],
                "na_janela": n["janela"], "no_baseline": n["baseline"],
                "anos_baseline": ANOS_BASELINE,
                "media_anual": round(media, 2) if media else "",
                "anos_vazios": ",".join(str(a) for a in vazios),
                "razao": round(razao, 2) if razao else "",
                "severidade": severidade if severidade is not None else "",
                "virou_evento": "true" if emitiu else "false",
                "motivo": motivo,
                "fonte": "CNJ/DataJud — API pública",
                "coletado_em": hoje, "confianca": 1.0,
            })

        if not media:
            # Sem histórico não há desvio a medir. "Não houve pressão anormal" e
            # "não havia com o que comparar" são conclusões diferentes.
            _registrar(f"sem processo dessa classe nos {ANOS_BASELINE} anos "
                       "anteriores — nao ha baseline para medir desvio")
            continue
        if intermitente:
            _registrar(
                f"carga do tribunal intermitente: ano(s) "
                f"{', '.join(str(a) for a in vazios)} sem nenhum processo desta "
                f"classe, enquanto outros anos tem movimento. A razao seria "
                f"artefato de alimentacao da base, nao surto real")
            continue

        razao = n["janela"] / media
        escala = max(0.0, min(1.0, (razao - 1.0) / (RAZAO_SATURACAO - 1.0)))
        severidade = round(cfg["severidade_min"]
                           + (cfg["severidade_max"] - cfg["severidade_min"]) * escala, 2)
        _registrar("", razao=razao, severidade=severidade, emitiu=True)
        eventos.append({
            # Mês no id para que o MERGE atualize o evento do mês corrente em
            # vez de acumular um nó por execução do pipeline.
            "id": f"DATAJUD-{regiao}-{cfg['tipo']}-{hoje[:7]}",
            "regiao": regiao,
            "tipo": cfg["tipo"],
            "data": hoje,
            "fonte": "CNJ/DataJud — API pública",
            "severidade": severidade,
            "descricao": (
                f"{cfg['nome']} em varas da microrregiao: {n['janela']} nos "
                f"ultimos {JANELA_DIAS} dias contra media de {media:.1f}/ano nos "
                f"{ANOS_BASELINE} anteriores ({razao:.1f}x). NAO atribuivel a "
                f"cliente — o DataJud publico nao expoe as partes (Portaria CNJ "
                f"160/2020)."),
            "quantidade": n["janela"],
            "razao_historica": round(razao, 2),
            "janela_dias": JANELA_DIAS,
            "coletado_em": hoje,
            # Confiança 1,0 no FATO: a contagem é exata (track_total_hits) e os
            # processos existem. A descrição carrega o aviso de não-atribuição.
            "confianca": 1.0,
        })

    print(f"  {len(eventos)} evento(s) regional(is) em {len(analises)} "
          "serie(s) microrregiao x classe")
    staging.escrever("eventos_datajud", [
        "id", "regiao", "tipo", "data", "fonte", "severidade", "descricao",
        "quantidade", "razao_historica", "janela_dias"], eventos)
    staging.escrever("analise_datajud", [
        "regiao", "classe", "classe_nome", "na_janela", "no_baseline",
        "anos_baseline", "media_anual", "anos_vazios", "razao", "severidade",
        "virou_evento", "motivo"], analises)


FONTE = Fonte(
    id="datajud",
    nome="CNJ/DataJud — API pública de metadados processuais",
    url="https://api-publica.datajud.cnj.jus.br/",
    orgao="Conselho Nacional de Justiça",
    periodicidade="diária (carga dos tribunais)",
    extract=extract,
    transform=transform,
    cobertura=[
        Cobertura(":Evento{tipo:'pedido_rj'} + SOBRE Cliente", "bloqueado", 0.0,
                  "O DataJud publico NAO expoe as partes (Portaria CNJ "
                  "160/2020): ha 1.291 pedidos de RJ no TJGO e nenhum e "
                  "atribuivel a um CNPJ por esta via. Para companhia registrada "
                  "na CVM o elo existe em outra fonte (ver cvm_cias.py); para "
                  "produtor PF e Ltda fechada, so DJE, API paga ou a intimacao "
                  "recebida como credora."),
        Cobertura(":EventoRegional{tipo:'pressao_rj_regional'}", "real", 1.0,
                  "Contagem EXATA (track_total_hits) de pedidos de RJ por "
                  "microrregiao, na janela de 365 dias, contra a media dos 4 "
                  "anos anteriores da MESMA microrregiao. Novo — nao existia no "
                  "seed."),
        Cobertura(":EventoRegional{tipo:'pressao_fiscal_regional'}", "real", 1.0,
                  "Idem para execucao fiscal (classe 1116)."),
        Cobertura("Deteccao de carga intermitente do tribunal", "real", 1.0,
                  "ACHADO NA INGESTAO: TJSP classe 129 no municipio 3550308 tem "
                  "2019:1 2022:13 2023:6 2024:0 2025:44 2026:118 — anos ZERADOS "
                  "no meio da serie. Uma vara de RJ em Sao Paulo nao teve zero "
                  "pedidos em 2024; o ano nao foi alimentado. Sem checar isso o "
                  "pipeline reportava '34x acima da media'. Agora detecta o ano "
                  "vazio e SE RECUSA a medir, gravando o motivo."),
        Cobertura("dataAjuizamento corrompido na origem", "real", 1.0,
                  "A base tem processos datados de 2206, 4201 e 8007 (visto em "
                  "TJSP e TJRS). A query passou a ter teto em 'hoje', senao um "
                  "processo de 2206 cai na janela dos ultimos 365 dias."),
        Cobertura("Contagem exata em UF de alto volume", "real", 1.0,
                  "RESOLVIDO: a versao paginada truncava em ~50 mil processos "
                  "(RS e SP pararam em 49.945 e 49.950, em ordem cronologica, "
                  "enviesando microrregiao para baixo). Agora conta por "
                  "agregacao com size:0 — sem paginacao e sem teto."),
        Cobertura("Classes de falencia / rec. extrajudicial", "parcial", 0.0,
                  "classe.nome nao e campo pesquisavel na API, entao nao da "
                  "para descobrir o codigo por busca textual. Tem de sair da "
                  "Tabela Processual Unificada do CNJ e ser somado a CLASSES."),
        Cobertura(":Evento{tipo:'protesto'} de duplicata", "bloqueado", 0.0,
                  "Protesto nao esta no DataJud — e ato de cartorio, nao "
                  "processo. A CENPROT tem consulta publica por documento, mas "
                  "com captcha e sem API. Protesto de CDA fiscal, esse sim, sai "
                  "da PGFN (ver pgfn_dau.py)."),
    ],
)
