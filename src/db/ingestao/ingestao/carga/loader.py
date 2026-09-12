"""Carga do staging para o Neo4j. Idempotente, em lotes, com conferência no fim.

A decisão central deste módulo está em `_props`: CAMPO VAZIO NÃO VIRA
PROPRIEDADE. Se a QSA não publica percentual de participação, a aresta TEM_SOCIO
sai do grafo SEM `participacao` — não com `participacao: 0.0`. A diferença é a
que separa "não sei" de "sei que é zero", e o motor de score trata as duas de
formas opostas: ausência ele ignora, zero ele usa como medição.
"""
from typing import Iterable

from ingestao import config, staging
from ingestao.carga import cypher, transporte

LOTE = 500

# Campos que são numéricos no grafo. Vêm como texto do CSV e precisam virar
# float antes do MERGE, senão o grafo acumula "890000.0" como string e toda
# soma de exposição falha silenciosamente — que é o pior modo de falhar.
NUMERICOS = {
    "valor", "valor_aberto", "garantia_valor", "severidade", "confianca",
    "hectares", "area_ha", "area_embargada_ha", "participacao", "queda_pct",
    "deficit_pct", "quantidade", "area_colhida_ha",
}
INTEIROS = {"dias_atraso", "ciclo_dias", "codigo_microrregiao",
            "codigo_mesorregiao", "janela_dias"}
BOOLEANOS = {"embargo_ibama", "reserva_legal_ok", "sintetico"}
DATAS = {"data_emissao", "data_vencimento", "data_entrada",
         "data_inicio_atividade", "cliente_desde"}


def _valor(chave: str, bruto: str):
    """Converte o texto do CSV para o tipo do grafo. None = não escrever."""
    if bruto is None:
        return None
    texto = bruto.strip()
    if texto == "":
        return None
    if chave in BOOLEANOS:
        return texto.lower() in ("true", "1", "sim", "s", "t")
    if chave in NUMERICOS:
        try:
            return float(texto)
        except ValueError:
            return None
    if chave in INTEIROS:
        try:
            return int(float(texto))
        except ValueError:
            return None
    return texto


def _props(linha: dict, excluir: Iterable[str] = ()) -> dict:
    fora = set(excluir)
    limpo = {}
    for chave, bruto in linha.items():
        if chave in fora or chave == "doc":
            continue
        valor = _valor(chave, bruto)
        if valor is not None:
            limpo[chave] = valor
    return limpo


class Carga:
    def __init__(self) -> None:
        # Bolt ou Query API — transporte.abrir() decide e explica a escolha.
        # Rede que bloqueia a 7687 ainda carrega por HTTPS.
        self._t = transporte.abrir()
        print(f"  conectado: {config.NEO4J_URI} / db={config.NEO4J_DATABASE}")

    def fechar(self) -> None:
        self._t.fechar()

    def executar(self, query: str, **params) -> list[dict]:
        return self._t.executar(query, **params)

    def em_lotes(self, rotulo: str, query: str, linhas: list[dict]) -> int:
        if not linhas:
            print(f"  {rotulo}: 0 linhas (staging ausente ou vazio)")
            return 0
        for i in range(0, len(linhas), LOTE):
            self.executar(query, linhas=linhas[i:i + LOTE])
        print(f"  {rotulo}: {len(linhas)} linha(s)")
        return len(linhas)


def _linhas_simples(nome: str, chave: str = "id") -> list[dict]:
    """Staging -> [{id, props}] para os MERGE de nó puro."""
    return [{chave: l[chave], "props": _props(l, excluir=[chave])}
            for l in staging.ler(nome) if l.get(chave)]


def _municipio_regiao() -> dict[str, str]:
    return {r["codigo_municipio_ibge"]: r["regiao"]
            for r in staging.ler("municipio_regiao")}


