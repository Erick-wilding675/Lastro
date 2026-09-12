# Project Canvas — Lastro

**Status:** Rascunho para revisão do time. Entregável **obrigatório**, submissão
no formulário até **15:00 de 12/09**.

**Estrutura:** os 10 blocos exigidos pela seção 7.1 do documento de desafio.
O template visual é o Project Model Canvas enviado pela organização — estes
conteúdos preenchem os campos dele.

---

## Pitch (uma frase)

Quando um cliente da Krilltech pede Recuperação Judicial, a empresa fica
legalmente impedida de executar garantia ou protestar por 180 dias. O Lastro
existe para que ela saiba antes: representa a carteira como uma rede, propaga o
risco pelos vínculos entre clientes e mostra quem vai cair junto — a tempo de agir.

---

## 1. Problema & Diagnóstico

A Krilltech vende tecnologia de alta produtividade direto ao produtor rural, a
prazo, com o pagamento casado à safra. Entre entregar o produto e receber existe
uma janela longa em que o risco só cresce. E o setor inteiro virou:

| Indicador | Valor | Fonte |
|---|---|---|
| Pedidos de RJ no agro, 2025 | **1.990** (+56,4% sobre 2024) | Serasa Experian |
| Inadimplência 90+ dias, produtor PF — jan/25 → jan/26 | **2,7% → 7,3%** | Banco Central |
| Inadimplência de produtor rural, 1T2026 | **8,8%** — recorde da série | Serasa Experian |

As causas são estruturais, não conjunturais: a Lei 14.112/2020 estendeu a RJ ao
produtor rural pessoa física; quebras de safra por El Niño/La Niña; queda nas
cotações de soja e milho; custo de insumo alto. E o efeito cascata contamina a
cadeia — o próprio case é explícito: a inadimplência do produtor contamina
distribuidores, revendas, tradings e **fornecedores de tecnologia, a exemplo da
Krill Tech**.

**O ponto cego:** a carteira é gerida como uma lista de vencimentos, mas o risco
no agro é correlacionado. Sete clientes podem compartilhar o mesmo avalista, o
mesmo grupo econômico, os mesmos sócios, a mesma microrregião e a mesma safra. Na
visão de lista, esse vínculo é invisível. Quando o alerta chega pelo aging, o
dinheiro já parou.

**E a janela fecha por lei:** deferido o processamento da RJ, começa o *stay
period* de 180 dias prorrogáveis em que nenhuma execução ou protesto é possível, e
o crédito entra no plano com deságio severo e prazo de anos. Por isso o problema
não é cobrar melhor. É **enxergar antes**.

## 2. Público-Alvo / Beneficiários

| Quem | O que ganha |
|---|---|
| Área de crédito e financeiro da Krilltech (usuário direto) | Para de descobrir risco tarde; decide limite e condição com base na rede, não só na ficha |
| Comitê de crédito e diretoria | Exposição consolidada, previsibilidade de caixa, decisão auditável |
| Time comercial | Deixa de perder cliente bom por cobrança cega; ganha argumento para renegociar no tempo certo |
| Produtor rural cliente | Tratado pela realidade da safra, com renegociação antes do colapso em vez de execução depois |
| Cadeia (revendas, distribuidores, cooperativas) | Mesma infraestrutura aplicável — o agro inteiro compartilha o problema |

## 3. Lógica de Funcionamento da Solução

Cinco etapas, quatro agentes, um grafo:

1. **Coleta & Parsing** — *Agente Coletor & Parser*. Recebe CNPJ/CPF e consulta as
   bases públicas: Receita Federal (QSA, capital social, CNAE), DataJud/CNJ e DJEs
   (execuções, protestos, distribuição de RJ), PGFN/TST/Caixa (certidões),
   SICAR/IBAMA (imóvel, embargos), Conab/MAPA-ZARC/INMET (produtividade e risco
   climático). Faz parsing de certidão e diário em PDF. Tudo entra como evento
   **com fonte e data**.
