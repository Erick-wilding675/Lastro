"""IBGE / PAM — Produção Agrícola Municipal, via API SIDRA.

Tabela 5457, agregada por município. Metadados verificados em 12/09/2026:
  variáveis  216 área colhida (ha) · 112 rendimento médio (kg/ha) · 8331 área plantada
  classif.   c782 produto — soja 40124 · milho 40122 · algodão herbáceo 40099
  série      1974 a 2024 (anual)

PARA QUE SERVE, DADO QUE A CONAB JÁ MEDE QUEBRA. Para duas coisas que a Conab
não faz:

  1. GRANULARIDADE. A Conab publica por UF; a PAM publica por MUNICÍPIO. É a
     única fonte pública que permite dizer "quebrou no Sudoeste de Goiás" em vez
     de "quebrou em Goiás". Como `:Regiao` é microrregião, agregar municípios da
     microrregião dá exatamente o recorte do motor.
  2. QUAL CULTURA EXISTE ONDE. `(:Cliente)-[:PLANTA]->(:Cultura)` não tem fonte
     pública — ninguém publica o que um produtor específico plantou. O que a PAM
     dá é a composição de lavouras do município, que serve para VALIDAR o que o
     cliente declarou (se ele diz algodão num município sem um hectare de
     algodão, é erro de cadastro) e nunca para AFIRMAR o que ele plantou.

O PREÇO: a PAM fecha com ~1 a 2 anos de defasagem. Em setembro de 2026 o último
ano disponível é 2024. Não serve para detectar a quebra da safra corrente — para
isso é a Conab. Serve para o baseline estrutural de onde se planta o quê.
"""
from collections import defaultdict

from ingestao import config, http, staging
from ingestao.fontes.base import Cobertura, Fonte

# /v/216,112 = área colhida + rendimento médio; /p/last%206 = 6 últimos anos
API = ("https://apisidra.ibge.gov.br/values/t/5457/n6/{municipios}"
       "/v/216,112/p/last%206/c782/{produtos}")
BRUTO = config.RAW / "ibge"
ARQUIVO = BRUTO / "pam-5457.json"

PRODUTOS = {
    "40124": ("CUL-SOJA", "Soja"),
    "40122": ("CUL-MILHO", "Milho"),
    "40099": ("CUL-ALGODAO", "Algodão"),
}

# Queda de rendimento municipal que vira evento regional. Mais alto que o limiar
# da Conab (8%) porque a série municipal oscila mais: um município pequeno tem
# variância alta por natureza, não por choque climático.
QUEDA_MINIMA = 0.12


def extract() -> None:
    import json
    from ingestao.fontes.ibge_regioes import _codigos

    # Mesma regra do ibge_regioes: a carteira manda, e o que ela não trouxer vem
    # do código de município que a Receita devolveu em staging/clientes.csv.
    codigos = sorted(_codigos(staging.carregar_carteira()))
    if not codigos:
        raise SystemExit("Sem codigo_municipio_ibge disponivel — rode 'qsa' "
                         "antes, ou preencha a coluna na carteira.")
    BRUTO.mkdir(parents=True, exist_ok=True)
    url = API.format(municipios=",".join(codigos), produtos=",".join(PRODUTOS))
    dados = http.json_get(url)
    ARQUIVO.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    # A primeira linha do SIDRA é o cabeçalho descritivo, não um dado.
    print(f"  ok: pam-5457.json ({len(dados) - 1} observacoes, "
          f"{len(codigos)} municipio(s))")


