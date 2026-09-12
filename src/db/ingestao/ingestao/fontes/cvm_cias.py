"""CVM — cadastro de companhias abertas. A fonte que fecha o `pedido_rj`.

ESTE MÓDULO DESMENTE, EM PARTE, O QUE ESTÁ ESCRITO EM datajud.py. Mantive o
texto de lá porque ele continua verdadeiro para o que descreve (o DataJud não
expõe as partes), mas a conclusão de que `pedido_rj` sobre um cliente
específico "não tem nenhuma fonte pública automatizável" estava errada.

A CVM publica, em CSV aberto e sem captcha:
  https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv

E o cadastro tem um campo ESTRUTURADO de situação do emissor, com a data de
início. Contagem real do arquivo em 12/09/2026 (2.677 registros, 755 ativos):

  SIT_EMISSOR                              n
  FASE OPERACIONAL                      1124
  FASE PRÉ-OPERACIONAL                   134
  EM RECUPERAÇÃO JUDICIAL OU EQUIVALENTE  40
  FALIDA                                  22
  LIQUIDAÇÃO EXTRAJUDICIAL                16
  EM LIQUIDAÇÃO JUDICIAL                   3
  EM RECUPERAÇÃO EXTRAJUDICIAL             3
  PARALISADA                               5

Exemplo direto do caso: AGROGALAXY PARTICIPAÇÕES S.A., CNPJ 21.240.146/0001-84,
Goiânia/GO, distribuidora de insumos agrícolas —
  SIT_EMISSOR        = 'EM RECUPERAÇÃO JUDICIAL OU EQUIVALENTE'
  DT_INI_SIT_EMISSOR = '2024-09-18'

Ou seja: CNPJ, situação e data, legíveis por máquina. É o `pedido_rj` do seed,
com a parte identificada.

O LIMITE, QUE É GRANDE E TEM DE SER DITO. Só existem ~755 companhias com
registro ativo na CVM em todo o Brasil. Produtor rural pessoa física não está
aqui. Sociedade limitada fechada não está aqui. Para a carteira típica da
Krilltech, a cobertura é de poucos clientes — mas são justamente os de maior
exposição individual: S.A. de capital aberto, emissores de CRA e veículos de
securitização do agro, que são todos registrados na CVM.

Então a leitura correta é: a CVM cobre a cauda de MAIOR valor da carteira, com
confiança total; o resto da carteira continua dependendo de DJE, API paga ou da
intimação que a Krilltech recebe como credora.
"""
import csv
from datetime import date

from ingestao import config, http, staging
from ingestao.fontes.base import Cobertura, Fonte

URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv"
ARQUIVO = config.RAW / "cvm" / "cad_cia_aberta.csv"

# SIT_EMISSOR -> (tipo de evento, severidade, situação do cliente)
# As severidades seguem a escala do seed: pedido_rj = 1.0, porque RJ é fato
# jurídico consumado e dispara o stay period de 180 dias.
SITUACOES = {
    "EM RECUPERAÇÃO JUDICIAL OU EQUIVALENTE": (
        "pedido_rj", 1.00, "recuperacao_judicial"),
    "EM RECUPERAÇÃO EXTRAJUDICIAL": (
        "recuperacao_extrajudicial", 0.85, "recuperacao_extrajudicial"),
    "FALIDA": ("falencia", 1.00, "falida"),
    "EM LIQUIDAÇÃO JUDICIAL": ("liquidacao_judicial", 1.00, "liquidacao"),
    "LIQUIDAÇÃO EXTRAJUDICIAL": ("liquidacao_extrajudicial", 0.90, "liquidacao"),
    "PARALISADA": ("atividade_paralisada", 0.70, "paralisada"),
}


def extract() -> None:
    http.baixar(URL, ARQUIVO)


