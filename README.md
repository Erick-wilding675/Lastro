# Lastro

Repositório do projeto **Lastro**, construído para o Hackathon 2026 do Student Club PMI-DF (11–12/09/2026, Brasília).

Toda a documentação de idealização, especificação e decisões do projeto vive em [`vault/`](vault/) — um vault do Obsidian, versionado neste repositório.

- **Para ler/editar a documentação:** abra a pasta `vault/` no Obsidian.
- **Para qualquer assistente de IA** (IBM Bob, Claude, etc.) trabalhando neste repositório: comece por [`AGENTS.md`](AGENTS.md), que aponta para [`vault/.ai/ai.md`](vault/.ai/ai.md) — o ponto de entrada único.

## O que é o Lastro

A **Krilltech** (agtech brasileira, produto Arbolin Biogenesis) enfrenta aumento de inadimplência e pedidos de Recuperação Judicial de produtores rurais clientes. Quando um cliente entra em RJ, a empresa fica legalmente impedida de executar garantia ou protestar por **180 dias** (*stay period*) — todo o valor está em saber antes.

O **Lastro** trata a carteira como rede, não como lista. Representa recebíveis, clientes, sócios, avalistas e vínculos de região/cultura em um grafo Neo4j; propaga risco pelos elos entre clientes; e mostra **por qual vínculo** a exposição chega — a tempo de ajustar limite, condição de pagamento e estratégia de recuperação.

**A tese em uma frase:** produtor rural não quebra sozinho — o componente de rede é o que bureau nenhum entrega.

## Stack

| Camada | Tecnologia |
|---|---|
| Orquestração de agentes | IBM watsonx Orchestrate |
| Engenharia & assistência | IBM Bob |
| Grafo | Neo4j AuraDB (free tier) |
| Backend | Python + FastAPI |
| Frontend | React + react-force-graph-2d |

## Estrutura do repositório

```
/
├── src/                   código (monólito modular — ver src/README.md)
│   ├── backend/           Python + FastAPI
│   ├── db/cypher/         schema, seed e queries do motor
│   └── frontend/          React
└── vault/                 documentação (Obsidian)
    └── .ai/               contexto para IAs, arquitetura, decisões e docs do produto
```

## Como subir

Ver [`src/README.md`](src/README.md) para instruções completas. Resumo:

1. **Banco** — cole `src/db/cypher/01-schema-e-seed.cypher` no console do AuraDB.
2. **Backend** — `pip install -r requirements.txt` → configure `.env` com credenciais do AuraDB → `uvicorn app.main:app --reload`.
3. **Frontend** — `npm install` → `npm run dev`.

## Documentação relevante

| Tópico | Arquivo |
|---|---|
| Contexto do projeto (ponto de entrada IA) | [`vault/.ai/ai.md`](vault/.ai/ai.md) |
| Project Canvas (entregável do hackathon) | [`vault/.ai/docs/project-canvas.md`](vault/.ai/docs/project-canvas.md) |
| Data model (grafo, motor de contágio) | [`vault/.ai/docs/data-model.md`](vault/.ai/docs/data-model.md) |
| Arquitetura e decisões (ARD-01 a 05) | [`vault/.ai/architecture.md`](vault/.ai/architecture.md) · [`vault/.ai/docs/ARD.md`](vault/.ai/docs/ARD.md) |
| Matching model (canais de exposição) | [`vault/.ai/docs/matching-model.md`](vault/.ai/docs/matching-model.md) |
| UI / design system | [`vault/.ai/ui_guidelines.md`](vault/.ai/ui_guidelines.md) · [`vault/.ai/docs/design-doc.md`](vault/.ai/docs/design-doc.md) |
| Edital e critérios de avaliação | [`vault/.ai/docs/edital-e-avaliacao.md`](vault/.ai/docs/edital-e-avaliacao.md) |

## Estado atual

**MVP funcional** construído no hackathon (12/09/2026). Canvas e pitch entregues até 15:00. Motor de exposição em dois canais (estrutural e sistêmico), score 0–1000 com rating A–D, matriz de red flags, 4 agentes no watsonx Orchestrate e aplicação web com mapa de exposição da carteira e dossiê do cliente.

> ⚠️ Referências a "Talent Graph", "squad" ou "Project Genome" encontradas no repositório são resíduos da versão anterior ao pivô de domínio (11/09) — trate como desatualizadas.
