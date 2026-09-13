# Motor de Exposição e Contágio (ex-"Matching Model")

**Status:** revisado pós-pivô — reconciliado com o sistema efetivamente implementado (`src/backend`, `src/db/cypher/02-queries-motor.cypher`) e com os 4 agentes reais de [`agentes.md`](agentes.md). Substitui integralmente as versões anteriores ("matching pessoa↔projeto" e o rascunho intermediário sob o codinome "Rizoma").

**Produto:** Lastro
**Versão:** 2.0 — pós-hackathon, alinhado ao código
**Data:** 2026-09-13

---

## Princípio

O motor produz **recomendação, não decisão**. Todo score é decomposto por componente e rastreável até o dado que o gerou. Nenhuma ação de cobrança, protesto ou execução é disparada automaticamente: o comitê de crédito decide. Ver [../harness.md](../harness.md) e as Hard Rules em [../ai.md](../ai.md).

Num contexto de crédito isso não é preferência de design, é requisito: decisão de crédito precisa ser auditável, defensável e reversível.

O nome "Matching Model" é herdado do produto anterior (matching pessoa↔projeto) e não descreve bem o que este motor faz — não há "match" entre duas entidades, há **propagação de risco pela rede** seguida de **priorização de recuperação**. O arquivo manteve o nome do caminho por compatibilidade de links, mas o conteúdo é outro.

**Regra de linguagem (vale para todo texto que o motor produz, calculado ou redigido por agente):** nunca "prever que o cliente vai quebrar" ou linguagem de destino/fatalidade. O sistema mede **exposição compartilhada** e mostra **por qual vínculo** ela chega — sempre as duas partes juntas, nunca um risco sem o caminho que o explica. Essa regra vale tanto para as camadas determinísticas (o campo `caminho`/`via` é obrigatório em toda aresta `EXPOSTO_A`) quanto para o agente Sintetizador, que nunca afirma que um cliente vai falir (ver [agentes.md](agentes.md)).

---

## Camada 0 — Motor de Contágio (o diferencial do produto)

Antes de qualquer priorização, o grafo responde: **quem está em risco que ainda não apareceu no aging?**

Entrada: mudança de estado de um `Cliente` (entrou em RJ, estourou 90 dias, protestou) — o parâmetro `$origem` da query.
Saída: arestas `EXPOSTO_A {peso, caminho, canais, calculado_em}` para cada vizinho alcançado.

Implementação: **função determinística**, uma única query Cypher multi-hop (`Q1` em [`02-queries-motor.cypher`](../../src/db/cypher/02-queries-motor.cypher), exposta como `POST /contagio/propagar/{origem}`). Não precisa de LLM: é propagação em grafo, não interpretação.

O motor tem **dois canais distintos**, e a diferença entre eles é conceitual, não cosmética:

| Canal | Vínculo | Peso | Relação Cypher |
|---|---|---|---|
| Estrutural | Mesmo grupo econômico | 0,90 | `PERTENCE_A` (ambos → `GrupoEconomico`) |
| Estrutural | Avalista em comum | 0,85 | `Recebivel-[:GARANTIDO_POR]->Avalista` compartilhado |
| Estrutural | Sócio em comum (QSA) | 0,70 | `TEM_SOCIO` (ambos → `Socio`) |
| Sistêmico | Mesma região + cultura, **com** evento regional confirmando o choque nos últimos 365 dias | 0,75 | `OPERA_EM` + `PLANTA` + `Evento{tipo IN [quebra_safra, alerta_zarc, queda_preco]}` |
| Sistêmico | Mesma região + cultura, **sem** evento confirmando | 0,30 | idem, sem o `Evento` |
| Sistêmico | Mesmo canal de revenda | 0,65 | `COMPRA_VIA` compartilhado |
| Sistêmico | Mesma cultura (sem mais nada em comum) | 0,40 | `PLANTA` compartilhado |

- **Estrutural** — o risco de um contamina o outro por vínculo jurídico ou patrimonial.
- **Sistêmico** — ninguém contamina ninguém; todos sofrem a mesma causa. O peso cheio de região+cultura só vale **quando existe evento regional confirmando o choque** — sem isso, um vizinho que quebrou por motivo próprio acenderia a microrregião inteira sem razão.

