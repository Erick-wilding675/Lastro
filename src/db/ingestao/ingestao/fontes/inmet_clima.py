"""INMET — dados históricos das estações automáticas. Corrobora a estiagem.

Arquivos anuais em https://portal.inmet.gov.br/uploads/dadoshistoricos/{ano}.zip
(2026: 64 MB, 639 estações; 2025: 91 MB). Um CSV por estação, latin-1, decimal
com vírgula, 8 linhas de cabeçalho de metadados antes do cabeçalho de colunas:

  REGIAO:;CO
  UF:;GO
  ESTACAO:;GOIANIA
  CODIGO (WMO):;A002
  LATITUDE:;-16,64277777
  LONGITUDE:;-49,22027777
  ALTITUDE:;727,3
  DATA DE FUNDACAO:;29/05/01
  Data;Hora UTC;PRECIPITAÇÃO TOTAL, HORÁRIO (mm);PRESSAO...
  2026/01/01;0000 UTC;0;932,5;...

POR QUE NÃO USAR A API apitempo.inmet.gov.br: a rota pública de série histórica
(/estacao/diaria/...) responde E_ROUTE_NOT_FOUND hoje e a variante /token/
exige chave ("CHAVE INVÁLIDA!"). Só /estacoes/{T|M} segue aberta, e ela devolve
o cadastro das estações, não a medição. Os ZIPs anuais são o caminho aberto.

PARA QUE SERVE: o motor só aplica peso cheio no canal sistêmico se houver
evento regional confirmando o choque. A Conab diz que a produtividade caiu; o
INMET diz se choveu menos. São evidências independentes, e o valor está
justamente em serem independentes — quebra de safra com chuva normal é problema
de manejo ou praga, não de clima, e isso muda a leitura de crédito.

DUAS HONESTIDADES NECESSÁRIAS:
  1. GRANULARIDADE. A estação tem lat/long, não município. Mapear estação ->
     microrregião exige ponto-em-polígono contra a malha do IBGE, que não está
     implementado aqui. A agregação sai por UF, e lat/long vai para o staging
     para que o join espacial seja possível depois.
  2. BASELINE CURTO. Climatologia de referência são 30 anos (normal
     climatológica). Aqui o baseline são os anos baixados (padrão: 5). Um
     baseline de 5 anos num período de estiagens recorrentes subestima o
     desvio, porque a própria referência já está seca.
"""
import csv
import io
import os
import zipfile
from collections import defaultdict
from datetime import date

from ingestao import config, http, staging
from ingestao.fontes.base import Cobertura, Fonte

URL = "https://portal.inmet.gov.br/uploads/dadoshistoricos/{ano}.zip"
BRUTO = config.RAW / "inmet"

# Janela da safra de verão no Centro-Oeste: plantio em outubro, colheita até
# março. É a janela em que a chuva decide a produtividade da soja.
MES_INICIO, MES_FIM = 10, 3

# Déficit de chuva na janela que vira evento. 20% abaixo da média é o patamar
# em que a literatura agronômica passa a associar perda de rendimento em soja
# de sequeiro no Cerrado.
DEFICIT_MINIMO = 0.20

# Safras completas mínimas no baseline. Cada safra out-mar atravessa dois
# arquivos anuais, e o ano-calendário mais antigo baixado nunca tem o seu
# out-dez — então N safras completas exigem N+2 anos de ZIP. Com o padrão de 5
# anos saem 3 safras completas: 2 de baseline, abaixo deste mínimo, e o INMET
# corretamente NÃO emite evento. Para o INMET valer é preciso LASTRO_INMET_ANOS=6
# ou mais (~500 MB).
BASELINE_MINIMO = 3


def _anos() -> list[int]:
    """Anos-calendário a baixar. Cada safra precisa de dois (out/ano, mar/ano+1)."""
    n = int(os.getenv("LASTRO_INMET_ANOS", "5"))
    atual = date.today().year
    return list(range(atual - n + 1, atual + 1))


def extract() -> None:
    for ano in _anos():
        http.baixar(URL.format(ano=ano), BRUTO / f"{ano}.zip")


def _ler_estacao(bruto) -> tuple[dict, list[tuple[str, float]]]:
    """Devolve (metadados, [(data, precipitacao_mm)]) de um CSV de estação."""
    texto = io.TextIOWrapper(bruto, encoding="latin-1", errors="replace", newline="")
    meta: dict[str, str] = {}
    for _ in range(8):
        linha = texto.readline()
        if not linha:
            return meta, []
        partes = linha.rstrip("\n").split(";")
        if len(partes) >= 2:
            meta[partes[0].rstrip(":").strip().upper()] = partes[1].strip()

    leitor = csv.reader(texto, delimiter=";")
    cabecalho = next(leitor, None)
    if not cabecalho:
        return meta, []
    # Acha a coluna de precipitação pelo prefixo: o rótulo tem acento e o
    # arquivo tem encoding inconsistente entre anos, então comparar a string
    # inteira é frágil.
    idx = next((i for i, c in enumerate(cabecalho)
                if c.upper().startswith("PRECIPITA")), 2)

    medicoes = []
    for linha in leitor:
        if len(linha) <= idx or not linha[0]:
            continue
        valor = linha[idx].strip().replace(",", ".")
        if not valor:
            continue  # vazio = sem medição, diferente de zero de chuva
        try:
            mm = float(valor)
        except ValueError:
            continue
        if mm < 0:
            continue  # INMET usa negativo como sentinela de falha de sensor
        # A data vem '2026/01/01' em alguns anos e '2026-01-01' em outros.
        medicoes.append((linha[0].strip().replace("/", "-"), mm))
    return meta, medicoes


