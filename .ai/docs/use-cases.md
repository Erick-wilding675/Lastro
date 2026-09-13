# Use Cases & User Flows

<!--
  Como os usuários interagem com o sistema: atores, casos de uso e os fluxos
  passo a passo das jornadas-chave.
-->

**Status:** revisado pós-pivô (13/09) — reescrito do zero para o produto real
(Lastro), substituindo a versão anterior que descrevia "Talent Graph" (produto
de squad matching / genoma de equipe), abandonado no pivô de 11/09.

**Projeto:** Lastro
**Versão:** 2.0
**Data:** 2026-09-13

---

## Atores

| Ator | Tipo | Descrição |
|---|---|---|
| Gestor/Analista de Crédito da Krilltech | Humano | Ator único do MVP — não há multi-tenant nem separação por perfil de acesso (consistente com [`architecture.md`](../architecture.md), seção Segurança). Abre a aplicação, investiga exposição, prioriza e executa recuperação, lê o parecer e decide limite/condição de pagamento. Toda decisão de crédito é sempre humana (Hard Rule 1 em [`ai.md`](../ai.md)). |
| Agente Coletor & Parser | Sistema (LLM) | Transforma fonte pública ou documento não estruturado (petição de RJ, certidão, diário oficial) em evento registrado, via `POST /eventos/registrar`. Atua nos bastidores da UC-03. |
| Motor de Decisão & Scoring | Sistema (determinístico, orquestrado) | Encadeia contágio → score → recomendação na ordem obrigatória via `POST /motor/ciclo`. Nunca calcula o número ele mesmo — só dispara as queries e interpreta o que mudou. Atua nos bastidores da UC-01 e UC-03. |
| Agente Sintetizador de Relatórios | Sistema (LLM) | Lê o dossiê (`GET /agentes/dossie/{cliente}`) e redige o parecer de risco em linguagem natural para o gestor decidir. Atua na UC-06. |

> **Nota de escopo:** propagação, scoring e priorização são deterministas em
> Cypher/Python; os agentes de IA entram só onde há texto livre, ambiguidade ou
> redação — nunca para calcular um número (ver [`agentes.md`](agentes.md)).

---

## Casos de Uso

| UC | Ator | Objetivo | Endpoint(s) | Prioridade |
|---|---|---|---|---|
| UC-01 | Gestor de Crédito | Visualizar o mapa de exposição da carteira como rede, não como lista de vencimentos | `GET /carteira/grafo`, `GET /carteira/kpis` | MVP |
| UC-02 | Gestor de Crédito | Investigar por qual vínculo um cliente específico ficou exposto | `GET /agentes/dossie/{cliente}` (drawer), tela `/evento/:id` (passo a passo da propagação) | MVP |
| UC-03 | Gestor de Crédito, com Agente Coletor & Parser e Motor de Decisão atuando nos bastidores | Registrar um evento novo (ex.: petição de RJ) e ver a repropagação em cadeia pela rede | `POST /eventos/registrar`, `POST /motor/ciclo?origem={cliente}` | MVP |
| UC-04 | Gestor de Crédito | Priorizar a fila de recuperação pela capacidade real do time | `GET /recuperacao/priorizar?capacidade=N` | MVP |
| UC-05 | Gestor de Crédito | Executar uma ação de recuperação e registrar a decisão com trilha de auditoria | `POST /recuperacao/executar/{cliente}` | MVP |
| UC-06 | Gestor de Crédito, com Agente Sintetizador atuando nos bastidores | Consultar o parecer redigido sobre um cliente para decidir limite e condição de pagamento | `GET /agentes/dossie/{cliente}` | MVP |
| UC-07 | Gestor de Crédito | Ter uma visão consolidada de KPIs da carteira e do que mudou recentemente | `GET /carteira/kpis`, `GET /eventos/radar?dias=90` | MVP |

---

## Diagrama de Casos de Uso

