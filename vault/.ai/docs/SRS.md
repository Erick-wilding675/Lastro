# SRS — Especificação de Requisitos de Software

**Status:** Aprovado por Erick em 10/09 ("Excelente ideia... Tudo de acordo.").

**Projeto:** Talent Graph
**Versão:** 0.2 — Rascunho
**Data:** 2026-09-10

---

## O que o sistema é

Um processo inteligente e contínuo de gestão de pessoas e projetos — não uma calculadora de squad de uso único. A aplicação web é a superfície visível desse processo: cria projetos, aciona o pipeline de matching sobre um Talent Graph e um Project Genome já povoados (Neo4j), e expõe tanto a recomendação de um squad quanto a evolução do conhecimento organizacional ao longo de múltiplos projetos.

**Usuários-alvo:** gestores de projetos e organizações como um todo (ver [system-description.md](system-description.md)).

---

## Requisitos Funcionais

| FR | Prioridade | Resumo |
|---|---|---|
| FR-01 | MVP | Cadastro de **novo projeto** (elicitação direta) — vira um nó no Project Genome. |
| FR-02 | MVP | **Não existe cadastro de pessoa pela interface.** Pessoas vêm exclusivamente do dataset seed artificial enriquecido, pré-carregado no Talent Graph. |
| FR-03 | MVP | Ao criar um projeto, o pipeline de matching (Nível 1 + Nível 2) roda e aloca candidatos entre os funcionários fictícios do seed automaticamente. |
| FR-04 | MVP | A recomendação de squad é apresentada como **visualização interativa do grafo** — não uma lista ou dashboard genérico. Ver "Visão de Interface" abaixo. |
| FR-05 | MVP | Explicação por dimensão é sempre **narrativa/visual** — nunca um número solto de "confiança" ou compatibilidade exposto na UI. O score continua calculado e decomposto internamente (rastreabilidade/GIRO); o que muda é a apresentação. |
| FR-06 | MVP | Usuário pode explorar squads alternativos (ex: trocar um membro) e ver a explicação recalculada — interação exploratória, não output estático de mão única. |
| FR-07 | MVP | Uma segunda vista de **"memória organizacional"** mostra a evolução do Talent Graph ao longo de múltiplos projetos simulados do seed (squads já formados, cobertura de competências mudando, colaborações se acumulando). |
| FR-08 | Pós-MVP | Previsão de sucesso do squad com dados temporais reais. Mencionada conceitualmente no pitch (ver Open Question 3 do system-description.md); não implementada. |

---

## Visão de Interface (requisito de produto, a formalizar no Step 3c)

Erick foi explícito: nada de "cadastra projeto → sistema recomenda → confirma → dashboard genérico". Três ideias concretas para carregar para o Wireframes, já alinhadas ao FR-04/05/06/07 e ao [harness.md](../harness.md):

1. **O grafo é a tela inicial, não um dashboard.** Um grafo de força (force-directed — ex: react-force-graph, vis-network, D3) mostrando pessoas e projetos, sempre "vivo" — a primeira impressão é a de um organismo, não de uma tabela.
2. **"Matching em movimento" no lugar de um resultado estático.** Ao criar um projeto, os candidatos se destacam progressivamente no grafo, dimensão por dimensão (competência → papel → interesse → disponibilidade → cobertura → complementaridade → colaboração), até o squad se desenhar — dramatiza a interpretabilidade do GIRO como experiência visual, não como log invisível.
3. **"Memória organizacional" como segunda vista, não um apêndice.** Um painel separado mostrando a evolução do Talent Graph através dos projetos simulados do seed — isso é o que prova, na demo, que o sistema é aprendizado e cultura organizacional, e não um formador de squad de uso único (ver reformulação da narrativa em [system-description.md](system-description.md)).

Tecnicamente viável no orçamento de tempo: bibliotecas de grafo de força são rápidas de integrar e o efeito visual/pitch compensa bem o esforço, dado que os 2 desenvolvedores fullstack ficam concentrados nisso.

---

## Requisitos Não-Funcionais

| NFR | Prioridade | Requisito |
|---|---|---|
| NFR-01 | MVP | A visualização de grafo é a experiência primária de interação — não um dashboard de KPIs como padrão principal. |
| NFR-02 | MVP | Nenhum número de confiança/score bruto exposto na UI (ver FR-05). |
| NFR-03 | MVP | Toda decisão do pipeline permanece rastreável e observável (GIRO) no backend/logs, mesmo que a UI não mostre números crus. |
| NFR-04 | Pós-MVP | Segurança formal (RLS, criptografia) fora do MVP — ver Fora de Escopo. |

---

## Restrições

- 12h de desenvolvimento (11/09 19h–21h + 12/09 9h–19h), case revelado só às 19h de 11/09.
- Stack: IBM watsonx Orchestrate + IBM Bob + Neo4j AuraDB free tier (ver [ARD.md](ARD.md), ARD-01).
- Verba considerada **infinita** para efeitos deste hackathon — nenhuma restrição orçamentária a resolver no MVP.

---

## Fora de Escopo (MVP)

- Cadastro de pessoa nova pela interface.
- Aplicativo mobile.
- Previsão de sucesso do squad com dados temporais reais (Pós-MVP — FR-08; mencionada só conceitualmente no pitch, se houver tempo).
- Row-Level Security (RLS).
- Criptografia de dados.
- Qualquer limite ou otimização de orçamento de infraestrutura.
