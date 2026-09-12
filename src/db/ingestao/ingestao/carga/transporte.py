"""Dois transportes para o mesmo Cypher: Bolt (driver) e Query API (HTTP).

POR QUE EXISTEM DOIS. O driver oficial fala Bolt na porta 7687. Em rede
corporativa — e em ambiente de execução restrito — só 80 e 443 saem. Medido
aqui em 12/09/2026: `0f36204d.databases.neo4j.io:7687` dá timeout enquanto
:443 abre, e o mesmo vale para github.com:22 e smtp.gmail.com:587, o que mostra
que o bloqueio é de porta, não da instância.

A Query API v2 do Aura serve o mesmo Cypher em HTTPS:
  POST https://<host>/db/<database>/query/v2
  Authorization: Basic <user:senha>
  {"statement": "...", "parameters": {...}}

Não é um substituto completo do driver — não tem roteamento de cluster nem
transação multi-statement — mas para uma carga que é uma sequência de `UNWIND
... MERGE` idempotentes, cada um já atômico por si, é equivalente no que
importa.

`LASTRO_NEO4J_TRANSPORTE` escolhe: 'auto' (padrão) tenta Bolt e cai para HTTP,
'bolt' ou 'http' forçam um dos dois. Forçar é útil para diagnóstico: em 'auto'
um erro de senha no Bolt viraria uma tentativa de HTTP e duas mensagens de erro
parecidas, o que confunde mais do que ajuda.
"""
import os
from urllib.parse import urlparse

from ingestao import config


class ErroCarga(RuntimeError):
    pass


class TransporteBolt:
    nome = "bolt (driver oficial, porta 7687)"

    def __init__(self) -> None:
        from neo4j import GraphDatabase
        self._driver = GraphDatabase.driver(
            config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))
        self._driver.verify_connectivity()

    def executar(self, query: str, **params) -> list[dict]:
        with self._driver.session(database=config.NEO4J_DATABASE) as s:
            return [dict(r) for r in s.run(query, **params)]

    def fechar(self) -> None:
        self._driver.close()


class TransporteHttp:
    nome = "Query API v2 (HTTPS, porta 443)"

    def __init__(self) -> None:
        import httpx
        host = urlparse(config.NEO4J_URI).hostname or config.NEO4J_URI
        self._url = (f"https://{host}/db/{config.NEO4J_DATABASE}/query/v2")
        self._cliente = httpx.Client(
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD),
            headers={"Content-Type": "application/json",
                     "Accept": "application/json",
                     "User-Agent": config.USER_AGENT},
            timeout=config.TIMEOUT)
        self.executar("RETURN 1 AS ok")

    def executar(self, query: str, **params) -> list[dict]:
        r = self._cliente.post(self._url, json={"statement": query,
                                               "parameters": params or {}})
        corpo = r.json() if r.content else {}
        # A Query API devolve 200 com `errors` em alguns casos e 4xx em outros;
        # checar as duas coisas evita que um erro de Cypher passe como sucesso.
        if erros := corpo.get("errors"):
            primeiro = erros[0]
            raise ErroCarga(f"{primeiro.get('code')}: {primeiro.get('message')}")
        if r.status_code >= 400:
            raise ErroCarga(f"HTTP {r.status_code}: {r.text[:300]}")
        dados = corpo.get("data") or {}
        campos = dados.get("fields") or []
        return [dict(zip(campos, linha)) for linha in dados.get("values") or []]

    def fechar(self) -> None:
        self._cliente.close()


def abrir():
    """Devolve o transporte utilizável, com mensagem clara quando nenhum serve."""
    if not config.NEO4J_PASSWORD:
        raise SystemExit(
            "NEO4J_PASSWORD vazio.\n"
            "Crie src/backend/.env (ou src/db/ingestao/.env) a partir do\n"
            ".env.example e preencha as credenciais do AuraDB. A carga nao\n"
            "roda as cegas contra 'bolt://localhost' por engano."
        )
    escolha = os.getenv("LASTRO_NEO4J_TRANSPORTE", "auto").strip().lower()
    if escolha not in ("auto", "bolt", "http"):
        raise SystemExit(f"LASTRO_NEO4J_TRANSPORTE invalido: {escolha!r} "
                         "(use auto, bolt ou http)")

    if escolha in ("auto", "bolt"):
        try:
            t = TransporteBolt()
            print(f"  transporte: {t.nome}")
            return t
        except Exception as e:
            if escolha == "bolt":
                raise SystemExit(f"Bolt falhou: {type(e).__name__}: {e}")
            print(f"  Bolt indisponivel ({type(e).__name__}) — tentando HTTPS. "
                  "Causa comum: porta 7687 bloqueada na rede.")

    t = TransporteHttp()
    print(f"  transporte: {t.nome}")
    return t
