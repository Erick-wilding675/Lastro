# Lastro: a narrativa completa, para estudo

Este texto existe para ser lido várias vezes, em voz alta se possível, até que a
história saia sem esforço. Não é o roteiro cronometrado do pitch, que está em
pitch-roteiro.md, e não é o banco de perguntas em formato de consulta rápida, que
está em pitch-estudo.md. É a solução inteira, contada como uma história só, em
prosa corrida, para você internalizar o raciocínio de ponta a ponta e nunca ficar
sem palavras quando a banca perguntar algo fora do script.

## A tese

Quando um cliente da Krilltech entra com pedido de Recuperação Judicial, começa
um período de proteção legal de cento e oitenta dias, prorrogável, em que a
empresa fica impedida de executar qualquer garantia ou de protestar o devedor.
Esse mecanismo existe na Lei 11.101 de 2005 e foi estendido ao produtor rural
pessoa física pela Lei 14.112 de 2020, o que colocou dentro da Recuperação
Judicial uma população inteira que antes ficava fora dela. A partir do momento em
que o pedido é protocolado, o crédito que a Krilltech tinha contra aquele cliente
entra num plano de pagamento com deságio e prazo alongado, decidido em conjunto
com todos os outros credores. Não existe mais decisão individual da Krilltech
sobre aquele caso. Por isso a frase que resume tudo é simples: depois do pedido
de Recuperação Judicial não existe mais uma boa decisão a tomar, só existe a
decisão que deveria ter sido tomada antes. Todo o valor do produto está
concentrado nesse "antes".

O problema é que esse "antes" está ficando mais raro e mais urgente ao mesmo
tempo. Em 2025 foram protocolados mil novecentos e noventa pedidos de
Recuperação Judicial no agronegócio brasileiro, um crescimento de cinquenta e
seis vírgula quatro por cento sobre 2024, segundo a Serasa Experian. No mesmo
intervalo, a inadimplência acima de noventa dias do produtor rural pessoa física
saltou de dois vírgula sete por cento para sete vírgula três por cento, de
acordo com o Banco Central, e o primeiro trimestre de 2026 fechou em oito vírgula
oito por cento de inadimplência rural, o maior número da série histórica da
Serasa. A causa não é um único evento: é a combinação de quebras de safra
ligadas a El Niño e La Niña, queda na cotação de soja e milho e custo de insumo
em alta, tudo acontecendo ao mesmo tempo sobre uma base de crédito que cresceu
nos últimos anos.

## Quem sente essa dor e por que ela chega até a Krilltech

A Krilltech é uma agtech de Brasília nascida de uma parceria com a UnB e a
Embrapa, criadora do produto Arbolin Biogenesis, uma solução de nanotecnologia
aplicada à produtividade agrícola. Ela vende diretamente ao produtor rural, a
prazo, em dezoito estados, para mais de duzentos clientes espalhados por vinte e
três culturas diferentes e cerca de trinta mil hectares monitorados. O modelo de
venda a prazo casado com o ciclo da safra é comum e racional no agro: o produtor
paga depois de colher. O problema é que esse mesmo modelo transforma a Krilltech
em credora de uma carteira inteira de risco agrícola, sem que ela tenha, hoje,
uma ferramenta para enxergar esse risco como rede. A empresa promete otimizar a
produtividade da lavoura do seu cliente através de tecnologia; falta a ela a
mesma inteligência aplicada à saúde financeira de quem compra dela. É esse o
espaço que o Lastro ocupa, e é por isso que o fecho do pitch conecta as duas
coisas: o mesmo negócio, fechando o ciclo.

Hoje essa carteira é gerida como uma lista de vencimentos, olhando cada cliente
isoladamente. Só que no agro o risco não se comporta assim. Um produtor não
quebra sozinho: ele quebra porque divide sócio, avalista ou grupo econômico com
outro que já quebrou, ou porque está na mesma região e na mesma cultura que
sofreu uma quebra de safra documentada. Tratar cada cliente como um ponto
isolado é o motivo pelo qual a Krilltech só descobre o problema quando ele já
apareceu na régua de vencidos, ou seja, tarde demais para agir com liberdade.

## O que é o Lastro

