# Matriz de cobertura — o que o pipeline alimenta de verdade

> **GERADO** por `python -m ingestao cobertura`. Não edite à mão: as
> declarações vivem em `ingestao/fontes/*.py`, ao lado do parser que as
> implementa. Última geração: 2026-09-12.

Legenda:

- **✅ real** — fonte pública preenche o alvo, com vínculo direto ao cliente.
- **🟡 parcial** — a fonte existe mas não fecha sozinha: nível agregado,
  casamento probabilístico ou campo ausente. Entra com `confianca < 1`.
- **⛔ bloqueado** — é pública mas não consumível por máquina hoje
  (captcha, chave restrita, sem a chave de ligação). Exige passo manual.
- **🔒 interno (ERP)** — não existe fonte pública, e nem deveria: é dado
  comercial da Krilltech.
- **🔴 sintético** — não há fonte pública nem dado interno. Tem de ser
  inventado — e isso tem de aparecer na tela.

## Resumo

| Situação | Alvos | % |
|---|---:|---:|
| 🔴 sintético | 2 | 3% |
| ⛔ bloqueado | 10 | 14% |
| 🔒 interno (ERP) | 14 | 20% |
| 🟡 parcial | 19 | 27% |
| ✅ real | 25 | 36% |
| **total** | **70** | |

## Por fonte

### Krilltech — ERP (recebíveis, garantias, grupos, lavoura)