```
   Gestor/Analista de Crédito (Krilltech)
        │
        ├──▶ UC-01: Visualizar mapa de exposição da carteira
        │           (grafo de força, tela inicial "/")
        │                │
        │                └──▶ UC-02: Investigar por qual vínculo um
        │                            cliente ficou exposto
        │                            (drawer do cliente, ou tela /evento/:id)
        │
        ├──▶ UC-03: Registrar evento novo → repropagação em cadeia
        │           (POST /motor/ciclo?origem=CLI001 — cena da demo)
        │
        ├──▶ UC-04: Priorizar fila de recuperação por capacidade do time
        │                │
        │                └──▶ UC-05: Executar ação de recuperação
        │                            (decisão registrada, trilha de auditoria)
        │
        ├──▶ UC-06: Consultar o parecer do Agente Sintetizador
        │           (decisão final sempre humana — Hard Rule 1)
        │
        └──▶ UC-07: Visão consolidada de KPIs da carteira ("/painel")

   Agente Coletor & Parser ──▶ acionado internamente pela UC-03,
                                grava o evento com fonte e data

   Motor de Decisão & Scoring ──▶ acionado internamente pela UC-01 e UC-03,
                                   nunca calcula o score, só dispara a
                                   propagação e o recálculo na ordem certa

   Agente Sintetizador ──▶ acionado internamente pela UC-06,
                            nunca inventa número, sempre devolve a
                            decisão ao gestor
```

---

## Fluxos de Usuário

### UC-01 — Visualizar Mapa de Exposição da Carteira

**Gatilho:** Gestor de Crédito abre a aplicação.
**Ator:** Gestor/Analista de Crédito da Krilltech
**Pré-condição:** Grafo já populado (seed ou ingestão real).

**Fluxo principal:**
1. Usuário abre a rota `/` (`PaginaGrafo`) e vê a carteira inteira como um grafo de força (`GrafoCarteira`) — clientes, vínculos estruturais (sócio, avalista, grupo econômico) e sistêmicos (região, cultura, safra).
2. A `FaixaKpis`, no topo, mostra os números agregados da carteira (`GET /carteira/kpis`).
3. A cor de cada nó reflete o rating do cliente. No cenário da demo, `CLI001 — Agro Vale do Cerrado` já está em Recuperação Judicial e aparece em vermelho/D, destacado no meio da rede.
4. `StatusConexao` mostra "Motor conectado" quando a API responde.
5. Usuário clica em qualquer nó — em `CLI001` ou em qualquer outro cliente da carteira — para abrir o `DrawerCliente` e seguir para a UC-02.

**Fluxos alternativos / erro:**
- API indisponível → fallback automático para `demoData.js`, com aviso visível de "modo demonstração"; o sistema nunca finge que o número é real.

**Pós-condição:** Usuário tem a visão de rede da carteira como ponto de partida para investigar qualquer cliente.

---

### UC-02 — Investigar por Qual Vínculo um Cliente Ficou Exposto

**Gatilho:** Usuário clica em um nó do grafo (na UC-01) ou abre diretamente a tela de propagação de um evento.
**Ator:** Gestor/Analista de Crédito da Krilltech
**Pré-condição:** Cliente existe no grafo; o motor já rodou ao menos um ciclo (UC-03) sobre a rede em que ele está.

**Fluxo principal:**
1. Clique no nó abre `DrawerCliente`, que busca `GET /agentes/dossie/{cliente}`.
2. Drawer mostra score 0–1000 e badge de rating, a seção "Por que acendeu" (cada entrada de `contagio` com o cliente de origem, o caminho do vínculo e o peso — ex.: `CLI002 Fazenda Santa Luzia` mostra peso 0,75, caminho via sócio em comum João Batista Moreira e via região/cultura), e a recomendação de estratégia do topo.
3. Alternativamente (ou a partir do botão "Ver dossiê"), usuário navega para `/evento/:id` (`PaginaPropagacao`), que ilustra o passo a passo: Evento detectado → Contágio propagado → Risco recalculado → Recuperação priorizada, com um SVG ligando o cliente-gatilho (`CLI001`, em vermelho) a cada cliente acendido, com o peso do vínculo em cada linha.
4. Na cena de demo, `/evento/CLI001` mostra os quatro vizinhos acendendo — `CLI005 Terra Nova` (grupo econômico, 0,90), `CLI003 Agropecuária Horizonte` (avalista em comum, 0,85), `CLI004 Sítio Boa Esperança` e `CLI002 Fazenda Santa Luzia` (região+cultura com quebra de safra confirmada, 0,75) — e `CLI006 Fazenda Ipê Amarelo` aparece como nó de controle, em verde, sem nenhuma linha até o gatilho.

**Fluxos alternativos / erro:**
- Cliente sem nenhuma exposição herdada → drawer mostra os demais componentes normalmente, sem o bloco "Por que acendeu".
- Parâmetro `?foco=` na URL de `/evento/:id` destaca um único vínculo entre os vários acesos, apagando os demais visualmente sem escondê-los.