Quando um cliente tem mais de um caminho até a origem, a query fica com `max(peso)` e concatena todos os `caminhos` — o risco nunca aparece sem dizer de onde veio (Hard Rule #3). Se dois clientes tiverem múltiplos vínculos (ex.: sócio em comum **e** mesma região com choque confirmado), ambos os caminhos ficam gravados na aresta.

O que precisa de LLM é **redigir a explicação em linguagem de negócio** para quem decide — esse é o papel do agente Sintetizador (ver [agentes.md](agentes.md)), não um agente separado de "narrativa de contágio".

---

## Camada 1 — Score 0–1000 e Rating A–D

Determinístico (`Q2`, `POST /scoring/recalcular`), cinco componentes com peso uniforme (0,2 cada — hipótese declarada e auditável, não calibração disfarçada):

| Componente | O que mede | Fonte |
|---|---|---|
| Comportamento de pagamento | Situação atual e dias de atraso máximo | `Cliente.situacao`, `Cliente.dias_atraso_max` |
| Eventos jurídicos e fiscais | RJ, protesto, execução fiscal, alteração societária nos últimos 180 dias | `Evento` ligado por `SOBRE` |
| Cobertura de garantia | Saldo em aberto coberto por garantia, com **haircut por tipo**: alienação fiduciária 1,00 · aval 0,70 · CPR 0,60 · penhor de safra 0,50 · nenhuma 0,00 | `Recebivel.garantia_tipo/garantia_valor` |
| **Exposição herdada da rede** | `max(peso)` das arestas `EXPOSTO_A` que chegam no cliente — o componente que nenhum bureau tem | Camada 0 |
| Risco agro e ambiental | Quebra de safra na região, embargo ambiental no imóvel | `Evento`, `Imovel.embargo_ibama` |

`score = round(1000 * (1 - média dos 5 riscos))`. Rating por faixa — **A** 800–1000, **B** 600–799, **C** 400–599, **D** 0–399 — com uma exceção deliberada: cliente em `recuperacao_judicial` recebe rating **D por override**, não por média, porque RJ é fato jurídico já consumado, não estimativa probabilística (ver comentário `FIX (12/09)` na query). O score e a decomposição continuam gravados intactos para auditoria mesmo quando o override se aplica.

---

## Camada 2 — Matriz de Red Flags

Determinístico (`Q3`, `GET /scoring/red-flags`). Uma linha por cliente com a lista de bandeiras acesas — RJ distribuída, protesto, execução fiscal, alteração de QSA, embargo ambiental, quebra de safra, contágio forte (`EXPOSTO_A.peso >= 0,8`), garantia frágil sem alienação fiduciária. Cada bandeira carrega gravidade e fonte; nenhuma é sintetizada em texto por um agente — a matriz é consumida como está pelo dossiê e pelo frontend.

---

## Camada 3 — Recomendação de Estratégia (por devedor)

Determinístico (`Q4`, `POST /recuperacao/recomendar/{cliente}` e `POST /recuperacao/recomendar-carteira`).

| Dimensão | O que avalia | Implementação |
|---|---|---|
| **Estágio jurídico** | `Recebivel.estagio_juridico` contra `EstrategiaRecuperacao.estagios_elegiveis` | Filtro duro de elegibilidade, não soma ao índice — não se propõe cobrança amigável a quem já está habilitado em RJ |
| **Valor recuperável esperado** | `exposição × taxa_sucesso_historica` da estratégia | Determinístico |
| **Índice de prioridade** | `valor_líquido / prazo_médio`, com bônus de até 30% se a estratégia preserva a relação **e** o cliente tem 3+ anos de casa | Determinístico — heurística gulosa, não um solver de otimização. Cabe no tempo do MVP, é explicável linha a linha e resolve o problema real |

A recomendação é **materializada** como `(Cliente)-[:RECOMENDADA {valor_recuperavel_estimado, prazo_estimado, indice, calculado_em}]->(EstrategiaRecuperacao)` — não é recalculada a cada abertura de tela, fica gravada e datada.

Não existe, na versão implementada, um "Strategy Fit Agent" pontuando contexto qualitativo do devedor (petição, relato comercial) dentro do índice — isso ficou fora do MVP de 12h. O contexto qualitativo entra hoje pela leitura humana do dossiê e, quando redigido por IA, pelo agente Sintetizador (texto, não número somado ao índice). Ver Open Questions.

---

## Camada 4 — Fila de Recuperação (capacidade do time)

Determinístico (`GET /recuperacao/priorizar?capacidade=N`). Ordena a carteira recomendada pelo índice da Camada 3 e corta na capacidade real informada — ação recomendada que ninguém executa é ação inexistente. Quando o time marca uma ação como feita, `POST /recuperacao/executar/{cliente}` grava quem decidiu, quando, e tira o cliente da fila do período (a "memória de recuperação" citada no Canvas).

---

## Corte agente de IA vs. função determinística

Mesma lógica em todo o sistema: interpretação de texto livre ou ambiguidade vira agente; cálculo reproduzível vira função. Ver [agentes.md](agentes.md) para o detalhe completo de cada um — resumo aqui só para fechar o corte:

| Agente (watsonx Orchestrate) | Nunca calcula, só... |
|---|---|
| Coletor & Parser | Classifica fonte pública/documento em evento estruturado com tipo, data, fonte, severidade |
| Risco Agro & Climático | Interpreta zoneamento (ZARC) e histórico regional em avaliação qualitativa |
| Motor de Decisão & Scoring (orquestrador) | Dispara `propagar_contagio` → `recalcular_scoring` na ordem certa e interpreta o que mudou |
| Sintetizador | Redige o parecer a partir do dossiê já calculado — nunca inventa ou arredonda número |

**Funções determinísticas (backend FastAPI, módulos `contagio`, `scoring`, `recuperacao`):** as 4 camadas acima, por inteiro. Nenhuma delas passa por um LLM.

**Fronteira física (ARD-04):** o watsonx Orchestrate nunca fala com o driver do Neo4j — todo agente chama a API do backend como tool.

---

## Pesos

Uniformes dentro de cada camada no MVP — auditável e honesto no pitch: "não calibramos com dados históricos reais porque ainda não os temos; cada componente pesa igual até existir base para ajustar". A memória de recuperação (Camada 4) é o mecanismo pelo qual esses pesos passariam a ser calibrados com dado real — ver roadmap de 90 dias no [Project Canvas](project-canvas.md).

---

## Open Questions

| # | Questão | Status |
|---|---|---|
| 1 | Catálogo real de estratégias que a Krilltech usa hoje (o do seed é o padrão de mercado — pode não bater) | Aberto — depende de dado real da empresa |
| 2 | Capacidade operacional real do time de cobrança (insumo direto da Camada 4) | Aberto — depende de dado real da empresa |
| 3 | Pesos de contágio e de score: manter uniformes ou calibrar com conhecimento de domínio | Resolvido para o MVP — uniformes por decisão declarada (ver seção Pesos); calibração é item de roadmap |
| 4 | Um agente dedicado a extrair dados estruturados de petição/contrato/CPR (`Document Extraction Agent`, do rascunho anterior) | Resolvido — essa responsabilidade foi absorvida pelo Coletor & Parser (ver `agentes.md`), não é um quinto agente |