def rodar() -> None:
    carga = Carga()
    try:
        print("\n-- constraints")
        for c in cypher.CONSTRAINTS:
            carga.executar(c)
        print(f"  {len(cypher.CONSTRAINTS)} constraint(s)/indice(s) garantido(s)")

        print("\n-- taxonomias")
        carga.em_lotes("Regiao", cypher.REGIOES, _linhas_simples("regioes"))
        carga.em_lotes("Cultura", cypher.CULTURAS, _linhas_simples("culturas"))
        carga.em_lotes("Safra", cypher.SAFRAS, _linhas_simples("safras"))

        print("\n-- clientes e vinculos")
        carga.em_lotes("Cliente", cypher.CLIENTES, _linhas_simples("clientes"))
        # DEPOIS do cadastro da Receita, nunca antes: a CVM é quem sabe que a
        # companhia está em RJ, e `situacao` é o campo que a Q2 usa como
        # override de rating D. Em ordem invertida o MERGE da Receita apagaria.
        # Só entram as linhas com `situacao` preenchida — uma linha histórica de
        # 'FASE OPERACIONAL' não pode sobrescrever um 'EM RECUPERAÇÃO JUDICIAL'
        # gravado por outra linha do mesmo CNPJ.
        # `fonte`/`coletado_em`/`confianca` ficam FORA: são a procedência do
        # cadastro do cliente, que é da Receita. Incluí-los aqui faria o MERGE
        # da CVM reescrever `c.fonte` como se razão social, UF e CNAE tivessem
        # vindo da CVM — e aí o dossiê atribuiria o dado à fonte errada. A
        # procedência da situação vai em `situacao_fonte`, no Cypher.
        carga.em_lotes("Cliente.situacao (CVM)", cypher.SITUACAO_CVM, [
            {"cliente": l["cliente"],
             "props": _props(l, excluir=["cliente", "documento", "fonte",
                                         "coletado_em", "confianca"])}
            for l in staging.ler("situacao_cvm")
            if l.get("cliente") and l.get("situacao")])
        carga.em_lotes("GrupoEconomico", cypher.GRUPOS, [
            {"cliente": l["cliente"], "grupo_id": l["grupo_id"],
             "grupo_nome": l.get("grupo_nome"),
             # O nó do grupo só existe porque foi inventado: marca o nó, não só
             # a aresta. Um GrupoEconomico vindo do ERP não teria a marca.
             "props_no": _props(l, excluir=["cliente", "grupo_id", "grupo_nome"]),
             "props": _props(l, excluir=["cliente", "grupo_id", "grupo_nome"])}
            for l in staging.ler("grupos") if l.get("grupo_id")])
        carga.em_lotes("Socio + TEM_SOCIO", cypher.SOCIOS, [
            {"cliente": l["cliente"], "socio_id": l["socio_id"],
             "socio_nome": l["socio_nome"],
             "props_socio": _props(l, excluir=[
                 "cliente", "socio_id", "socio_nome", "qualificacao",
                 "data_entrada", "participacao"]),
             # Documento é atributo da PESSOA, não do vínculo: fica só no nó.
             "props_aresta": _props(l, excluir=[
                 "cliente", "socio_id", "socio_nome", "documento",
                 "documento_mascarado"])}
            for l in staging.ler("socios") if l.get("socio_id")])
        carga.em_lotes("TEM_SOCIO.participacao", cypher.PARTICIPACOES, [
            l for l in staging.ler("participacoes") if l.get("participacao")])

        # Atributos que só o ERP teria. Depois de SITUACAO_CVM de propósito: o
        # gerador deixa `situacao` vazia para a AgroGalaxy para não sobrescrever
        # a RJ real da CVM com uma derivada de atraso inventado.
        carga.em_lotes("Cliente.atributos (SINTETICO)", cypher.ATRIBUTOS_SINTETICOS, [
            {"cliente": l["cliente"], "props": _props(l, excluir=["cliente"])}
            for l in staging.ler("atributos_sinteticos") if l.get("cliente")])

        print("\n-- territorio e lavoura")
        carga.em_lotes("COMPRA_VIA", cypher.COMPRA_VIA, [
            {"cliente": l["cliente"], "revenda": l["revenda"],
             "props": _props(l, excluir=["cliente", "revenda"])}
            for l in staging.ler("compra_via")])
        carga.em_lotes("OPERA_EM", cypher.OPERA_EM, [
            {"cliente": l["cliente"], "regiao": l["regiao"],
             "props": _props(l, excluir=["cliente", "regiao"])}
            for l in staging.ler("opera_em")])
        carga.em_lotes("PLANTA", cypher.PLANTA, [
            {"cliente": l["cliente"], "cultura": l["cultura"],
             "props": _props(l, excluir=["cliente", "cultura"])}
            for l in staging.ler("planta")])

        print("\n-- imoveis")
        mun_reg = _municipio_regiao()
        imoveis = []
        for nome in ("imoveis", "imoveis_interno"):
            for l in staging.ler(nome):
                if not l.get("id") or not l.get("cliente"):
                    continue
                imoveis.append({
                    "id": l["id"], "cliente": l["cliente"],
                    "regiao": mun_reg.get((l.get("codigo_municipio_ibge") or "").strip()),
                    "props": _props(l, excluir=["id", "cliente"])})
        carga.em_lotes("Imovel + POSSUI", cypher.IMOVEIS, imoveis)

        print("\n-- recebiveis e avais (dados internos)")
        carga.em_lotes("Recebivel + DE", cypher.RECEBIVEIS, [
            {"id": l["id"], "cliente": l["cliente"],
             "safra": (l.get("safra") or "").strip() or None,
             "props": _props(l, excluir=["id", "cliente", "safra"])}
            for l in staging.ler("recebiveis") if l.get("id")])
        carga.em_lotes("Avalista + GARANTIDO_POR", cypher.AVALISTAS, [
            {"recebivel": l["recebivel"], "avalista_id": l["avalista_id"],
             "avalista_nome": l.get("avalista_nome"),
             "props_avalista": _props(l, excluir=[
                 "recebivel", "avalista_id", "avalista_nome"]),
             "props_aresta": _props(l, excluir=[
                 "recebivel", "avalista_id", "avalista_nome", "tipo", "documento"])}
            for l in staging.ler("avalistas") if l.get("avalista_id")])

        print("\n-- eventos de CLIENTE (fonte publica com CPF/CNPJ)")
        for nome in ("eventos_qsa", "eventos_cvm", "eventos_pgfn", "eventos_ibama"):
            carga.em_lotes(nome, cypher.EVENTOS_CLIENTE, [
                {"id": l["id"], "cliente": l["cliente"], "data": l["data"],
                 "props": _props(l, excluir=["id", "cliente", "data"])}
                for l in staging.ler(nome) if l.get("data")])

        print("\n-- eventos de REGIAO (fonte sem atribuicao a cliente)")
        for nome in ("eventos_pam", "eventos_datajud"):
            carga.em_lotes(nome, cypher.EVENTOS_REGIAO, [
                {"id": l["id"], "regiao": l["regiao"], "data": l["data"],
                 "cultura": (l.get("cultura") or "").strip() or None,
                 "props": _props(l, excluir=["id", "regiao", "data"])}
                for l in staging.ler(nome) if l.get("data")])
        for nome in ("eventos_conab", "eventos_inmet"):
            carga.em_lotes(nome, cypher.EVENTOS_UF, [
                {"id": l["id"], "uf": l["uf"], "data": l["data"],
                 "cultura": (l.get("cultura") or "").strip() or None,
                 "props": _props(l, excluir=["id", "uf", "data"])}
                for l in staging.ler(nome) if l.get("data")])

        print("\n-- exposicao materializada")
        for r in carga.executar(cypher.EXPOSICAO):
            print(f"  {r['clientes']} cliente(s), exposicao total "
                  f"R$ {r['exposicao_total']:,.0f}")

        print("\n-- conferencia")
        for r in carga.executar(cypher.CONFERENCIA):
            print(f"  :{r['rotulo']:<22} {r['n']:>8}")
        for r in carga.executar(cypher.CONFERENCIA_ARESTAS):
            print(f"  -[:{r['tipo']}]->".ljust(28) + f"{r['n']:>8}")
    finally:
        carga.fechar()
