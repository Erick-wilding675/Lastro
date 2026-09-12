"""Preenche sinteticamente o que nenhuma fonte pública entrega — declarado.

Existe porque o núcleo do grafo (recebível, garantia, avalista, grupo, lavoura,
atraso) é dado do ERP da Krilltech, e sem ele o motor não roda: sem exposição
não há score, não há matriz de red flags e não há recomendação de estratégia.
Enquanto o export do ERP não chega, isto ocupa o lugar — **sempre marcado**.

TODA linha gerada aqui sai com `fonte='SINTÉTICO — demo'` e `sintetico=true` no
nó e na aresta. Nenhuma consulta precisa adivinhar o que é medido e o que é
inventado: `MATCH (n) WHERE n.sintetico IS NULL` devolve só o real.

---
A LINHA QUE ESTE MÓDULO NÃO CRUZA

Os clientes da carteira de teste são companhias ABERTAS, com nome e CNPJ
públicos. Inventar fato sobre elas não é o mesmo que inventar um número.

  PODE — quantitativo proprietário. Recebível, valor, garantia, dias de atraso,
  hectares. Ninguém lê como fato público, porque não existe fonte pública disso.

  PODE, COM FICÇÃO EXPLÍCITA — vínculo entre empresas. Grupo econômico e
  avalista em comum são o coração do motor (pesos 0,90 e 0,85) e precisam
  existir para a demo. Então existem, mas o NOME do nó diz que é fictício:
  "Grupo Fictício Alfa (SINTÉTICO)". Um print do Bloom não engana ninguém.

  NÃO PODE — fato regulatório, ambiental ou jurídico sobre empresa real.
  `reserva_legal_ok=false` na SLC Agrícola, ou `pedido_rj` em quem não pediu,
  é afirmação falsa sobre entidade identificável, e continuar marcando
  "sintético" não conserta. Esses campos ficam VAZIOS, e a lacuna vai para a
  matriz de cobertura. A única RJ no grafo é a da AgroGalaxy, que é real e vem
  da CVM.

  NÃO PODE — sócio em comum inventado. Criar um vínculo societário falso entre
  duas empresas reais é inventar fato sobre as PESSOAS FÍSICAS do QSA, que têm
  nome no grafo. O que este módulo faz é só acrescentar `participacao` às
  arestas TEM_SOCIO que a Receita já confirmou.

---
DE ONDE VEM O "TEOR REAL"

Os números não são aleatórios sobre o nada — são escalados por dado que o
pipeline já ingeriu:

  hectares      fração plausível da área REALMENTE colhida no município do
                cliente, segundo a PAM/IBGE (tabela 5457). Chapadão do Céu tem
                557.400 ha de soja colhida; um grande produtor ali opera alguns
                por cento disso, não 50.
  cultura       só culturas que a PAM registra NAQUELE município. Não se atribui
                algodão a quem está em município sem um hectare de algodão.
  valor         hectares x custo de insumo biológico por hectare (R$ 180-380/ha,
                faixa de mercado). O recebível é de venda de insumo, não o
                faturamento da empresa — é o que a Krilltech venderia a prazo.
  safra         SAF-2526, a safra em curso segundo a série da Conab.
  regiao        a microrregião real do IBGE, já resolvida.

---
DETERMINISMO. `random.Random(SEMENTE)` com semente fixa: rodar duas vezes gera
exatamente os mesmos recebíveis, com os mesmos ids. Sem isso, cada execução
criaria uma carteira nova e o MERGE acumularia recebíveis para sempre.

PRECEDÊNCIA. Se `data/interno/<arquivo>.csv` existir, o alvo correspondente NÃO
é gerado — dado real do ERP sempre vence o sintético.
"""
import random
from datetime import date, timedelta

from ingestao import config, staging
from ingestao.fontes.base import Cobertura, Fonte

SEMENTE = 20260912
PROCEDENCIA = "SINTÉTICO — demo"
INTERNO = config.RAIZ / "data" / "interno"

# Custo de insumo biológico por hectare, faixa de mercado. É o que dimensiona o
# recebível: a Krilltech vende insumo, então o título é do tamanho da lavoura
# atendida, não do faturamento do cliente.
CUSTO_INSUMO_HA = (180.0, 380.0)

# Fração da área colhida do município que um cliente grande opera. Mantida baixa
# de propósito: nenhuma empresa isolada planta metade de um município do Cerrado.
FRACAO_MUNICIPIO = (0.02, 0.09)

