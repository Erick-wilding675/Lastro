"""IBGE — malha territorial. Define o que `:Regiao` é, de verdade.

API de localidades, sem chave, sem limite prático:
  https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{codigo}

O seed inventava regiões com nomes quase certos ('Sudoeste Goiano', 'Médio-Norte
Mato-grossense'). O recorte oficial do IBGE para Rio Verde/GO é:
  microrregião  52013  Sudoeste de Goiás
  mesorregião    5205  Sul Goiano
  região imediata 520010 Rio Verde

POR QUE A MICRORREGIÃO É O RECORTE CERTO PARA O CANAL SISTÊMICO. A aresta
`OPERA_EM` existe para responder "estes dois produtores sofrem a mesma seca?".
Mesorregião é grande demais (o Sul Goiano atravessa regimes de chuva
diferentes); município é pequeno demais (vizinho do outro lado da linha divisória
sofre a mesma estiagem). A microrregião é a unidade em que o choque climático é
aproximadamente homogêneo — e é a que o IBGE usa para agregar a PAM.

NOTA SOBRE NOMENCLATURA: o IBGE substituiu oficialmente micro/mesorregião por
'região imediata'/'região intermediária' em 2017, mas manteve as duas na API e
a PAM continua publicada por microrregião. Este módulo grava as duas chaves
para não amarrar o grafo a uma escolha que pode mudar.
"""
from ingestao import config, http, staging
from ingestao.fontes.base import Cobertura, Fonte

API = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{codigo}"
BRUTO = config.RAW / "ibge"


def _codigos(carteira: list[dict]) -> set[str]:
    """Códigos de município da carteira, completados pelo que a QSA resolveu.

    A carteira costuma vir do ERP com UF e nome de município, sem o código do
    IBGE. A Receita devolve o código no cadastro do CNPJ, então quem rodou `qsa`
    antes já o tem em staging/clientes.csv — exigir que a pessoa o digitasse à
    mão seria pedir trabalho que o pipeline já fez.
    """
    codigos = {(c.get("codigo_municipio_ibge") or "").strip() for c in carteira}
    for c in staging.ler("clientes"):
        codigos.add((c.get("codigo_municipio_ibge") or "").strip())
    return codigos - {""}


def extract() -> None:
    import json
    carteira = staging.carregar_carteira()
    BRUTO.mkdir(parents=True, exist_ok=True)
    codigos = sorted(_codigos(carteira))
    if not codigos:
        raise SystemExit(
            "Nenhum codigo_municipio_ibge disponivel.\n"
            "Sem ele nao da para resolver a microrregiao — e a microrregiao e o\n"
            "recorte do canal sistemico do motor. Preencha a coluna na carteira,\n"
            "ou rode 'qsa' antes: a Receita devolve o codigo e este modulo o le\n"
            "de staging/clientes.csv automaticamente."
        )
    for codigo in codigos:
        destino = BRUTO / f"municipio-{codigo}.json"
        if destino.exists() and destino.stat().st_size > 0:
            continue
        dados = http.json_get(API.format(codigo=codigo))
        destino.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
        print(f"  ok: {codigo} {dados.get('nome')} -> "
              f"{dados['microrregiao']['nome']}")


def transform() -> None:
    import json
    carteira = staging.carregar_carteira()
    regioes: dict[str, dict] = {}
    opera_em, municipios = [], {}

    for arquivo in sorted(BRUTO.glob("municipio-*.json")):
        d = json.loads(arquivo.read_text(encoding="utf-8"))
        micro = d["microrregiao"]
        meso = micro["mesorregiao"]
        uf = meso["UF"]["sigla"]
        rid = f"REG-{uf}-{micro['id']}"
        regioes[rid] = {
            "id": rid,
            "nome": micro["nome"],
            "uf": uf,
            "codigo_microrregiao": micro["id"],
            "mesorregiao": meso["nome"],
            "codigo_mesorregiao": meso["id"],
            "regiao_imediata": (d.get("regiao-imediata") or {}).get("nome", ""),
            "fonte": "IBGE — malha territorial (localidades)",
            "coletado_em": staging.hoje(),
            "confianca": 1.0,
        }
        municipios[str(d["id"])] = rid

    # Município por cliente: a carteira manda, e o que ela não disser vem do
    # cadastro da Receita resolvido por `qsa`.
    da_qsa = {c["id"]: (c.get("codigo_municipio_ibge") or "").strip()
              for c in staging.ler("clientes") if c.get("id")}
    for c in carteira:
        codigo = ((c.get("codigo_municipio_ibge") or "").strip()
                  or da_qsa.get(c["id"], ""))
        rid = municipios.get(codigo)
        if not rid:
            continue
        opera_em.append({
            "cliente": c["id"],
            "regiao": rid,
            # hectares NAO vem do IBGE — é área do cliente, dado de cadastro
            # ou do CAR. Fica vazio para o loader não gravar número inventado.
            "hectares": "",
            "fonte": "IBGE — malha territorial (localidades)",
            "coletado_em": staging.hoje(),
            "confianca": 1.0,
        })

    staging.escrever("regioes", [
        "id", "nome", "uf", "codigo_microrregiao", "mesorregiao",
        "codigo_mesorregiao", "regiao_imediata"], regioes.values())
    staging.escrever("opera_em", ["cliente", "regiao", "hectares"], opera_em)
    staging.escrever("municipio_regiao", ["codigo_municipio_ibge", "regiao"], [
        {"codigo_municipio_ibge": k, "regiao": v,
         "fonte": "IBGE — malha territorial (localidades)",
         "coletado_em": staging.hoje(), "confianca": 1.0}
        for k, v in sorted(municipios.items())])


FONTE = Fonte(
    id="ibge_regioes",
    nome="IBGE — malha territorial (micro e mesorregião)",
    url="https://servicodados.ibge.gov.br/api/v1/localidades/",
    orgao="IBGE",
    periodicidade="estável (revisão censitária)",
    extract=extract,
    transform=transform,
    cobertura=[
        Cobertura(":Regiao (id, nome, uf, codigos)", "real", 1.0,
                  "Recorte oficial. Substitui os nomes aproximados do seed "
                  "('Sudoeste Goiano') pelo oficial ('Sudoeste de Goias', "
                  "microrregiao 52013)."),
        Cobertura("(:Cliente)-[:OPERA_EM]->(:Regiao)", "parcial", 0.8,
                  "Derivada do municipio da SEDE do cliente (endereco do CNPJ). "
                  "Produtor com fazendas em duas microrregioes aparece so na da "
                  "sede — e ai o canal sistemico subestima a exposicao. Cobrir "
                  "direito exige o CAR de cada imovel (SICAR, bloqueado) ou o "
                  "cadastro da Krilltech."),
        Cobertura("OPERA_EM.hectares", "interno", 0.0,
                  "Area operada e dado de cadastro/CAR, nao do IBGE."),
    ],
)
