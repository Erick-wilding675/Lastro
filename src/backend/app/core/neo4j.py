"""Acesso ao Neo4j. Único ponto do sistema que fala com o driver.

Regra de arquitetura (ARD-04): o watsonx Orchestrate nunca toca o driver.
Ele chama a API deste backend, que é quem consulta o grafo.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from neo4j import GraphDatabase, Driver

from app.core.config import settings

_driver: Driver | None = None


def get_driver() -> Driver:
    if _driver is None:
        raise RuntimeError("Driver Neo4j não inicializado — a app subiu sem lifespan?")
    return _driver


def run(query: str, **params):
    """Executa uma query e devolve lista de dicts. Falha ruidosa por padrão."""
    with get_driver().session(database=settings.neo4j_database) as session:
        return [dict(record) for record in session.run(query, **params)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _driver
    _driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )
    _driver.verify_connectivity()
    yield
    _driver.close()
    _driver = None
