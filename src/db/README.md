# Lastro — Banco de dados (Neo4j)

Duas partes: o **schema/queries** versionados em `.cypher` e o **pipeline de
ingestão** em Python que alimenta o grafo com dado público real.

```
src/db/
├── cypher/
│   ├── 01-schema-e-seed.cypher       constraints, índices e seed sintético (cenário de demo)
│   ├── 02-queries-motor.cypher       as 5 queries que o backend chama via API — referência, não roda solto
│   └── 03-completar-lacunas.cypher   corrige/completa depois do seed + da ingestão conviverem no grafo
├── seed.py                           aplica 01 + 03 via driver — alternativa a colar no console do AuraDB
└── ingestao/                         pipeline extract → transform → load de fontes públicas reais
```

## Subir o schema

**Console do AuraDB** (como no hackathon): cole `01-schema-e-seed.cypher`
(Bloco A, depois Bloco B) no Neo4j Browser.

**Via script**, a partir da raiz do repo:

```bash
cp .env.example .env   # preencha NEO4J_URI/USER/PASSWORD
python src/db/seed.py                       # aplica 01-schema-e-seed.cypher
python src/db/seed.py 03-completar-lacunas.cypher
# ou: make seed / make seed-lacunas
```

`02-queries-motor.cypher` fica de fora de propósito — são as 5 queries
parametrizadas (`$origem`, `$capacidade`...) que `src/backend/app/modules/*/queries.py`
chama via API. Leia o arquivo como referência de como o motor calcula, não
como script para rodar direto.

## O grafo, em resumo

Nós: `Cliente`, `Recebivel`, `Socio`, `Avalista`, `GrupoEconomico`, `Regiao`,
`Cultura`, `Safra`, `Imovel`, `Evento`, `EstrategiaRecuperacao`. Dois canais
de propagação de exposição — **estrutural** (grupo econômico, avalista
comum, sócio comum) e **sistêmico** (região + cultura + safra, revenda
comum, só entra com peso cheio se houver evento regional confirmando o
choque). Modelo completo, com pesos e propriedades, em
[`../../.ai/docs/data-model.md`](../../.ai/docs/data-model.md).

## Pipeline de ingestão

`ingestao/` baixa e normaliza dado real de fontes públicas (PGFN, IBAMA,
Receita/QSA, Conab, IBGE, INMET, DataJud, SICAR) filtrado pela carteira real
da Krilltech — nunca "ingere o Brasil inteiro". Documentação própria e
extensa, incluindo o mapa de cobertura por fonte (o que é real, parcial,
bloqueado ou necessariamente sintético) em
[`ingestao/README.md`](ingestao/README.md) e [`ingestao/COBERTURA.md`](ingestao/COBERTURA.md).

```bash
cd src/db/ingestao
pip install -r requirements.txt
python -m ingestao all      # extract → transform → load
```

## Nenhum dado real de produtor no repositório

Hard Rule #8. `01-schema-e-seed.cypher` é seed sintético e mascarado; tudo
que a ingestão baixa de verdade fica em `ingestao/data/`, ignorado pelo git.
