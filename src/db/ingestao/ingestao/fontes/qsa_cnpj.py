"""QSA / cadastro CNPJ — Receita Federal, via BrasilAPI.

POR QUE NAO O DUMP DA RECEITA. O repositório oficial
(arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/) é um Nextcloud
cujo download direto não responde a URL previsível — todos os padrões
publicados em tutoriais devolvem 404 hoje (verificado em 12/09/2026). Além
disso são ~5 GB mensais para extrair algumas dezenas de CNPJ. A BrasilAPI serve
o MESMO dado da Receita por CNPJ, que é exatamente o recorte que a carteira
precisa. O dump volta a valer se um dia o Lastro precisar varrer o país para
DESCOBRIR vínculos fora da carteira — hoje ele só confirma os de dentro.

O QUE ESTA FONTE ENTREGA DE VERDADE:
  :Cliente  razão social, UF, município, porte, CNAE, situação cadastral  -> real
  :Socio    nome, qualificação, data de entrada                           -> real
  TEM_SOCIO a aresta existe                                               -> parcial

O QUE ELA NAO ENTREGA — e isso muda o peso 0,70 do motor:
  1. A QSA pública NAO tem percentual de participação. Só `qualificacao_socio`
     ("Sócio-Administrador", "Diretor"). Logo `TEM_SOCIO.participacao` não tem
     fonte pública: ou vem do contrato social (interno), ou é sintético.
  2. O CPF do sócio vem MASCARADO ('***912137**'). Para dizer que o sócio de
     CLI001 é o MESMO de CLI002 sobram 6 dígitos do CPF + o nome completo. Isso
     é casamento probabilístico, não identidade. Vai para o grafo com
     confianca=0.85 e nunca como fato fechado.
"""
import json
import re
import time
import unicodedata
from datetime import date, timedelta

import httpx

from ingestao import config, http, staging
from ingestao.fontes.base import Cobertura, Fonte

API = "https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
BRUTO = config.RAW / "qsa"

# A BrasilAPI encadeia provedores com limite de taxa. 2s entre chamadas passa
# para uma carteira de dezenas de CNPJ; em milhares, troque por um dump.
ESPERA = 2.0
CONFIANCA_SOCIO = 0.85  # CPF mascarado: identidade é inferida, não lida


def _slug(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z0-9]+", "-", sem_acento.upper()).strip("-")


def id_socio(nome: str, cpf_mascarado: str) -> str:
    """Identidade do sócio entre empresas diferentes.

    Os 6 dígitos visíveis do CPF entram na chave porque dois 'JOSE DA SILVA'
    em QSAs distintos são pessoas distintas com altíssima probabilidade se os
    dígitos diferirem — e o nome sozinho é colisão garantida num país com
    homônimos. A chave é determinística para que rodar o pipeline duas vezes
    não crie dois nós para a mesma pessoa.
    """
    return f"SOC-{staging.so_digitos(cpf_mascarado) or 'SEMDOC'}-{_slug(nome)[:40]}"


def _porte(bruto: str | None) -> str:
    """Porte da Receita -> vocabulario do esquema. Vazio quando nao da para dizer.

    O esquema usa pequeno/medio/grande. A Receita usa MICRO EMPRESA, EMPRESA DE
    PEQUENO PORTE e DEMAIS — e 'DEMAIS' significa "tudo acima de EPP", ou seja
    engloba medio E grande sem distinguir. Mapear DEMAIS para 'grande' marcaria
    toda S.A. media como grande; mapear para 'medio' faria o contrario. A
    distincao medio/grande e classificacao comercial da Krilltech (faturamento,
    area plantada, limite de credito), nao dado da Receita.

    Entao DEMAIS sai VAZIO, e `porte_receita` guarda o valor cru. Vazio o loader
    nao grava, e a ausencia fica visivel em vez de virar um 'grande' inventado.
    """
    texto = (bruto or "").strip().upper()
    if texto.startswith("MICRO") or "PEQUENO PORTE" in texto:
        return "pequeno"
    return ""


