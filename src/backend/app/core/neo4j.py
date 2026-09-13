"""Acesso ao Neo4j. Único ponto do sistema que fala com o driver.

Regra de arquitetura (ARD-04): o watsonx Orchestrate nunca toca o driver.
Ele chama a API deste backend, que é quem consulta o grafo.

Como este é o único ponto de contato com o driver, é também aqui que os tipos
do Neo4j viram tipos de JSON — ver `_json_safe`.
"""
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from neo4j import Driver, GraphDatabase
from neo4j.graph import Node, Path, Relationship
from neo4j.spatial import Point
from neo4j.time import Date, DateTime, Duration, Time

from app.core.config import settings

log = logging.getLogger("lastro.neo4j")

_driver: Driver | None = None


def get_driver() -> Driver:
    if _driver is None:
        raise RuntimeError("Driver Neo4j não inicializado — a app subiu sem lifespan?")
    return _driver


def _json_safe(valor: Any) -> Any:
    """Converte os tipos do driver em tipos que o JSON do FastAPI entende.

    Sem isto o `date()` do Cypher chega ao React como
    `{"_Date__ordinal": 739871, "_Date__year": 2026, ...}` — o objeto interno
    do driver serializado campo a campo pelo encoder do FastAPI. Não é erro
    500: é pior, passa silencioso e só quebra na tela, porque o React não
    renderiza objeto como filho (`Objects are not valid as a React child`).

    Datas saem em ISO-8601. Formatar para pt-BR é decisão da interface, não
    da API: o mesmo endpoint serve o frontend e o watsonx Orchestrate.
    """
    if isinstance(valor, (Date, DateTime, Time)):
        return valor.iso_format()
    if isinstance(valor, Duration):
        return str(valor)
    if isinstance(valor, Point):
        return {"srid": valor.srid, "coordenadas": list(valor)}
    if isinstance(valor, (Node, Relationship)):
        return {chave: _json_safe(v) for chave, v in dict(valor).items()}
    if isinstance(valor, Path):
        return [_json_safe(rel) for rel in valor.relationships]
    if isinstance(valor, dict):
        return {chave: _json_safe(v) for chave, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_json_safe(v) for v in valor]
    return valor


def run(query: str, **params) -> list[dict]:
    """Executa uma query e devolve lista de dicts. Falha ruidosa por padrão."""
    with get_driver().session(database=settings.neo4j_database) as session:
        return [_json_safe(dict(record)) for record in session.run(query, **params)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Abre o driver no boot e avisa alto se o banco não responder.

    NÃO derruba o processo quando a conexão falha, e isso é deliberado: a
    instância gratuita do AuraDB pausa sozinha depois de dias parada, e um boot
    que aborta vira crash loop no PaaS — a API some inteira, inclusive o
    /health que diria o que houve. Subindo degradada, /health responde 503 com
    o motivo e a interface mostra "sem conexão" em vez de uma página morta.

    Cada query continua falhando ruidosamente. O que muda é só quem descobre
    o problema primeiro: quem consome a API, e não o orquestrador de containers.
    """
    global _driver
    _driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )
    try:
        _driver.verify_connectivity()
        log.info("Neo4j conectado em %s", settings.neo4j_uri)
    except Exception as erro:
        log.error("Neo4j INDISPONÍVEL em %s — a API sobe degradada e /health "
                  "vai responder 503. Causa: %s", settings.neo4j_uri, erro)
    yield
    _driver.close()
    _driver = None