def _safra_de(data_iso: str) -> str | None:
    """'2026-01-15' -> '2025/26'. None se estiver fora da janela da safra."""
    try:
        ano, mes = int(data_iso[:4]), int(data_iso[5:7])
    except ValueError:
        return None
    if mes >= MES_INICIO:
        return f"{ano}/{str(ano + 1)[-2:]}"
    if mes <= MES_FIM:
        return f"{ano - 1}/{str(ano)[-2:]}"
    return None  # abril a setembro: entressafra, não entra no acumulado


def transform() -> None:
    # (uf, safra, estacao) -> mm acumulados na janela
    acumulado: dict[tuple[str, str, str], float] = defaultdict(float)
    # (uf, safra) -> meses da janela que realmente têm medição. Sem isso o
    # cálculo compara uma janela completa (out-mar, 6 meses) com uma truncada
    # (jan-mar, 3 meses) e reporta "superavit de 90%" — foi exatamente o que
    # aconteceu na primeira execucao: o arquivo de um ano-calendario comeca em
    # janeiro, entao a safra mais ANTIGA da serie nunca tem o seu out-dez.
    meses_vistos: dict[tuple[str, str], set[int]] = defaultdict(set)
    estacoes: dict[str, dict] = {}

    for ano in _anos():
        caminho = BRUTO / f"{ano}.zip"
        if not caminho.exists():
            print(f"  ausente: {ano}.zip — rode o extract primeiro")
            continue
        with zipfile.ZipFile(caminho) as z:
            nomes = [n for n in z.namelist() if n.upper().endswith(".CSV")]
            for i, nome in enumerate(nomes, 1):
                with z.open(nome) as f:
                    meta, medicoes = _ler_estacao(f)
                uf = meta.get("UF", "").strip().upper()
                codigo = meta.get("CODIGO (WMO)", "").strip()
                if not uf or not codigo:
                    continue
                estacoes[codigo] = {
                    "codigo": codigo,
                    "nome": meta.get("ESTACAO", ""),
                    "uf": uf,
                    "latitude": meta.get("LATITUDE", "").replace(",", "."),
                    "longitude": meta.get("LONGITUDE", "").replace(",", "."),
                    "altitude": meta.get("ALTITUDE", "").replace(",", "."),
                    "fonte": "INMET — estações automáticas",
                    "coletado_em": staging.hoje(), "confianca": 1.0,
                }
                for data_iso, mm in medicoes:
                    safra = _safra_de(data_iso)
                    if safra:
                        acumulado[(uf, safra, codigo)] += mm
                        meses_vistos[(uf, safra)].add(int(data_iso[5:7]))
            print(f"  {ano}: {len(nomes)} estacao(oes) lida(s)")

    # Meses que compõem a janela out-mar. Uma safra só é comparável se TODOS
    # estiverem presentes: 3 meses contra 6 não é déficit de chuva, é déficit de
    # arquivo.
    JANELA = {10, 11, 12, 1, 2, 3}

    # Média entre estações da UF: uma UF com 40 estações e outra com 3 não pode
    # ter o total somado comparado — o que compara é a média por estação.
    por_uf_safra: dict[tuple[str, str], list[float]] = defaultdict(list)
    descartadas = 0
    for (uf, safra, _codigo), mm in acumulado.items():
        if mm <= 0:
            continue
        if not JANELA.issubset(meses_vistos.get((uf, safra), set())):
            descartadas += 1
            continue
        por_uf_safra[(uf, safra)].append(mm)
    if descartadas:
        print(f"  {descartadas} serie(s) estacao x safra descartada(s) por "
              "janela out-mar incompleta nos arquivos baixados")

    series: dict[str, dict[str, float]] = defaultdict(dict)
    contagens: dict[tuple[str, str], int] = {}
    for (uf, safra), valores in por_uf_safra.items():
        series[uf][safra] = sum(valores) / len(valores)
        contagens[(uf, safra)] = len(valores)

    eventos, analises = [], []
    for uf, por_safra in sorted(series.items()):
        # Só safras com janela completa chegaram aqui, então a última da lista JÁ
        # é a última completa — não se chuta mais "a penúltima".
        ordenados = sorted(por_safra.items())
        safra_atual, mm_atual = ordenados[-1]
        anteriores = [v for _, v in ordenados[:-1]]
        if len(anteriores) < BASELINE_MINIMO:
            # Registra o motivo em vez de sumir: "o INMET nao acusou estiagem" e
            # "o INMET nao tinha dado para avaliar" sao conclusoes diferentes, e
            # quem le o relatorio precisa saber qual das duas aconteceu.
            analises.append({
                "uf": uf, "safra": safra_atual,
                "chuva_media_mm": round(mm_atual, 1),
                "baseline_mm": "", "safras_no_baseline": len(anteriores),
                "estacoes": contagens.get((uf, safra_atual), 0),
                "deficit_pct": "", "virou_evento": "false",
                "motivo": (f"baseline insuficiente: {len(anteriores)} safra(s) "
                           f"completa(s), minimo {BASELINE_MINIMO} — baixe mais "
                           f"anos com LASTRO_INMET_ANOS"),
                "fonte": "INMET — estações automáticas",
                "coletado_em": staging.hoje(), "confianca": 1.0,
            })
            continue
        baseline = sum(anteriores) / len(anteriores)
        deficit = (baseline - mm_atual) / baseline if baseline else 0.0

        analises.append({
            "uf": uf, "safra": safra_atual,
            "chuva_media_mm": round(mm_atual, 1),
            "baseline_mm": round(baseline, 1),
            "safras_no_baseline": len(anteriores),
            "estacoes": contagens.get((uf, safra_atual), 0),
            "deficit_pct": round(100 * deficit, 1),
            "virou_evento": "true" if deficit >= DEFICIT_MINIMO else "false",
            "motivo": "" if deficit >= DEFICIT_MINIMO else
                      f"deficit de {100 * deficit:.1f}% abaixo do limiar de "
                      f"{100 * DEFICIT_MINIMO:.0f}%",
            "fonte": "INMET — estações automáticas",
            "coletado_em": staging.hoje(), "confianca": 1.0,
        })
        if deficit < DEFICIT_MINIMO:
            continue
        eventos.append({
            "id": f"INMET-{uf}-{safra_atual.replace('/', '')}",
            "uf": uf,
            "tipo": "estiagem",
            "data": f"20{safra_atual[-2:]}-03-01",
            "fonte": "INMET — estações automáticas",
            "severidade": round(min(0.70, max(0.30, 0.20 + 1.5 * deficit)), 2),
            "descricao": (
                f"Deficit de {100 * deficit:.0f}% na chuva acumulada da janela "
                f"out-mar em {uf} na safra {safra_atual}: {mm_atual:.0f} mm "
                f"medios por estacao contra {baseline:.0f} mm das "
                f"{len(anteriores)} safras anteriores "
                f"({contagens.get((uf, safra_atual), 0)} estacoes)"),
            "deficit_pct": round(100 * deficit, 1),
            # Confiança 0,7 e não 1,0: o fato medido é real, mas o baseline de
            # poucos anos não é normal climatológica.
            "coletado_em": staging.hoje(), "confianca": 0.7,
        })

    staging.escrever("estacoes_inmet", [
        "codigo", "nome", "uf", "latitude", "longitude", "altitude"],
        estacoes.values())
    staging.escrever("eventos_inmet", [
        "id", "uf", "tipo", "data", "fonte", "severidade", "descricao",
        "deficit_pct"], eventos)
    staging.escrever("analise_chuva", [
        "uf", "safra", "chuva_media_mm", "baseline_mm", "safras_no_baseline",
        "estacoes", "deficit_pct", "virou_evento", "motivo"], analises)