def extract() -> None:
    carteira = staging.carregar_carteira()
    BRUTO.mkdir(parents=True, exist_ok=True)
    pessoas_juridicas = [c for c in carteira if len(c["doc"]) == 14]
    pf = len(carteira) - len(pessoas_juridicas)
    if pf:
        print(f"  {pf} cliente(s) PF ignorado(s): nao ha QSA de pessoa fisica "
              "(produtor rural PF nao tem quadro societario publico)")

    for i, cliente in enumerate(pessoas_juridicas, 1):
        destino = BRUTO / f"{cliente['doc']}.json"
        if destino.exists() and destino.stat().st_size > 0:
            print(f"  [{i}/{len(pessoas_juridicas)}] cache: {cliente['doc']}")
            continue
        for tentativa in range(4):
            try:
                dados = http.json_get(API.format(cnpj=cliente["doc"]))
                destino.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
                razao = (dados.get("razao_social") or "")[:40]
                print(f"  [{i}/{len(pessoas_juridicas)}] ok: {cliente['doc']} {razao}")
                break
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    # CNPJ inexistente na Receita é achado, não erro de rede:
                    # registra e segue, para aparecer no relatório de cobertura.
                    print(f"  [{i}/{len(pessoas_juridicas)}] NAO ENCONTRADO na Receita: "
                          f"{cliente['doc']}")
                    break
                espera = ESPERA * (2 ** tentativa)
                print(f"  [{i}/{len(pessoas_juridicas)}] HTTP {e.response.status_code}, "
                      f"retry em {espera:.0f}s")
                time.sleep(espera)
        else:
            raise SystemExit(f"BrasilAPI falhou 4x para {cliente['doc']} — aborta "
                             "para nao gravar carteira parcial silenciosamente")
        time.sleep(ESPERA)


def transform() -> None:
    carteira = staging.carregar_carteira()
    por_doc = staging.indice_por_documento(carteira)
    clientes, socios, eventos = [], [], []
    corte_qsa = (date.today() - timedelta(days=180)).isoformat()

    for arquivo in sorted(BRUTO.glob("*.json")):
        cliente = por_doc.get(arquivo.stem)
        if cliente is None:
            continue
        doc = arquivo.stem
        d = json.loads(arquivo.read_text(encoding="utf-8"))

        clientes.append({
            "id": cliente["id"],
            "nome": d.get("razao_social") or cliente.get("nome", ""),
            "documento": doc,
            # `tipo` (produtor_pj / produtor_pf / revenda) é classificação
            # COMERCIAL da Krilltech, não da Receita: o CNAE diz o que a empresa
            # faz, não o papel dela na carteira. Vem da carteira de entrada, e é
            # propriedade do esquema — sem ela o dossiê não sabe se o cliente é
            # produtor ou revenda.
            "tipo": cliente.get("tipo", ""),
            "uf": d.get("uf", ""),
            "municipio": d.get("municipio", ""),
            "codigo_municipio_ibge": (d.get("codigo_municipio_ibge")
                                      or cliente.get("codigo_municipio_ibge", "")),
            "porte": _porte(d.get("porte")),
            # Valor cru da Receita preservado: 'demais' é informação real, só não
            # é o vocabulário do esquema.
            "porte_receita": (d.get("porte") or "").lower(),
            "cnae": d.get("cnae_fiscal", ""),
            "cnae_descricao": d.get("cnae_fiscal_descricao", ""),
            "situacao_cadastral": d.get("descricao_situacao_cadastral", ""),
            "data_inicio_atividade": d.get("data_inicio_atividade", ""),
            "fonte": "Receita Federal (QSA via BrasilAPI)",
            "coletado_em": staging.hoje(),
            "confianca": 1.0,
        })

        for s in d.get("qsa") or []:
            nome = (s.get("nome_socio") or "").strip()
            if not nome:
                continue
            mascarado = s.get("cnpj_cpf_do_socio") or ""
            entrada = s.get("data_entrada_sociedade") or ""
            socios.append({
                "cliente": cliente["id"],
                "socio_id": id_socio(nome, mascarado),
                "socio_nome": nome,
                # O esquema (01-schema-e-seed.cypher) chama este campo de
                # `documento`, e no seed ele tambem e mascarado
                # ('***.456.789-**'). Gravar so como `documento_mascarado`
                # deixava `s.documento` nulo para os 54 socios reais, e qualquer
                # query do dossiê que leia `documento` nao acharia nada.
                "documento": mascarado,
                "documento_mascarado": mascarado,
                "qualificacao": s.get("qualificacao_socio") or "",
                "data_entrada": entrada,
                # participacao fica VAZIA de propósito: a QSA pública não publica
                # percentual. Preencher com 0 ou 1 seria inventar número que o
                # motor usaria como se fosse medido.
                "participacao": "",
                "fonte": "Receita Federal (QSA via BrasilAPI)",
                "coletado_em": staging.hoje(),
                "confianca": CONFIANCA_SOCIO,
            })

            # Entrada recente de sócio é o evento `alteracao_qsa` do motor
            # (severidade 0.4 no seed). Saída de sócio exigiria comparar dois
            # snapshots — ver nota de cobertura.
            if entrada and entrada >= corte_qsa:
                sufixo = staging.so_digitos(mascarado) or _slug(nome)[:12]
                eventos.append({
                    "id": f"QSA-{doc}-{sufixo}-{entrada}",
                    "cliente": cliente["id"],
                    "tipo": "alteracao_qsa",
                    "data": entrada,
                    "fonte": "Receita Federal (QSA via BrasilAPI)",
                    "severidade": 0.4,
                    "descricao": (f"Entrada de {nome} no quadro societario como "
                                  f"{s.get('qualificacao_socio') or 'socio'}"),
                    "coletado_em": staging.hoje(),
                    "confianca": 1.0,
                })

    staging.escrever("clientes", [
        "id", "nome", "documento", "tipo", "uf", "municipio", "codigo_municipio_ibge",
        "porte", "porte_receita", "cnae", "cnae_descricao", "situacao_cadastral",
        "data_inicio_atividade"], clientes)
    staging.escrever("socios", [
        "cliente", "socio_id", "socio_nome", "documento", "documento_mascarado",
        "qualificacao", "data_entrada", "participacao"], socios)
    staging.escrever("eventos_qsa", [
        "id", "cliente", "tipo", "data", "fonte", "severidade", "descricao"], eventos)


