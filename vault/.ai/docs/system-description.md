# System Description

**Status:** Aprovado por Erick em 10/09 (com o adendo de narrativa registrado abaixo).

**Projeto:** Talent Graph
**Versão:** 0.2 — Rascunho
**Data:** 2026-09-10

---

## Visão Geral

> **Adendo de Erick, aprovado em 10/09 — importante para o pitch:** a narrativa do Talent Graph nunca deve se reduzir a "recomendação de squad explicável". É um **processo inteligente e contínuo de gestão de pessoas e projetos** — aprendizado organizacional, melhoria processual e cultura — do qual a recomendação de squad é apenas uma das saídas, não a identidade do produto.

O Talent Graph é, por ora, o pipeline genérico de inteligência para gestão de equipes e projetos descrito na Tese: transforma dados dispersos sobre pessoas e projetos em conhecimento organizacional vivo, que evolui a cada projeto executado. Formar um squad explicável é uma capacidade desse processo — não o processo inteiro. Não é recortado para um nicho — é infraestrutura de gestão aplicável a qualquer organização que forma equipes para projetos.

Duas estruturas são **implementadas fisicamente**, não só descritas: o **Talent Graph** como um grafo de pessoas, e o **Project Genome** como um modelo de características de projeto. Um pipeline de agentes, orquestrado sobre IBM watsonx Orchestrate, compara as duas e devolve recomendações de squad explicáveis, decompostas por dimensão. IBM Bob é o backbone de engenharia usado para construir o sistema.

---

## Problema & Valor

- **Problema que resolve:** formação de squads depende de memória e percepção de poucas pessoas; não escala, é pouco rastreável e ignora complementaridade real de competências (ver Tese, seção I).
- **Quem tem esse problema:** gestores de projetos e organizações como um todo — qualquer estrutura que precisa formar equipes repetidamente.
- **Como é resolvido hoje:** indicação, proximidade pessoal, disponibilidade momentânea, percepção subjetiva.
- **O valor que agregamos:** um processo contínuo de inteligência organizacional — conhecimento estruturado e evolutivo sobre pessoas, projetos e colaborações — que entre outras saídas produz recomendações de squad explicáveis e auditáveis, sem nunca substituir a decisão humana de gestão.

> **Tensão identificada, em stand-by:** o produto é deliberadamente genérico, mas o critério de maior peso do edital (Diagnóstico do Problema & Impacto, 25%) pede "dados para embasar a escolha do problema" e "quem será impactado" de forma concreta. Decisão de Erick (10/09): não resolver isso agora — a narrativa concreta de diagnóstico só é definida quando o case oficial do hackathon for revelado (11/09, 19h). O motor do produto continua genérico até lá.

---

## Usuários & Atores

| Ator | Descrição | Nível técnico | Escala aproximada | No MVP? |
|---|---|---|---|---|
| Gestor de projetos | Forma squads, consulta recomendações, mantém governança sobre notas de avaliação | Baixo–médio | 1 por organização/projeto | **Sim** |
| Organização | Mantém o Talent Graph e o Project Genome vivos ao longo do tempo | — | N/A (ator institucional) | Sim (implícito) |
| Orchestrator Agent + agentes especializados | Executam ingestão, matching e explicação | — (sistema) | 1 orquestrador + N agentes por dimensão | **Sim** |
| Alta Gestão (diretoria, presidência) | Consumiria visão institucional agregada sobre pessoas e projetos — reforça a narrativa de apoio à decisão estratégica de gestão de pessoas | Baixo | 1 por organização | **Não** — multi-tenant, só narrativa de pitch (ver [use-cases.md](use-cases.md), UC-06) |
| Talento (autoatendimento) | Observaria, com acesso próprio, seus projetos, o Project Genome relacionado e sua evolução pessoal no Talent Graph | Baixo | Múltiplos por organização | **Não** — multi-tenant, só narrativa de pitch (ver [use-cases.md](use-cases.md), UC-07) |

> Confirmado por Erick no Step 3a (10/09): Alta Gestão e Talento entram como atores válidos para a narrativa do produto — "alimenta a narrativa de auxílio na visão institucional sobre pessoas" — mas exigem multi-tenancy e não entram no MVP do hackathon.

---

## Objetivos & Sucesso

