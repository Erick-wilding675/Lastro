"""Conab — série histórica de grãos. É daqui que sai o `quebra_safra` REAL.

Arquivo único, 2,7 MB, latin-1, separador ';', série de 1976/77 até a safra
corrente:
  ano_agricola;dsc_safra_previsao;uf;produto;id_produto;
  area_plantada_mil_ha;producao_mil_t;produtividade_mil_ha_mil_t

POR QUE ESTA FONTE É O PILAR DO CANAL SISTÊMICO. O motor (Q1) só aplica peso
cheio (0,75) em "mesma região e cultura" se existir evento regional
confirmando o choque; sem evento, cai para 0,30. Esse evento era plantado à mão
no seed (EVT007). Aqui ele passa a ser MEDIDO: produtividade da safra corrente
contra a média das safras anteriores, na mesma UF e mesmo produto.

ACHADO NA SÉRIE REAL (12/09/2026), já com a régua deste módulo: GO / MILHO /
2ª SAFRA está em 5,0 t/ha na safra 2025/26 contra média de 5,64 das 5
anteriores — queda de 11,3%, que vira evento de severidade 0,43. A quebra
existe no dado, não precisa ser inventada.

E o contraexemplo importa tanto quanto: GO / SOJA está em 3,9 t/ha contra
baseline de 3,86 — ou seja, 1% ACIMA da média, apesar de ter caído de 4,2 no
ano anterior. Comparar com o ano anterior apontaria "queda de 7%"; comparar com
o baseline mostra que 4,2 foi safra excepcional, não que 3,9 seja quebra. É por
isso que o baseline é de 5 safras e não do ano passado.

DUAS ARMADILHAS TRATADAS AQUI:
  1. Milho tem 1ª, 2ª e 3ª safra com produtividades muito diferentes (10,4 vs
     7,0 vs 0). Comparar sem separar por safra produziria queda fantasma de 50%
     só por mudança de mix. O agrupamento é por (uf, produto, safra_previsao).
  2. Linhas com produtividade 0 significam "não se planta isso aqui", não
     "quebrou tudo". Entram como zero na média elas destruiriam o baseline.
     São excluídas.

LIMITE QUE NÃO DÁ PARA ESCONDER: a Conab publica por UF, não por microrregião.
O motor modela `:Regiao` como microrregião ('Sudoeste Goiano'). Um evento de UF
aceso em 'GO' cobre o Sudoeste Goiano e também o Nordeste Goiano, que pode ter
chovido normalmente. Para granularidade municipal existe o IBGE/PAM
(ibge_pam.py), que é mais fino mas atrasa ~1 ano. As duas fontes são
complementares: Conab diz "agora", PAM diz "onde".
"""
import csv
from collections import defaultdict

from ingestao import config, http, staging
from ingestao.fontes.base import Cobertura, Fonte

URL = "https://portaldeinformacoes.conab.gov.br/downloads/arquivos/SerieHistoricaGraos.txt"
ARQUIVO = config.RAW / "conab" / "SerieHistoricaGraos.txt"

# Quantas safras anteriores formam o baseline. 5 é o usual em análise de
# produtividade agrícola: absorve um ano ruim isolado sem virar média secular
# que ignora ganho tecnológico.
SAFRAS_BASELINE = 5

# Queda mínima para virar evento. Abaixo de 8% é ruído de estimativa da própria
# Conab (ela revisa os números ao longo da safra).
QUEDA_MINIMA = 0.08

# Mínimo de safras anteriores para que a média valha como referência.
BASELINE_MINIMO = 3

# Quantas safras para trás ainda contam como "atual". 1 = só a safra corrente;
# 2 permite que uma combinação cuja estimativa ainda não saiu neste ciclo use a
# anterior. Acima disso o radar passa a reportar história, não risco.
SAFRAS_ATUAIS = 2

# Produtos da Conab -> :Cultura do grafo. O seed tem três culturas; o resto da
# série fica de fora por ora, mas basta uma linha aqui para entrar.
CULTURAS = {
    "SOJA": ("CUL-SOJA", "Soja", 120),
    "MILHO": ("CUL-MILHO", "Milho", 150),
    "ALGODAO EM CAROCO": ("CUL-ALGODAO", "Algodão", 180),
}


def extract() -> None:
    http.baixar(URL, ARQUIVO)


