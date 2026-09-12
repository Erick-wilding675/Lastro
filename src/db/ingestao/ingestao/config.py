"""Configuração do pipeline. Lê do .env — nunca hardcode credencial."""
import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent

# O .env do pipeline é o mesmo do backend, se existir: a credencial do AuraDB
# é a mesma e duplicá-la em dois arquivos é como os dois saem de sincronia.
for candidato in (RAIZ / ".env", RAIZ.parent.parent / "backend" / ".env"):
    if candidato.exists():
        load_dotenv(candidato)
        break

RAW = RAIZ / "data" / "raw"
STAGING = RAIZ / "data" / "staging"

# A carteira é o filtro de tudo. O pipeline não ingere o Brasil inteiro:
# ele parte dos clientes que a Krilltech já tem e os enriquece nas fontes
# públicas. Isso é o que torna viável (PGFN tem 1,3 GB) e defensável em LGPD
# (só se consulta quem já é contraparte, não a população).
CARTEIRA = Path(os.getenv("LASTRO_CARTEIRA", RAIZ / "carteira.csv"))

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Receita, IBAMA, INMET e Conab devolvem 403 ou conexão recusada para o
# User-Agent default do httpx. Não é bloqueio de robô, é filtro de UA vazio.
USER_AGENT = os.getenv(
    "LASTRO_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Lastro/0.1 (pesquisa academica)",
)

# Chave pública do DataJud, publicada pelo próprio CNJ em
# https://datajud-wiki.cnj.jus.br/api-publica/acesso/ — é pública por desenho,
# não é segredo. Fica sobrescritível por .env caso o CNJ a rotacione.
DATAJUD_APIKEY = os.getenv(
    "DATAJUD_APIKEY",
    "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==",
)

TIMEOUT = float(os.getenv("LASTRO_HTTP_TIMEOUT", "180"))


def preparar_diretorios() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    STAGING.mkdir(parents=True, exist_ok=True)