FONTE = Fonte(
    id="inmet",
    nome="INMET — dados históricos das estações automáticas",
    url="https://portal.inmet.gov.br/dadoshistoricos",
    orgao="Instituto Nacional de Meteorologia",
    periodicidade="diária (arquivo anual acumulado)",
    extract=extract,
    transform=transform,
    cobertura=[
        Cobertura(":Evento{tipo:'estiagem'} (novo tipo)", "real", 0.7,
                  "Chuva acumulada na janela out-mar, medida, contra o baseline "
                  "dos anos baixados. Evidencia INDEPENDENTE da Conab: quebra "
                  "com chuva normal nao e clima, e manejo ou praga — e isso "
                  "muda a leitura de credito."),
        Cobertura("Granularidade microrregional", "parcial", 0.4,
                  "A estacao tem lat/long, nao municipio. Agregacao sai por UF. "
                  "lat/long vai para staging/estacoes_inmet.csv para viabilizar "
                  "o join espacial contra a malha do IBGE depois."),
        Cobertura("Baseline climatologico", "parcial", 0.5,
                  "Normal climatologica sao 30 anos; aqui sao 5 (os ZIPs "
                  "baixados). Num periodo de estiagens recorrentes a propria "
                  "referencia ja esta seca, o que SUBESTIMA o desvio."),
        Cobertura("API apitempo.inmet.gov.br", "bloqueado", 0.0,
                  "A rota de serie historica responde E_ROUTE_NOT_FOUND e a "
                  "variante /token/ exige chave. So /estacoes/ segue aberta, e "
                  "devolve cadastro, nao medicao. Por isso os ZIPs anuais."),
    ],
)