FONTE = Fonte(
    id="qsa",
    nome="Receita Federal — cadastro CNPJ e QSA",
    url="https://brasilapi.com.br/api/cnpj/v1/{cnpj}",
    orgao="Receita Federal do Brasil",
    periodicidade="mensal na origem; consulta sob demanda",
    extract=extract,
    transform=transform,
    cobertura=[
        Cobertura(":Cliente.nome / .uf / .municipio", "real", 1.0,
                  "Razao social e endereco do cadastro CNPJ."),
        Cobertura(":Cliente.porte", "parcial", 1.0,
                  "VOCABULARIOS INCOMPATIVEIS. O esquema usa pequeno/medio/"
                  "grande; a Receita usa MICRO EMPRESA / EMPRESA DE PEQUENO "
                  "PORTE / DEMAIS, e 'DEMAIS' engloba medio E grande sem "
                  "distinguir. Micro e EPP viram 'pequeno'; DEMAIS fica VAZIO "
                  "(valor cru preservado em `porte_receita`). A distincao "
                  "medio/grande e classificacao comercial da Krilltech."),
        Cobertura(":Cliente.cnae / .situacao_cadastral", "real", 1.0,
                  "Campos novos, nao existiam no seed. Situacao cadastral "
                  "('BAIXADA', 'SUSPENSA') e red flag de graca."),
        Cobertura(":Socio.nome / .qualificacao", "real", 1.0,
                  "Quadro societario completo da PJ."),
        Cobertura(":Socio.documento", "parcial", 1.0,
                  "CPF MASCARADO ('***912137**'), como no seed. O campo existe e "
                  "e real, mas nao identifica a pessoa — e por isso que a "
                  "identidade entre duas empresas fica em confianca 0,85."),
        Cobertura(":Cliente.tipo", "interno", 1.0,
                  "produtor_pj / produtor_pf / revenda e classificacao COMERCIAL "
                  "da Krilltech: o CNAE diz o que a empresa faz, nao o papel "
                  "dela na carteira. Vem da carteira de entrada."),
        Cobertura("(:Cliente)-[:TEM_SOCIO]->(:Socio)", "parcial", 0.85,
                  "A aresta e real, a IDENTIDADE do socio entre duas empresas e "
                  "inferida: CPF vem mascarado ('***912137**'), casa-se por 6 "
                  "digitos + nome. E o vetor de peso 0,70 do motor — sustenta "
                  "investigacao, nao decisao automatica."),
        Cobertura("TEM_SOCIO.participacao", "interno", 0.0,
                  "A QSA publica NAO publica percentual de participacao. So sai "
                  "do contrato social / cadastro da Krilltech."),
        Cobertura(":Evento{tipo:'alteracao_qsa'} (entrada de socio)", "real", 1.0,
                  "Derivado de data_entrada_sociedade < 180 dias."),
        Cobertura(":Evento{tipo:'alteracao_qsa'} (SAIDA de socio)", "parcial", 0.0,
                  "A QSA e um retrato do agora: quem saiu nao aparece. Exige "
                  "guardar snapshots e comparar — o pipeline grava o JSON bruto "
                  "em data/raw/qsa/ justamente para viabilizar isso no 2o mes."),
        Cobertura(":Socio de cliente PF", "parcial", 0.0,
                  "Produtor rural PF nao tem QSA. Cobrir exige CPF->empresas, "
                  "que a Receita nao publica."),
        Cobertura(":GrupoEconomico + PERTENCE_A", "sintetico", 0.0,
                  "NAO EXISTE base publica de grupo economico no Brasil. E o "
                  "vetor de maior peso do motor (0,90) e o mais fragil de "
                  "alimentar: ou vem do cadastro da Krilltech, ou e INFERIDO "
                  "(socio em comum + mesmo endereco) — e ai e hipotese, nao fato."),
    ],
)
