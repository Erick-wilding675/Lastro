# Harness — GIRO

<!--
  Framework de governança dos agentes de IA usados para construir e operar o
  Lastro. Não é um documento de produto: é o método de desenvolvimento de
  Erick/Síntese Labs, aplicado a este projeto.
-->

**Status:** revisado pós-pivô e pós-hackathon.

O Harness é o mecanismo que garante, sobre qualquer agente envolvido neste
projeto — tanto os agentes que **constroem** o Lastro (IBM Bob, Claude, etc.)
quanto os agentes que **operam dentro** do Lastro (Coletor & Parser, Risco
Agro & Climático, Decisão & Scoring, Sintetizador — ver
[`docs/agentes.md`](docs/agentes.md)) — quatro pilares, resumidos no
acrônimo **GIRO**:

| Pilar | O que garante |
|---|---|
| **G**overnança | Quem pode ler/escrever o quê, e sob qual regra. |
| **I**nterpretabilidade | Por que uma decisão ou análise do agente chegou àquele resultado. |
| **R**astreabilidade | De onde veio cada decisão e rota, ligada às rotas declaradas na idealização (Canvas/ARD). |
| **O**bservabilidade | Acompanhamento de desempenho e eficiência dos agentes no dia a dia. |

## Por que isso importa aqui em particular

Existe um paralelo direto entre o Harness e o próprio produto: o Lastro
promete, para os *seus* usuários, que toda exposição mostrada seja
explicável — nunca um score sem o caminho que o produziu (Hard Rule #3 em
[`ai.md`](ai.md)). O Harness aplica **o mesmo princípio** aos agentes que
constroem e operam o sistema — a explicabilidade não é só uma feature do
produto, é como o próprio projeto é construído.

## Rastreabilidade

- Toda decisão de rota tomada por um agente (de construção ou de operação)
  deve poder ser ligada de volta à rota declarada no
  [Project Canvas](docs/project-canvas.md) ou em um ARD ([docs/ARD.md](docs/ARD.md)).
- Nenhuma inferência de IA — sobre risco de um cliente ou sobre uma escolha
  de arquitetura — vira fato consolidado sem registrar sua fonte. No
  produto, isso é literal: todo `Evento` no grafo carrega `fonte` e `data`
  (Hard Rule #2/#8); nenhum dos 4 agentes cita número que não veio de uma
  tool (ver guardrails em [`docs/agentes.md`](docs/agentes.md)).
- Registro de rastreabilidade no MVP: a decisão de exposição/score em si é
  materializada no próprio grafo (o caminho de propagação fica gravado, não
  só o número final). Observabilidade operacional (chamadas, latência) fica
  a cargo da telemetria nativa do watsonx Orchestrate — ver abaixo.

## Observabilidade

- Cada um dos 4 agentes deve expor o suficiente para acompanhar desempenho e
  eficiência: número de chamadas, latência, taxa de confirmação humana das
  recomendações.
- **Decisão tomada:** usar a rastreabilidade/observabilidade nativa do IBM
  watsonx Orchestrate. Fallback, se ela não cobrir a necessidade em uma
  operação real: Langfuse — já em uso no restante do método da Síntese Labs.

## Governança

- Aplica as regras de acesso do domínio: hoje o MVP roda com um único perfil
  autenticado (área de crédito/comitê) — ver
  [`docs/ARD.md`](docs/ARD.md), decisão sobre autenticação. Governança
  multi-papel (ex.: separar quem só consulta de quem decide limite) é
  evolução pós-MVP, não lacuna do harness.
- Regra de fronteira física, não só de convenção: **o watsonx Orchestrate
  nunca fala com o driver do Neo4j** (ARD-04). Toda governança de acesso ao
  dado passa pela API do backend.

## Interpretabilidade

- Todo score do Lastro é decomposto por componente (comportamento de
  pagamento, eventos jurídicos/fiscais, cobertura de garantia, exposição
  herdada da rede, risco agro/ambiental) — nunca um número isolado. Ver
  [`docs/matching-model.md`](docs/matching-model.md).
- Toda saída de um agente de IA é apresentada como recomendação sujeita a
  decisão humana, nunca como ação automática (Hard Rule #1).

## Nuance importante: a decisão humana final não é um gate síncrono

O motor de exposição/scoring não espera aprovação humana para recalcular —
ele é, antes de tudo, um processo contínuo de inteligência de risco: reage a
eventos, atualiza o grafo e produz recomendações como uma das suas saídas,
não como uma etapa que trava o sistema esperando confirmação. A decisão
humana existe e é final (**nenhuma cobrança, protesto ou ação judicial
dispara sozinha** — Hard Rule #1), mas é **posterior e não-bloqueante**:
`POST /recuperacao/executar/{cliente}` registra quem decidiu e quando,
depois que o comitê de crédito já viu a recomendação — nunca um gate
síncrono no meio do pipeline de propagação/scoring.

## Aplicado aos agentes de construção (IA que trabalha no código/docs)

Esta seção do Harness também rege o próprio trabalho de manutenção do
repositório: mudanças estruturais amplas (mover pastas, apagar arquivos,
reescrever documentação) seguem o mesmo princípio de rastreabilidade — a
razão de cada mudança fica registrada (commit, changelog ou o próprio
histórico de conversas), e decisões de produto/arquitetura não são tomadas
unilateralmente por um agente sem checar com o tech lead (ver
[`config/system.md`](config/system.md)).

## Open Questions

1. ~~Qual ferramenta de observabilidade usar?~~ Resolvido — watsonx nativo,
   fallback Langfuse.
2. ~~Onde ficam os registros de rastreabilidade (fonte + confiança +
   decisão) no MVP?~~ Resolvido — a decisão de exposição/score é
   materializada no próprio grafo; observabilidade operacional fica com o
   Orchestrate.
3. Autenticação/autorização multi-papel formal — fora do escopo do MVP,
   entra como evolução se o Lastro sair do protótipo (ver
   [`architecture.md`](architecture.md), seção Evolução conhecida).