def transform() -> None:
    if not ARQUIVO.exists():
        print("  ausente: cad_cia_aberta.csv — rode o extract primeiro")
        return
    carteira = staging.carregar_carteira()
    por_doc = staging.indice_por_documento(carteira)
    eventos: dict[str, dict] = {}
    situacoes, registros = [], 0

    # latin-1: o cadastro traz 'RECUPERAÇÃO' e 'GOIÂNIA'.
    with ARQUIVO.open(encoding="latin-1", newline="") as f:
        for linha in csv.DictReader(f, delimiter=";"):
            registros += 1
            doc = staging.so_digitos(linha.get("CNPJ_CIA"))
            cliente = por_doc.get(doc)
            if cliente is None:
                continue
            sit_emissor = (linha.get("SIT_EMISSOR") or "").strip().upper()
            sit_registro = (linha.get("SIT") or "").strip()

            # O cadastro da CVM tem a companhia em mais de uma linha quando há
            # histórico de registro. Guarda-se a situação e deixa-se o MERGE
            # resolver — mas a situação de CRISE nunca é sobrescrita por uma
            # linha de 'FASE OPERACIONAL' mais antiga: se houver qualquer
            # registro de RJ/falência, é ele que vale.
            situacoes.append({
                "cliente": cliente["id"],
                "documento": doc,
                "denominacao_cvm": (linha.get("DENOM_SOCIAL") or "").strip(),
                "sit_registro_cvm": sit_registro,
                "sit_emissor_cvm": sit_emissor,
                "data_sit_emissor": (linha.get("DT_INI_SIT_EMISSOR") or "").strip(),
                "setor_cvm": (linha.get("SETOR_ATIV") or "").strip(),
                "codigo_cvm": (linha.get("CD_CVM") or "").strip(),
                "situacao": SITUACOES.get(sit_emissor, (None, 0, ""))[2],
                "fonte": "CVM — cadastro de companhias abertas",
                "coletado_em": staging.hoje(), "confianca": 1.0,
            })

            if sit_emissor not in SITUACOES:
                continue
            tipo, severidade, _ = SITUACOES[sit_emissor]
            data = (linha.get("DT_INI_SIT_EMISSOR") or "").strip()
            if not data:
                # Sem data não dá para pôr no radar, e inventar a data de hoje
                # faria um evento de 2019 parecer de agora.
                print(f"  {doc}: {sit_emissor} sem DT_INI_SIT_EMISSOR — "
                      "situacao registrada, evento descartado")
                continue
            eid = f"CVM-{doc}-{tipo}-{data}"
            eventos[eid] = {
                "id": eid,
                "cliente": cliente["id"],
                "tipo": tipo,
                "data": data,
                "fonte": "CVM — cadastro de companhias abertas",
                "severidade": severidade,
                "descricao": (
                    f"Situacao do emissor na CVM: {sit_emissor} desde {data}. "
                    f"Denominacao registrada: "
                    f"{(linha.get('DENOM_SOCIAL') or '').strip()}"),
                "coletado_em": staging.hoje(),
                "confianca": 1.0,
            }

    print(f"  {registros} registro(s) no cadastro, {len(situacoes)} da carteira, "
          f"{len(eventos)} evento(s) de insolvencia")
    staging.escrever("eventos_cvm", [
        "id", "cliente", "tipo", "data", "fonte", "severidade", "descricao"],
        eventos.values())
    staging.escrever("situacao_cvm", [
        "cliente", "documento", "denominacao_cvm", "sit_registro_cvm",
        "sit_emissor_cvm", "data_sit_emissor", "setor_cvm", "codigo_cvm",
        "situacao"], situacoes)


FONTE = Fonte(
    id="cvm",
    nome="CVM — cadastro de companhias abertas",
    url=URL,
    orgao="Comissão de Valores Mobiliários",
    periodicidade="diária",
    extract=extract,
    transform=transform,
    cobertura=[
        Cobertura(":Evento{tipo:'pedido_rj'} + SOBRE Cliente", "real", 1.0,
                  "CORRIGE O QUE datajud.py AFIRMA. SIT_EMISSOR='EM RECUPERACAO "
                  "JUDICIAL OU EQUIVALENTE' + DT_INI_SIT_EMISSOR, com CNPJ, em "
                  "CSV aberto. Ex.: AGROGALAXY (GO), 21.240.146/0001-84, desde "
                  "2024-09-18. O gatilho da demo TEM fonte publica — para "
                  "companhia registrada na CVM."),
        Cobertura(":Evento{tipo:'falencia'} (novo tipo)", "real", 1.0,
                  "SIT_EMISSOR='FALIDA'. 22 companhias no cadastro atual."),
        Cobertura(":Evento{tipo:'recuperacao_extrajudicial'} (novo)", "real", 1.0,
                  "SIT_EMISSOR='EM RECUPERACAO EXTRAJUDICIAL'."),
        Cobertura(":Cliente.situacao", "real", 1.0,
                  "Deriva de SIT_EMISSOR. E o campo que a Q2 usa como override "
                  "de rating D — aqui ele deixa de ser digitado a mao."),
        Cobertura("Cobertura da carteira", "parcial", 1.0,
                  "LIMITE GRANDE: so ~755 companhias tem registro ativo na CVM "
                  "no Brasil inteiro. Produtor rural PF nao esta aqui; Ltda "
                  "fechada nao esta aqui. Cobre a cauda de MAIOR exposicao "
                  "individual (S.A. aberta, emissor de CRA, veiculo de "
                  "securitizacao do agro), nao a carteira."),
        Cobertura("Produtor rural PF e Ltda fechada em RJ", "sintetico", 0.0,
                  "Continua sem fonte publica aberta: DJE (PDF por comarca), API "
                  "comercial paga, ou a intimacao que a Krilltech recebe como "
                  "credora no processo."),
    ],
)
