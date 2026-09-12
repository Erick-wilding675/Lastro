"""IBAMA — áreas embargadas (Termos de Embargo).

Segunda fonte que publica CPF/CNPJ do autuado, então também fecha join
determinístico com a carteira. ~148 MB de CSV, atualizado diariamente
(Last-Modified verificado em 11/09/2026).

Layout verificado (separador ';', campos citados com '"'):
  SEQ_TAD;NUM_TAD;SER_TAD;DAT_EMBARGO;DAT_ULT_ALTERACAO;COD_UF_TAD;SIG_UF_TAD;
  COD_MUNICIPIO_TAD;NOM_MUNICIPIO_TAD;NUM_LONGITUDE_TAD;NUM_LATITUDE_TAD;...;
  NOME_IMOVEL;DES_LOCALIZACAO_TAD;NOME_PESSOA_EMBARGADA;CPF_CNPJ_EMBARGADO;
  SIT_DESMATAMENTO;...;QTD_AREA_EMBARGADA;...;WKT_GEOM_AREA_EMBARGADA;...;
  QTD_AREA_DESMATADA;DES_INFRACAO;COD_TIPO_BIOMA;DES_TIPO_BIOMA

ATENCAO AO QUE ISSO *NAO* É. O seed modela `:Imovel` com id de CAR
('CAR-GO-0001'), `area_ha` e `reserva_legal_ok`. O IBAMA não publica código do
CAR nem situação de reserva legal — ele publica o imóvel pelo nome e pela
geometria do embargo. Então:
  - `:Imovel.embargo_ibama = true` sai daqui, real;
  - `:Imovel.id` como código do CAR e `:Imovel.reserva_legal_ok` só saem do
    SICAR, que hoje é bloqueado por captcha (ver sicar_car.py).
O id usado aqui é o do próprio termo de embargo, e isso é honesto: o que se
conhece é o embargo, não a matrícula.
"""
import csv
from datetime import date, timedelta

from ingestao import config, http, staging
from ingestao.fontes.base import Cobertura, Fonte

URL = "https://servicos.ibama.gov.br/ctf/publico/areasembargadas/arquivos/areas_embargadas.csv"
ARQUIVO = config.RAW / "ibama" / "areas_embargadas.csv"

# Severidade do seed para embargo_ambiental. Mantida para não criar régua nova.
SEVERIDADE = 0.55
# Embargo é ato de efeito continuado: não "vence" em 180 dias como um protesto.
# Mas para o radar de eventos (janela de 90/180 dias) só faz sentido acender o
# que é recente OU ainda em desmatamento ativo.
JANELA_RADAR_DIAS = 730


def extract() -> None:
    http.baixar(URL, ARQUIVO)