2. **Grafo** — cliente, recebível, sócio, avalista, grupo econômico, imóvel,
   região, cultura, safra e evento viram nós e arestas em Neo4j.
3. **Motor de Contágio** — determinístico, em Cypher. Propaga risco multi-hop com
   peso por tipo de vínculo (grupo econômico 0,90; avalista comum 0,85; sócio em
   comum 0,80; mesma revenda 0,50; mesma região e cultura 0,45) e **guarda o
   caminho percorrido**.
4. **Motor de Decisão & Scoring** — calcula score 0–1000 e rating A–D, decomposto
   em cinco componentes.
5. **Recomendação & Relatório** — *Agente de Risco Agro & Climático* e *Agente
   Sintetizador* produzem a estratégia por devedor, a fila priorizada pela
   capacidade real do time e o Relatório Padronizado de Risco em linguagem natural.

Sobre tudo isso roda o **GIRO** (governança, interpretabilidade, rastreabilidade,
observabilidade): todo dado carrega fonte e confiança, toda decisão é rastreável,
e **nenhuma recomendação vira ação automática** — quem decide é o comitê de crédito.

## 4. Score & Classificação de Rating

Nota de **0 a 1000**, onde score alto significa risco baixo. Cinco componentes com
peso uniforme — hipótese declarada e auditável, não calibração disfarçada:

| Componente | O que mede |
|---|---|
| Comportamento de pagamento | Atraso máximo, situação atual, histórico |
| Eventos jurídicos e fiscais | RJ, protesto, execução fiscal, alteração societária (janela de 180 dias) |
| Cobertura de garantia | Garantia sobre exposição, ponderada pelo tipo |
| **Contágio herdado da rede** | Risco que chega pelos vínculos — **o componente que nenhum bureau tem** |
| Risco agro e ambiental | Quebra de safra na região, embargo no imóvel |

| Rating | Faixa | Leitura |
|---|---|---|
| **A** | 800–1000 | Baixo risco |
| **B** | 600–799 | Risco moderado |
| **C** | 400–599 | Risco alto |
| **D** | 0–399 | Risco crítico / **Alerta de RJ** |

Nenhuma nota aparece sozinha: sempre com a decomposição e, quando há contágio, com
o vínculo que a produziu.

## 5. Matriz de Red Flags

| Bandeira | Fonte | Gravidade | Ação sugerida |
|---|---|---|---|
| RJ distribuída | DataJud / DJE | 1,00 | Habilitar crédito; stay period ativo, execução bloqueada |
| Protesto de título | Cartório / DJE | 0,70 | Suspender limite, abrir renegociação |
| Execução fiscal / dívida ativa | PGFN | 0,60 | Revisar limite e exigir garantia |
| **Contágio forte (≥ 0,80)** | **Grafo (QSA, aval, grupo)** | **0,80+** | **Revisão preventiva antes do vencimento** |
| Embargo ambiental no imóvel | IBAMA / SICAR | 0,55 | Reavaliar garantia: área embargada não produz |
| Quebra de safra na região | Conab / INMET / ZARC | 0,50 | Antecipar renegociação para a safra seguinte |
| Garantia frágil (penhor ou sem garantia) | Contrato | 0,45 | **Converter para alienação fiduciária** |
| Alteração societária recente | Receita Federal (QSA) | 0,40 | Reavaliar aval e cadeia de responsabilidade |

## 6. Recomendação de Decisão Operacional

Por rating, o sistema orienta limite e condição de pagamento:

| Rating | Limite de crédito | Condição de pagamento |
|---|---|---|
| A | Mantido ou ampliado | Prazo padrão da safra |
| B | Mantido | Exigir garantia real na renovação |
| C | Reduzido | Venda condicionada a garantia reforçada ou barter |
| D | Suspenso | Somente à vista ou antecipado; se já há exposição, recuperação |

Para a carteira vencida, cada devedor recebe estratégia recomendada com **valor
recuperável estimado, prazo e custo** — renegociação, barter, acordo parcelado,
cobrança amigável, protesto, execução judicial, securitização ou habilitação em
RJ. O estágio jurídico funciona como filtro duro: não se propõe cobrança amigável
a quem já está habilitado em RJ.