def transform() -> None:
    import json
    if not ARQUIVO.exists():
        print("  ausente: pam-5457.json — rode o extract primeiro")
        return
    linhas = json.loads(ARQUIVO.read_text(encoding="utf-8"))[1:]
    municipio_regiao = {r["codigo_municipio_ibge"]: r["regiao"]
                        for r in staging.ler("municipio_regiao")}
    if not municipio_regiao:
        print("  AVISO: staging/municipio_regiao.csv ausente — rode ibge_regioes "
              "antes, senao nao da para agregar por microrregiao")

    # A PAM vem "longa": uma linha por município x variável x ano x produto.
    # Recompõe-se primeiro a observação municipal completa (área E rendimento
    # no mesmo ano), porque a agregação para microrregião precisa das duas
    # juntas para ponderar.
    obs: dict[tuple[str, str, str], dict[str, float]] = defaultdict(dict)
    lavouras: dict[tuple[str, str], float] = defaultdict(float)

    for linha in linhas:
        cod_mun = linha.get("D1C", "")
        if cod_mun not in municipio_regiao:
            continue
        ano = linha.get("D3C", "")
        cultura = PRODUTOS.get(linha.get("D4C", ""), (None, None))[0]
        if not cultura:
            continue
        try:
            valor = float(linha.get("V") or 0)
        except (ValueError, TypeError):
            continue  # SIDRA usa '...' e '-' para sigilo e zero
        chave = (cod_mun, cultura, ano)
        if linha.get("D2C") == "216":      # área colhida (ha)
            obs[chave]["area"] = valor
            lavouras[(cod_mun, cultura)] += valor
        elif linha.get("D2C") == "112":    # rendimento médio (kg/ha)
            obs[chave]["rend"] = valor

    # Agrega município -> microrregião com média ponderada por área colhida.
    # Somar rendimentos sem peso inverteria o sinal numa microrregião com um
    # município grande e cinco pequenos: o grande é quem carrega a carteira.
    area: dict[tuple[str, str, str], float] = defaultdict(float)
    rend_x_area: dict[tuple[str, str, str], float] = defaultdict(float)
    for (cod_mun, cultura, ano), v in obs.items():
        a, r = v.get("area", 0.0), v.get("rend", 0.0)
        if a <= 0 or r <= 0:
            continue  # sem as duas variáveis a observação não pondera
        chave = (municipio_regiao[cod_mun], cultura, ano)
        area[chave] += a
        rend_x_area[chave] += r * a

    rendimento: dict[tuple[str, str], dict[str, float]] = defaultdict(dict)
    for chave, soma in rend_x_area.items():
        regiao, cultura, ano = chave
        rendimento[(regiao, cultura)][ano] = soma / area[chave]

    eventos, series = [], []
    for (regiao, cultura), por_ano in sorted(rendimento.items()):
        ordenados = sorted(por_ano.items())
        if len(ordenados) < 3:
            continue
        ano_atual, rend_atual = ordenados[-1]
        anteriores = [v for _, v in ordenados[:-1]]
        baseline = sum(anteriores) / len(anteriores)
        queda = (baseline - rend_atual) / baseline if baseline else 0.0
        series.append({
            "regiao": regiao, "cultura": cultura, "ano": ano_atual,
            "rendimento_kg_ha": round(rend_atual, 1),
            "baseline_kg_ha": round(baseline, 1),
            "anos_no_baseline": len(anteriores),
            "queda_pct": round(100 * queda, 1),
            "area_colhida_ha": round(area.get((regiao, cultura, ano_atual), 0.0), 1),
            "virou_evento": "true" if queda >= QUEDA_MINIMA else "false",
            "fonte": "IBGE/PAM — tabela 5457",
            "coletado_em": staging.hoje(), "confianca": 1.0,
        })
        if queda < QUEDA_MINIMA:
            continue
        eventos.append({
            "id": f"PAM-{regiao}-{cultura}-{ano_atual}",
            "regiao": regiao,
            "cultura": cultura,
            "tipo": "quebra_safra",
            # Ano-calendário da PAM = ano da colheita. 1º de março, mesma
            # convenção da Conab, para que os dois eventos sejam comparáveis.
            "data": f"{ano_atual}-03-01",
            "fonte": "IBGE/PAM — tabela 5457",
            "severidade": round(min(0.80, max(0.30, 0.20 + 2.0 * queda)), 2),
            "descricao": (
                f"Queda de {100 * queda:.0f}% no rendimento medio de {cultura} "
                f"em {regiao} no ano {ano_atual}: {rend_atual:.0f} kg/ha contra "
                f"media de {baseline:.0f} kg/ha dos {len(anteriores)} anos anteriores"),
            "queda_pct": round(100 * queda, 1),
            "coletado_em": staging.hoje(), "confianca": 0.8,
        })

    lavoura_rows = [{
        "codigo_municipio_ibge": cod, "cultura": cultura,
        "area_colhida_ha": round(a, 1),
        "fonte": "IBGE/PAM — tabela 5457",
        "coletado_em": staging.hoje(), "confianca": 1.0,
    } for (cod, cultura), a in sorted(lavouras.items()) if a > 0]

    staging.escrever("eventos_pam", [
        "id", "regiao", "cultura", "tipo", "data", "fonte", "severidade",
        "descricao", "queda_pct"], eventos)
    staging.escrever("analise_pam", [
        "regiao", "cultura", "ano", "rendimento_kg_ha", "baseline_kg_ha",
        "anos_no_baseline", "queda_pct", "area_colhida_ha", "virou_evento"], series)
    staging.escrever("lavoura_municipio", [
        "codigo_municipio_ibge", "cultura", "area_colhida_ha"], lavoura_rows)


FONTE = Fonte(
    id="ibge_pam",
    nome="IBGE — Produção Agrícola Municipal (PAM, SIDRA 5457)",
    url="https://apisidra.ibge.gov.br/",
    orgao="IBGE",
    periodicidade="anual, com 1 a 2 anos de defasagem",
    extract=extract,
    transform=transform,
    cobertura=[
        Cobertura(":Evento{tipo:'quebra_safra'} por microrregiao", "real", 0.8,
                  "Unica fonte publica com granularidade municipal, agregavel a "
                  "microrregiao — o recorte que o motor usa em :Regiao."),
        Cobertura("Validacao de (:Cliente)-[:PLANTA]->(:Cultura)", "parcial", 0.6,
                  "A PAM diz o que se colhe no MUNICIPIO, nao o que o cliente "
                  "plantou. Serve para CONTESTAR cadastro implausivel (algodao "
                  "num municipio sem algodao), nunca para afirmar a cultura."),
        Cobertura("(:Cliente)-[:PLANTA]->(:Cultura)", "interno", 0.0,
                  "Nao existe fonte publica do que um produtor especifico "
                  "plantou. Vem da nota fiscal / contrato de insumo da Krilltech."),
        Cobertura("Defasagem", "parcial", 0.5,
                  "Em 09/2026 o ultimo ano da PAM e 2024. Nao detecta a quebra "
                  "da safra corrente; para isso a Conab. Aqui fica o baseline "
                  "estrutural."),
    ],
)