def transform() -> None:
    if not ARQUIVO.exists():
        print("  ausente: areas_embargadas.csv — rode o extract primeiro")
        return
    carteira = staging.carregar_carteira()
    por_doc = staging.indice_por_documento(carteira)
    imoveis: dict[str, dict] = {}
    eventos: dict[str, dict] = {}
    lidas = casadas = 0
    corte = (date.today() - timedelta(days=JANELA_RADAR_DIAS)).isoformat()

    # utf-8 confirmado no arquivo real ("Imaruí", "Apiacás" legíveis).
    # errors='replace' para que um byte solto não derrube 148 MB de ingestão.
    with ARQUIVO.open(encoding="utf-8", errors="replace", newline="") as f:
        for linha in csv.DictReader(f, delimiter=";"):
            lidas += 1
            if lidas % 200_000 == 0:
                print(f"  {lidas:,} termos lidos, {casadas} da carteira")
            doc = staging.so_digitos(linha.get("CPF_CNPJ_EMBARGADO"))
            cliente = por_doc.get(doc)
            if cliente is None:
                continue
            data = staging.data_br(linha.get("DAT_EMBARGO"))
            if not data:
                continue
            casadas += 1

            seq = (linha.get("SEQ_TAD") or "").strip()
            area = (linha.get("QTD_AREA_EMBARGADA") or "").replace(",", ".").strip()
            try:
                area_ha = float(area) if area else None
            except ValueError:
                area_ha = None

            imovel_id = f"IBAMA-TAD-{seq}"
            imoveis[imovel_id] = {
                "id": imovel_id,
                "cliente": cliente["id"],
                "nome": (linha.get("NOME_IMOVEL") or "").strip() or "(sem nome no termo)",
                "municipio": (linha.get("NOM_MUNICIPIO_TAD") or "").strip(),
                "codigo_municipio_ibge": (linha.get("COD_MUNICIPIO_TAD") or "").strip(),
                "uf": (linha.get("SIG_UF_TAD") or "").strip(),
                "area_embargada_ha": area_ha if area_ha is not None else "",
                "embargo_ibama": "true",
                # reserva_legal_ok NAO vem do IBAMA. Deixado vazio de propósito:
                # o loader não grava propriedade vazia, então o grafo fica com a
                # ausência visível em vez de um false inventado.
                "reserva_legal_ok": "",
                "bioma": (linha.get("DES_TIPO_BIOMA") or "").strip(),
                "fonte": "IBAMA — áreas embargadas",
                "coletado_em": staging.hoje(),
                "confianca": 1.0,
            }

            desmatamento_ativo = (linha.get("SIT_DESMATAMENTO") or "").strip().upper() == "D"
            if data >= corte or desmatamento_ativo:
                eid = f"IBAMA-{seq}"
                infracao = (linha.get("DES_INFRACAO") or "").strip()
                # Estar nesta lista significa embargo EM VIGOR: o IBAMA remove o
                # termo quando é levantado ou prescreve. Então um embargo de 1995
                # que aparece aqui é restrição viva, não história — mas a DATA é
                # a do termo, e num radar de "últimos 90 dias" isso engana. A
                # descrição diz a idade para que a leitura não confunda as duas
                # coisas, e `:Imovel.embargo_ibama` é quem carrega a condição
                # permanente (é o que a matriz de red flags consulta).
                idade = date.today().year - int(data[:4])
                eventos[eid] = {
                    "id": eid,
                    "cliente": cliente["id"],
                    "tipo": "embargo_ambiental",
                    "data": data,
                    "fonte": "IBAMA — áreas embargadas",
                    "severidade": SEVERIDADE,
                    "descricao": (
                        f"Embargo EM VIGOR de {area_ha or '?'} ha em "
                        f"{linha.get('NOM_MUNICIPIO_TAD', '').strip()}/"
                        f"{linha.get('SIG_UF_TAD', '').strip()}"
                        + (f", termo de {data} ({idade} anos)" if idade >= 2 else "")
                        + (f" — {infracao[:160]}" if infracao else "")),
                    "imovel": imovel_id,
                    "vigente": "true",
                    "idade_anos": idade,
                    "desmatamento_ativo": "true" if desmatamento_ativo else "false",
                    "coletado_em": staging.hoje(),
                    "confianca": 1.0,
                }

    print(f"  total: {lidas:,} termos varridos, {casadas} pertencem a carteira")
    staging.escrever("imoveis", [
        "id", "cliente", "nome", "municipio", "codigo_municipio_ibge", "uf",
        "area_embargada_ha", "embargo_ibama", "reserva_legal_ok", "bioma"],
        imoveis.values())
    staging.escrever("eventos_ibama", [
        "id", "cliente", "tipo", "data", "fonte", "severidade", "descricao",
        "imovel", "vigente", "idade_anos", "desmatamento_ativo"], eventos.values())


FONTE = Fonte(
    id="ibama",
    nome="IBAMA — áreas embargadas",
    url=URL,
    orgao="IBAMA",
    periodicidade="diária",
    extract=extract,
    transform=transform,
    cobertura=[
        Cobertura(":Evento{tipo:'embargo_ambiental'} + SOBRE Cliente", "real", 1.0,
                  "Fonte publica CPF_CNPJ_EMBARGADO: join deterministico."),
        Cobertura(":Imovel.embargo_ibama", "real", 1.0,
                  "E o proprio objeto do termo de embargo. Estar na lista = "
                  "embargo EM VIGOR (o IBAMA retira o termo quando levantado). "
                  "Esta propriedade e quem deve alimentar a matriz de red flags; "
                  "o :Evento serve ao radar por data."),
        Cobertura(":Evento.data de embargo vs radar de 90 dias", "parcial", 0.8,
                  "A data e a do TERMO, nao do 'agora'. Ha embargos vigentes de "
                  "1995 nesta base. O radar por janela curta nao os mostra, "
                  "embora sejam restricao viva — por isso os campos `vigente` e "
                  "`idade_anos` acompanham o evento."),
        Cobertura("(:Cliente)-[:POSSUI]->(:Imovel)", "parcial", 0.9,
                  "O termo liga o autuado ao imovel embargado. Cobre so os "
                  "imoveis COM embargo — nao e o inventario de imoveis do "
                  "cliente, e a lista dos que tem problema."),
        Cobertura(":Imovel.id como codigo do CAR", "bloqueado", 0.0,
                  "O IBAMA identifica o imovel por nome e geometria, nao por "
                  "codigo do CAR. O id usado e o do termo (IBAMA-TAD-*)."),
        Cobertura(":Imovel.area_ha (area total)", "bloqueado", 0.0,
                  "O campo disponivel e QTD_AREA_EMBARGADA, que e a area "
                  "EMBARGADA, nao a area do imovel. Confundir as duas "
                  "superestimaria o dano. Area total so do SICAR."),
        Cobertura(":Imovel.reserva_legal_ok", "bloqueado", 0.0,
                  "Nao existe no IBAMA. Exclusivo do SICAR."),
    ],
)
