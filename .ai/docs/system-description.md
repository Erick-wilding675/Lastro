# System Description

**Status:** revisado pós-pivô.

**Projeto:** Lastro
**Versão:** 1.0
**Data:** 2026-09-13

---

## Visão Geral

O Lastro é um sistema de **inteligência de risco relacional e recuperação de
capital** para carteiras de crédito no agronegócio. Ele nasceu de um problema
real: a Krilltech — agtech brasileira nascida de parceria com UnB e EMBRAPA,
fabricante da tecnologia de alta produtividade Arbolin Biogenesis — vende a
prazo, com o pagamento casado à safra, e vê a inadimplência de seus clientes
produtores rurais crescer junto com a onda de Recuperação Judicial (RJ) que
atravessa o setor.

A tese do produto cabe em uma frase: **produtor rural não quebra sozinho — o
componente de rede é o que bureau nenhum entrega.** Um score de crédito
tradicional olha para a ficha de um cliente isoladamente. O Lastro representa a
carteira inteira como uma rede — clientes, sócios, avalistas, grupos
econômicos, imóveis, regiões, culturas e safras conectados por vínculos reais
— e mostra como o risco de um se propaga para os outros, e **por qual caminho**
ele chega. É esse caminho, não um número solto, que vira decisão.

Por quê agora: a Lei 14.112/2020 estendeu a Recuperação Judicial ao produtor
rural pessoa física, e quebras de safra por El Niño/La Niña, queda nas
cotações de soja e milho e custo de insumo alto elevaram os pedidos de RJ no
agro a um patamar recorde. Uma vez deferido o processamento da RJ, a empresa
credora entra em um *stay period* de 180 dias prorrogáveis em que está
legalmente impedida de executar garantia ou protestar título — o crédito
segue para o plano de recuperação com deságio severo e prazo de anos. Depois
do pedido, não há o que fazer. Todo o valor está em enxergar antes.

O sistema é para uso direto da área de crédito e financeiro da Krilltech, com
visão agregada para o comitê de crédito e a diretoria, e apoio ao time
comercial na relação com o cliente. A mesma infraestrutura se aplica à cadeia
inteira — revendas, distribuidoras, tradings, cooperativas — que compartilha
exatamente o mesmo problema e hoje não tem nenhuma ferramenta relacional para
enxergá-lo.

---

## Problema & Diagnóstico

A Krilltech entrega tecnologia de alta produtividade ao produtor rural e
recebe depois, na safra. Entre a entrega e o recebimento existe uma janela
longa em que o risco só cresce — e o setor inteiro sente o mesmo aperto:

| Indicador | Valor | Fonte |
|---|---|---|
| Pedidos de RJ no agro, 2025 | **1.990** (+56,4% sobre 2024) | Serasa Experian |
| Inadimplência 90+ dias, produtor PF — jan/25 → jan/26 | **2,7% → 7,3%** | Banco Central |
| Inadimplência de produtor rural, 1T2026 | **8,8%** — recorde da série | Serasa Experian |

As causas são estruturais, não conjunturais: a extensão legal da RJ ao
produtor rural pessoa física, quebras de safra recorrentes, cotações em queda
e custo de insumo em alta. E o efeito é em cascata — a inadimplência do
produtor contamina distribuidores, revendas, tradings e fornecedores de
tecnologia, a exemplo da própria Krilltech.

**O ponto cego:** a carteira é gerida como uma lista de vencimentos, mas o
risco no agro é correlacionado. Sete clientes podem compartilhar o mesmo
avalista, o mesmo grupo econômico, os mesmos sócios, a mesma microrregião e a
mesma safra. Numa visão de lista, esse vínculo é invisível — cada ficha é
avaliada como se fosse uma ilha. Quando o alerta finalmente chega pelo aging
de pagamento, o dinheiro já parou de circular.