def _severidade(queda: float) -> float:
    """Queda relativa de produtividade -> severidade 0..1.

    Ancorada no seed, que descrevia "perda de 18%" como severidade 0,6 e
    "perda de 22%" como 0,5/1,0 inconsistentemente. Aqui a régua é única e
    linear: 10% -> 0,40; 20% -> 0,60; 30% -> 0,80; teto em 0,90 porque quebra
    de safra, por grave que seja, não é fato jurídico consumado como uma RJ.
    """
    return round(min(0.90, max(0.30, 0.20 + 2.0 * queda)), 2)


def transform() -> None:
    if not ARQUIVO.exists():
        print("  ausente: SerieHistoricaGraos.txt — rode o extract primeiro")
        return

    # (uf, produto, safra_previsao) -> {ano_agricola: produtividade}
    series: dict[tuple[str, str, str], dict[str, float]] = defaultdict(dict)
    areas: dict[tuple[str, str], float] = defaultdict(float)
    anos: set[str] = set()

    # latin-1 confirmado: 'dsc_safra_previsao' traz "1ª SAFRA" e utf-8 quebra.
    with ARQUIVO.open(encoding="latin-1", newline="") as f:
        for linha in csv.DictReader(f, delimiter=";"):
            produto = (linha.get("produto") or "").strip()
            if produto not in CULTURAS:
                continue
            uf = (linha.get("uf") or "").strip()
            ano = (linha.get("ano_agricola") or "").strip()
            safra_prev = (linha.get("dsc_safra_previsao") or "").strip()
            try:
                prod = float((linha.get("produtividade_mil_ha_mil_t") or "0").strip())
                area = float((linha.get("area_plantada_mil_ha") or "0").strip())
            except ValueError:
                continue
            # Produtividade 0 = não se cultiva ali. Não é quebra; é ausência.
            if prod <= 0:
                continue
            series[(uf, produto, safra_prev)][ano] = prod
            areas[(uf, produto)] += area
            anos.add(ano)

    # A safra mais recente da série inteira. Serve de âncora de atualidade:
    # muitas combinações UF x produto têm série que ENCERRA no passado (algodão
    # no CE para em 2017/18, por exemplo, porque deixou-se de plantar). Sem essa
    # âncora o pipeline emitia "quebra de safra" datada de 1999/00 — fato
    # histórico verdadeiro, sinal de risco inútil num radar de crédito.
    safras_atuais = set(sorted(anos)[-SAFRAS_ATUAIS:])

    eventos, analises = [], []
    for (uf, produto, safra_prev), por_ano in sorted(series.items()):
        # Ordem lexicográfica de '2024/25' coincide com a cronológica, e os
        # rótulos sem barra ('2025', trigo) ficam no lugar certo também.
        ordenados = sorted(por_ano.items())
        ano_atual, prod_atual = ordenados[-1]
        anteriores = [p for _, p in ordenados[-(SAFRAS_BASELINE + 1):-1]]
        # Baseline de 1 ou 2 safras não é baseline, é comparação com um ano
        # isolado: qualquer variação normal vira "quebra de 20%".
        if len(anteriores) < BASELINE_MINIMO:
            continue
        baseline = sum(anteriores) / len(anteriores)
        queda = (baseline - prod_atual) / baseline if baseline else 0.0

        cultura_id, cultura_nome, _ = CULTURAS[produto]
        analises.append({
            "uf": uf, "produto": produto, "cultura": cultura_id,
            "safra_previsao": safra_prev, "ano_agricola": ano_atual,
            "produtividade": round(prod_atual, 3),
            "baseline": round(baseline, 3),
            "safras_no_baseline": len(anteriores),
            "queda_pct": round(100 * queda, 1),
            "serie_atual": "true" if ano_atual in safras_atuais else "false",
            "virou_evento": ("true" if queda >= QUEDA_MINIMA
                             and ano_atual in safras_atuais else "false"),
            "fonte": "Conab — série histórica de grãos",
            "coletado_em": staging.hoje(), "confianca": 1.0,
        })
        # Série encerrada no passado: a queda é fato histórico, não risco vivo.
        if ano_atual not in safras_atuais:
            continue
        if queda < QUEDA_MINIMA:
            continue

        rotulo_safra = safra_prev if safra_prev and safra_prev != "UNICA" else ""
        eventos.append({
            "id": f"CONAB-{uf}-{cultura_id}-{ano_atual.replace('/', '')}"
                  f"{'-' + rotulo_safra.replace(' ', '').replace('ª', '') if rotulo_safra else ''}",
            "uf": uf,
            "cultura": cultura_id,
            "tipo": "quebra_safra",
            # A Conab não datilografa um "dia do evento". O ano agrícola é o
            # recorte; usa-se 1º de março do ano-calendário de colheita, que é
            # o pico da colheita de verão no Centro-Oeste. Aproximação
            # declarada, não escondida.
            "data": f"20{ano_atual[-2:]}-03-01" if "/" in ano_atual else f"{ano_atual[:4]}-03-01",
            "fonte": "Conab — série histórica de grãos",
            "severidade": _severidade(queda),
            "descricao": (
                f"Queda de {100 * queda:.0f}% na produtividade de "
                f"{cultura_nome.lower()}{' (' + rotulo_safra.lower() + ')' if rotulo_safra else ''}"
                f" em {uf}: {prod_atual:.1f} t/ha na safra {ano_atual} contra "
                f"media de {baseline:.1f} t/ha nas {len(anteriores)} anteriores"),
            "queda_pct": round(100 * queda, 1),
            "ano_agricola": ano_atual,
            "coletado_em": staging.hoje(),
            "confianca": 1.0,
        })

    culturas = [{
        "id": cid, "nome": nome, "ciclo_dias": ciclo,
        "produto_conab": produto,
        "fonte": "Conab — série histórica de grãos",
        "coletado_em": staging.hoje(), "confianca": 1.0,
    } for produto, (cid, nome, ciclo) in CULTURAS.items()]

    # Só as safras recentes interessam ao grafo; 1976/77 é baseline, não nó.
    safras = [{
        "id": f"SAF-{ano.replace('/', '')[-4:]}" if "/" in ano else f"SAF-{ano}",
        "ano_agricola": ano,
        "status": "em_curso" if ano == max(anos) else "encerrada",
        "fonte": "Conab — série histórica de grãos",
        "coletado_em": staging.hoje(), "confianca": 1.0,
    } for ano in sorted(anos)[-6:]]

    staging.escrever("culturas", ["id", "nome", "ciclo_dias", "produto_conab"], culturas)
    staging.escrever("safras", ["id", "ano_agricola", "status"], safras)
    staging.escrever("eventos_conab", [
        "id", "uf", "cultura", "tipo", "data", "fonte", "severidade",
        "descricao", "queda_pct", "ano_agricola"], eventos)
    staging.escrever("analise_safra", [
        "uf", "produto", "cultura", "safra_previsao", "ano_agricola",
        "produtividade", "baseline", "safras_no_baseline", "queda_pct",
        "serie_atual", "virou_evento"], analises)
    print(f"  {len(eventos)} evento(s) de quebra de safra medido(s) em "
          f"{len(analises)} serie(s) UF x cultura x safra")


