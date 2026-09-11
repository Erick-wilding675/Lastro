# Matching Model

<!--
  Especificação da lógica de comparação entre Talent Model e Project Genome —
  os três níveis (individual, squad, portfólio) e os agentes especializados de
  cada dimensão. Preenchido junto ao Step 3b (Data Model) e ao Step 4
  (Architecture), depois de aprovados.
-->

**Status:** Rascunho completo — corte agente/função, pesos e persistência da explicação decididos por Erick em 11/09 (Step 4).

> **Fonte:** `Tese-Talent_Graph_IBM.pdf`, seção IV (Matching Model), e `Resumo-Tecnico-Talent_Graph_IBM.pdf`, seções IV–VIII. Grande parte da lógica já está definida lá; este arquivo estrutura o que for confirmado para o MVP do hackathon.

## Princípio

O Matching Model produz **recomendação, não decisão**. Todo score é explicável e decomposto por dimensão — nunca uma caixa-preta. Ver [../harness.md](../harness.md).

## Nível 1 — Adequação Individual

| Dimensão | Implementação (decidido 11/09) | Peso (MVP) |
|---|---|---|
| Competências | **Agente LLM** — Competency Matching Agent (watsonx Orchestrate) | Uniforme |
| Papéis | **Agente LLM** — Role Matching Agent (watsonx Orchestrate) | Uniforme |
| Interesse e Preferência | **Agente LLM** — Interest Alignment Agent (watsonx Orchestrate) | Uniforme |
| Experiência Contextual | **Função determinística** — backend (comparação categórica complexidade/estágio × experiência contextual) | Uniforme |
| Disponibilidade | **Função determinística** — backend | — (funciona como filtro, não soma ao score) |

## Nível 2 — Adequação de Squad

| Dimensão | Implementação (decidido 11/09) | Peso (MVP) |
|---|---|---|
| Cobertura | **Função determinística** — backend (cálculo sobre o grafo) | Uniforme |
| Complementaridade | **Função determinística** — backend | Uniforme |
| Distribuição de Experiência | **Função determinística** — backend | Uniforme |
| Disponibilidade Agregada | **Função determinística** — backend | Uniforme |
| Colaboração | **Função determinística** — backend (lê `COLABOROU_COM`/`AVALIADO_EM`) | Uniforme |

**Racional do corte agente/função (Erick, 11/09):** viram agente LLM só as três dimensões que exigem interpretação semântica de texto livre ou taxonomia difusa (competência declarada vs. evidenciada, papel, interesse). Todas as demais são cálculo determinístico direto sobre o grafo — reduz o risco de escopo de 11 componentes (ver "Risco real de escopo" em [system-description.md](system-description.md)) para 4 agentes LLM de fato (Competency, Role, Interest, mais o Annotation Normalizing Agent de [use-cases.md](use-cases.md)) + funções determinísticas no backend + o Orchestrator. Consistente com a própria Tese: "ferramentas determinísticas executam filtros, cálculos e regras" (Resumo Técnico, seção II.2).

**Pesos (decidido 11/09):** uniformes dentro de cada nível para o MVP — simples de calcular, totalmente auditável, e honesto no pitch ("ainda não calibramos com dados reais de uso — cada dimensão pesa igual até termos histórico suficiente para ajustar", ver Tese, Matching Model item 8, "Pesos são Hipóteses").

**Persistência da explicação (decidido 11/09, ver [ARD.md](ARD.md) ARD-05):** o score decomposto por dimensão de cada recomendação é **materializado** no grafo como a relação `RECOMENDADO_PARA {score_decomposto}` entre `Pessoa` e `Projeto` — não recalculado a cada consulta. Isso é o que permite a Memória Organizacional (UC-05) mostrar squads formados anteriormente sem re-rodar o pipeline.

## Nível 3 — Otimização de Portfólio

Agente especializado: Portfolio Optimization Agent. **Fora do escopo do MVP do hackathon — decidido em 10/09.** Muito trabalho para pouco ganho de pontuação no tempo disponível. Fica documentado aqui como visão futura, igual descrito na Tese/Resumo Técnico, mas não é construído.

## Orchestrator Agent

Coordena o fluxo completo: entrada → ingestão/atualização do Talent Model e Project Genome → validação de evidência e confiança → filtragem de elegibilidade → matching individual → construção e avaliação de squads → [opcional: otimização de portfólio] → geração de recomendação e explicação → revisão e decisão humana → registro de feedback.

Ver [../harness.md](../harness.md) para a nuance sobre a decisão humana **não** ser um gate síncrono dentro desse fluxo.

## Progressão do MVP

Prioridade confirmada pela Tese: **regras e pesos** (comparação direta, determinística, totalmente auditável). Similaridade semântica, análise de grafo e aprendizado a partir do histórico são evoluções posteriores — confirmar no Step 4 se alguma entra no escopo do hackathon.

## Open Questions

1. ~~Quais pesos iniciais usar?~~ Resolvido em 11/09 — uniformes dentro de cada nível para o MVP.
2. ~~O MVP cobre os 3 níveis ou só Nível 1 e 2?~~ Resolvido em 10/09 — só Nível 1 e 2.
3. Como popular o dataset seed artificial mencionado no Resumo Técnico (seção X — MVP)? Ligado à Open Question 3 do system-description.md (em stand-by até o case real).
4. ~~Como o sistema deve se comportar quando nenhuma pessoa disponível atinge um score mínimo de adequação individual?~~ Resolvido em use-cases.md (UC-02/UC-04): sinaliza a lacuna e explica o porquê, mas sempre recomenda ao menos 1–2 candidatos, mesmo sem bater o limiar.
5. ~~Quais dimensões dos Níveis 1/2 viram agente LLM de fato e quais viram função determinística?~~ Resolvido em 11/09 — ver tabelas de Nível 1/2 acima.