**E a janela fecha por lei:** uma vez deferido o processamento da RJ, começa o
*stay period* de 180 dias prorrogáveis em que nenhuma execução de garantia ou
protesto é possível, e o crédito entra no plano de recuperação judicial com
deságio severo e prazo de anos para reaver o que ainda for possível. Por isso
o problema não é cobrar melhor depois. É **enxergar antes**.

---

## Solução Proposta

Cinco etapas, um grafo, quatro agentes de IA — tudo determinístico onde
precisa ser, e explicável do início ao fim.

1. **Coleta & Parsing.** O *Agente Coletor & Parser* recebe CNPJ/CPF e consulta
   as bases públicas relevantes: Receita Federal (QSA, capital social, CNAE),
   DataJud/CNJ e Diários de Justiça (execuções, protestos, distribuição de
   RJ), PGFN/TST/Caixa (certidões), SICAR/IBAMA (imóvel, embargos),
   Conab/MAPA-ZARC/INMET (produtividade e risco climático). Faz parsing de
   certidão e diário em PDF. Cada dado entra no sistema como um evento **com
   fonte e data**.
2. **Grafo.** Cliente, recebível, sócio, avalista, grupo econômico, imóvel,
   região, cultura, safra e evento viram nós e arestas em Neo4j. A carteira
   deixa de ser uma tabela e passa a ser uma rede navegável.
3. **Motor de Exposição.** Determinístico, escrito em Cypher, com dois canais
   que o sistema nunca confunde entre si:
   - **Estrutural** — o risco de um cliente atinge o outro por vínculo
     jurídico ou patrimonial direto: mesmo grupo econômico (peso 0,90),
     avalista em comum (0,85), sócio em comum (0,70).
   - **Sistêmico** — ninguém contamina ninguém, mas todos sofrem a mesma
     causa externa: mesma região e cultura (0,75), mesma revenda (0,65),
     mesma cultura (0,40). Esse canal só atinge peso cheio **quando existe
     um evento regional confirmando o choque** — quebra de safra na
     Conab/INMET, alerta ZARC, queda de cotação. Sem evento confirmado, entra
     reduzido.
   Em qualquer um dos dois canais, **o caminho percorrido fica gravado** — é
   ele a explicação da exposição, não um coeficiente solto.
4. **Motor de Decisão & Scoring.** Calcula um score de 0 a 1000 e um rating de
   A a D, sempre decomposto em cinco componentes com peso uniforme —
   comportamento de pagamento, eventos jurídicos e fiscais, cobertura de
   garantia (com *haircut* por tipo de instrumento), exposição herdada da
   rede, e risco agro e ambiental. Nenhuma nota aparece sozinha: sempre vem
   com sua decomposição e, quando há contágio, com o vínculo que o produziu.
5. **Recomendação & Relatório.** O *Agente de Risco Agro & Climático* e o
   *Agente Sintetizador* produzem a estratégia recomendada por devedor, a
   fila de trabalho priorizada pela capacidade real do time de crédito, e o
   Relatório Padronizado de Risco em linguagem natural.

Um radar de eventos varre continuamente as fontes públicas e registra cada
ocorrência com fonte, data e severidade. Todo evento relevante **dispara
repropagação do contágio e recálculo do score** dos clientes afetados — não
apenas do cliente onde o evento ocorreu. O alerta chega com o caminho, nunca
com um número solto: *"este cliente acendeu porque divide avalista com o
produtor que pediu RJ ontem."* Cada ação executada e seu resultado
realimentam a taxa de sucesso por estratégia — o sistema fica mais preciso a
cada safra.

Toda decisão fica com trilha de auditoria: cada dado carrega fonte e data,
cada nota carrega sua decomposição, e **nenhuma recomendação vira ação
automática** — quem decide limite, condição de pagamento e estratégia de
cobrança é o comitê de crédito da Krilltech.

---

## Diferencial

