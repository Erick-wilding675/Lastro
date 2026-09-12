# Lastro — Documento de estudo para o pitch

**Para quem:** Erick, que vai defender sozinho em 3 minutos e responder 1 minuto
de arguição sem direito a tréplica.

**Como usar:** leia inteiro uma vez. Depois volte só no banco de perguntas e na
cola final. O roteiro literal está em [pitch-roteiro.md](pitch-roteiro.md).

---

## 1. A solução em três profundidades

Treine as três. Na arguição, você escolhe a profundidade pelo tempo que sobrou.

**Em 10 segundos:** "O Lastro mede risco de crédito pela rede, não pela ficha.
Mostra quem está exposto ao mesmo risco e por qual vínculo, antes do vencimento."

**Em 30 segundos:** "A Krilltech vende a prazo para produtor rural. Quando um
cliente pede Recuperação Judicial, ela fica 180 dias impedida de executar garantia.
O Lastro representa a carteira como grafo — clientes, avalistas, sócios, grupos,
região, cultura — e propaga risco pelos vínculos. Dá score de 0 a 1000 com rating
A a D, matriz de red flags e recomendação de limite e condição de pagamento,
sempre mostrando o caminho que gerou o alerta."

**Em 1 minuto:** acrescente os dois canais (estrutural e sistêmico), a condicional
do evento regional, os quatro agentes e a trilha de auditoria.

---

## 2. Os números, e de onde vieram

| Número | Fonte | Quando usar |
|---|---|---|
| **1.990 pedidos de RJ no agro em 2025, +56,4% sobre 2024** | Serasa Experian | Abertura do diagnóstico |
| **Inadimplência 90+ do produtor PF: 2,7% (jan/25) → 7,3% (jan/26)** | Banco Central | O par que mostra velocidade |
| **8,8% de inadimplência rural no 1T2026, recorde da série** | Serasa Experian | Reserva, se pedirem mais |
| **Stay period: 180 dias prorrogáveis** | Lei 11.101/2005, citada no glossário do desafio | A tese inteira |
| **Lei 14.112/2020 estendeu RJ ao produtor PF** | Documento de desafio, seção 3 | Explica por que agora |
| **Krilltech: 210 clientes, 18 estados, 23 culturas, 30 mil hectares** | Site da empresa | Mostra que você pesquisou |

Se errar um número, **corrija na hora e siga**. Jurado perdoa correção; não perdoa
número inventado que não fecha com a tela.

---

## 3. Glossário — o que a banca pode cobrar

**Recuperação Judicial (RJ).** Procedimento da Lei 11.101/2005 em que empresa ou
produtor renegocia dívidas coletivamente sob supervisão judicial, para evitar
falência. Créditos anteriores ao pedido entram no plano com deságio e prazos longos.

**Stay period.** Os 180 dias, prorrogáveis, após o deferimento do processamento da
RJ, em que ficam suspensas execuções e cobranças contra o devedor. É a janela em
que a Krilltech não pode fazer nada. **É a razão de existir do produto.**

**Inadimplência técnica × financeira.** A financeira é o não pagamento no
vencimento. A técnica é a violação de índice ou cláusula contratual *antes* do
atraso. A técnica é o sinal antecedente — é nela que o early warning atua.

**CPR — Cédula de Produto Rural.** Título em que o produtor promete entrega futura
de produto (CPR Física) ou liquidação em dinheiro (CPR Financeira). Comum como
lastro em barter e crédito direto no agro.

**Barter.** Insumo ou serviço pago com a entrega da safra futura. Exige
acompanhamento de produtividade, clima e integridade da área plantada — três
coisas que o Lastro monitora.

**Alienação fiduciária × penhor.** A alienação fiduciária transfere a propriedade
resolúvel do bem ao credor e o crédito fica **fora** dos efeitos da RJ
(extraconcursal). O penhor apenas vincula safra ou máquina como garantia, e entra
no concurso. Por isso o haircut do penhor é 0,50 e o da alienação fiduciária é 1,00.

