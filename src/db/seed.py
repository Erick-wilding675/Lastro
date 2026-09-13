"""Aplica os arquivos .cypher deste diretório no Neo4j via driver.

Substitui o "cole no console do AuraDB" manual por um comando único
(`make seed`). Lê as mesmas variáveis NEO4J_* do backend — reusa o .env de
`src/backend/.env` se existir, senão o `.env` da raiz.

Uso:
    python src/db/seed.py                          # aplica o schema+seed
    python src/db/seed.py cypher/02-queries-motor.cypher  # aplica um arquivo específico
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
DIR_CYPHER = Path(__file__).resolve().parent / "cypher"

for candidato in (RAIZ_REPO / "src" / "backend" / ".env", RAIZ_REPO / ".env"):
    if candidato.exists():
        load_dotenv(candidato)
        break

import os

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


def _statements(texto: str) -> list[str]:
    """Divide um arquivo .cypher em statements executáveis.

    Remove comentários de linha (`//`) antes de dividir por `;` — um `;`
    dentro de comentário não deve fechar statement. Descarta blocos vazios.
    """
    sem_comentarios = re.sub(r"//.*", "", texto)
    return [s.strip() for s in sem_comentarios.split(";") if s.strip()]


def aplicar(caminho: Path) -> None:
    statements = _statements(caminho.read_text(encoding="utf-8"))
    print(f"== {caminho.relative_to(RAIZ_REPO)} — {len(statements)} statement(s)")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        driver.verify_connectivity()
        with driver.session(database=NEO4J_DATABASE) as session:
            for i, stmt in enumerate(statements, start=1):
                try:
                    session.run(stmt)
                except Exception as erro:
                    print(f"  [{i}/{len(statements)}] FALHOU: {erro}\n    statement: {stmt[:120]}...")
                    raise
                else:
                    print(f"  [{i}/{len(statements)}] ok")
    finally:
        driver.close()


def main() -> None:
    if len(sys.argv) > 1:
        arg = Path(sys.argv[1])
        if arg.is_absolute():
            alvos = [arg]
        elif (DIR_CYPHER / arg).exists():
            alvos = [DIR_CYPHER / arg]
        else:
            alvos = [RAIZ_REPO / arg]
    else:
        alvos = [DIR_CYPHER / "01-schema-e-seed.cypher"]

    if not NEO4J_PASSWORD:
        print("NEO4J_PASSWORD vazio — configure src/backend/.env ou .env na raiz "
              "(veja .env.example).", file=sys.stderr)
        sys.exit(1)

    for caminho in alvos:
        aplicar(caminho)
    print("Concluído.")


if __name__ == "__main__":
    main()