FONTE = Fonte(
    id="conab",
    nome="Conab — série histórica de grãos",
    url=URL,
    orgao="Companhia Nacional de Abastecimento",
    periodicidade="mensal durante a safra",
    extract=extract,
    transform=transform,
    cobertura=[
        Cobertura(":Evento{tipo:'quebra_safra'} (nivel UF)", "real", 1.0,
                  "MEDIDO: produtividade da safra corrente vs media das 5 "
                  "anteriores, por UF x produto x safra. Substitui o EVT007 "
                  "plantado a mao no seed."),
        Cobertura(":Cultura (taxonomia)", "real", 1.0,
                  "Nomes e serie por produto. ciclo_dias vem de agronomia, nao "
                  "da Conab — e constante do dominio, nao dado observado."),
        Cobertura(":Safra (taxonomia + status)", "real", 1.0,
                  "ano_agricola da serie; status em_curso = safra mais recente."),
        Cobertura("Granularidade de :Regiao (microrregiao)", "parcial", 0.6,
                  "A Conab publica por UF. Um evento em 'GO' acende o Sudoeste "
                  "Goiano e tambem o Nordeste Goiano, que pode nao ter quebrado. "
                  "Superestima a abrangencia do choque. Granularidade municipal "
                  "so via IBGE/PAM, com ~1 ano de defasagem."),
        Cobertura(":Evento.data de quebra_safra", "parcial", 0.7,
                  "A serie e por ano agricola, sem data de ocorrencia. Usa-se 1o "
                  "de marco do ano de colheita como proxy do pico da colheita "
                  "de verao no Centro-Oeste."),
        Cobertura(":Evento{tipo:'queda_preco'}", "parcial", 0.0,
                  "A serie historica de GRAOS nao traz preco. A Conab publica "
                  "precos em outra base (SIMA/precos agropecuarios), nao "
                  "coberta por este pipeline. O motor lista 'queda_preco' como "
                  "gatilho do canal sistemico e hoje ele nunca dispara."),
    ],
)