**Rating e PD.** Classificação (A a D) que expressa probabilidade de inadimplência
em um horizonte. O desafio pede 0 a 1000, de Baixo Risco [A] a Risco Crítico /
Alerta de RJ [D].

**QSA.** Quadro de Sócios e Administradores, público na base de CNPJs da Receita.
É o que permite descobrir que dois clientes diferentes têm o mesmo dono.

---

## 4. Como o sistema funciona, camada por camada

**Camada 1 — Coleta.** O Agente Coletor & Parser recebe CNPJ ou CPF, consulta as
bases públicas e faz parsing de documento em PDF. Tudo vira evento com tipo,
data, fonte e severidade.

**Camada 2 — Grafo (Neo4j).** Onze tipos de nó: Cliente, Recebível, Sócio,
Avalista, Grupo Econômico, Imóvel, Região, Cultura, Safra, Evento e Estratégia de
Recuperação. As arestas são os vínculos que transmitem ou compartilham risco.

**Camada 3 — Motor de exposição.** Determinístico, em Cypher. Dois canais:

- **Estrutural** — o risco de um atinge o outro por vínculo jurídico ou
  patrimonial. Grupo econômico 0,90 · avalista em comum 0,85 · sócio em comum 0,70.
- **Sistêmico** — ninguém contamina ninguém; todos sofrem a mesma causa. Região +
  cultura 0,75 · mesma revenda 0,65 · mesma cultura 0,40. **Região e cultura só
  atingem peso cheio se houver evento regional confirmando o choque** (quebra de
  safra, alerta ZARC, queda de cotação nos últimos 365 dias). Sem evento, cai
  para 0,30.

Toda aresta de exposição guarda **o caminho** que a gerou. É a explicação.

**Camada 4 — Score.** Cinco componentes, peso uniforme, score alto = risco baixo.

**Camada 5 — Decisão.** Recomendação de limite e condição por rating; estratégia
de recuperação por devedor, filtrada por estágio jurídico; e fila priorizada pela
capacidade real do time.

**Camada 6 — Relatório.** O Agente Sintetizador redige o parecer em linguagem
natural, citando apenas números que vieram do dossiê.

---

## 5. O score, em detalhe

`score = 1000 × (1 − média dos 5 componentes de risco)`

| Componente | Como é calculado |
|---|---|
| Comportamento de pagamento | RJ = 1,0 · 90+ dias = 0,90 · 30+ = 0,60 · 1+ = 0,30 · em dia = 0 |
| Eventos jurídicos e fiscais | Maior severidade entre RJ, protesto, execução fiscal e alteração de QSA nos últimos 180 dias |
| Cobertura de garantia | 1 − (garantia ajustada ÷ exposição), com **haircut** por tipo |
| Exposição herdada da rede | Maior peso de aresta de exposição apontando para o cliente |
| Risco agro e ambiental | Maior severidade entre quebra de safra e embargo ambiental |

**Haircut por tipo de garantia:** alienação fiduciária 1,00 · aval 0,70 · CPR 0,60
· penhor de safra 0,50 · nenhuma 0,00. Traduzindo: R$ 300 mil em penhor de safra
entram na conta como R$ 150 mil, porque penhor evapora com a seca e entra no
concurso da RJ.

**Escala:** A 800–1000 · B 600–799 · C 400–599 · D 0–399 (alerta de RJ).

**Knockout:** cliente em Recuperação Judicial é **D por definição**, com score
limitado a 350. Sem essa regra, a média dos cinco componentes diluiria o sinal
mais grave que existe e quem acabou de pedir RJ sairia como "risco alto". Critério
de knockout é prática padrão em política de crédito — se perguntarem, é assim que
se chama.

---

## 6. As fontes de dados, e o que cada uma entrega

| Dimensão | Base | O que extrai |
|---|---|---|
| Cadastral e societário | Receita Federal (CNPJ Abertos) / Redesim | **QSA**, capital social, CNAE, filiais, tempo de atividade |
| Processual e jurídico | DataJud (CNJ), DJEs, Jusbrasil, Escavador | Execuções, protestos, pedidos de falência, distribuição de RJ |
| Territorial e ambiental | SICAR, IBAMA | Regularidade do imóvel, área de plantio, embargos |
| Fiscal e trabalhista | PGFN, TST (CNDT), Caixa (CRF-FGTS) | Certidões, execuções fiscais, passivos trabalhistas |
| Agronômico e climático | Conab, MAPA (ZARC), INMET | Produtividade regional, risco climático por cultura e safra, séries históricas |