# A Krilltech é agtech recente (parceria UnB/EMBRAPA). Ancorar `cliente_desde`
# só na abertura da empresa produzia "cliente desde 1980" para a SLC Agrícola,
# fundada em 1977 — relacionamento anterior à existência do fornecedor.
PRIMEIRO_ANO_RELACIONAMENTO = 2016

# Distribuição de garantias, com o haircut que o score aplica em cada uma.
# Proporções escolhidas para que a carteira tenha os quatro casos que a Q2
# precisa exercitar, incluindo o pior (nenhuma).
GARANTIAS = [
    ("alienacao_fiduciaria", 1.00, 0.20),
    ("aval", 0.70, 0.30),
    ("cpr", 0.60, 0.25),
    ("penhor_safra", 0.50, 0.15),
    ("nenhuma", 0.00, 0.10),
]


def _existe_interno(arquivo: str) -> bool:
    return (INTERNO / arquivo).exists()


def _proc(extra: dict | None = None) -> dict:
    base = {"fonte": PROCEDENCIA, "coletado_em": staging.hoje(),
            # confianca 0.0 não é "dado ruim": é "não é medição". O motor pode
            # usar, o dossiê tem de mostrar.
            "confianca": 0.0, "sintetico": "true"}
    base.update(extra or {})
    return base


def extract() -> None:
    """Não há o que baixar: a entrada deste módulo é o próprio staging."""
    print("  fonte sintetica — sem download. Gera a partir de:")
    for n in ("clientes", "lavoura_municipio", "municipio_regiao", "safras", "socios"):
        print(f"     staging/{n}.csv: {len(staging.ler(n))} linha(s)")
    presentes = [a for a in ("recebiveis.csv", "avalistas.csv", "grupos.csv",
                             "planta.csv", "participacoes.csv")
                 if _existe_interno(a)]
    if presentes:
        print(f"  ERP tem {', '.join(presentes)} — esses alvos NAO serao sinteticos")


def _cliente_desde(inicio_atividade: str, hoje: date, rnd: random.Random) -> str:
    """Início do relacionamento com a Krilltech, nunca antes de a Krilltech existir.

    Ancorado na abertura real da empresa quando ela é posterior ao piso; senão o
    piso manda. Sem isso a SLC Agrícola (fundada em 1977) virava "cliente desde
    1980", o que descreve um relacionamento que não poderia ter existido.
    """
    piso = date(PRIMEIRO_ANO_RELACIONAMENTO, 1, 1)
    if len(inicio_atividade) == 10:
        try:
            abertura = date.fromisoformat(inicio_atividade)
            candidato = abertura + timedelta(days=rnd.randint(400, 3000))
            if candidato > piso:
                return min(candidato, hoje - timedelta(days=180)).isoformat()
        except ValueError:
            pass
    dias = (hoje - timedelta(days=180) - piso).days
    return (piso + timedelta(days=rnd.randint(0, max(1, dias)))).isoformat()


def _porte_cliente(hectares: float, registrada_cvm: bool) -> str:
    """Porte por área operada, com piso para companhia aberta.

    A área vem da PAM do município da SEDE, e para empresa cuja sede não é onde
    ela planta isso subestima muito: a SLC Agrícola tem sede em Porto Alegre e
    lavoura em MT, BA e GO, então a régua por hectares sozinha a classificaria
    como 'pequeno'. Registro ativo na CVM é evidência pública de que a companhia
    não é pequena — serve de piso.
    """
    if hectares > 5000:
        return "grande"
    if registrada_cvm:
        return "medio"
    return "medio" if hectares > 800 else "pequeno"


