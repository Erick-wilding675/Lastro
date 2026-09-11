# Wireframes

<!--
  Layout de baixa fidelidade de cada tela, para cada dispositivo em que o
  software roda. Terceiro documento da fase de modelagem (Step 3c). Depende
  dos use cases. Só relevante se o MVP tiver UI própria — a confirmar no
  Step 4/5.
-->

**Status:** Aprovado por Erick em 11/09.

**Projeto:** Talent Graph
**Versão:** 0.1 — Rascunho
**Data:** 2026-09-11

> O MVP tem UI própria — aplicação web (ver [system-description.md](system-description.md), Escopo). Confirmado, não condicional.

---

## Dispositivos-alvo

| Dispositivo | Suportado | Notas |
|---|---|---|
| Web — desktop | Sim | Único alvo do MVP. |
| Mobile | Não | Fora de escopo (ver [SRS.md](SRS.md), Fora de Escopo). |

---

## Inventário de Telas

| Tela / estado | Rota / entrada | UC relacionado | Propósito |
|---|---|---|---|
| Tela Inicial (grafo vivo) | `/` | UC-01, UC-02 (ponto de entrada) | Mostra todo o Talent Graph + Project Genome de uma vez; ponto de partida de tudo. |
| Modal — Cadastrar Projeto | overlay sobre `/` | UC-02 | Elicitação direta dos campos do Project Genome. |
| Matching em Movimento | overlay sobre `/`, acionado após o modal | UC-02 | Anima a formação do squad dimensão por dimensão. |
| Painel Lateral — Detalhe do Projeto | drawer sobre `/`, ao selecionar um `Projeto` | UC-01, UC-03, UC-04 | Mostra as dimensões do projeto/squad; hospeda anotações e substituição. |
| Memória Organizacional | `/memoria` | UC-05 | Visão estratégica separada, evolução temporal do Talent Graph. |

---

## Padrão visual compartilhado: estado de aresta e nó no grafo

Antes dos wireframes — um padrão usado em mais de uma tela, então vale fixar uma vez:

| Elemento | Estado | Significado |
|---|---|---|
| Aresta (relação) | Sólida, cor "confirmado" | Membro efetivamente alocado ao squad (`PARTICIPOU_DE` ativa) |
| Aresta (relação) | Tracejada | Recomendação com ressalva — candidato sugerido mesmo sem bater o limiar (ver use-cases.md, UC-02/UC-04, "sempre recomendar 1-2 mesmo com lacuna") |
| Nó de papel/competência | Preenchido (com uma `Pessoa` conectada) | Requisito coberto |
| Nó de papel/competência | "Fantasma" — contorno tracejado, sem preenchimento sólido | Lacuna: nenhuma `Pessoa` bate o critério com confiança suficiente |
| Badge de aviso | Ícone de alerta (▲ ou !) ancorado no canto superior do nó fantasma | Sinaliza a lacuna sem precisar de um número de score — ao clicar/hover, expande um mini-card explicando por que ninguém bateu o critério naquela dimensão e lista os 1-2 candidatos com ressalva (conectados por aresta tracejada) |

Esse par sólido/tracejado + nó fantasma + badge é o mecanismo central de "explicação sem números crus" (NFR-02) — a resposta à pergunta 6 do Step 3c.

---

## Wireframes

### Tela Inicial (grafo vivo) — `/`

**Propósito:** primeira impressão do sistema como organismo vivo, não dashboard. Mostra **todos** os projetos e pessoas do seed simultaneamente (confirmado por Erick — sem filtro/paginação no MVP).
**Ação primária:** clicar num nó `Projeto` (→ Painel Lateral) ou no botão de novo projeto (→ Modal Cadastrar Projeto).
**Interação:** só clicar e arrastar (pan/zoom do grafo de força) — sem busca, sem filtros no MVP.

```
+----------------------------------------------------------------+
|  Talent Graph                                    [+ Novo Projeto] |
+----------------------------------------------------------------+
|                                                                  |
|        (Pessoa)---(Pessoa)                                      |
|            \          |                                         |
|          (Projeto)--(Pessoa)---(Projeto)                        |
|            /  \                    \                            |
|      (Pessoa) (Pessoa)---(Pessoa)  (Pessoa)                     |
|                                                                  |
|         grafo de força ocupa 100% da viewport,                  |
|         sempre em leve movimento (simulação viva)                |
|                                                                  |
+----------------------------------------------------------------+
```