Todas foram listadas pelo próprio documento de desafio, seção 5. Se a banca
perguntar de onde você tirou, a resposta é: do enunciado.

---

## 7. Os quatro agentes, em uma linha cada

1. **Coletor & Parser** — lê base pública e PDF, devolve evento com fonte.
2. **Risco Agro & Climático** — cruza CAR, ZARC, cultura e safra com a região.
3. **Decisão & Scoring** — dispara a propagação e o recálculo, e interpreta o que
   mudou. **Não calcula o score.**
4. **Sintetizador** — escreve o Relatório Padronizado de Risco, citando apenas
   números do dossiê.

**A frase que resume a arquitetura:** *"IA entra onde há texto e ambiguidade.
Onde há conta, é query determinística — e por isso o score não alucina."*

---

## 8. Banco de perguntas e respostas

**"Por que grafo e não banco relacional?"**
A pergunta do produto é multi-hop, com peso por tipo de vínculo e reconstrução do
caminho. Em SQL isso vira junção recursiva ilegível e cara. Em Cypher é uma query.
E o caminho é o que vira explicação para o gestor.

**"E se o modelo errar o score?"**
O score não é gerado por modelo. É query determinística, reproduzível e auditável.
O LLM entra para ler documento e redigir parecer, não para pontuar.

**"Isso não é só um Serasa?"**
Bureau olha o cliente sozinho. Dois clientes com o mesmo balanço e o mesmo score
de bureau têm risco diferente se um deles divide avalista com quem acabou de pedir
RJ. Esse componente de rede não existe em bureau — e é a metade do nosso score.

**"De onde vêm esses vínculos?"**
Três origens: o QSA da Receita, que é público; o avalista, que está nos próprios
contratos da Krilltech; e o CAR, para o imóvel. Nada depende de dado que a empresa
não tenha ou não possa obter.

**"Como vocês validaram os pesos?"**
Não validamos, e dizemos isso: são hipótese declarada, com peso uniforme dentro de
cada nível. O que garante honestidade é que o caminho fica visível, então o gestor
julga o raciocínio, não só a nota. A calibração com histórico real é o marco de
30 e 90 dias do roadmap.

**"A carteira inteira não fica vermelha?"**
Não, e isso é desenho, não sorte. O canal sistêmico só atinge peso cheio quando
existe evento regional confirmando o choque. Sem evento da Conab ou alerta ZARC, a
vizinhança de região e cultura entra com menos da metade do peso. Na demonstração,
um cliente permanece verde justamente por isso.

**"Onde entra IA de verdade?"**
Em quatro pontos com texto livre: ler petição de RJ e certidão, interpretar
contexto agroclimático, decidir quando recalcular, e redigir o parecer. Todo o
resto é cálculo — de propósito.

**"E se o dado público estiver desatualizado?"**
Cada evento carrega fonte e data, e o sistema mostra a idade do dado. Ele degrada
com transparência: sinaliza que a dimensão está sem cobertura em vez de preencher
com estimativa.

**"E a LGPD?"**
Três camadas de resposta. Primeira: usamos dado público e dado contratual da
própria empresa, para finalidade legítima de análise de crédito. Segunda: não
tratamos categoria sensível. Terceira, e a mais importante: a LGPD dá ao titular o
direito de revisão de decisão automatizada — e o Lastro **não decide nada
sozinho**, ele recomenda e registra a trilha. O desenho já nasce compatível.

**"Escala para dez mil clientes?"**
O grafo suporta com folga; o tier gratuito que usamos já comporta 200 mil nós e
400 mil relacionamentos. A propagação é limitada em profundidade, então o custo
cresce com a vizinhança, não com a carteira inteira. Testamos em escala de
demonstração — dizer que testamos em produção seria mentira.