def transform() -> None:
    rnd = random.Random(SEMENTE)
    clientes = staging.ler("clientes")
    if not clientes:
        print("  staging/clientes.csv vazio — rode 'qsa' antes")
        return

    mun_regiao = {r["codigo_municipio_ibge"]: r["regiao"]
                  for r in staging.ler("municipio_regiao")}
    # município -> [(cultura, area_colhida_real)] ordenado da maior lavoura
    lavoura: dict[str, list[tuple[str, float]]] = {}
    for r in staging.ler("lavoura_municipio"):
        try:
            area = float(r["area_colhida_ha"])
        except (ValueError, KeyError):
            continue
        lavoura.setdefault(r["codigo_municipio_ibge"], []).append((r["cultura"], area))
    for v in lavoura.values():
        v.sort(key=lambda x: -x[1])

    # Quem a CVM diz estar em insolvência — usado para manter os títulos
    # coerentes com o fato real, e como piso de porte.
    situacoes = staging.ler("situacao_cvm")
    em_rj = {r["cliente"] for r in situacoes
             if r.get("situacao") in ("recuperacao_judicial", "falida",
                                      "recuperacao_extrajudicial")}
    registrada_cvm = {r["cliente"] for r in situacoes if r.get("cliente")}

    safras = [s["id"] for s in staging.ler("safras")]
    safra_atual = safras[-1] if safras else "SAF-2526"

    # ---------------- lavoura: PLANTA + hectares ----------------
    planta, hectares_cliente = [], {}
    for c in clientes:
        mun = (c.get("codigo_municipio_ibge") or "").strip()
        culturas = lavoura.get(mun, [])[:2]  # as duas maiores do município
        total = 0.0
        for cultura, area_mun in culturas:
            ha = round(area_mun * rnd.uniform(*FRACAO_MUNICIPIO))
            if ha < 10:
                continue
            total += ha
            planta.append({"cliente": c["id"], "cultura": cultura, "hectares": ha,
                           **_proc({"base_real": f"PAM/IBGE: {area_mun:.0f} ha de "
                                                 f"{cultura} colhidos no municipio "
                                                 f"{mun}"})})
        hectares_cliente[c["id"]] = total

    # ---------------- recebíveis ----------------
    hoje = date.today()
    recebiveis, atraso_max = [], {}
    for c in clientes:
        ha = hectares_cliente.get(c["id"], 0)
        if ha <= 0:
            # Sem lavoura atribuída (município sem PAM para as três culturas),
            # gera um título menor de revenda em vez de deixar o cliente sem
            # exposição — mas sem inventar hectare que a PAM não sustenta.
            ha = rnd.randint(300, 1200)
        n_titulos = rnd.randint(1, 3)
        for i in range(1, n_titulos + 1):
            fatia = ha / n_titulos
            valor = round(fatia * rnd.uniform(*CUSTO_INSUMO_HA), -3)
            if valor < 20000:
                valor = 20000.0
            emissao = hoje - timedelta(days=rnd.randint(120, 400))
            vencimento = emissao + timedelta(days=rnd.choice([180, 210, 240, 270]))
            dias = max(0, (hoje - vencimento).days)
            # Empresa em recuperação judicial com zero dias de atraso é
            # incoerente: a RJ é justamente o desfecho da inadimplência. Para
            # quem está em RJ pela CVM, os títulos vencem antes do pedido.
            if c["id"] in em_rj:
                vencimento = hoje - timedelta(days=rnd.randint(95, 260))
                emissao = vencimento - timedelta(days=rnd.choice([180, 210, 240]))
                dias = (hoje - vencimento).days

            tipos, _, pesos = zip(*[(g, h, p) for g, h, p in GARANTIAS])
            garantia = rnd.choices(tipos, weights=pesos, k=1)[0]
            cobertura = 0.0 if garantia == "nenhuma" else rnd.uniform(0.55, 1.0)

            if dias == 0:
                status, estagio, aberto = "aberto", "nenhum", valor
            elif dias < 30:
                status, estagio, aberto = "vencido", "nenhum", valor
            elif dias < 90:
                status, estagio, aberto = "vencido", "notificado", valor
            else:
                status, estagio, aberto = "vencido", "protestado", valor

            # A AgroGalaxy está em RJ de verdade (CVM, 18/09/2024): o estágio
            # jurídico dos títulos dela reflete isso, e é o que faz a Q4
            # recomendar habilitação no plano em vez de protesto.
            if c["id"] == "TST001" and dias > 0:
                estagio = "habilitado_rj"

            atraso_max[c["id"]] = max(atraso_max.get(c["id"], 0), dias)
            recebiveis.append({
                "id": f"SINT-{c['id']}-{i:02d}",
                "cliente": c["id"], "valor": valor, "valor_aberto": aberto,
                "data_emissao": emissao.isoformat(),
                "data_vencimento": vencimento.isoformat(),
                "dias_atraso": dias, "status": status,
                "garantia_tipo": garantia,
                "garantia_valor": round(valor * cobertura, -3),
                "estagio_juridico": estagio, "safra": safra_atual,
                **_proc({"base_real": f"dimensionado por {ha:.0f} ha x R$/ha de "
                                      "insumo biologico"})})

    # ---------------- avalistas (nomes explicitamente fictícios) -------------
    # O avalista em comum é o vetor de peso 0,85 do motor. Precisa existir para
    # a demo — e o nome precisa dizer que é ficção, porque as empresas nas duas
    # pontas do vínculo são reais.
    avalistas = []
    fic = [("AVA-SINT-001", "Avalista Ficticio Alfa (SINTETICO)", "pf"),
           ("AVA-SINT-002", "Garantidora Ficticia Beta Ltda (SINTETICO)", "pj")]
    com_aval = [r for r in recebiveis if r["garantia_tipo"] == "aval"]
    for r in com_aval:
        aid, nome, tipo = fic[hash(r["cliente"]) % len(fic)]
        avalistas.append({"recebivel": r["id"], "avalista_id": aid,
                          "avalista_nome": nome, "tipo": tipo,
                          "documento": "***.000.000-** (ficticio)", **_proc()})

    # ---------------- grupo econômico (idem) ----------------
    grupos = []
    ids = sorted(c["id"] for c in clientes)
    for i, cid in enumerate(ids):
        # Dois grupos, alternando, para que exista pelo menos um par por grupo e
        # o vetor de peso 0,90 tenha o que propagar.
        g = "GRP-SINT-A" if i % 2 == 0 else "GRP-SINT-B"
        nome = ("Grupo Ficticio Alfa (SINTETICO - nao e vinculo societario real)"
                if g.endswith("A") else
                "Grupo Ficticio Beta (SINTETICO - nao e vinculo societario real)")
        grupos.append({"cliente": cid, "grupo_id": g, "grupo_nome": nome, **_proc()})

    # ---------------- participação societária ----------------
    # Só nas arestas TEM_SOCIO que a Receita JÁ confirmou. Não se cria vínculo
    # societário novo: isso seria inventar fato sobre as pessoas do QSA.
    por_cliente: dict[str, list[str]] = {}
    for s in staging.ler("socios"):
        por_cliente.setdefault(s["cliente"], []).append(s["socio_id"])
    participacoes = []
    for cliente, socios in por_cliente.items():
        pesos = [rnd.random() for _ in socios]
        soma = sum(pesos) or 1.0
        for sid, p in zip(socios, pesos):
            participacoes.append({"cliente": cliente, "socio_id": sid,
                                  "participacao": round(p / soma, 4), **_proc()})

    # ---------------- atributos de cliente ----------------
    atributos = []
    for c in clientes:
        dias = atraso_max.get(c["id"], 0)
        # A situação da AgroGalaxy é REAL (CVM) e não pode ser sobrescrita por
        # uma derivada de atraso sintético.
        if c["id"] == "TST001":
            situacao = ""
        elif dias >= 90:
            situacao = "inadimplente"
        elif dias > 0:
            situacao = "atraso"
        else:
            situacao = "adimplente"
        inicio = (c.get("data_inicio_atividade") or "").strip()
        atributos.append({
            "cliente": c["id"],
            "dias_atraso_max": dias,
            "situacao": situacao,
            # cliente_desde é o início do relacionamento com a Krilltech, que é
            # sempre posterior à abertura da empresa. Ancorado na data real de
            # início de atividade quando ela existe.
            "cliente_desde": _cliente_desde(inicio, hoje, rnd),
            # porte: a Receita só diz 'DEMAIS' para todas estas. A faixa por área
            # operada é a régua do agro, e é declarada.
            "porte": _porte_cliente(hectares_cliente.get(c["id"], 0),
                                    c["id"] in registrada_cvm),
            **_proc({"base_real": "porte por area operada, com piso 'medio' para "
                                  "companhia registrada na CVM; situacao derivada "
                                  "do atraso dos titulos sinteticos"})})

    # ---------------- canal de revenda ----------------
    # TST001 é revenda de insumos de verdade (CNAE de holding, mas o grupo é
    # distribuidor). Os produtores comprando por ela é plausível e é o vetor
    # sistêmico de 0,65 — mas o vínculo comercial em si é inventado.
    compra_via = []
    revendas = [c["id"] for c in clientes if c.get("tipo") == "revenda"]
    if revendas:
        for c in clientes:
            if c["id"] in revendas or rnd.random() > 0.5:
                continue
            compra_via.append({"cliente": c["id"], "revenda": revendas[0],
                               "volume_safra": round(rnd.uniform(2e5, 3e6), -3),
                               **_proc()})

    escritos = []
    if not _existe_interno("planta.csv"):
        staging.escrever("planta", ["cliente", "cultura", "hectares", "base_real"], planta)
        escritos.append("planta")
    if not _existe_interno("recebiveis.csv"):
        staging.escrever("recebiveis", [
            "id", "cliente", "valor", "valor_aberto", "data_emissao",
            "data_vencimento", "dias_atraso", "status", "garantia_tipo",
            "garantia_valor", "estagio_juridico", "safra", "base_real"], recebiveis)
        escritos.append("recebiveis")
    if not _existe_interno("avalistas.csv"):
        staging.escrever("avalistas", [
            "recebivel", "avalista_id", "avalista_nome", "tipo", "documento"], avalistas)
        escritos.append("avalistas")
    if not _existe_interno("grupos.csv"):
        staging.escrever("grupos", ["cliente", "grupo_id", "grupo_nome"], grupos)
        escritos.append("grupos")
    if not _existe_interno("participacoes.csv"):
        staging.escrever("participacoes", ["cliente", "socio_id", "participacao"],
                         participacoes)
        escritos.append("participacoes")
    staging.escrever("atributos_sinteticos", [
        "cliente", "dias_atraso_max", "situacao", "cliente_desde", "porte",
        "base_real"], atributos)
    staging.escrever("compra_via", ["cliente", "revenda", "volume_safra"], compra_via)

    total = sum(r["valor_aberto"] for r in recebiveis)
    print(f"  gerado: {len(recebiveis)} recebiveis, exposicao sintetica "
          f"R$ {total:,.0f}")
    print(f"  arquivos: {', '.join(escritos)}, atributos_sinteticos, compra_via")


