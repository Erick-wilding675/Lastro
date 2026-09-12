"""Dados internos da Krilltech — o ERP. Metade do grafo sai daqui, e só daqui.

NENHUMA FONTE PÚBLICA NO BRASIL PUBLICA RECEBÍVEL PRIVADO. Isso não é lacuna de
pesquisa, é como deve ser: o que a Krilltech vendeu a prazo para quem, com que
garantia e com quantos dias de atraso é segredo comercial das duas partes. O
pipeline público enriquece o CONTEXTO de risco dos clientes; o núcleo da
exposição é interno por natureza.

Este módulo não baixa nada: ele LÊ arquivos que uma pessoa coloca em
data/interno/ e os normaliza para o mesmo staging das fontes públicas, para que
o loader não precise saber de onde veio o quê.

ARQUIVOS ESPERADOS (todos opcionais — o que faltar simplesmente não é staged):

  data/interno/recebiveis.csv
    id,cliente,valor,valor_aberto,data_emissao,data_vencimento,dias_atraso,
    status,garantia_tipo,garantia_valor,estagio_juridico,safra
  data/interno/avalistas.csv
    recebivel,avalista_id,avalista_nome,tipo,documento
  data/interno/grupos.csv
    cliente,grupo_id,grupo_nome
  data/interno/planta.csv
    cliente,cultura,hectares
  data/interno/participacoes.csv
    cliente,socio_id,participacao
  data/interno/imoveis.csv
    id,cliente,area_ha,reserva_legal_ok,codigo_municipio_ibge

O CAMPO `fonte` DE CADA LINHA FICA 'Krilltech — ERP (interno)'. Isso importa:
na tela e no dossiê, o gestor vê que o valor veio do sistema dele e o evento
veio da PGFN. Hard Rule #3 — exposição sempre explica o caminho, e o caminho
inclui a procedência.

SE UM DESSES ARQUIVOS NÃO EXISTIR e o time decidir gerar sintético para a demo,
o sintético deve vir com fonte='SINTÉTICO — demo' e nunca herdar
'Krilltech — ERP'. Ver src/db/cypher/01-schema-e-seed.cypher, que é exatamente
isso: sintético declarado.
"""
import csv

from ingestao import config, staging
from ingestao.fontes.base import Cobertura, Fonte

INTERNO = config.RAIZ / "data" / "interno"
PROCEDENCIA = "Krilltech — ERP (interno)"

# arquivo de entrada -> (nome no staging, colunas preservadas)
MAPA = {
    "recebiveis.csv": ("recebiveis", [
        "id", "cliente", "valor", "valor_aberto", "data_emissao",
        "data_vencimento", "dias_atraso", "status", "garantia_tipo",
        "garantia_valor", "estagio_juridico", "safra"]),
    "avalistas.csv": ("avalistas", [
        "recebivel", "avalista_id", "avalista_nome", "tipo", "documento"]),
    "grupos.csv": ("grupos", ["cliente", "grupo_id", "grupo_nome"]),
    "planta.csv": ("planta", ["cliente", "cultura", "hectares"]),
    "participacoes.csv": ("participacoes", ["cliente", "socio_id", "participacao"]),
    "imoveis.csv": ("imoveis_interno", [
        "id", "cliente", "area_ha", "reserva_legal_ok", "codigo_municipio_ibge"]),
}


def extract() -> None:
    INTERNO.mkdir(parents=True, exist_ok=True)
    presentes = [n for n in MAPA if (INTERNO / n).exists()]
    ausentes = [n for n in MAPA if n not in presentes]
    print(f"  lendo de {INTERNO}")
    for n in presentes:
        print(f"  presente: {n}")
    for n in ausentes:
        print(f"  AUSENTE: {n} — o alvo correspondente fica vazio no grafo")
    if not presentes:
        print("  Nenhum arquivo interno. O grafo sai SEM recebiveis, ou seja,")
        print("  sem exposicao, sem score e sem recomendacao de estrategia —")
        print("  o motor inteiro depende deles.")


def transform() -> None:
    for arquivo, (nome, colunas) in MAPA.items():
        caminho = INTERNO / arquivo
        if not caminho.exists():
            continue
        with caminho.open(encoding="utf-8-sig", newline="") as f:
            linhas = []
            for linha in csv.DictReader(f):
                linha["fonte"] = PROCEDENCIA
                linha["coletado_em"] = staging.hoje()
                linha["confianca"] = 1.0
                linhas.append(linha)
        staging.escrever(nome, colunas, linhas)


FONTE = Fonte(
    id="interno",
    nome="Krilltech — ERP (recebíveis, garantias, grupos, lavoura)",
    url="(arquivos em data/interno/)",
    orgao="Krilltech",
    periodicidade="conforme o ERP",
    extract=extract,
    transform=transform,
    passo_manual=(
        "Exportar do ERP para data/interno/*.csv nos layouts do docstring de "
        "interno_krilltech.py. Nada disso tem equivalente publico."),
    cobertura=[
        Cobertura(":Recebivel (todo o no)", "interno", 1.0,
                  "Valor, vencimento, atraso, status. NENHUMA fonte publica "
                  "publica recebivel privado — e nem deveria."),
        Cobertura(":Recebivel.garantia_tipo / .garantia_valor", "interno", 1.0,
                  "Contrato. E o insumo do haircut por tipo de garantia, que e "
                  "um dos 5 componentes do score."),
        Cobertura(":Recebivel.estagio_juridico", "interno", 1.0,
                  "Filtro de elegibilidade da Q4. So o juridico da empresa sabe "
                  "em que estagio esta cada titulo."),
        Cobertura(":Avalista + GARANTIDO_POR", "interno", 1.0,
                  "Aval e clausula de contrato privado. E o vetor de peso 0,85 "
                  "do motor (avalista em comum) e nao tem substituto publico."),
        Cobertura(":GrupoEconomico + PERTENCE_A", "interno", 1.0,
                  "Vetor de peso 0,90, o maior do motor. Nao existe base publica "
                  "de grupo economico. Ou vem do cadastro, ou e inferido de "
                  "socio+endereco — e inferencia tem de ir ao grafo marcada."),
        Cobertura("(:Cliente)-[:PLANTA]->(:Cultura) + hectares", "interno", 1.0,
                  "A nota fiscal de insumo diz o que o produtor plantou. A PAM "
                  "so diz o que o municipio colheu."),
        Cobertura("TEM_SOCIO.participacao", "interno", 1.0,
                  "Contrato social. A QSA publica nao traz percentual."),
        Cobertura(":Cliente.dias_atraso_max / .situacao", "interno", 1.0,
                  "Comportamento de pagamento e o componente de maior peso "
                  "pratico do score e e 100% interno."),
        Cobertura(":EstrategiaRecuperacao (catalogo)", "interno", 1.0,
                  "Custo medio, prazo e taxa de sucesso historica sao do "
                  "historico de cobranca da propria empresa. O catalogo do seed "
                  "e estimativa de mercado — util para demo, nao para decisao."),
        Cobertura("(:Cliente)-[:COMPRA_VIA]->(revenda)", "interno", 1.0,
                  "Canal de venda e cadastro comercial."),
    ],
)