O componente que nenhum bureau de crédito entrega é a **exposição herdada da
rede**. Um bureau tradicional avalia cada CPF/CNPJ isoladamente; o Lastro
mede o quanto do risco de um cliente vem emprestado de outros, por vínculo
real, e mostra exatamente qual vínculo é esse.

A separação entre os dois canais de exposição é o que sustenta essa métrica
sem virar alarme falso: o canal **estrutural** captura contaminação legítima
— quando o risco de um cliente de fato se propaga para outro por vínculo
jurídico ou patrimonial (aval, grupo econômico, sociedade). O canal
**sistêmico** captura algo diferente — clientes que não se contaminam entre
si, mas compartilham a mesma causa externa (a mesma seca, a mesma queda de
preço), e por isso só atinge peso cheio quando há um evento regional
confirmado, nunca por coincidência geográfica pura. Essa distinção é o que
evita que o sistema penalize um bom pagador só porque o vizinho da mesma
região quebrou por um motivo que não o atinge.

O grafo faz essa propagação em múltiplos saltos — uma consulta que em SQL
viraria uma junção recursiva ilegível é, em Cypher, uma query direta. E o
caminho percorrido pelo motor fica sempre visível: o sistema nunca apresenta
um risco de 0,8 sem dizer por qual vínculo ele chegou.

**Linguagem obrigatória do produto:** o Lastro mede *exposição compartilhada*,
nunca prevê quem vai quebrar. Ele não prescreve instrumento jurídico — mostra,
com número, o quanto da exposição está coberto por garantias que perdem valor
justamente no cenário de Recuperação Judicial, e deixa a decisão de política
de crédito com quem é dono dela: a área financeira e o jurídico da Krilltech.

---

## Escopo: MVP do hackathon vs. visão de produto completo

**Construído no hackathon (12/09/2026):** grafo em Neo4j AuraDB (tier
gratuito) com clientes, recebíveis, sócios, avalistas, grupos econômicos,
imóveis, regiões, culturas e safras; motor de exposição em dois canais
(estrutural e sistêmico) rodando em Cypher; motor de score 0–1000 e rating
A–D com decomposição em cinco componentes; matriz de red flags; quatro
agentes orquestrados sobre IBM watsonx Orchestrate; aplicação web (Python +
FastAPI no backend, React no frontend) com mapa de exposição da carteira e
dossiê por cliente; dataset seed sintético e mascarado — nenhum dado real de
produtor entra no repositório. Custo direto de infraestrutura do protótipo é
praticamente zero: AuraDB Free, créditos IBM do evento, fontes públicas
gratuitas.

**Fora do MVP, na visão de produto completo — horizontes definidos no
Canvas:**

| Horizonte | Entrega |
|---|---|
| **30 dias** | Conectar a base real de recebíveis da Krilltech; calibrar os pesos de contágio com o histórico próprio da empresa, em vez da hipótese declarada usada no protótipo |
| **60 dias** | Automatizar a coleta em rotina (DataJud, Receita, SICAR, INMET) em vez de consulta pontual; régua de alertas ativa para o time de crédito |
| **90 dias** | Calibrar a probabilidade de inadimplência com resultado observado — a memória de recuperação por estratégia vira modelo, com horizontes de 6, 12 e 24 meses |
| **Depois** | Abrir como serviço para revendas, distribuidoras e cooperativas da cadeia — o mesmo problema relacional, sem ferramenta hoje |

Na operação madura, o consumo de LLM é **por evento** (mudança de status,
novo documento, nova anotação), não por varredura contínua — o que mantém
baixo o custo por decisão. As fontes de dado usadas no MVP são públicas e
abertas, então não há custo recorrente de bureau. O modelo de sustentação
começa como capacidade interna da Krilltech — o retorno é custo evitado,
capital que não virou perda — e evolui para serviço oferecido à cadeia. Um
único recebível relevante recuperado antes de virar perda já paga o ano de
operação.
