"""PGFN — Dívida Ativa da União e do FGTS.

A MELHOR fonte pública do pipeline, e por um motivo simples: ela publica o
CPF/CNPJ do devedor. Isso fecha o join com a carteira de forma determinística,
sem casamento por nome. Tudo o que sai daqui entra no grafo com confianca=1.0.

Layout verificado no arquivo 2026_trimestre_02 (latin-1, separador ';'):
  CPF_CNPJ;TIPO_PESSOA;TIPO_DEVEDOR;NOME_DEVEDOR;UF_DEVEDOR;UNIDADE_RESPONSAVEL;
  ENTIDADE_RESPONSAVEL;UNIDADE_INSCRICAO;NUMERO_INSCRICAO;TIPO_SITUACAO_INSCRICAO;
  SITUACAO_INSCRICAO;RECEITA_PRINCIPAL;DATA_INSCRICAO;INDICADOR_AJUIZADO;
  VALOR_CONSOLIDADO

INDICADOR_AJUIZADO é o campo que importa: 'SIM' significa execução fiscal
efetivamente proposta — o `execucao_fiscal` de severidade 0,6 do seed. 'NAO'
é inscrição em dívida ativa sem ação ainda, que é pressão real mas menor.
Tratar os dois como a mesma coisa inflaria a red flag.

Tamanhos reais (2026_trimestre_02): Não Previdenciário 1,3 GB, Previdenciário
83 MB, FGTS 18 MB. Por isso o transform é streaming sobre o zip, sem extrair.
"""
import io
import zipfile
from pathlib import Path

from ingestao import config, http, staging
from ingestao.fontes.base import Cobertura, Fonte

BASE = "https://dadosabertos.pgfn.gov.br/{trimestre}/Dados_abertos_{sistema}.zip"
BRUTO = config.RAW / "pgfn"

SISTEMAS = ("Nao_Previdenciario", "Previdenciario", "FGTS")

# A PGFN publica trimestralmente, com defasagem. Sobrescreva via
# LASTRO_PGFN_TRIMESTRE se um trimestre mais novo já estiver no ar.
TRIMESTRE_PADRAO = "2026_trimestre_02"

# Severidade: inscrição ajuizada é ação judicial em curso; inscrição sem
# ajuizamento é cobrança administrativa. Os valores seguem a escala do seed
# (execucao_fiscal = 0,6) para não criar uma segunda régua de gravidade.
SEVERIDADE_AJUIZADA = 0.60
SEVERIDADE_INSCRITA = 0.45
# Protesto de CDA fica entre as duas: é ato de constrição com efeito imediato no
# crédito, mas não é ação de execução. Alinhado ao 0,7 que o seed dava a
# protesto de duplicata, descontado por não ser título comercial.
SEVERIDADE_PROTESTADA = 0.65


def _trimestre() -> str:
    import os
    return os.getenv("LASTRO_PGFN_TRIMESTRE", TRIMESTRE_PADRAO)


def extract() -> None:
    trimestre = _trimestre()
    for sistema in SISTEMAS:
        http.baixar(BASE.format(trimestre=trimestre, sistema=sistema),
                    BRUTO / trimestre / f"{sistema}.zip")


def _linhas_do_zip(caminho: Path):
    """Gera dicts de todos os CSV dentro do zip, sem extrair para disco."""
    with zipfile.ZipFile(caminho) as z:
        for nome in z.namelist():
            if not nome.lower().endswith(".csv"):
                continue
            with z.open(nome) as bruto:
                # latin-1 confirmado: utf-8 quebra em "Pessoa jurídica".
                texto = io.TextIOWrapper(bruto, encoding="latin-1", newline="")
                import csv
                for linha in csv.DictReader(texto, delimiter=";"):
                    yield nome, linha


