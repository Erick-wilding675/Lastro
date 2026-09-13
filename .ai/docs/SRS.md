# SRS — Especificação de Requisitos de Software

**Status:** revisado pós-pivô (13/09) — reescrito para o produto real (Lastro),
substituindo a versão pré-pivô que descrevia "Talent Graph".

**Projeto:** Lastro
**Versão:** 1.0
**Data:** 2026-09-13

---

## O que o sistema é

Um processo contínuo de gestão de risco relacional e recuperação de capital
para carteiras de recebíveis do agro. A aplicação web é a superfície visível
desse processo: representa clientes, recebíveis, sócios, avalistas e vínculos
de região/cultura como um grafo Neo4j; propaga exposição pelos vínculos entre
clientes; calcula score e rating; prioriza recuperação; e expõe tudo isso
sempre com o caminho que explica a decisão — nunca um número sozinho.

**Usuários-alvo:** área de crédito e financeiro da Krilltech, comitê de
crédito (ver [`system-description.md`](system-description.md)).

---

## Requisitos Funcionais

| FR | Prioridade | Resumo |
|---|---|---|
| FR-01 | MVP | Representar a carteira como grafo: `Cliente`, `Recebivel`, `Socio`, `Avalista`, `GrupoEconomico`, `Regiao`, `Cultura`, `Safra`, `Imovel`, `Evento`, `EstrategiaRecuperacao` (ver [`data-model.md`](data-model.md)). Dados de clientes vêm do seed sintético ou da ingestão de fontes públicas — nunca cadastro manual de pessoa pela interface. |
| FR-02 | MVP | Propagar exposição a partir de um cliente de origem pelos dois canais — estrutural (grupo econômico, avalista, sócio) e sistêmico (região, cultura, safra, revenda) — via `POST /contagio/propagar/{origem}`. |
| FR-03 | MVP | Calcular score 0–1000 e rating A–D, decomposto em 5 componentes (comportamento de pagamento, eventos jurídicos/fiscais, cobertura de garantia com haircut, exposição herdada da rede, risco agro/ambiental), via `POST /scoring/recalcular`. |
| FR-04 | MVP | Encadear contágio → scoring → recomendação na ordem obrigatória com um único endpoint, `POST /motor/ciclo`, evitando número desatualizado por chamada fora de ordem. |
| FR-05 | MVP | Toda exposição exibida na UI vem acompanhada do **caminho** que a produziu (por qual vínculo o risco chegou) — nunca um número isolado (Hard Rule 3 em [`ai.md`](../ai.md)). |
| FR-06 | MVP | Recomendar estratégia de recuperação por cliente (renegociação, barter, cobrança amigável, acordo parcelado, reforço de garantia, protesto, execução judicial, habilitação em RJ), com valor recuperável, prazo e custo, via `POST /recuperacao/recomendar-carteira` / `POST /recuperacao/recomendar/{cliente}`. |
| FR-07 | MVP | Priorizar a fila de recuperação pela capacidade real do time (`GET /recuperacao/priorizar?capacidade=N`) e registrar a execução humana de uma ação (`POST /recuperacao/executar/{cliente}`), gravando **quem** executou e **quando** — o sistema nunca dispara cobrança, protesto ou ação judicial sozinho (Hard Rule 1). |
| FR-08 | MVP | Radar de eventos: registrar ocorrências de fontes públicas (RJ, protesto, execução fiscal, embargo ambiental, quebra de safra, alteração societária, alerta ZARC, queda de preço) com fonte e data, via `POST /eventos/registrar` / `GET /eventos/radar`. Evento relevante dispara repropagação e recálculo dos clientes afetados. |
| FR-09 | MVP | Expor matriz de red flags consolidada da carteira (`GET /scoring/red-flags`). |
| FR-10 | MVP | Visualizar o grafo de exposição da carteira inteira (`GET /carteira/grafo`), os KPIs agregados (`GET /carteira/kpis`) e o detalhe de um cliente com seus vínculos (`GET /carteira/cliente/{cliente_id}`) — a tela inicial (`/`) do frontend. |
| FR-11 | MVP | Gerar dossiê e parecer em linguagem natural para um cliente (`GET /agentes/dossie/{cliente}`), redigido pelo Agente Sintetizador a partir do score decomposto, da exposição com caminho e das recomendações — nunca um número inventado fora do dossiê (ver [`agentes.md`](agentes.md)). |
| FR-12 | MVP | Quatro agentes de IA (Coletor & Parser, Risco Agro & Climático, Motor de Decisão & Scoring, Sintetizador) chamam a API do backend como tools no watsonx Orchestrate — nunca falam direto com o driver do Neo4j (ARD-04; ver [`agentes.md`](agentes.md)). |
| FR-13 | MVP | Frontend com fallback: se a API não responder, a tela usa dados sintéticos do case e **avisa visivelmente** ("Modo demonstração") — nunca finge que o número é real. |
| FR-14 | Pós-MVP | Calibração dos pesos de contágio e da probabilidade de inadimplência com histórico real da Krilltech (ver [`project-canvas.md`](project-canvas.md), bloco 10). Não implementada no MVP — pesos são hipótese declarada e auditável. |