---

### Modal — Cadastrar Projeto (UC-02)

**Propósito:** elicitação direta dos campos do Project Genome (ver [data-model.md](data-model.md), nó `Projeto`).
**Ação primária:** "Criar" → fecha o modal e dispara a animação de Matching em Movimento.
**Estilo:** card com fundo de vidro (glassmorphism) flutuando **sobre** o grafo, que continua visível e em movimento por trás — reforça que o modal é uma interrupção mínima, não uma troca de tela.

```
+----------------------------------------------------------------+
|   [grafo ao fundo, desfocado/dimmed, ainda em movimento]        |
|                                                                  |
|      ┌──────────────────────────────────────────────┐          |
|      │  Novo Projeto                            [X]  │  ← card  |
|      │  vidro fosco / glassmorphism                   │          |
|      │──────────────────────────────────────────────  │          |
|      │  Problema:            [________________]       │          |
|      │  Público-alvo:        [________________]       │          |
|      │  Domínio:             [________________]       │          |
|      │  Funcionalidades      [________________]       │          |
|      │   essenciais:         [+ adicionar]             │          |
|      │  Estágio:             [dropdown]                │          |
|      │  Complexidade         [téc.][prod.][mercado]    │          |
|      │  (3 eixos):                                     │          |
|      │                                                  │          |
|      │              [ Cancelar ]   [ Criar Projeto ]   │          |
|      └──────────────────────────────────────────────┘          |
+----------------------------------------------------------------+
```

---

### Matching em Movimento — overlay sobre `/`

**Propósito:** dramatizar a formação do squad, dimensão por dimensão, em vez de entregar um resultado estático (ver SRS.md, item 2 da Visão de Interface).
**Ação primária:** nenhuma — é uma animação, não uma interação; termina abrindo automaticamente o Painel Lateral com o squad já formado.
**Sequência:** o modal fecha, a câmera do grafo centraliza no novo nó `Projeto`, e candidatos se destacam progressivamente: competência → papel → interesse → disponibilidade → cobertura → complementaridade → colaboração. Ao final, as arestas `PARTICIPOU_DE` já estão desenhadas como sólidas — sem gate de aprovação no meio do caminho (ver [harness.md](../harness.md)).

```
+----------------------------------------------------------------+
|  Formando squad para "Novo Projeto"...                          |
+----------------------------------------------------------------+
|                                                                  |
|              (Projeto: NOVO) ← câmera centraliza aqui            |
|             ╱   |   ╲                                            |
|      (Pessoa) (Pessoa) (Pessoa)  ← se destacam em sequência,     |
|         ↑ passo 1: competência    dimensão por dimensão,         |
|         ↑ passo 2: papel           até virar squad formado        |
|         ↑ passo 3: interesse...                                  |
|                                                                  |
+----------------------------------------------------------------+
```

---

### Painel Lateral — Detalhe do Projeto (UC-01, UC-03, UC-04)

**Propósito:** um único componente de painel lateral (drawer), reaproveitado para acompanhar o projeto (UC-01) e para adicionar anotações pós-formação (UC-03) — mesma superfície, abas diferentes. Escolha deliberada: manter o grafo visível ao lado, em vez de navegar para uma tela cheia separada, preserva a sensação de "organismo vivo" e permite comparar o painel com o grafo ainda interativo ao mesmo tempo (útil sobretudo para UC-01, planejamento de sprint com apoio visual do grafo).

**Ação primária:** varia por aba — em "Squad" é substituir um membro (UC-04); em "Anotações" é salvar (aciona o Annotation Normalizing Agent).

**Recomendação de fluxo (Erick pediu para eu sugerir o melhor caminho para o MVP):** painel lateral deslizando da direita, ocupando ~35–40% da largura, com o grafo ainda visível e clicável nos 60% restantes — não bloqueia a tela, não exige navegação. Três abas: **Genoma do Projeto** (problema, requisitos, complexidade/estágio — Project Model), **Squad** (grafo do Talent Graph daquele projeto + substituição), **Anotações** (texto livre + histórico do que o Annotation Normalizing Agent já normalizou).