**Pós-condição:** Usuário sabe exatamente por que aquele cliente está no rating em que está — nunca um número sozinho (Hard Rule 3).

---

### UC-03 — Registrar Novo Evento e Ver a Repropagação em Cadeia

**Gatilho:** Uma fonte pública publica algo relevante (DJE, PGFN, SICAR/IBAMA, Conab/ZARC/INMET) ou chega um documento — no cenário da demo, a petição de Recuperação Judicial de `CLI001 — Agro Vale do Cerrado`.
**Ator:** Gestor/Analista de Crédito da Krilltech (aciona o ciclo), com Agente Coletor & Parser e Motor de Decisão & Scoring atuando nos bastidores.
**Pré-condição:** Cliente de origem já existe no grafo com seus vínculos mapeados.

**Fluxo principal:**
1. Agente Coletor & Parser classifica o achado em um tipo de evento conhecido (`pedido_rj`, `protesto`, `execucao_fiscal`, `embargo_ambiental`, `quebra_safra`, `alteracao_qsa`, `alerta_zarc`, `queda_preco`) e grava via `POST /eventos/registrar`, sempre com fonte e data.
2. Usuário (ou o próprio motor) dispara `POST /motor/ciclo?origem=CLI001`, que encadeia na ordem obrigatória: contágio (acende os vizinhos pelos canais estrutural e sistêmico) → score (recalcula usando o contágio como componente) → recomendação (regenera a fila de recuperação da carteira).
3. Resposta do ciclo devolve as origens processadas, as propagações (quem acendeu, por qual vínculo, com qual peso), quantos clientes foram reavaliados e o resumo agregado.
4. Usuário acompanha o resultado na tela `/evento/CLI001` (UC-02): `CLI005`, `CLI003`, `CLI004` e `CLI002` acendem; `CLI006`, sem vínculo algum com `CLI001`, permanece verde — a prova de que o sistema não pinta a carteira toda de vermelho.

**Fluxos alternativos / erro:**
- Fonte desconhecida → evento descartado, nunca vira evento genérico.
- Achado não se encaixa em nenhum tipo do vocabulário → marcado como não classificado para revisão humana.
- Canal sistêmico sem evento regional confirmando o choque (ex.: sem a quebra de safra da Conab) → peso reduzido (0,75 → 0,30) em vez de peso cheio; a vizinhança correspondente não dispara.
- Chamar os endpoints de contágio/score fora da ordem, sem passar por `/motor/ciclo`, devolve número desatualizado sem erro explícito.

**Pós-condição:** Evento na trilha de auditoria com fonte e data; score e rating dos vizinhos atualizados, cada um carregando o caminho que explica por que acendeu; fila de recuperação (UC-04) regenerada.

---

### UC-04 — Priorizar Fila de Recuperação por Capacidade do Time

**Gatilho:** Time de crédito inicia o período de trabalho.
**Ator:** Gestor/Analista de Crédito da Krilltech
**Pré-condição:** `POST /recuperacao/recomendar-carteira` já rodou (parte do `POST /motor/ciclo` da UC-03) — sem isso a fila vem vazia, não por erro, por ordem de execução do motor.

**Fluxo principal:**
1. Usuário abre `/fila` (`FilaRecuperacao`), que consulta `GET /recuperacao/priorizar?capacidade=N` (capacidade padrão: 5 ações no período).
2. Fila respeita a capacidade real do time — não lista tudo que está elegível, só o que cabe.
3. Cada linha traz cliente/contexto, a estratégia recomendada com valor recuperável estimado e prazo; a cor da linha reflete a urgência (crítica ≤ 20 dias, atenção ≤ 45 dias, normal acima disso).
4. Clique no nome do cliente abre o `DrawerCliente` (UC-02) sem sair da fila, para revalidar o caminho do contágio antes de decidir.

**Fluxos alternativos / erro:**
- Estágio jurídico do cliente funciona como filtro duro — não se propõe cobrança amigável a quem já está habilitado em RJ.

**Pós-condição:** Usuário vê exatamente o que o time consegue executar no período, com o contexto de risco por trás de cada item.

---

### UC-05 — Executar uma Ação de Recuperação e Registrar a Decisão

**Gatilho:** Usuário decide agir sobre um item da fila (UC-04).
**Ator:** Gestor/Analista de Crédito da Krilltech
**Pré-condição:** Existe recomendação pendente para o cliente (gerada pela UC-03).