**A ação preventiva de maior valor:** converter a garantia para **alienação
fiduciária** nos clientes em deterioração, antes do pedido de RJ. Alienação
fiduciária é crédito extraconcursal e sobrevive à Recuperação Judicial; penhor,
não. É a diferença entre receber e entrar na fila.

E a fila de trabalho respeita a capacidade real do time de cobrança: ação
recomendada que ninguém consegue executar é ação inexistente.

## 7. Monitoramento Contínuo (Early Warning System)

- O **radar de eventos** varre as fontes públicas e registra cada ocorrência com
  fonte, data e severidade.
- Todo evento relevante **dispara repropagação do contágio e recálculo do score**
  dos clientes afetados — não apenas do cliente do evento.
- O alerta chega com o caminho, não com um número solto: *"este cliente acendeu
  porque divide avalista com o produtor que pediu RJ ontem"*.
- Vigia a **inadimplência técnica antes da financeira**: quebra de covenant,
  alteração societária e embargo aparecem antes do atraso de pagamento.
- **Memória de recuperação:** cada ação executada e seu resultado realimentam a
  taxa de sucesso por estratégia. O sistema fica mais preciso a cada safra.

## 8. Arquitetura de Negócios & Custos

**Protótipo (hackathon):** Neo4j AuraDB Free, créditos IBM do evento, fontes
públicas gratuitas. Custo direto de infraestrutura ≈ R$ 0; o custo real é hora de
equipe.

**Operação:** grafo gerenciado em tier inicial, consumo de LLM **por evento**
(mudança de status, novo documento, nova anotação) e não por varredura contínua, o
que mantém baixo o custo por decisão. As fontes listadas no desafio são públicas e
abertas, então não há custo recorrente de bureau no MVP.

**Modelo de sustentação:** começa como capacidade interna, e o retorno é custo
evitado — capital que não virou perda. Evolui para serviço oferecido à cadeia
(revendas, distribuidores, cooperativas), que tem o mesmo problema e nenhuma
ferramenta relacional.

**Ponto de equilíbrio:** um único recebível relevante recuperado antes de virar
perda paga o ano de operação.

## 9. Premissas, Restrições e Riscos

**Premissas:** a venda é a prazo, casada à safra; existe controle de recebíveis
extraível (planilha ou ERP); há informação suficiente para inferir vínculos entre
clientes por documento, QSA e aval; a capacidade do time de cobrança é limitada.

**Restrições:** janela do hackathon; stack IBM (watsonx Orchestrate + Bob); sem
acesso a base real da Krilltech; nenhum dado pessoal real no repositório — o seed
é sintético e mascarado.

| Risco | Mitigação |
|---|---|
| A base atual não tem os vínculos mapeados | O enriquecimento por QSA é etapa do pipeline, não pré-requisito |
| Pesos de contágio soarem arbitrários | Declarados como hipótese auditável, com o caminho sempre visível e ajustáveis por domínio |
| Parecer "mais um score de crédito" | O componente de rede é justamente o que bureau nenhum entrega |
| Falso positivo queimar relação comercial | Recomendação nunca vira ação automática; o comitê decide, e a estratégia que preserva relação tem bônus no ranqueamento |
| Dado público desatualizado | Cada evento carrega fonte e data; o sistema mostra a idade do dado em vez de fingir atualidade |

## 10. Próximos Passos

| Horizonte | Entrega |
|---|---|
| **30 dias** | Conectar a base real da Krilltech; calibrar os pesos de contágio com o histórico próprio da empresa |
| **60 dias** | Automatizar a coleta em rotina (DataJud, Receita, SICAR, INMET); régua de alertas para o time de crédito |
| **90 dias** | Calibrar a probabilidade de inadimplência com resultado observado — a memória de recuperação vira modelo, com horizontes de 6, 12 e 24 meses |
| **Depois** | Abrir como serviço para revendas, distribuidores e cooperativas da cadeia |