```
+----------------------------------------------------------------+
|  [grafo, ~60% da tela, ainda navegável]  |  Projeto: Acme CRM   |
|                                           |  [Genoma][Squad][Anot]|
|      (Pessoa)---(Pessoa)                 |----------------------|
|          \                               |  aba "Squad":         |
|        (Projeto*)--(Pessoa)              |  ┌────────────────┐  |
|         (*=selecionado)                  |  │ Ana — Eng. Dados│  |
|                                           |  │ Beto — PO       │  |
|                                           |  │ (vaga) ▲ lacuna │◀─┼── nó fantasma
|                                           |  │  [ver substitutos]│  |  + badge
|                                           |  └────────────────┘  |
|                                           |  [ Cobertura, comple-|
|                                           |    mentaridade... ]  |
+----------------------------------------------------------------+
```

**Substituição de membro (UC-04), dentro da aba Squad:**

```
  Ana — Eng. Dados       [Substituir ▾]
     ┌─────────────────────────────┐
     │ Lista de substituição:       │
     │  • Carla — 92% cobertura     │  ← sem números crus na tela
     │    (mostrado como barra/tag, │     principal; aqui, no fluxo
     │     não como "92%" solto)    │     de decisão de troca, é
     │  • Diego — cobertura parcial │     aceitável mais detalhe
     │    ⚠ lacuna em "Cloud"       │     técnico (ver Open Question
     └─────────────────────────────┘     abaixo)
```

---

### Memória Organizacional — `/memoria`

**Propósito:** tela separada e estratégica — evolução temporal do Talent Graph através dos projetos simulados do seed. Não é um apêndice; é o que prova, na demo, que o sistema é aprendizado e cultura organizacional contínuos (ver [SRS.md](SRS.md), item 3 da Visão de Interface).
**Ação primária:** nenhuma ação transacional — é uma tela de leitura/insight.
**Conteúdo (definido por Erick, 11/09):** linha do tempo com evolução temporal; relações mais recorrentes (pares que mais colaboraram); pessoas com mais experiência acumulada; evolução de cobertura de competências ao longo dos projetos simulados — visão estratégica, não operacional.

```
+----------------------------------------------------------------+
|  Memória Organizacional                          [← voltar]      |
+----------------------------------------------------------------+
|  Linha do tempo:  proj.1 ──▶ proj.2 ──▶ proj.3 ──▶ proj.4 ...    |
|                                                                  |
|  +----------------------+  +--------------------------------+  |
|  | Colaborações mais     |  | Evolução de cobertura de        |  |
|  | recorrentes (pares)   |  | competências ao longo do tempo  |  |
|  | Ana ↔ Beto: 4 projetos|  | [gráfico de área/linha crescente]|  |
|  +----------------------+  +--------------------------------+  |
|                                                                  |
|  +------------------------------------------------------------+ |
|  | Pessoas com mais experiência contextual acumulada           | |
|  | [ranking ou destaque no próprio grafo, não uma tabela crua]  | |
|  +------------------------------------------------------------+ |
+----------------------------------------------------------------+
```

---

## Modelo de Navegação

```
  Tela Inicial (/) ──┬──▶ Modal Cadastrar Projeto ──▶ Matching em Movimento ──▶ Painel Lateral (Squad)
                      │
                      ├──▶ Painel Lateral (clique num Projeto existente) ──┬──▶ aba Genoma
                      │                                                     ├──▶ aba Squad ──▶ Substituição (UC-04)
                      │                                                     └──▶ aba Anotações (UC-03)
                      │
                      └──▶ Memória Organizacional (/memoria) ──▶ [← voltar para Tela Inicial]
```

---

## Questões em Aberto

| # | Questão | Owner | Status |
|---|---|---|---|
| 1 | Na lista de substituição (UC-04), até que ponto mostrar "mais detalhe técnico" (ex. % de cobertura) é aceitável, já que NFR-02 proíbe números crus na UI principal — esse é um contexto de decisão mais técnico, ou a regra vale sem exceção? | Erick + equipe fullstack | Open — Step 4/5 |
| 2 | Biblioteca de grafo de força exata (react-force-graph, vis-network, D3 puro) — critério de escolha entre elas dado o tempo dos 2 devs fullstack | Erick + equipe fullstack | Open — Step 4 |
| 3 | O gráfico de "evolução de cobertura de competências" na Memória Organizacional usa a mesma biblioteca de grafo, ou uma lib de charts separada (ex. Chart.js/D3)? | Erick + equipe fullstack | Open — Step 4 |