**Fluxo principal:**
1. Na tela `/fila`, usuário clica em "Marcar executada" para o cliente escolhido.
2. Frontend chama `POST /recuperacao/executar/{cliente}` (parâmetro `responsavel`), que grava quem decidiu e quando sobre qual recomendação, fechando a trilha de auditoria.
3. Cliente sai da fila do período assim que a chamada retorna com sucesso.

**Fluxos alternativos / erro:**
- Nenhuma recomendação pendente para o cliente (ciclo do motor não rodou, ou já foi executada) → `404`, com a orientação de rodar `POST /recuperacao/recomendar-carteira` (ou o ciclo completo) antes.

**Pós-condição:** Ação registrada com trilha de auditoria (Hard Rule 2); fila reflete só o que ainda está pendente. O sistema nunca executa a ação sozinho — quem decide é sempre o gestor (Hard Rule 1).

---

### UC-06 — Consultar o Parecer do Agente Sintetizador

**Gatilho:** Gestor precisa decidir limite/condição de pagamento sobre um cliente específico — tipicamente um dos que acenderam na UC-02/UC-03.
**Ator:** Gestor/Analista de Crédito da Krilltech, com o Agente Sintetizador atuando nos bastidores.
**Pré-condição:** Dossiê do cliente disponível (`GET /agentes/dossie/{cliente}`).

**Fluxo principal:**
1. Agente Sintetizador lê o dossiê do cliente e redige o parecer com estrutura fixa: Situação atual · O que mudou · Exposição herdada e por qual vínculo · Recomendação · Janela de tempo.
2. Todo número citado vem do dossiê — nenhum valor inventado ou arredondado.
3. Parecer nunca afirma que o cliente vai quebrar (fala em exposição e probabilidade) e nunca prescreve instrumento jurídico específico — aponta a fragilidade de cobertura de garantia com número e deixa a escolha do instrumento para a política de crédito da Krilltech.
4. Parecer fecha sempre devolvendo a decisão ao gestor de crédito.
5. Exemplo de referência (usado na demo): parecer sobre `CLI002 — Fazenda Santa Luzia`, cliente adimplente que compartilha sócio em comum com `CLI001` (que pediu RJ) e está na mesma região/cultura com quebra de safra confirmada pela Conab — o parecer nomeia os dois vínculos, não inventa número e recomenda decisão de crédito com prazo.

**Fluxos alternativos / erro:**
- Cliente sem exposição herdada → parecer segue a mesma estrutura, apenas sem o bloco de vínculo de rede.

**Pós-condição:** Gestor decide limite e condição de pagamento com base num texto curto, rastreável e sem número inventado.

---

### UC-07 — Visão Consolidada de KPIs da Carteira

**Gatilho:** Gestor quer uma leitura executiva da carteira, sem abrir cliente por cliente.
**Ator:** Gestor/Analista de Crédito da Krilltech
**Pré-condição:** Ciclo do motor já rodou ao menos uma vez sobre a carteira.

**Fluxo principal:**
1. Usuário abre `/painel` (`PainelGeral`), que consulta `GET /carteira/kpis` (via `KpiGrid`) e `GET /eventos/radar?dias=90`.
2. `KpiGrid` mostra os agregados da carteira (exposição, vencido e demais números da tela inicial, na mesma fonte da UC-01).
3. Seção "O que mudou" lista, em linha do tempo, os eventos dos últimos 90 dias — cliente, descrição/tipo e data — com o selo "Radar IA" indicando que a curadoria de eventos passa pelo Agente Coletor & Parser (UC-03).

**Fluxos alternativos / erro:**
- API indisponível para KPIs ou radar → seções caem para estado vazio (`{}` / `[]`) em vez de travar a tela; nenhum número é inventado no lugar do dado ausente.

**Pós-condição:** Gestor tem, numa única tela, a leitura agregada da carteira e o contexto dos eventos recentes que a movimentaram — a mesma base de dados da UC-01, em formato executivo.

---

## Questões em Aberto

Nenhuma questão de use case ficou pendente da reescrita — as decisões
relevantes (ordem obrigatória do motor, filtro duro por estágio jurídico,
fallback de conexão do frontend, ator único sem multi-tenant) já estão
implementadas e descritas acima. Questões que ainda seguem abertas no produto
(modelo de LLM por agente, cobertura de eventos ao vivo na demo) estão
registradas em [`agentes.md`](agentes.md#questões-em-aberto), não aqui.