FONTE = Fonte(
    id="sintetico",
    nome="SINTÉTICO — preenche o que nenhuma fonte pública entrega",
    url="(gerado a partir do staging, com semente fixa)",
    orgao="—",
    periodicidade="sob demanda",
    extract=extract,
    transform=transform,
    passo_manual=(
        "Substituir pelo export real do ERP em data/interno/*.csv. Qualquer "
        "arquivo que exista la tem precedencia e o alvo deixa de ser sintetico."),
    cobertura=[
        Cobertura(":Recebivel + DE (SINTETICO)", "sintetico", 0.0,
                  "Valor dimensionado por hectares x custo de insumo biologico "
                  "(R$ 180-380/ha), e os hectares vem da area REALMENTE colhida "
                  "no municipio segundo a PAM/IBGE. Numero inventado, escala "
                  "real."),
        Cobertura(":Recebivel.garantia_tipo (SINTETICO)", "sintetico", 0.0,
                  "Distribuicao escolhida para exercitar os quatro haircuts da "
                  "Q2, inclusive 'nenhuma'."),
        Cobertura("(:Cliente)-[:PLANTA]->(:Cultura) (SINTETICO)", "sintetico", 0.0,
                  "So culturas que a PAM registra NAQUELE municipio — nao se "
                  "atribui algodao a quem esta onde nao ha algodao. A atribuicao "
                  "ao cliente e que e inventada."),
        Cobertura(":GrupoEconomico + PERTENCE_A (SINTETICO)", "sintetico", 0.0,
                  "Vetor de peso 0,90 do motor. Os nos se chamam 'Grupo Ficticio "
                  "Alfa/Beta (SINTETICO)' porque as empresas nas pontas sao "
                  "reais e um print nao pode sugerir vinculo societario que nao "
                  "existe."),
        Cobertura(":Avalista + GARANTIDO_POR (SINTETICO)", "sintetico", 0.0,
                  "Vetor de peso 0,85. Mesma regra: nome do no diz que e ficcao."),
        Cobertura("TEM_SOCIO.participacao (SINTETICO)", "sintetico", 0.0,
                  "Percentual acrescentado SO a arestas que a Receita ja "
                  "confirmou. Nao se cria vinculo societario novo: isso seria "
                  "inventar fato sobre as pessoas fisicas nomeadas no QSA."),
        Cobertura(":Cliente.dias_atraso_max / .situacao (SINTETICO)", "sintetico", 0.0,
                  "Derivados dos titulos sinteticos, coerentes entre si. A "
                  "situacao da AgroGalaxy NAO e sobrescrita: a RJ dela e real e "
                  "vem da CVM."),
        Cobertura(":Imovel.area_ha / .reserva_legal_ok", "bloqueado", 0.0,
                  "NAO SINTETIZADO DE PROPOSITO. Sao os dois imoveis embargados "
                  "de empresas reais e nomeadas; inventar irregularidade de "
                  "reserva legal e afirmacao falsa sobre entidade identificavel, "
                  "e rotular 'sintetico' nao conserta. Fica a lacuna do SICAR."),
        Cobertura(":Evento{tipo:'pedido_rj'} para os demais clientes", "bloqueado", 0.0,
                  "NAO SINTETIZADO. A unica RJ no grafo e a da AgroGalaxy, que e "
                  "real (CVM, 18/09/2024). Inventar pedido de RJ para companhia "
                  "aberta que nao pediu e o pior fato falso possivel neste "
                  "dominio."),
    ],
)
