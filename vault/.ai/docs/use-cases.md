# Use Cases & User Flows

<!--
  Como os usuários interagem com o sistema: atores, casos de uso (com
  diagramas), e os fluxos passo a passo das jornadas-chave. Primeiro documento
  da fase de modelagem (Step 3a). Depende do SRS.
-->

**Status:** Aprovado por Erick em 10/09.

**Projeto:** Talent Graph
**Versão:** 0.1 — Rascunho
**Data:** 2026-09-10

---

## Atores

| Ator | Tipo | Descrição |
|---|---|---|
| Gestor de Projetos | Humano | Ator principal do MVP. Abre a aplicação, acompanha projetos existentes, cadastra projetos novos, aprova/ajusta squads formados, substitui membros, planeja sprints com apoio do grafo. |
| Alta Gestão (diretoria, presidência) | Humano | **Fora do MVP** — ator multi-tenant, registrado aqui só para a narrativa do pitch (alimenta a visão institucional sobre pessoas). Não é construído no hackathon. |
| Talento | Humano | **Fora do MVP** — ator multi-tenant, registrado aqui só para a narrativa do pitch. Autoatendimento: observaria seus próprios projetos, o Project Genome relacionado e sua própria evolução no Talent Graph. Não é construído no hackathon. |
| Orchestrator Agent + agentes especializados | Sistema | Executam ingestão, matching (Nível 1 e 2) e explicação por dimensão. Acionados internamente pelos casos de uso do Gestor — não são atores diretos da UI. |
| Annotation Normalizing Agent | Sistema | Agente dedicado que lê anotações livres do Gestor (requisitos adicionais, impedimentos, observações) inseridas **depois** que um squad já foi formado, interpreta esse texto e devolve normalizado nas dimensões corretas do Project Genome / Talent Graph. Manifestação concreta da regra de [harness.md](../harness.md) — "a decisão humana final não é um gate síncrono". |

> **Nota de escopo:** Alta Gestão e Talento entram como atores multi-tenant pós-MVP porque abrem a superfície de autenticação/autorização e isolamento de dados entre organizações — fora do orçamento de 12h (ver NFR-04, "Fora de Escopo" no [SRS.md](SRS.md)). Ficam documentados aqui para não perder a narrativa no pitch, mas nenhum caso de uso abaixo os implementa.

---

## Casos de Uso

| UC | Ator | Objetivo | FR relacionado | Prioridade |
|---|---|---|---|---|
| UC-01 | Gestor de Projetos | Acompanhar um projeto existente: ver Project Genome, desempenho e o Talent Graph do squad; usar o grafo para planejar sprints e escolher pessoas por task | FR-04 | MVP |
| UC-02 | Gestor de Projetos | Cadastrar um novo projeto e ver o squad se formar ao vivo ("matching em movimento"), sem um gate de aprovação síncrono | FR-01, FR-03, FR-04, FR-05 | MVP |
| UC-03 | Gestor de Projetos | Adicionar detalhes, requisitos, anotações ou impedimentos depois que o squad já foi formado, normalizados de volta nas dimensões por um agente dedicado | FR-01 (extensão pós-formação) | MVP |
| UC-04 | Gestor de Projetos | Substituir um membro do squad (troca exploratória) e ver o esquema se recalcular automaticamente | FR-06 | MVP |
| UC-05 | Gestor de Projetos | Consultar a "memória organizacional": evolução do Talent Graph através dos projetos simulados do seed | FR-07 | MVP |
| UC-06 | Alta Gestão (diretoria, presidência) | Obter uma visão institucional agregada sobre pessoas e projetos | — | **Pós-MVP / só pitch** |
| UC-07 | Talento | Autoconsultar seus próprios projetos, genoma relacionado e evolução pessoal | — | **Pós-MVP / só pitch** |

---

## Diagrama de Casos de Uso

```
   Gestor de Projetos
        │
        ├──▶ UC-01: Acompanhar projeto existente
        │           (Project Genome + Talent Graph do squad, apoio a sprint)
        │
        ├──▶ UC-02: Cadastrar novo projeto
        │           (matching em movimento, squad formado sem gate síncrono)
        │                │
        │                └──▶ UC-03: Adicionar anotações pós-formação
        │                            (Annotation Normalizing Agent normaliza)
        │
        ├──▶ UC-04: Substituir membro do squad
        │           (lista de substituição → escolha → recálculo automático)
        │
        └──▶ UC-05: Consultar memória organizacional
                    (evolução do Talent Graph nos projetos do seed)

   Alta Gestão (diretoria/presidência) ──▶ UC-06: Visão institucional         [pós-MVP, só pitch]
   Talento (autoatendimento)           ──▶ UC-07: Autoconsulta de evolução    [pós-MVP, só pitch]

   Orchestrator Agent + agentes especializados
        │
        └──▶ acionado internamente por UC-02, UC-03 e UC-04 — não aparece
             como ator direto na UI, só nos bastidores (GIRO/rastreabilidade)
```

