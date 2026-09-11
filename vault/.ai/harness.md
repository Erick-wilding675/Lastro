# Harness — GIRO

<!--
  Framework de governança dos agentes de IA usados para construir e operar o
  Talent Graph. Não é um documento de produto: é a "cereja do bolo" do método
  de desenvolvimento de Erick/Síntese Labs, aplicado a este projeto.
-->

**Status:** Rascunho completo — conteúdo já definido por Erick, não depende de entrevista.

O Harness é o mecanismo que garante, sobre qualquer agente envolvido neste projeto — tanto os agentes que **constroem** o Talent Graph (IBM Bob, Claude, etc.) quanto os agentes que **operam dentro** do Talent Graph (Orchestrator Agent, Competency Matching Agent, etc.) — quatro pilares, resumidos no acrônimo **GIRO**:

| Pilar | O que garante |
|---|---|
| **G**overnança | Quem pode ler/escrever o quê, e sob qual regra. |
| **I**nterpretabilidade | Por que uma decisão ou análise do agente chegou àquele resultado. |
| **R**astreabilidade | De onde veio cada decisão e rota, ligada às rotas declaradas na idealização (Tese). |
| **O**bservabilidade | Acompanhamento de desempenho e eficiência dos agentes no dia a dia (foundation). |

## Por que isso importa aqui em particular

Existe um paralelo direto entre o Harness e o próprio produto: o Talent Graph promete, para os *seus* usuários, que toda recomendação de squad seja explicável, decomposta por dimensão e nunca uma caixa-preta (ver [docs/matching-model.md](docs/matching-model.md), princípio de Transparência). O Harness aplica **o mesmo princípio** aos agentes que constroem e operam o sistema — a explicabilidade não é só uma feature do produto, é como o próprio projeto é construído.

## Rastreabilidade

- Toda decisão de rota tomada por um agente (de construção ou de operação) deve poder ser ligada de volta à rota declarada na Tese ou em um ARD ([docs/ARD.md](docs/ARD.md)).
- Nenhuma inferência de IA — sobre competência de uma pessoa ou sobre uma escolha de arquitetura — vira fato consolidado sem registrar sua fonte (ver Talent Model, item 5 — "Evidência e Fonte" — e Project Model, item 12 — "Fonte e Confiança", na Tese).
- **A definir:** onde e como esses registros de rastreabilidade são armazenados no MVP (log estruturado, banco de decisões, ou ambos) — vira uma entrada em [docs/ARD.md](docs/ARD.md) quando decidido.

## Observabilidade

- Cada agente especializado do Matching Model (Competency Matching Agent, Role Matching Agent, Coverage Agent, etc. — ver [docs/matching-model.md](docs/matching-model.md)) deve expor o suficiente para acompanhar desempenho e eficiência: número de chamadas, latência, taxa de confirmação humana das sugestões, taxa de dados de baixa confiança.
- **Decidido (10/09):** usar a rastreabilidade/observabilidade nativa do IBM watsonx Orchestrate se ela cobrir a necessidade. Caso não cubra, fallback para Langfuse — já em uso no restante do método da Síntese Labs (hooks em `~/.claude/settings.json`). Confirmar qual dos dois casos se aplica assim que houver acesso prático ao watsonx Orchestrate (early no Step 4 ou já no dia do hackathon).

## Governança

- Aplica diretamente as regras de acesso já definidas na idealização: separação entre **registro de fato** (visível a qualquer pessoa com acesso ao Talent Model) e **nota de avaliação** (visível só a quem decide formação de squad, nunca à pessoa avaliada) — Talent Model, item 11 da Tese.
- Mesma lógica de camadas de acesso para informação sensível de projeto (Project Model, item 14 da Tese).
- **A definir:** modelo de autenticação/autorização do MVP (Step 4 — Architecture).

## Interpretabilidade

- Todo score do Matching Model é decomposto por dimensão (competências, papéis, interesse, experiência, disponibilidade / cobertura, complementaridade, distribuição, disponibilidade agregada, colaboração) — nunca um número isolado.
- Toda sugestão gerada por IA (extração de currículo, extração de documentação de projeto) é apresentada como sugestão sujeita a confirmação, nunca como fato definitivo.

## Nuance importante: a "decisão humana final" não é um gate síncrono

O Talent Graph não deve ser implementado como "o modelo retorna um squad e explica o porquê, esperando uma resposta do humano para prosseguir". A liderança humana mantém a decisão final sobre **formar o time no mundo real** — mas isso não deve bloquear ou interromper o pipeline inteligente. O sistema é, antes de tudo, uma ferramenta contínua de apoio à gestão: ele armazena informação, evolui o conhecimento sobre pessoas, projetos e a organização como um todo, e produz recomendações de squad como uma das suas entregas — não como uma etapa que trava esperando aprovação para o resto do sistema continuar funcionando.

**Manifestação concreta no fluxo (confirmada por Erick no Step 3a, 10/09):** ver [docs/use-cases.md](docs/use-cases.md), UC-02 e UC-03. Ao cadastrar um projeto, o sistema forma o squad e já registra as relações no grafo ao final da animação de matching — sem pausar esperando aprovação. Só **depois** disso o gestor pode adicionar anotações/requisitos/impedimentos em texto livre, que um agente dedicado (Annotation Normalizing Agent) interpreta e devolve normalizado nas dimensões. A aprovação humana existe, mas é posterior e não-bloqueante — nunca um gate síncrono no meio do pipeline.

## Open Questions

1. ~~Qual ferramenta de observabilidade usar?~~ Resolvido em 10/09 — ver seção Observabilidade acima (watsonx nativo, fallback Langfuse).
2. ~~Onde e em que formato os registros de rastreabilidade (fonte + confiança + decisão) são persistidos no MVP?~~ Parcialmente resolvido em 11/09 (Step 4, ARD-05): a decisão de matching em si (score decomposto) é materializada no próprio grafo, como a relação `RECOMENDADO_PARA`. Ainda em aberto: onde fica o log de eventos/observabilidade operacional (chamadas, latência) — depende de qual opção de Observabilidade acima se confirmar no dia do hackathon.
3. Quem, na prática, dentro da equipe do hackathon, tem permissão de leitura sobre notas de avaliação e informação sensível de projeto? Na prática, o MVP roda com um único papel autenticado (Gestor de Projetos — ver [docs/data-model.md](docs/data-model.md), Decisão de modelagem #2), então a resposta funcional é "qualquer um operando o sistema no papel de Gestor". Governança formal multi-papel fica para pós-MVP.