**Objetivos que o MVP do hackathon precisa alcançar:**
1. Agentes especializados do Matching Model, Nível 1 e 2, implementados e orquestrados (Nível 3 — otimização de portfólio — fora do MVP, decidido em 10/09: muito trabalho para pouco ganho no tempo disponível).
2. Aplicação web funcional (frontend + backend).
3. Pipeline de orquestração moderno, bem documentado, sobre IBM watsonx Orchestrate.
4. Talent Graph implementado fisicamente como grafo de pessoas.
5. Project Genome implementado fisicamente como modelo de características de projeto.
6. GIRO com cobertura completa e demonstrável ao vivo (ver [../harness.md](../harness.md)).
7. A demo prova visualmente que o sistema é aprendizado e cultura organizacional, não um formador de squad de uso único — ver "memória organizacional" em [SRS.md](SRS.md).

**Sucesso é:** o sistema web executando o pipeline completo — ingestão, matching, explicação — sobre múltiplos projetos simulados, com dataset seed artificial enriquecido o suficiente para produzir recomendações quase perfeitas, e GIRO 100% coberto e visível na demo.

> **Risco real de escopo:** o Resumo Técnico lista 11 agentes especializados (5 no Nível 1, 5 no Nível 2, mais o Orchestrator) — sem contar Nível 3. "Todos os agentes" nesse sentido literal, em ~10h efetivas de build com 2 pessoas na frente de agentes/orquestração, é uma meta apertada. O próprio Resumo Técnico já abre a saída para isso: nem todo agente precisa ser um agente LLM — "ferramentas determinísticas executam filtros, cálculos e regras" (seção II.2). Recomendo decidir no Step 4 quais dimensões viram agentes de fato (raciocínio/interpretação) e quais viram funções determinísticas chamadas pelo Orchestrator — reduz superfície de implementação sem violar o princípio arquitetural da própria Tese.

---

## Escopo

- **Dentro do MVP:** Matching Model Nível 1 e 2, Talent Graph e Project Genome fisicamente implementados em Neo4j (AuraDB, tier gratuito — ver [ARD.md](ARD.md), ARD-01), aplicação web (front+back), orquestração sobre watsonx Orchestrate, GIRO completo, dataset seed artificial enriquecido.
- **Fora do MVP, decidido:** Nível 3 (otimização de portfólio) — documentado como visão futura, não construído.
- **Fora do MVP por padrão (a própria Tese trata como evolução pós-MVP):** similaridade semântica, análise de grafo avançada, aprendizado a partir de histórico.
- **Visão de longo prazo:** a descrita na Tese — infraestrutura organizacional completa de talent intelligence.

---

## Contexto & Restrições

- **Prazo:** 12h de desenvolvimento (11/09 19h–21h + 12/09 9h–19h), case revelado só às 19h de 11/09.
- **Equipe:** 5 pessoas — Erick (engenheiro de IA, tech lead + pitch), 2 analistas de sistemas em agentes + orquestração, 2 desenvolvedores fullstack em aplicação + dados (front e back). Erick atua transversalmente apoiando os dois subgrupos técnicos, além de liderar o pitch.
- **Stack fixa:** IBM watsonx Orchestrate (orquestração) + IBM Bob (engenharia) — obrigatórios pelo contexto do hackathon/parceria IBM.
- **Observabilidade:** usar a rastreabilidade nativa do watsonx Orchestrate se ela cobrir a necessidade; caso contrário, fallback para Langfuse (já usado no restante do método da Síntese Labs). Ver [../harness.md](../harness.md).
- **Sistemas a integrar:** nenhum sistema externo além do ecossistema IBM confirmado até aqui.

---

## Questões em Aberto

| # | Questão | Owner | Status |
|---|---|---|---|
| 1 | ~~Em qual subgrupo Erick atua?~~ | Erick | Resolvido 10/09 — tech lead transversal + pitch |
| 2 | ~~Nível 3 entra no MVP?~~ | Erick | Resolvido 10/09 — fora do MVP |
| 3 | Domínio concreto para o dataset seed / narrativa de Diagnóstico do Problema | Erick | **Em stand-by** — decidido quando o case real for revelado (11/09, 19h) |
| 4 | ~~Tecnologia de grafo?~~ | Erick + equipe | Resolvido 10/09 — Neo4j (AuraDB, tier gratuito), ver [ARD.md](ARD.md) ARD-01 |
| 5 | ~~Quais dimensões do Matching Model viram agente LLM de fato vs. função determinística?~~ | Erick + Claude | Resolvido 11/09 — ver [matching-model.md](matching-model.md) |
