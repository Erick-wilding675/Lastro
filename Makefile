# Lastro — automação do monólito modular.
# Windows: rode via `make` do Git Bash/WSL, ou `python -m ...` direto se
# preferir sem make. venv em .venv na raiz (ver .vscode/settings.json).
#
# PYTHON precisa ser 3.11 (o Dockerfile do backend fixa a mesma versão —
# pydantic-core ainda não publica wheel para 3.13+, a build cai no
# cargo/PyO3). `py -3.11` é o launcher padrão do Windows; em Mac/Linux rode
# `make setup PYTHON=python3.11`.
PYTHON        ?= py -3.11
VENV          := .venv
VENV_BIN      := $(VENV)/Scripts
PY            := $(VENV_BIN)/python
PIP           := $(VENV_BIN)/pip

.PHONY: help setup venv backend frontend seed seed-lacunas ingest ingest-cobertura \
        docker-backend lint clean

help:
	@echo "alvos:"
	@echo "  setup          cria .venv na raiz e instala backend+ingestao+frontend"
	@echo "  backend        sobe a API (uvicorn --reload) em :8000"
	@echo "  frontend       sobe o dev server do Vite em :5173"
	@echo "  seed           aplica src/db/cypher/01-schema-e-seed.cypher no AuraDB"
	@echo "  seed-lacunas   aplica src/db/cypher/03-completar-lacunas.cypher"
	@echo "  ingest         roda o pipeline de ingestao completo (extract+transform+load)"
	@echo "  ingest-cobertura  regenera src/db/ingestao/COBERTURA.md"
	@echo "  docker-backend build da imagem docker do backend"
	@echo "  lint           ruff check no backend"
	@echo "  clean          remove .venv, node_modules, dist, __pycache__"

venv:
	$(PYTHON) -m venv $(VENV)

setup: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r src/backend/requirements.txt
	$(PIP) install -r src/db/ingestao/requirements.txt
	$(PIP) install -r requirements-dev.txt
	cd src/frontend && npm install

backend:
	cd src/backend && "$(CURDIR)/$(PY)" -m uvicorn app.main:app --reload

frontend:
	cd src/frontend && npm run dev

seed:
	"$(PY)" src/db/seed.py

seed-lacunas:
	"$(PY)" src/db/seed.py 03-completar-lacunas.cypher

ingest:
	cd src/db/ingestao && "$(CURDIR)/$(PY)" -m ingestao all

ingest-cobertura:
	cd src/db/ingestao && "$(CURDIR)/$(PY)" -m ingestao cobertura

docker-backend:
	docker build -t lastro-api ./src/backend

lint:
	"$(PY)" -m ruff check src/backend

clean:
	rm -rf $(VENV) src/frontend/node_modules src/frontend/dist
	find . -type d -name __pycache__ -not -path "*/.venv/*" -prune -exec rm -rf {} +