O Lastro é um processo contínuo de inteligência de risco relacional e
recuperação de capital. Ele representa a carteira de recebíveis da Krilltech
como um grafo em vez de uma tabela: cada cliente é um nó, e os vínculos entre
eles (sócio em comum, avalista em comum, grupo econômico, região, cultura,
canal de venda) são arestas. Quando um cliente muda de situação, por exemplo
entra em Recuperação Judicial, o sistema propaga esse evento pela rede e
identifica quais outros clientes estão expostos ao mesmo risco antes que esse
risco apareça no aging da carteira. Para cada cliente ele calcula um score de
zero a mil, convertido num rating de A a D, monta uma matriz de red flags, e
recomenda limite de crédito, condição de pagamento e estratégia de recuperação,
sempre explicando por qual caminho aquele risco chegou até ali. Nada disso é
disparado automaticamente: o sistema entrega a decisão pronta para o comitê de
crédito da empresa tomar, com a fonte e a data de cada dado que sustentou a
recomendação.

O diferencial técnico central é que o motor de propagação de risco é
implementado como grafo em Neo4j, não como banco relacional. A pergunta que o
produto responde ("quem mais está exposto ao mesmo risco que este cliente, e
por qual caminho") é uma pergunta de múltiplos saltos, com peso diferente por
tipo de vínculo e com necessidade de reconstruir o caminho percorrido para
explicar o resultado a um humano. Em SQL essa pergunta vira uma junção
recursiva difícil de escrever, de manter e de explicar. Em Cypher, a linguagem
de consulta do Neo4j, ela é uma única query legível. Essa é a justificativa
técnica que sustenta a nota de viabilidade técnica e execução, que vale vinte e
cinco por cento da avaliação.

## O motor de exposição e os dois canais de contágio

O coração do Lastro é o motor que decide como o risco se espalha pela rede, e a
decisão mais importante de todo o desenho foi separar esse espalhamento em dois
canais com naturezas diferentes.

O primeiro canal é o estrutural. Nele, o risco de um cliente contamina o outro
porque existe um vínculo jurídico ou patrimonial direto entre eles: pertencer
ao mesmo grupo econômico, compartilhar o mesmo avalista, ou ter o mesmo sócio no
quadro societário, informação que vem do Quadro de Sócios e Administradores da
Receita Federal, uma base pública. Esses três vínculos recebem, respectivamente,
peso zero vírgula noventa, zero vírgula oitenta e cinco e zero vírgula setenta.
A lógica aqui é de contaminação real: se um sócio ou avalista comum quebra, o
patrimônio que sustentava a garantia do outro cliente também está comprometido.

O segundo canal é o sistêmico, e a lógica dele é oposta. Aqui nenhum cliente
contamina o outro: todos sofrem a mesma causa externa, como uma seca regional
ou uma queda de preço da commodity. Os vínculos sistêmicos são a combinação de
mesma região e mesma cultura, com peso zero vírgula setenta e cinco, a mesma
revenda ou canal de compra, com peso zero vírgula sessenta e cinco, e a mesma
cultura isoladamente, com peso zero vírgula quarenta. A diferença crucial é que
o peso cheio de região e cultura só é aplicado quando existe um evento regional
confirmando o choque, como uma quebra de safra registrada pela Conab, um alerta
do Zoneamento Agrícola de Risco Climático ou uma queda de cotação documentada
nos últimos trezentos e sessenta e cinco dias. Sem esse evento confirmando a
causa comum, o peso cai para zero vírgula trinta. Essa condicional existe
especificamente para responder à pergunta mais óbvia que a banca pode fazer: se
a região inteira acende só porque um vizinho quebrou. A resposta é não, e não
por sorte, mas por desenho: a vizinhança geográfica só é tratada como risco
real quando existe uma causa documentada, com fonte, e não apenas por
proximidade no mapa.

Toda aresta de exposição calculada guarda o caminho que a originou. Isso
significa que o sistema nunca mostra um número de risco isolado: ele sempre diz
por que aquele número existe, seja "este cliente divide avalista com quem
acabou de pedir Recuperação Judicial" ou "este cliente está na mesma
microrregião onde a Conab confirmou quebra de safra de dezoito por cento". O
caminho é a explicação, e é essa explicação que transforma um alerta em algo
que um gestor de crédito consegue defender numa reunião.

## O score, o rating e a regra que impede um erro grave

O score final vai de zero a mil e é calculado como mil multiplicado pela
diferença entre um e a média de cinco componentes de risco, cada um também
numa escala de zero a um. Os cinco componentes são o comportamento de
pagamento, os eventos jurídicos e fiscais observados numa janela de cento e
oitenta dias, a cobertura de garantia, a exposição herdada da rede através do
motor de contágio, e o risco agro e ambiental. Hoje todos os cinco pesam igual,
uma escolha deliberada e declarada como hipótese inicial, não como verdade
calibrada. A honestidade aqui é proposital: dizer que os pesos ainda não foram
calibrados com histórico real é mais defensável do que fingir uma precisão que
o time não tem.

O componente de cobertura de garantia merece atenção especial porque não é um
simples percentual. Antes de comparar a garantia com a exposição, o sistema
aplica um desconto, chamado de haircut, que varia por tipo de garantia: a
alienação fiduciária recebe haircut de um, ou seja, conta cheia, porque é um
instrumento extraconcursal e sobrevive à Recuperação Judicial; o aval recebe
zero vírgula setenta; a Cédula de Produto Rural recebe zero vírgula sessenta; o
penhor de safra recebe zero vírgula cinquenta, porque evapora com a seca e
ainda assim entra no concurso de credores da Recuperação Judicial; e a ausência
de garantia recebe zero. Na prática isso significa que trezentos mil reais
garantidos por penhor de safra entram na conta como cento e cinquenta mil
reais, porque é isso que esse tipo de garantia efetivamente protege num
cenário de estresse.

A escala de rating segue a mesma lógica em todo o mercado de crédito: de
oitocentos a mil pontos o cliente é rating A, de seiscentos a setecentos e
noventa e nove é rating B, de quatrocentos a quinhentos e noventa e nove é
rating C, e abaixo de quatrocentos é rating D, o alerta de Recuperação
Judicial. Existe ainda uma regra de exceção, chamada de knockout, que trava o
score em no máximo trezentos e cinquenta, ou seja, rating D, para qualquer
cliente que já esteja formalmente em Recuperação Judicial, independentemente
da média dos cinco componentes. Essa regra existe porque, sem ela, a média
simples dos cinco componentes pode diluir o sinal mais grave que existe no
sistema de crédito: um cliente que acabou de entrar em Recuperação Judicial não
pode, por uma questão aritmética, sair classificado como risco moderado. É uma
prática padrão em política de crédito, e é uma correção que o time encontrou e
aplicou antes de levar os números ao ensaio, exatamente para que a
demonstração ao vivo mostrasse o rating certo no cliente certo.

## Os quatro agentes de inteligência artificial

A decisão de arquitetura mais importante do Lastro não é sobre onde usar
inteligência artificial, mas sobre onde não usar. Toda a propagação de risco
pelo grafo, o cálculo do score, o haircut de garantia, a cobertura e a
priorização da carteira são determinísticos: rodam como consultas ou funções
no backend, são reproduzíveis, auditáveis e não alucinam. Isso responde de
antemão a uma das perguntas mais perigosas que a banca pode fazer, que é o que
acontece se o modelo errar o score: o score não é gerado por um modelo, é
calculado por uma fórmula fixa.

A inteligência artificial entra exatamente onde existe texto livre, ambiguidade
ou necessidade de redação, e está organizada em quatro agentes, seguindo a
arquitetura de referência sugerida no próprio documento do desafio. O primeiro
é o Agente Coletor e Parser, que recebe um CNPJ, um CPF ou um documento em PDF,
como uma petição de Recuperação Judicial ou uma certidão, consulta as bases
públicas e transforma o que encontra em eventos estruturados, cada um com
tipo, data, fonte e severidade, nunca inventando uma classificação que não
exista no vocabulário definido. O segundo é o Agente de Risco Agro e
Climático, que cruza a localização do imóvel, o zoneamento agrícola de risco
climático, a cultura plantada e o histórico de quebra da microrregião para
dizer se o contexto produtivo agrava o risco de pagamento naquela safra,
sempre citando a fonte e nunca convertendo essa avaliação em número por conta
própria. O terceiro é o Motor de Decisão e Scoring, que não calcula nada: ele
apenas decide quando disparar a propagação de exposição e o recálculo de
score, na ordem correta, e interpreta o resultado para dizer qual componente
causou a mudança de rating. O quarto e último é o Agente Sintetizador de
Relatórios, que lê o dossiê já calculado de um cliente e redige o Relatório
Padronizado de Risco de Crédito em linguagem natural, citando apenas números
que já existem no dossiê, sempre nomeando o vínculo que trouxe o risco, nunca
prescrevendo qual instrumento jurídico a Krilltech deveria adotar, e sempre
fechando com a indicação de que a decisão final é do comitê de crédito. A
frase que resume essa arquitetura inteira é que inteligência artificial entra
onde há texto e ambiguidade, e onde há conta, é consulta determinística, e é
por isso que o score não alucina.

## As fontes de dados

Todos os vínculos que alimentam o motor de contágio vêm de bases públicas ou de
dados que a própria Krilltech já possui, o que significa que o sistema não
depende de nenhuma informação inacessível. A dimensão cadastral e societária
vem da Receita Federal e da Redesim, de onde sai o Quadro de Sócios e
Administradores, o capital social, o CNAE e o tempo de atividade da empresa. A
dimensão processual e jurídica vem do DataJud do Conselho Nacional de Justiça,
dos Diários de Justiça Eletrônicos, do Jusbrasil e do Escavador, de onde saem
execuções, protestos e pedidos de Recuperação Judicial. A dimensão territorial
e ambiental vem do Sistema de Cadastro Ambiental Rural e do Ibama, mostrando a
regularidade do imóvel e eventuais embargos. A dimensão fiscal e trabalhista
vem da Procuradoria-Geral da Fazenda Nacional, do Tribunal Superior do
Trabalho e da Caixa Econômica Federal, trazendo certidões e execuções fiscais.
E a dimensão agronômica e climática vem da Conab, do Zoneamento Agrícola de
Risco Climático do Ministério da Agricultura e do Instituto Nacional de
Meteorologia, trazendo produtividade regional e risco climático por cultura e
por safra. Todas essas cinco fontes estão listadas no próprio documento do
desafio, na seção que trata das bases de dados disponíveis, o que significa
que, se a banca perguntar de onde veio essa lista, a resposta honesta é que
veio do enunciado.

## A cena que conta a história

A demonstração do pitch mostra um único cenário, escolhido para provar todo o
raciocínio de uma vez. Um cliente chamado Agro Vale do Cerrado acaba de
protocolar pedido de Recuperação Judicial. Seu score cai para trezentos e
cinquenta, rating D, sobre uma exposição de um milhão e duzentos mil reais.
Assim que esse evento é registrado, o Lastro propaga a exposição pela rede e
quatro outros clientes acendem, nenhum deles em atraso na carteira até aquele
momento. A Terra Nova acende porque pertence ao mesmo grupo econômico, com
peso zero vírgula noventa, mas mantém rating A porque sua garantia é forte o
suficiente para sobreviver ao cenário de Recuperação Judicial, o que prova que
o sistema distingue exposição alta de perda esperada alta. A Fazenda Santa
Luzia acende por dividir um sócio no quadro societário público, um produtor
chamado João Batista Moreira, e também por estar na mesma região e cultura. A
Agropecuária Horizonte acende por compartilhar o mesmo avalista, Marcos
Ferreira Duarte, um dado que já está nos próprios contratos da Krilltech. E o
Sítio Boa Esperança acende porque está na mesma região e cultura de uma quebra
de safra de dezoito por cento confirmada pela Conab, e carrega ainda um
embargo ambiental do Ibama. Juntos, esses quatro clientes representam um
milhão duzentos e cinquenta e oito mil reais de exposição que, até o momento
do pedido de Recuperação Judicial do vizinho, estava classificada como
saudável. Um quinto cliente, a Fazenda Ipê Amarelo, permanece verde, porque
está em outra região, outra cultura, e não tem nenhum vínculo com o cliente
que quebrou. Esse contraste, entre os quatro que acendem e o que permanece
verde, é a prova visual de que o sistema não pinta a carteira inteira de
vermelho: ele mostra exatamente por qual caminho o risco se espalha, e onde
ele para.

## A decisão e a governança

Para cada cliente que acende, o sistema recomenda uma ação com prazo e valor
estimado de recuperação, mas em nenhum momento executa essa ação sozinho. O
exemplo usado no pitch é o Sítio Boa Esperança, com score de quinhentos e
trinta e rating C, ainda adimplente no momento da análise: o parecer explica o
que mudou, por qual vínculo o risco chegou, e recomenda reduzir o limite de
crédito e condicionar a próxima venda, com prazo definido, deixando a decisão
final para o comitê de crédito. Essa separação entre recomendar e decidir é
uma regra dura do produto, junto com outras duas: toda decisão carrega uma
trilha de auditoria, com fonte, data e decomposição de quem recomendou o quê,
e o sistema nunca prescreve um instrumento jurídico específico, como
alienação fiduciária, para a Krilltech adotar. Ele mostra, com número, quanto
da cobertura de garantia é frágil num cenário de Recuperação Judicial; o que
fazer com essa informação é uma decisão de política de crédito que pertence à
empresa, não ao sistema. A linguagem usada em todo o produto segue a mesma
disciplina: o Lastro nunca promete prever quem vai quebrar, ele mede exposição
compartilhada e mostra por qual vínculo ela chega, porque essa é a diferença
entre uma afirmação verificável e uma promessa que ninguém consegue defender
sob pressão.

## As perguntas difíceis, explicadas por extenso

Algumas perguntas quase certamente vão aparecer na arguição, e vale entender o
raciocínio por trás de cada resposta, não só decorar a frase pronta. Sobre por
que usar grafo em vez de banco relacional, o argumento é que a pergunta central
do produto exige múltiplos saltos com peso por tipo de vínculo e reconstrução
do caminho percorrido, algo que em SQL se torna uma junção recursiva difícil de
escrever e de manter, e que em Cypher é uma única consulta legível. Sobre o que
acontece se o modelo errar, a resposta é que não existe modelo gerando o score:
existe uma fórmula determinística, e a inteligência artificial só entra para
ler documentos e redigir pareceres. Sobre se isso não é apenas um escore de
crédito parecido com o de um bureau, a diferença é que um bureau olha o
cliente isoladamente, enquanto dois clientes com o mesmo balanço e o mesmo
histórico de pagamento podem ter risco muito diferente se um deles divide
avalista com alguém que acabou de entrar em Recuperação Judicial, e esse
componente de rede simplesmente não existe em nenhum bureau de crédito
tradicional. Sobre a validação dos pesos do motor de contágio, a resposta
honesta é que eles ainda não foram calibrados com histórico real: são uma
hipótese declarada, com peso uniforme dentro de cada canal, e o que sustenta a
confiança nessa hipótese é que o caminho que gerou cada exposição fica sempre
visível, permitindo que o gestor julgue o raciocínio, não apenas a nota final;
a calibração com dado histórico real é justamente o marco dos trinta e dos
noventa dias do roadmap. Sobre a proteção de dados pessoais, a resposta tem
três camadas: primeiro, o sistema usa dado público e dado contratual que a
própria empresa já possui, para uma finalidade legítima de análise de crédito;
segundo, nenhuma categoria de dado sensível é tratada; terceiro, e mais
importante, a legislação garante ao titular do dado o direito de revisão de
uma decisão automatizada, e o Lastro nunca decide sozinho, apenas recomenda e
registra a trilha de quem decidiu, o que significa que o desenho já nasce
compatível com essa exigência. Sobre escala, o grafo suporta um volume muito
maior do que o usado na demonstração, e o custo de processamento cresce com a
vizinhança de cada evento, não com o tamanho total da carteira, o que torna a
arquitetura sustentável mesmo com dez mil clientes. Sobre custo de operação,
não existe custo de bureau porque todas as fontes usadas são públicas e
gratuitas, o banco de grafos roda em um patamar inicial de baixo custo, e o
consumo de modelo de linguagem acontece por evento, não por varredura
contínua da base inteira, o que mantém o custo por decisão baixo. Sobre como a
Krilltech adotaria isso na prática, a proposta é começar em modo sombra: o
sistema roda ao lado do processo atual durante uma safra inteira, sem nenhum
poder de decisão, e a área de crédito compara o que ele sinalizou com o que
realmente aconteceu; ganhando confiança, ele passa a ser insumo formal do
comitê, sem substituir ninguém e sem exigir mudança na política de crédito
logo no primeiro dia. E sobre se o time está dizendo que a Krilltech erra
hoje, a resposta é não: o processo atual foi desenhado para um cenário de
risco individual, que era a realidade até poucos anos atrás; o que mudou foi o
setor, que passou a ter risco correlacionado, e a ferramenta é nova porque o
problema também é.

## O que vem depois do hackathon

O roadmap declarado tem quatro marcos. Em trinta dias, a prioridade é conectar
o sistema à base real da Krilltech e começar a calibrar os pesos do motor com
o histórico próprio da empresa. Em sessenta dias, a coleta das bases públicas
passa a rodar em rotina automatizada, alimentando um radar de eventos para o
time de crédito. Em noventa dias, a probabilidade de inadimplência passa a ser
calibrada com resultado observado, em horizontes de seis, doze e vinte e
quatro meses. E depois disso, a visão é abrir o mesmo serviço para revendas,
distribuidoras e cooperativas, que enfrentam exatamente o mesmo problema de
carteira correlacionada. Esse roadmap se desdobra num plano de conclusão mais
concreto, com equipe, orçamento e cronograma de execução detalhados, que está
descrito à parte e é o fechamento do pitch: a prova de que a proposta não
termina no protótipo de doze horas, mas tem um caminho real até produção.

## O fecho

A Krilltech existe para dar ao produtor rural a mesma inteligência que ela
aplica à lavoura dele através da Arbolin Biogenesis: entender, medir e
antecipar. O Lastro entrega essa mesma inteligência para a própria Krilltech,
aplicada à saúde financeira de quem compra dela. É o mesmo negócio, olhando
para dentro em vez de olhar só para fora, fechando o ciclo que a empresa já
promete ao seu cliente.