---

## Fluxos de Usuário

### Acompanhar Projeto Existente (UC-01)

**Gatilho:** Gestor abre a aplicação e, a partir da tela inicial (o grafo vivo — ver "Visão de Interface" no [SRS.md](SRS.md)), escolhe acompanhar um projeto já existente.
**Ator:** Gestor de Projetos
**Pré-condição:** Projeto já cadastrado; squad já formado (via UC-02) ou em formação.

**Caminho principal:**
1. Gestor abre a aplicação e vê o organismo (grafo de força, pessoas + projetos) em movimento na tela inicial.
2. Gestor seleciona um projeto existente para acompanhar.
3. Sistema apresenta todas as dimensões relevantes: Project Genome (requisitos, desempenho) e o Talent Graph do squad alocado àquele projeto.
4. Gestor visualiza os registros de formação da equipe — o mapeamento projeto ↔ pessoas já feito.
5. Gestor usa o grafo para planejar sprints: identifica requisitos do projeto ainda não atendidos e usa a própria visualização como apoio para escolher pessoas para tasks específicas (não é uma feature separada de "atribuir task" no MVP — é o grafo servindo de instrumento de decisão).

**Caminhos alternativos / erro:**
- Projeto sem requisitos pendentes → sistema indica cobertura completa, sem sugestão adicional.
- Projeto ainda em processo de formação (UC-02 em andamento) → sistema direciona para a visualização de "matching em movimento" em vez do estado final.

**Pós-condição:** Gestor tem uma visão viva e decomposta por dimensão do estado do projeto e da equipe; decisões de planejamento (redistribuição de tasks) acontecem fora do sistema, apoiadas por ele.

---

### Cadastrar Novo Projeto (UC-02)

**Gatilho:** Gestor decide criar um novo projeto.
**Ator:** Gestor de Projetos
**Pré-condição:** Talent Graph já populado pelo dataset seed.

**Caminho principal:**
1. Gestor cadastra um novo projeto a partir da tela inicial (elicitação direta — ver FR-01).
2. Sistema anima ao vivo a formação do squad no grafo: candidatos se destacam progressivamente, dimensão por dimensão — competência → papel → interesse → disponibilidade → cobertura → complementaridade → colaboração (ver "Matching em movimento", [SRS.md](SRS.md)).
3. Ao final da animação, o squad recomendado já está formado **e as relações pessoa↔projeto já estão registradas no grafo** — o sistema não pausa esperando uma aprovação explícita antes de registrar isso. Essa é a manifestação concreta da regra de [harness.md](../harness.md): a decisão humana final não é um gate síncrono dentro do pipeline.
4. Gestor visualiza o squad formado e a explicação decomposta por dimensão.
5. Gestor segue em frente (aprovação tácita) ou aciona UC-03 para adicionar informações complementares.

**Caminhos alternativos / erro:**
- Nenhum candidato atinge o limiar de adequação em uma ou mais dimensões → sistema sinaliza a lacuna explicitamente, explica por que ninguém "bateu" o critério **e ainda assim recomenda pelo menos 1–2 candidatos possíveis** — a recomendação nunca retorna vazia, mesmo com lacuna.

**Pós-condição:** Projeto criado; squad formado e registrado no grafo; pronto para UC-03 (anotações) ou UC-04 (substituição) a qualquer momento depois.

---

### Adicionar Anotações Pós-Formação (UC-03)

**Gatilho:** Gestor, depois de ver o squad formado (UC-02), quer registrar detalhes adicionais.
**Ator:** Gestor de Projetos (com o Annotation Normalizing Agent atuando nos bastidores)
**Pré-condição:** Squad já formado por UC-02.