**"Qual o retorno? Como mede?"**
Custo evitado. Quatro métricas: clientes sinalizados antes do vencimento, prazo
médio entre vencimento e recuperação, taxa de recuperação por safra, e percentual
de casos resolvidos por via que preserva a relação comercial. O ponto de
equilíbrio é baixo: um recebível relevante recuperado antes de virar perda paga o
ano de operação.

**"Quanto custa rodar?"**
Fontes públicas, sem custo de bureau. Grafo gerenciado em tier inicial. E o
consumo de LLM é **por evento** — quando muda status, chega documento ou entra
anotação — não por varredura contínua. Isso mantém o custo por decisão baixo.

**"Como a Krilltech adota isso na prática?"**
Começa em modo sombra: o sistema roda ao lado do processo atual por uma safra,
sem poder de decisão, e a área de crédito compara o que ele sinalizou com o que
aconteceu. Ganhando confiança, vira insumo do comitê. Não substitui ninguém e não
exige mudar a política de crédito no dia um.

**"Vocês estão dizendo que a Krilltech faz errado hoje?"**
Não. O processo atual funciona para risco individual, que era o cenário até 2023.
O que mudou foi o setor: o risco virou correlacionado. A ferramenta é nova porque
o problema é novo.

**"E o cliente sinalizado injustamente?"**
Nada é automático. O sinal vai para uma pessoa com o caminho explícito, e essa
pessoa decide. E a estratégia que preserva a relação comercial tem bônus no
ranqueamento, justamente para o sistema não empurrar todo mundo para a via
judicial.

**"Vocês testaram com dado real da Krilltech?"**
Não. Trabalhamos com carteira sintética calibrada pelos indicadores públicos do
setor, e nenhum dado pessoal real entrou no repositório. Conectar a base real é o
primeiro marco dos 30 dias.

**"Por que vocês não sugerem trocar as garantias?"**
Porque não conhecemos a política de crédito e jurídica da empresa. O sistema
mostra, com número, quanto da exposição está coberta por garantia que perde valor
no cenário de RJ. O que fazer com essa informação é decisão de quem é dono dela.

**"O que vem depois do hackathon?"**
Trinta dias para conectar a base real e calibrar os pesos com histórico próprio.
Sessenta para automatizar a coleta em rotina. Noventa para calibrar probabilidade
de inadimplência com resultado observado, em horizontes de 6, 12 e 24 meses.
Depois, abrir para revendas e cooperativas, que têm o mesmo problema.

---

## 9. O que nunca dizer

| Não diga | Diga |
|---|---|
| "prevê quem vai quebrar" | "mede exposição compartilhada" |
| "o sistema decide o crédito" | "o sistema entrega a decisão pronta para o comitê tomar" |
| "a Krilltech deveria usar alienação fiduciária" | "o sistema mostra quanto da garantia perde valor em RJ" |
| "a cobrança deles é cega / ruim" | "o processo atual foi desenhado para risco individual" |
| "nosso modelo de IA calcula o risco" | "o cálculo é determinístico; a IA lê documento e redige" |
| "testamos e funciona" | "validamos em carteira simulada; base real é o marco de 30 dias" |
| "GIRO", "governança de agentes", "harness" | "trilha de auditoria da decisão de crédito" |

---

## 10. Cola dos 5 minutos antes de subir

1. **A tese:** 180 dias de stay period. Depois do pedido, não existe boa decisão.
2. **Os três números:** 1.990 RJs (+56,4%) · 2,7% → 7,3% · carteira em 18 estados.
3. **A cena:** Agro Vale do Cerrado pede RJ → quatro acendem → **R$ 1.258.000** de
   exposição classificada como saudável → um fica verde.
4. **Os quatro vínculos:** grupo econômico · avalista · sócio no QSA · região e
   cultura com quebra confirmada pela Conab.
5. **A decisão:** Sítio Boa Esperança, 530, rating C, adimplente hoje.
6. **O fecho:** produtividade da lavoura ↔ saúde financeira de quem compra.
7. **Respire depois de "só existe decisão antes".** Conte até dois.