def transform() -> None:
    carteira = staging.carregar_carteira()
    por_doc = staging.indice_por_documento(carteira)
    trimestre = _trimestre()
    eventos: dict[str, dict] = {}
    lidas = casadas = sem_data = 0

    for sistema in SISTEMAS:
        caminho = BRUTO / trimestre / f"{sistema}.zip"
        if not caminho.exists():
            print(f"  ausente: {sistema}.zip — rode o extract primeiro")
            continue
        for arquivo, linha in _linhas_do_zip(caminho):
            lidas += 1
            if lidas % 2_000_000 == 0:
                print(f"  {lidas:,} inscricoes lidas, {casadas} da carteira")
            doc = staging.so_digitos(linha.get("CPF_CNPJ"))
            cliente = por_doc.get(doc)
            if cliente is None:
                continue
            data = staging.data_br(linha.get("DATA_INSCRICAO"))
            if not data:
                sem_data += 1
                continue
            casadas += 1

            ajuizada = (linha.get("INDICADOR_AJUIZADO") or "").strip().upper() == "SIM"
            situacao = (linha.get("SITUACAO_INSCRICAO") or "").strip().upper()
            inscricao = (linha.get("NUMERO_INSCRICAO") or "").strip()
            valor = (linha.get("VALOR_CONSOLIDADO") or "0").replace(",", ".")
            try:
                valor_num = float(valor)
            except ValueError:
                valor_num = 0.0

            # SITUACAO_INSCRICAO = 'PROTESTADA' significa que a Certidão de
            # Dívida Ativa foi levada a protesto. Não é o mesmo que protesto de
            # duplicata comercial (que é o `protesto` do seed e fica em
            # cartório, sem base pública), mas é protesto de verdade, com nome
            # em cartório e efeito sobre crédito. Sai como tipo próprio para
            # que ninguém confunda os dois na leitura.
            protestada = situacao == "PROTESTADA"
            if protestada:
                tipo, severidade = "protesto_cda", SEVERIDADE_PROTESTADA
            elif ajuizada:
                tipo, severidade = "execucao_fiscal", SEVERIDADE_AJUIZADA
            else:
                tipo, severidade = "divida_ativa", SEVERIDADE_INSCRITA

            rotulo = {"protesto_cda": "CDA levada a protesto",
                      "execucao_fiscal": "Execucao fiscal ajuizada",
                      "divida_ativa": "Inscricao em divida ativa"}[tipo]

            # O id é o número da inscrição: estável entre trimestres, o que faz
            # o MERGE atualizar a mesma inscrição em vez de duplicar a cada
            # trimestre novo ingerido.
            eid = f"PGFN-{inscricao}"
            eventos[eid] = {
                "id": eid,
                "cliente": cliente["id"],
                "tipo": tipo,
                "data": data,
                "fonte": f"PGFN — {sistema.replace('_', ' ')} ({trimestre})",
                "severidade": severidade,
                "descricao": (
                    f"{rotulo} — {linha.get('RECEITA_PRINCIPAL', '').strip()}"
                    f" — R$ {valor_num:,.2f} — situacao: {situacao}"),
                "valor": valor_num,
                "coletado_em": staging.hoje(),
                "confianca": 1.0,
            }

    print(f"  total: {lidas:,} inscricoes varridas, {casadas} pertencem a carteira")
    if sem_data:
        print(f"  {sem_data} descartada(s) por DATA_INSCRICAO ilegivel")
    staging.escrever("eventos_pgfn", [
        "id", "cliente", "tipo", "data", "fonte", "severidade", "descricao",
        "valor"], eventos.values())


FONTE = Fonte(
    id="pgfn",
    nome="PGFN — Dívida Ativa da União e FGTS",
    url="https://dadosabertos.pgfn.gov.br/",
    orgao="Procuradoria-Geral da Fazenda Nacional",
    periodicidade="trimestral",
    extract=extract,
    transform=transform,
    cobertura=[
        Cobertura(":Evento{tipo:'execucao_fiscal'} + SOBRE Cliente", "real", 1.0,
                  "Fonte publica CPF/CNPJ do devedor: join deterministico com a "
                  "carteira. INDICADOR_AJUIZADO='SIM' e execucao proposta."),
        Cobertura(":Evento{tipo:'protesto_cda'} (novo tipo)", "real", 1.0,
                  "ACHADO NA INGESTAO: SITUACAO_INSCRICAO='PROTESTADA' indica "
                  "CDA levada a protesto. Nao e protesto de duplicata "
                  "comercial (esse e de cartorio, sem base publica), mas e "
                  "protesto com nome em cartorio e efeito sobre credito. Cobre "
                  "PARCIALMENTE o 'protesto' do seed, que antes parecia nao ter "
                  "nenhuma fonte publica."),
        Cobertura(":Evento{tipo:'divida_ativa'} (novo tipo)", "real", 1.0,
                  "Inscricao sem ajuizamento. Nao existia no seed; separado de "
                  "execucao_fiscal porque a gravidade e menor (0,45 vs 0,60)."),
        Cobertura(":Evento.valor (exposicao fiscal em R$)", "real", 1.0,
                  "VALOR_CONSOLIDADO. Campo novo: permite ponderar a red flag "
                  "por tamanho da divida, nao so por existencia."),
        Cobertura("Defasagem temporal", "parcial", 1.0,
                  "Publicacao trimestral: uma inscricao de hoje aparece em ate "
                  "3 meses. Para o caso de uso (antecipar RJ com meses de "
                  "antecedencia) e aceitavel; para decisao intraday, nao."),
    ],
)