- **id:** `interno` · **órgão:** Krilltech · **periodicidade:** conforme o ERP
- **endpoint:** (arquivos em data/interno/)
- **automação:** extract + transform
- **passo manual necessário:** Exportar do ERP para data/interno/*.csv nos layouts do docstring de interno_krilltech.py. Nada disso tem equivalente publico.

| Alvo no grafo | Situação | Conf. | Nota |
|---|---|---:|---|
| `:Recebivel (todo o no)` | 🔒 interno (ERP) | 1.00 | Valor, vencimento, atraso, status. NENHUMA fonte publica publica recebivel privado — e nem deveria. |
| `:Recebivel.garantia_tipo / .garantia_valor` | 🔒 interno (ERP) | 1.00 | Contrato. E o insumo do haircut por tipo de garantia, que e um dos 5 componentes do score. |
| `:Recebivel.estagio_juridico` | 🔒 interno (ERP) | 1.00 | Filtro de elegibilidade da Q4. So o juridico da empresa sabe em que estagio esta cada titulo. |
| `:Avalista + GARANTIDO_POR` | 🔒 interno (ERP) | 1.00 | Aval e clausula de contrato privado. E o vetor de peso 0,85 do motor (avalista em comum) e nao tem substituto publico. |
| `:GrupoEconomico + PERTENCE_A` | 🔒 interno (ERP) | 1.00 | Vetor de peso 0,90, o maior do motor. Nao existe base publica de grupo economico. Ou vem do cadastro, ou e inferido de socio+endereco — e inferencia tem de ir ao grafo marcada. |
| `(:Cliente)-[:PLANTA]->(:Cultura) + hectares` | 🔒 interno (ERP) | 1.00 | A nota fiscal de insumo diz o que o produtor plantou. A PAM so diz o que o municipio colheu. |
| `TEM_SOCIO.participacao` | 🔒 interno (ERP) | 1.00 | Contrato social. A QSA publica nao traz percentual. |
| `:Cliente.dias_atraso_max / .situacao` | 🔒 interno (ERP) | 1.00 | Comportamento de pagamento e o componente de maior peso pratico do score e e 100% interno. |
| `:EstrategiaRecuperacao (catalogo)` | 🔒 interno (ERP) | 1.00 | Custo medio, prazo e taxa de sucesso historica sao do historico de cobranca da propria empresa. O catalogo do seed e estimativa de mercado — util para demo, nao para decisao. |
| `(:Cliente)-[:COMPRA_VIA]->(revenda)` | 🔒 interno (ERP) | 1.00 | Canal de venda e cadastro comercial. |

### Receita Federal — cadastro CNPJ e QSA

- **id:** `qsa` · **órgão:** Receita Federal do Brasil · **periodicidade:** mensal na origem; consulta sob demanda
- **endpoint:** https://brasilapi.com.br/api/cnpj/v1/{cnpj}
- **automação:** extract + transform

| Alvo no grafo | Situação | Conf. | Nota |
|---|---|---:|---|
| `:GrupoEconomico + PERTENCE_A` | 🔴 sintético | 0.00 | NAO EXISTE base publica de grupo economico no Brasil. E o vetor de maior peso do motor (0,90) e o mais fragil de alimentar: ou vem do cadastro da Krilltech, ou e INFERIDO (socio em comum + mesmo endereco) — e ai e hipotese, nao fato. |
| `:Cliente.tipo` | 🔒 interno (ERP) | 1.00 | produtor_pj / produtor_pf / revenda e classificacao COMERCIAL da Krilltech: o CNAE diz o que a empresa faz, nao o papel dela na carteira. Vem da carteira de entrada. |
| `TEM_SOCIO.participacao` | 🔒 interno (ERP) | 0.00 | A QSA publica NAO publica percentual de participacao. So sai do contrato social / cadastro da Krilltech. |
| `:Cliente.porte` | 🟡 parcial | 1.00 | VOCABULARIOS INCOMPATIVEIS. O esquema usa pequeno/medio/grande; a Receita usa MICRO EMPRESA / EMPRESA DE PEQUENO PORTE / DEMAIS, e 'DEMAIS' engloba medio E grande sem distinguir. Micro e EPP viram 'pequeno'; DEMAIS fica VAZIO (valor cru preservado em `porte_receita`). A distincao medio/grande e classificacao comercial da Krilltech. |
| `:Socio.documento` | 🟡 parcial | 1.00 | CPF MASCARADO ('***912137**'), como no seed. O campo existe e e real, mas nao identifica a pessoa — e por isso que a identidade entre duas empresas fica em confianca 0,85. |
| `(:Cliente)-[:TEM_SOCIO]->(:Socio)` | 🟡 parcial | 0.85 | A aresta e real, a IDENTIDADE do socio entre duas empresas e inferida: CPF vem mascarado ('***912137**'), casa-se por 6 digitos + nome. E o vetor de peso 0,70 do motor — sustenta investigacao, nao decisao automatica. |
| `:Evento{tipo:'alteracao_qsa'} (SAIDA de socio)` | 🟡 parcial | 0.00 | A QSA e um retrato do agora: quem saiu nao aparece. Exige guardar snapshots e comparar — o pipeline grava o JSON bruto em data/raw/qsa/ justamente para viabilizar isso no 2o mes. |
| `:Socio de cliente PF` | 🟡 parcial | 0.00 | Produtor rural PF nao tem QSA. Cobrir exige CPF->empresas, que a Receita nao publica. |
| `:Cliente.nome / .uf / .municipio` | ✅ real | 1.00 | Razao social e endereco do cadastro CNPJ. |
| `:Cliente.cnae / .situacao_cadastral` | ✅ real | 1.00 | Campos novos, nao existiam no seed. Situacao cadastral ('BAIXADA', 'SUSPENSA') e red flag de graca. |
| `:Socio.nome / .qualificacao` | ✅ real | 1.00 | Quadro societario completo da PJ. |
| `:Evento{tipo:'alteracao_qsa'} (entrada de socio)` | ✅ real | 1.00 | Derivado de data_entrada_sociedade < 180 dias. |

### CVM — cadastro de companhias abertas

- **id:** `cvm` · **órgão:** Comissão de Valores Mobiliários · **periodicidade:** diária
- **endpoint:** https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv
- **automação:** extract + transform

| Alvo no grafo | Situação | Conf. | Nota |
|---|---|---:|---|
| `Produtor rural PF e Ltda fechada em RJ` | 🔴 sintético | 0.00 | Continua sem fonte publica aberta: DJE (PDF por comarca), API comercial paga, ou a intimacao que a Krilltech recebe como credora no processo. |
| `Cobertura da carteira` | 🟡 parcial | 1.00 | LIMITE GRANDE: so ~755 companhias tem registro ativo na CVM no Brasil inteiro. Produtor rural PF nao esta aqui; Ltda fechada nao esta aqui. Cobre a cauda de MAIOR exposicao individual (S.A. aberta, emissor de CRA, veiculo de securitizacao do agro), nao a carteira. |
| `:Evento{tipo:'pedido_rj'} + SOBRE Cliente` | ✅ real | 1.00 | CORRIGE O QUE datajud.py AFIRMA. SIT_EMISSOR='EM RECUPERACAO JUDICIAL OU EQUIVALENTE' + DT_INI_SIT_EMISSOR, com CNPJ, em CSV aberto. Ex.: AGROGALAXY (GO), 21.240.146/0001-84, desde 2024-09-18. O gatilho da demo TEM fonte publica — para companhia registrada na CVM. |
| `:Evento{tipo:'falencia'} (novo tipo)` | ✅ real | 1.00 | SIT_EMISSOR='FALIDA'. 22 companhias no cadastro atual. |
| `:Evento{tipo:'recuperacao_extrajudicial'} (novo)` | ✅ real | 1.00 | SIT_EMISSOR='EM RECUPERACAO EXTRAJUDICIAL'. |
| `:Cliente.situacao` | ✅ real | 1.00 | Deriva de SIT_EMISSOR. E o campo que a Q2 usa como override de rating D — aqui ele deixa de ser digitado a mao. |

### IBGE — malha territorial (micro e mesorregião)

- **id:** `ibge_regioes` · **órgão:** IBGE · **periodicidade:** estável (revisão censitária)
- **endpoint:** https://servicodados.ibge.gov.br/api/v1/localidades/
- **automação:** extract + transform

| Alvo no grafo | Situação | Conf. | Nota |
|---|---|---:|---|
| `OPERA_EM.hectares` | 🔒 interno (ERP) | 0.00 | Area operada e dado de cadastro/CAR, nao do IBGE. |
| `(:Cliente)-[:OPERA_EM]->(:Regiao)` | 🟡 parcial | 0.80 | Derivada do municipio da SEDE do cliente (endereco do CNPJ). Produtor com fazendas em duas microrregioes aparece so na da sede — e ai o canal sistemico subestima a exposicao. Cobrir direito exige o CAR de cada imovel (SICAR, bloqueado) ou o cadastro da Krilltech. |
| `:Regiao (id, nome, uf, codigos)` | ✅ real | 1.00 | Recorte oficial. Substitui os nomes aproximados do seed ('Sudoeste Goiano') pelo oficial ('Sudoeste de Goias', microrregiao 52013). |

### IBGE — Produção Agrícola Municipal (PAM, SIDRA 5457)

- **id:** `ibge_pam` · **órgão:** IBGE · **periodicidade:** anual, com 1 a 2 anos de defasagem
- **endpoint:** https://apisidra.ibge.gov.br/
- **automação:** extract + transform

| Alvo no grafo | Situação | Conf. | Nota |
|---|---|---:|---|
| `(:Cliente)-[:PLANTA]->(:Cultura)` | 🔒 interno (ERP) | 0.00 | Nao existe fonte publica do que um produtor especifico plantou. Vem da nota fiscal / contrato de insumo da Krilltech. |
| `Validacao de (:Cliente)-[:PLANTA]->(:Cultura)` | 🟡 parcial | 0.60 | A PAM diz o que se colhe no MUNICIPIO, nao o que o cliente plantou. Serve para CONTESTAR cadastro implausivel (algodao num municipio sem algodao), nunca para afirmar a cultura. |
| `Defasagem` | 🟡 parcial | 0.50 | Em 09/2026 o ultimo ano da PAM e 2024. Nao detecta a quebra da safra corrente; para isso a Conab. Aqui fica o baseline estrutural. |
| `:Evento{tipo:'quebra_safra'} por microrregiao` | ✅ real | 0.80 | Unica fonte publica com granularidade municipal, agregavel a microrregiao — o recorte que o motor usa em :Regiao. |

### Conab — série histórica de grãos

- **id:** `conab` · **órgão:** Companhia Nacional de Abastecimento · **periodicidade:** mensal durante a safra
- **endpoint:** https://portaldeinformacoes.conab.gov.br/downloads/arquivos/SerieHistoricaGraos.txt
- **automação:** extract + transform

| Alvo no grafo | Situação | Conf. | Nota |
|---|---|---:|---|
| `Granularidade de :Regiao (microrregiao)` | 🟡 parcial | 0.60 | A Conab publica por UF. Um evento em 'GO' acende o Sudoeste Goiano e tambem o Nordeste Goiano, que pode nao ter quebrado. Superestima a abrangencia do choque. Granularidade municipal so via IBGE/PAM, com ~1 ano de defasagem. |
| `:Evento.data de quebra_safra` | 🟡 parcial | 0.70 | A serie e por ano agricola, sem data de ocorrencia. Usa-se 1o de marco do ano de colheita como proxy do pico da colheita de verao no Centro-Oeste. |
| `:Evento{tipo:'queda_preco'}` | 🟡 parcial | 0.00 | A serie historica de GRAOS nao traz preco. A Conab publica precos em outra base (SIMA/precos agropecuarios), nao coberta por este pipeline. O motor lista 'queda_preco' como gatilho do canal sistemico e hoje ele nunca dispara. |
| `:Evento{tipo:'quebra_safra'} (nivel UF)` | ✅ real | 1.00 | MEDIDO: produtividade da safra corrente vs media das 5 anteriores, por UF x produto x safra. Substitui o EVT007 plantado a mao no seed. |
| `:Cultura (taxonomia)` | ✅ real | 1.00 | Nomes e serie por produto. ciclo_dias vem de agronomia, nao da Conab — e constante do dominio, nao dado observado. |
| `:Safra (taxonomia + status)` | ✅ real | 1.00 | ano_agricola da serie; status em_curso = safra mais recente. |

### INMET — dados históricos das estações automáticas

- **id:** `inmet` · **órgão:** Instituto Nacional de Meteorologia · **periodicidade:** diária (arquivo anual acumulado)
- **endpoint:** https://portal.inmet.gov.br/dadoshistoricos
- **automação:** extract + transform

| Alvo no grafo | Situação | Conf. | Nota |
|---|---|---:|---|
| `API apitempo.inmet.gov.br` | ⛔ bloqueado | 0.00 | A rota de serie historica responde E_ROUTE_NOT_FOUND e a variante /token/ exige chave. So /estacoes/ segue aberta, e devolve cadastro, nao medicao. Por isso os ZIPs anuais. |
| `Granularidade microrregional` | 🟡 parcial | 0.40 | A estacao tem lat/long, nao municipio. Agregacao sai por UF. lat/long vai para staging/estacoes_inmet.csv para viabilizar o join espacial contra a malha do IBGE depois. |
| `Baseline climatologico` | 🟡 parcial | 0.50 | Normal climatologica sao 30 anos; aqui sao 5 (os ZIPs baixados). Num periodo de estiagens recorrentes a propria referencia ja esta seca, o que SUBESTIMA o desvio. |
| `:Evento{tipo:'estiagem'} (novo tipo)` | ✅ real | 0.70 | Chuva acumulada na janela out-mar, medida, contra o baseline dos anos baixados. Evidencia INDEPENDENTE da Conab: quebra com chuva normal nao e clima, e manejo ou praga — e isso muda a leitura de credito. |

### PGFN — Dívida Ativa da União e FGTS

- **id:** `pgfn` · **órgão:** Procuradoria-Geral da Fazenda Nacional · **periodicidade:** trimestral
- **endpoint:** https://dadosabertos.pgfn.gov.br/
- **automação:** extract + transform

| Alvo no grafo | Situação | Conf. | Nota |
|---|---|---:|---|
| `Defasagem temporal` | 🟡 parcial | 1.00 | Publicacao trimestral: uma inscricao de hoje aparece em ate 3 meses. Para o caso de uso (antecipar RJ com meses de antecedencia) e aceitavel; para decisao intraday, nao. |
| `:Evento{tipo:'execucao_fiscal'} + SOBRE Cliente` | ✅ real | 1.00 | Fonte publica CPF/CNPJ do devedor: join deterministico com a carteira. INDICADOR_AJUIZADO='SIM' e execucao proposta. |
| `:Evento{tipo:'protesto_cda'} (novo tipo)` | ✅ real | 1.00 | ACHADO NA INGESTAO: SITUACAO_INSCRICAO='PROTESTADA' indica CDA levada a protesto. Nao e protesto de duplicata comercial (esse e de cartorio, sem base publica), mas e protesto com nome em cartorio e efeito sobre credito. Cobre PARCIALMENTE o 'protesto' do seed, que antes parecia nao ter nenhuma fonte publica. |
| `:Evento{tipo:'divida_ativa'} (novo tipo)` | ✅ real | 1.00 | Inscricao sem ajuizamento. Nao existia no seed; separado de execucao_fiscal porque a gravidade e menor (0,45 vs 0,60). |
| `:Evento.valor (exposicao fiscal em R$)` | ✅ real | 1.00 | VALOR_CONSOLIDADO. Campo novo: permite ponderar a red flag por tamanho da divida, nao so por existencia. |

### IBAMA — áreas embargadas

- **id:** `ibama` · **órgão:** IBAMA · **periodicidade:** diária
- **endpoint:** https://servicos.ibama.gov.br/ctf/publico/areasembargadas/arquivos/areas_embargadas.csv
- **automação:** extract + transform

| Alvo no grafo | Situação | Conf. | Nota |
|---|---|---:|---|
| `:Imovel.id como codigo do CAR` | ⛔ bloqueado | 0.00 | O IBAMA identifica o imovel por nome e geometria, nao por codigo do CAR. O id usado e o do termo (IBAMA-TAD-*). |
| `:Imovel.area_ha (area total)` | ⛔ bloqueado | 0.00 | O campo disponivel e QTD_AREA_EMBARGADA, que e a area EMBARGADA, nao a area do imovel. Confundir as duas superestimaria o dano. Area total so do SICAR. |
| `:Imovel.reserva_legal_ok` | ⛔ bloqueado | 0.00 | Nao existe no IBAMA. Exclusivo do SICAR. |
| `:Evento.data de embargo vs radar de 90 dias` | 🟡 parcial | 0.80 | A data e a do TERMO, nao do 'agora'. Ha embargos vigentes de 1995 nesta base. O radar por janela curta nao os mostra, embora sejam restricao viva — por isso os campos `vigente` e `idade_anos` acompanham o evento. |
| `(:Cliente)-[:POSSUI]->(:Imovel)` | 🟡 parcial | 0.90 | O termo liga o autuado ao imovel embargado. Cobre so os imoveis COM embargo — nao e o inventario de imoveis do cliente, e a lista dos que tem problema. |
| `:Evento{tipo:'embargo_ambiental'} + SOBRE Cliente` | ✅ real | 1.00 | Fonte publica CPF_CNPJ_EMBARGADO: join deterministico. |
| `:Imovel.embargo_ibama` | ✅ real | 1.00 | E o proprio objeto do termo de embargo. Estar na lista = embargo EM VIGOR (o IBAMA retira o termo quando levantado). Esta propriedade e quem deve alimentar a matriz de red flags; o :Evento serve ao radar por data. |

### CNJ/DataJud — API pública de metadados processuais

- **id:** `datajud` · **órgão:** Conselho Nacional de Justiça · **periodicidade:** diária (carga dos tribunais)
- **endpoint:** https://api-publica.datajud.cnj.jus.br/
- **automação:** extract + transform

| Alvo no grafo | Situação | Conf. | Nota |
|---|---|---:|---|
| `:Evento{tipo:'pedido_rj'} + SOBRE Cliente` | ⛔ bloqueado | 0.00 | O DataJud publico NAO expoe as partes (Portaria CNJ 160/2020): ha 1.291 pedidos de RJ no TJGO e nenhum e atribuivel a um CNPJ por esta via. Para companhia registrada na CVM o elo existe em outra fonte (ver cvm_cias.py); para produtor PF e Ltda fechada, so DJE, API paga ou a intimacao recebida como credora. |
| `:Evento{tipo:'protesto'} de duplicata` | ⛔ bloqueado | 0.00 | Protesto nao esta no DataJud — e ato de cartorio, nao processo. A CENPROT tem consulta publica por documento, mas com captcha e sem API. Protesto de CDA fiscal, esse sim, sai da PGFN (ver pgfn_dau.py). |
| `Classes de falencia / rec. extrajudicial` | 🟡 parcial | 0.00 | classe.nome nao e campo pesquisavel na API, entao nao da para descobrir o codigo por busca textual. Tem de sair da Tabela Processual Unificada do CNJ e ser somado a CLASSES. |
| `:EventoRegional{tipo:'pressao_rj_regional'}` | ✅ real | 1.00 | Contagem EXATA (track_total_hits) de pedidos de RJ por microrregiao, na janela de 365 dias, contra a media dos 4 anos anteriores da MESMA microrregiao. Novo — nao existia no seed. |
| `:EventoRegional{tipo:'pressao_fiscal_regional'}` | ✅ real | 1.00 | Idem para execucao fiscal (classe 1116). |
| `Deteccao de carga intermitente do tribunal` | ✅ real | 1.00 | ACHADO NA INGESTAO: TJSP classe 129 no municipio 3550308 tem 2019:1 2022:13 2023:6 2024:0 2025:44 2026:118 — anos ZERADOS no meio da serie. Uma vara de RJ em Sao Paulo nao teve zero pedidos em 2024; o ano nao foi alimentado. Sem checar isso o pipeline reportava '34x acima da media'. Agora detecta o ano vazio e SE RECUSA a medir, gravando o motivo. |
| `dataAjuizamento corrompido na origem` | ✅ real | 1.00 | A base tem processos datados de 2206, 4201 e 8007 (visto em TJSP e TJRS). A query passou a ter teto em 'hoje', senao um processo de 2206 cai na janela dos ultimos 365 dias. |
| `Contagem exata em UF de alto volume` | ✅ real | 1.00 | RESOLVIDO: a versao paginada truncava em ~50 mil processos (RS e SP pararam em 49.945 e 49.950, em ordem cronologica, enviesando microrregiao para baixo). Agora conta por agregacao com size:0 — sem paginacao e sem teto. |

### SICAR — Cadastro Ambiental Rural

- **id:** `sicar` · **órgão:** Serviço Florestal Brasileiro · **periodicidade:** contínua
- **endpoint:** https://consultapublica.car.gov.br/
- **automação:** só declaração (sem código de coleta)
- **passo manual necessário:** Pedir ao cliente o recibo de inscrição no CAR (rotina em credito rural) e carregar como dado interno em data/interno/imoveis.csv. Alternativa institucional: convenio com o SFB.

| Alvo no grafo | Situação | Conf. | Nota |
|---|---|---:|---|
| `:Imovel.id (codigo do CAR)` | ⛔ bloqueado | 0.00 | Consulta publica com captcha, shapefile por estado. |
| `:Imovel.area_ha (area total)` | ⛔ bloqueado | 0.00 | So o SICAR tem area total. O IBAMA tem area EMBARGADA, que e coisa diferente e menor. |
| `:Imovel.reserva_legal_ok` | ⛔ bloqueado | 0.00 | Exclusivo do SICAR. |
| `Chave imovel -> cliente` | ⛔ bloqueado | 0.00 | O download publico do CAR NAO traz CPF/CNPJ do proprietario. Sem essa chave o shapefile nao liga ao grafo, mesmo baixado. |
| `(:Imovel)-[:LOCALIZADO_EM]->(:Regiao)` | 🟡 parcial | 0.90 | Derivavel do municipio do imovel quando ele vem do IBAMA; para os imoveis sem embargo, nao ha imovel no grafo. |

## O que isso significa para o pitch

Os dois vetores de MAIOR peso do motor de contágio são os de pior
cobertura pública:

| Vetor | Peso | De onde vem de verdade |
|---|---:|---|
| Mesmo grupo econômico | 0,90 | 🔒 cadastro da Krilltech — **não existe base pública de grupo econômico no Brasil** |
| Avalista em comum | 0,85 | 🔒 contrato de aval, dado privado |
| Sócio em comum (QSA) | 0,70 | 🟡 Receita, com CPF mascarado — casamento por nome + 6 dígitos |
| Mesma região e cultura | 0,75 | 🟡 região real (IBGE) + choque real (Conab), mas cultura do cliente é interna |

E o gatilho da demo — `pedido_rj` sobre um cliente específico — é o
único elo que **nenhuma** fonte pública automatizável entrega: o DataJud
tem os 1.291 pedidos de RJ do TJGO e, por desenho da Portaria CNJ
160/2020, não tem as partes.

A leitura honesta: **o Lastro é um sistema cuja espinha é o dado interno
da Krilltech, enriquecido por fonte pública no contexto de risco.** O que
o público entrega bem — e entrega de verdade, medido, não plantado — é
dívida ativa com CNPJ (PGFN), embargo ambiental com CNPJ (IBAMA), quebra
de safra (Conab), déficit de chuva (INMET), recorte territorial (IBGE) e
pressão judicial regional (DataJud). Isso é contexto de primeira linha.
Não é a carteira.