---

## Visão de Interface

A interface não é um dashboard de formulários — é um mapa de exposição vivo,
alinhado a FR-01/02/05 e ao [`harness.md`](../harness.md). Três ideias
concretas, já implementadas em `src/frontend/src/`:

1. **O grafo de força é a tela inicial (`/`), não um dashboard.**
   `PaginaGrafo`/`GrafoCarteira` mostram a carteira inteira como rede, com a
   cor de cada nó refletindo o rating (A verde → D vermelho).
2. **Propagação animada, não um resultado estático.** Em `/evento/:id`
   (`PaginaPropagacao`), a exposição se propaga vizinho por vizinho, com o
   peso do vínculo visível — dramatiza a interpretabilidade como experiência
   visual, não como log invisível.
3. **Fila de recuperação (`/fila`) e painel geral (`/painel`) como vistas
   próprias**, não apêndices do grafo — a fila respeita a capacidade real do
   time; o painel consolida KPIs da carteira.

Biblioteca de grafo de força usada: `react-force-graph-2d` (decisão fechada,
ver [`wireframes.md`](wireframes.md)).

---

## Requisitos Não-Funcionais

| NFR | Prioridade | Requisito |
|---|---|---|
| NFR-01 | MVP | O mapa de exposição (grafo) é a experiência primária de interação — KPIs complementam, não substituem a visão de rede. |
| NFR-02 | MVP | Nenhuma exposição ou score aparece na UI sem a decomposição por componente e, quando há contágio, sem o vínculo que a produziu (FR-05). |
| NFR-03 | MVP | Toda decisão (evento, recálculo, execução de recuperação) permanece rastreável: fonte, data, decomposição, quem decidiu (Hard Rule 2). |
| NFR-04 | MVP | Sem autenticação multi-papel no MVP — um único usuário autenticado (área de crédito), consistente com [`architecture.md`](../architecture.md), seção Segurança. |
| NFR-05 | MVP | Nenhum dado real de produtor entra no repositório — seed sintético e mascarado (Hard Rule 8). |
| NFR-06 | MVP | Falha ruidosa em vez de degradação silenciosa: se o Neo4j cair, `/health` devolve `503` com corpo explicando o motivo; se a API cair, o frontend avisa "Modo demonstração" em vez de mostrar número sintético como se fosse real (Hard Rule 7). |
| NFR-07 | MVP | Nenhum agente de IA calcula, estima ou arredonda número por conta própria: score, exposição, valor recuperável e prazo só existem se vieram na resposta de uma tool (`/contagio/*`, `/scoring/*`, `/recuperacao/*`, `/carteira/*`). O agente lê e interpreta — nunca inventa ou alucina um valor (ver guardrails de cada agente em [`agentes.md`](agentes.md)). |
| NFR-08 | Pós-MVP | Segurança formal (RLS, criptografia de dados sensíveis, autenticação multi-papel) fora do MVP — ver Fora de Escopo. |

---

## Restrições

- Construído em ~12h de hackathon (PMI-DF 2026), case revelado no dia anterior.
- Stack: IBM watsonx Orchestrate + IBM Bob (engenharia) + Neo4j AuraDB free
  tier + Python/FastAPI + React (ver [`ARD.md`](ARD.md)).
- watsonx Orchestrate importa as tools via specs OpenAPI 3.0.3 escritos à mão
  (`src/backend/openapi/`) — o OpenAPI 3.1 autogerado pelo FastAPI não é
  aceito pelo importador (ver [`watsonx-orchestrate-setup.md`](watsonx-orchestrate-setup.md)).
- Verba de infraestrutura ≈ R$ 0 no protótipo (AuraDB free, créditos IBM do
  evento, fontes públicas gratuitas) — ver [`project-canvas.md`](project-canvas.md), bloco 8.

---

## Fora de Escopo (MVP)

- Cadastro de cliente novo pela interface (vem do seed ou da ingestão).
- Aplicativo mobile.
- Calibração da probabilidade de inadimplência com histórico real (FR-14,
  Pós-MVP).
- Autenticação multi-papel, Row-Level Security, criptografia de dados.
- Qualquer instrumento jurídico prescrito automaticamente — o sistema
  diagnostica fragilidade de garantia; qual instrumento adotar é política de
  crédito da Krilltech (Hard Rule 3).
- Execução automática de cobrança, protesto ou ação judicial (Hard Rule 1).
