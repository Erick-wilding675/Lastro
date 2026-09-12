# Estado atual — quadro vivo

**Última atualização:** 12/09, ~00h, antes da reunião de alinhamento.
**Quem atualiza:** qualquer agente, ao concluir uma entrega. Mantenha honesto.

---

## Pronto (não refazer)

| Item | Onde | Nota |
|---|---|---|
| Especificação completa do produto | `vault/.ai/docs/` | Reescrita para o case KRILLTECH |
| Decisões de arquitetura ARD-01 a ARD-05 | `vault/.ai/docs/ARD.md` | Neo4j, FastAPI, React, integração via API, explicação materializada |
| Design system (paleta, tipografia, tokens) | `vault/.ai/ui_guidelines.md` | Tema escuro, paleta Síntese, wordmark Sora |
| Schema + seed do grafo | `src/db/cypher/01-schema-e-seed.cypher` | Cenário de demo plantado (CLI001 pede RJ e acende 4 vizinhos) |
| As 5 queries do motor | `src/db/cypher/02-queries-motor.cypher` | Contágio, score 0-1000, red flags, recomendação, KPIs |
| Estrutura do monólito modular | `src/` | Backend 6 módulos + frontend com grafo e painel |

## Em aberto

| Item | Dono | Bloqueia |
|---|---|---|
| Instância AuraDB criada e populada | Analista A1 | Tudo que roda |
| Agentes no watsonx Orchestrate | Analista A2 | Demo dos agentes no pitch |
| Backend rodando contra o Aura | Dev D1 | Frontend com dado real |
| Frontend renderizando o grafo | Dev D2 | A cena do pitch |
| **Project Canvas** (entregável obrigatório) | Erick | Submissão às 15:00 |
| **Roteiro do pitch de 3 min** | Erick | Avaliação 15:20 |

## Decisões tomadas que o time precisa saber

- O produto se chama **Lastro**.
- O desafio **não exige código** — Canvas e pitch são os obrigatórios; app,
  agentes, código e painéis são "entregáveis competitivos". Decisão do Erick:
  fazemos MVP funcional mesmo assim, porque é o que diferencia em Viabilidade
  Técnica (25% da nota). Mas **o Canvas tem prioridade absoluta sobre o build.**
- Painel de KPIs sai como artefato separado, não dentro do sistema.
- Números aparecem na tela (R$, dias, score). A regra antiga de "nada de número
  cru" era do projeto anterior e foi derrubada.

## Cenário da demo (todo mundo conta a mesma história)

`CLI001 — Agro Vale do Cerrado` pede Recuperação Judicial. O Lastro propaga o
risco e acende quatro clientes que ninguém ligava a ele:

| Cliente | Acende por | Peso |
|---|---|---|
| CLI002 Fazenda Santa Luzia | sócio em comum no QSA (João Batista Moreira) | 0,80 |
| CLI003 Agropecuária Horizonte | avalista em comum (Marcos Ferreira Duarte) | 0,85 |
| CLI005 Terra Nova | mesmo grupo econômico via CLI003 | 0,90 |
| CLI004 Sítio Boa Esperança | mesma região e cultura, e ainda tem embargo IBAMA | 0,45 |

`CLI006 Fazenda Ipê Amarelo` é o controle: nenhum vínculo, continua verde.
É isso que prova que o sistema não está pintando a carteira toda de vermelho.