**Caminho principal:**
1. Gestor adiciona texto livre: detalhes do projeto, requisitos adicionais, anotações, impedimentos.
2. O Annotation Normalizing Agent lê esse texto, interpreta e normaliza.
3. Sistema devolve a informação já estruturada, adicionada às dimensões corretas do Project Genome e/ou Talent Graph (ex.: um impedimento vira uma restrição de disponibilidade; um requisito adicional vira uma exigência de competência no Project Genome).
4. Gestor vê o grafo refletir essa atualização.

**Caminhos alternativos / erro:**
- Texto ambíguo ou não mapeável a nenhuma dimensão conhecida → **a definir no Step 4**: o agente sinaliza como não-normalizado em vez de descartar silenciosamente (consistente com a Hard Rule 8 do [ai.md](../ai.md) — falha ruidosa, nunca degradação silenciosa).

**Pós-condição:** Anotações do gestor incorporadas nas dimensões estruturadas, com rastreabilidade de que a origem foi texto livre interpretado por IA (nunca vira "fato consolidado" sem essa marcação — ver [harness.md](../harness.md), Interpretabilidade).

---

### Substituir Membro do Squad (UC-04)

**Gatilho:** Gestor identifica que um membro está indisponível, ausente, ou que uma posição ficou com lacuna sinalizada (ver UC-02, caminho alternativo).
**Ator:** Gestor de Projetos
**Pré-condição:** Squad já formado.

**Caminho principal:**
1. Gestor seleciona o membro antigo (ou o campo em aberto/lacuna) diretamente no grafo.
2. Sistema abre uma lista de substituição com candidatos possíveis para aquela posição.
3. Gestor escolhe o substituto na lista.
4. Sistema atualiza automaticamente o esquema (grafo) para refletir a nova composição — recalcula e registra as novas relações e características.

**Caminhos alternativos / erro:**
- Nenhum substituto atinge o limiar → mesma regra de UC-02: sinaliza a lacuna, explica o porquê, mas recomenda ao menos 1–2 candidatos possíveis.

**Pós-condição:** Squad atualizado; troca registrada com rastreabilidade (o que mudou, quando, por quê).

---

### Consultar Memória Organizacional (UC-05)

**Gatilho:** Gestor navega para a tela separada de "memória organizacional" (ver [SRS.md](SRS.md), item 3 da Visão de Interface).
**Ator:** Gestor de Projetos
**Pré-condição:** Existem múltiplos projetos simulados do seed já processados.

**Caminho principal:**
1. Gestor acessa a tela de memória organizacional (não é um apêndice da tela inicial — é uma vista própria).
2. Sistema apresenta a evolução do Talent Graph ao longo dos projetos simulados do seed: squads já formados, cobertura de competências mudando ao longo do tempo, colaborações se acumulando.

**Pós-condição:** Gestor enxerga visualmente que o sistema é aprendizado e cultura organizacional contínuos — não um formador de squad de uso único (ver adendo de narrativa em [system-description.md](system-description.md)).

---

### (Pós-MVP / só pitch) Visão Institucional (UC-06) e Autoconsulta de Talento (UC-07)

Não implementados no MVP — exigem multi-tenancy e autenticação/autorização por papel, fora do orçamento de 12h. Documentados aqui só para não perder a narrativa no pitch:

- **UC-06 — Alta Gestão:** consumiria uma visão agregada, institucional, sobre pessoas e projetos — reforça a narrativa de que o Talent Graph apoia decisões estratégicas de gestão de pessoas, não só a formação pontual de um squad.
- **UC-07 — Talento:** cada colaborador observaria, com seu próprio acesso, os projetos em que está, o Project Genome relacionado e sua própria evolução dentro do Talent Graph.

---

## Questões em Aberto

| # | Questão | Owner | Status |
|---|---|---|---|
| 1 | Critério de ordenação da lista de substituição em UC-04 (por maior score na mesma dimensão que abriu a lacuna? por score agregado Nível 2?) | Erick + Claude | Open — decidir no Step 3b/4 junto do Matching Model |
| 2 | Onde na UI o Gestor insere anotações em UC-03 (painel lateral no grafo? modal?) | Erick + equipe fullstack | Open — Step 3c (Wireframes) |
| 3 | O Annotation Normalizing Agent é um agente LLM de fato ou uma função determinística com prompt fixo? | Erick + Claude | Open — mesma decisão pendente registrada em [matching-model.md](matching-model.md) |
| 4 | Comportamento exato quando o texto de UC-03 não é mapeável a nenhuma dimensão conhecida | Erick + equipe de agentes | Open — Step 4 |
