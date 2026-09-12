"""Camada de staging: CSV normalizado entre a fonte e o grafo.

Existe para que `transform` e `load` possam ser revisados por um humano antes
de qualquer coisa tocar o Neo4j. Um CSV de staging é auditável no Excel; um
MERGE direto da fonte para o grafo não é.
"""
import csv
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Iterator

from ingestao import config

# O CSV do IBAMA traz WKT_GEOM_AREA_EMBARGADA: o polígono da área embargada
# como texto. Um perímetro de fazenda grande passa de 131.072 caracteres, que é
# o limite default do módulo csv, e a leitura morre com "field larger than field
# limit" no meio de 148 MB. Sobe-se o limite ao máximo que a plataforma aceita.
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

# Colunas de procedência, obrigatórias em toda linha de staging.
# data-model.md: "Toda informação carrega fonte e confiança (...) nunca vira
# fato consolidado silenciosamente."
#
# `sintetico` entra aqui, e não na lista de colunas de cada fonte, por causa de
# `extrasaction="ignore"` no DictWriter abaixo: um campo fora do fieldnames é
# descartado EM SILÊNCIO. Foi exatamente o que aconteceu na primeira versão do
# gerador sintético — a marca era produzida e sumia na escrita do CSV, e o grafo
# recebeu 176 nós sem nenhuma forma de distinguir inventado de medido. Sendo
# procedência, tem de valer para toda fonte: vazio nas reais (o loader não grava
# propriedade vazia), 'true' nas sintéticas.
PROCEDENCIA = ("fonte", "coletado_em", "confianca", "sintetico")


def escrever(nome: str, colunas: Iterable[str], linhas: Iterable[dict]) -> Path:
    """Escreve data/staging/{nome}.csv. Devolve o caminho e loga a contagem."""
    config.preparar_diretorios()
    caminho = config.STAGING / f"{nome}.csv"
    campos = list(colunas) + [c for c in PROCEDENCIA if c not in colunas]
    n = 0
    with caminho.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for linha in linhas:
            w.writerow(linha)
            n += 1
    print(f"  staging/{nome}.csv: {n} linhas")
    return caminho


def ler(nome: str) -> list[dict]:
    caminho = config.STAGING / f"{nome}.csv"
    if not caminho.exists():
        return []
    with caminho.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def hoje() -> str:
    return date.today().isoformat()


def so_digitos(documento: str | None) -> str:
    """Normaliza CPF/CNPJ para comparação entre fontes.

    Necessário porque cada fonte escolhe um formato: a PGFN publica
    '10.496.760/0001-95', o IBAMA publica '75776849000150' e a carteira da
    empresa pode vir de qualquer um dos dois. Sem isso, nenhum join fecha.
    """
    return re.sub(r"\D", "", documento or "")


def data_br(texto: str | None) -> str | None:
    """'16/12/1987 15:40:00' ou '16/12/1987' -> '1987-12-16'. None se não parsear.

    Devolver None em vez de levantar é deliberado aqui: um registro da PGFN de
    2019 com data corrompida não deve derrubar a ingestão dos outros 40 mil.
    A linha é descartada e contada pelo chamador.
    """
    if not texto:
        return None
    texto = texto.strip().strip('"')
    for formato in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto[:len(formato) + 6], formato).date().isoformat()
        except ValueError:
            continue
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", texto)
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def carregar_carteira() -> list[dict]:
    """Lê a carteira que serve de filtro para todas as fontes.

    Schema esperado (ver carteira.example.csv):
      id,documento,nome,tipo,uf,municipio,codigo_municipio_ibge
    """
    if not config.CARTEIRA.exists():
        raise SystemExit(
            f"Carteira não encontrada em {config.CARTEIRA}.\n"
            "Copie carteira.example.csv para carteira.csv e preencha com os\n"
            "clientes reais (ou defina LASTRO_CARTEIRA apontando para o arquivo).\n"
            "Sem carteira o pipeline não tem o que enriquecer."
        )
    with config.CARTEIRA.open(encoding="utf-8-sig") as f:
        carteira = [linha for linha in csv.DictReader(f) if linha.get("id")]
    for c in carteira:
        c["doc"] = so_digitos(c.get("documento"))
    return carteira


def indice_por_documento(carteira: list[dict]) -> dict[str, dict]:
    """doc normalizado -> cliente. O join de toda fonte que publica CPF/CNPJ."""
    return {c["doc"]: c for c in carteira if c["doc"]}


def iterar_csv(caminho: Path, encoding: str = "utf-8",
               delimitador: str = ";") -> Iterator[dict]:
    """Itera um CSV grande sem carregar na memória."""
    with caminho.open(encoding=encoding, errors="replace", newline="") as f:
        yield from csv.DictReader(f, delimiter=delimitador)
