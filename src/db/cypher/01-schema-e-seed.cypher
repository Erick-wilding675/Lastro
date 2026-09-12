// =====================================================================
// SETUP NEO4J — Schema + Seed sintético
// Case KRILLTECH — Hackathon PMI-DF 2026
//
// COMO USAR no Neo4j Browser / AuraDB:
//   Cole e rode BLOCO A PRIMEIRO (constraints), depois BLOCO B (seed).
//   O seed é idempotente (MERGE), pode rodar de novo sem duplicar.
//
// O seed NÃO é aleatório: tem um cenário de demonstração plantado.
// CLI001 pede RJ e acende 4 vizinhos por 4 vetores diferentes de
// contágio, mais 1 cliente de controle que continua verde.
// É essa história que sustenta os 3 minutos de pitch.
// =====================================================================


// =====================================================================
// BLOCO A — CONSTRAINTS E ÍNDICES
// =====================================================================

CREATE CONSTRAINT cliente_id IF NOT EXISTS FOR (c:Cliente) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT recebivel_id IF NOT EXISTS FOR (r:Recebivel) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT socio_id IF NOT EXISTS FOR (s:Socio) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT avalista_id IF NOT EXISTS FOR (a:Avalista) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT grupo_id IF NOT EXISTS FOR (g:GrupoEconomico) REQUIRE g.id IS UNIQUE;
CREATE CONSTRAINT regiao_id IF NOT EXISTS FOR (r:Regiao) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT cultura_id IF NOT EXISTS FOR (c:Cultura) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT safra_id IF NOT EXISTS FOR (s:Safra) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT imovel_id IF NOT EXISTS FOR (i:Imovel) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT evento_id IF NOT EXISTS FOR (e:Evento) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT estrategia_id IF NOT EXISTS FOR (e:EstrategiaRecuperacao) REQUIRE e.id IS UNIQUE;

CREATE INDEX cliente_situacao IF NOT EXISTS FOR (c:Cliente) ON (c.situacao);
CREATE INDEX recebivel_status IF NOT EXISTS FOR (r:Recebivel) ON (r.status);
CREATE INDEX evento_data IF NOT EXISTS FOR (e:Evento) ON (e.data);
CREATE INDEX evento_tipo IF NOT EXISTS FOR (e:Evento) ON (e.tipo);


// =====================================================================
// BLOCO B — SEED
// =====================================================================

// --- Taxonomias -------------------------------------------------------

MERGE (:Regiao {id:'REG-GO-SUD', nome:'Sudoeste Goiano', uf:'GO'});
MERGE (:Regiao {id:'REG-MT-MED', nome:'Médio-Norte Mato-grossense', uf:'MT'});
MERGE (:Regiao {id:'REG-BA-OES', nome:'Oeste Baiano', uf:'BA'});
MERGE (:Regiao {id:'REG-MS-SUL', nome:'Sul Mato-grossense', uf:'MS'});

MERGE (:Cultura {id:'CUL-SOJA',    nome:'Soja',    ciclo_dias:120});
MERGE (:Cultura {id:'CUL-MILHO',   nome:'Milho',   ciclo_dias:150});
MERGE (:Cultura {id:'CUL-ALGODAO', nome:'Algodão', ciclo_dias:180});

MERGE (:Safra {id:'SAF-2526', ano_agricola:'2025/26', status:'em_curso'});
MERGE (:Safra {id:'SAF-2425', ano_agricola:'2024/25', status:'encerrada'});

// --- Grupos econômicos, sócios e avalistas ---------------------------

MERGE (:GrupoEconomico {id:'GRP001', nome:'Grupo Terra Nova'});
MERGE (:GrupoEconomico {id:'GRP002', nome:'Holding Agro Ipê'});

MERGE (:Socio {id:'SOC001', nome:'João Batista Moreira',  documento:'***.456.789-**'});
MERGE (:Socio {id:'SOC002', nome:'Marcelo Andrade Pinto', documento:'***.112.334-**'});
MERGE (:Socio {id:'SOC003', nome:'Regina Alves Campos',   documento:'***.778.221-**'});
MERGE (:Socio {id:'SOC004', nome:'Paulo Sérgio Tavares',  documento:'***.901.455-**'});

MERGE (:Avalista {id:'AVA001', nome:'Marcos Ferreira Duarte', tipo:'pf', documento:'***.334.567-**'});
MERGE (:Avalista {id:'AVA002', nome:'Agropecuária Cruzeiro Ltda', tipo:'pj', documento:'**.456.789/0001-**'});
MERGE (:Avalista {id:'AVA003', nome:'Helena Moretti Braga', tipo:'pf', documento:'***.667.889-**'});

// --- Catálogo de estratégias de recuperação --------------------------

MERGE (e:EstrategiaRecuperacao {id:'EST-RENEG'}) SET e.nome='Renegociação',
  e.custo_medio=1200.0, e.prazo_medio_dias=45, e.taxa_sucesso_historica=0.62,
  e.preserva_relacao=true, e.estagios_elegiveis=['nenhum','notificado'];
MERGE (e:EstrategiaRecuperacao {id:'EST-BARTER'}) SET e.nome='Barter (pagamento em safra)',
  e.custo_medio=2500.0, e.prazo_medio_dias=120, e.taxa_sucesso_historica=0.71,
  e.preserva_relacao=true, e.estagios_elegiveis=['nenhum','notificado'];
MERGE (e:EstrategiaRecuperacao {id:'EST-AMIG'}) SET e.nome='Cobrança amigável',
  e.custo_medio=400.0, e.prazo_medio_dias=20, e.taxa_sucesso_historica=0.48,
  e.preserva_relacao=true, e.estagios_elegiveis=['nenhum','notificado'];
MERGE (e:EstrategiaRecuperacao {id:'EST-PARC'}) SET e.nome='Acordo parcelado',
  e.custo_medio=900.0, e.prazo_medio_dias=90, e.taxa_sucesso_historica=0.55,
  e.preserva_relacao=true, e.estagios_elegiveis=['nenhum','notificado','protestado'];
MERGE (e:EstrategiaRecuperacao {id:'EST-CONVGAR'}) SET e.nome='Conversão de garantia para alienação fiduciária',
  e.custo_medio=3500.0, e.prazo_medio_dias=30, e.taxa_sucesso_historica=0.80,
  e.preserva_relacao=true, e.estagios_elegiveis=['nenhum','notificado'];
MERGE (e:EstrategiaRecuperacao {id:'EST-PROT'}) SET e.nome='Protesto',
  e.custo_medio=600.0, e.prazo_medio_dias=15, e.taxa_sucesso_historica=0.35,
  e.preserva_relacao=false, e.estagios_elegiveis=['notificado'];
MERGE (e:EstrategiaRecuperacao {id:'EST-JUD'}) SET e.nome='Execução judicial',
  e.custo_medio=15000.0, e.prazo_medio_dias=540, e.taxa_sucesso_historica=0.40,
  e.preserva_relacao=false, e.estagios_elegiveis=['protestado','judicial'];
MERGE (e:EstrategiaRecuperacao {id:'EST-HABRJ'}) SET e.nome='Habilitação no plano de RJ',
  e.custo_medio=8000.0, e.prazo_medio_dias=900, e.taxa_sucesso_historica=0.22,
  e.preserva_relacao=false, e.estagios_elegiveis=['habilitado_rj'];

// --- Clientes ---------------------------------------------------------
// CLI001 é o gatilho da demo: entra em RJ.
// CLI002..CLI005 acendem por vetores DIFERENTES de contágio.
// CLI006 é o controle: nenhum vínculo, segue verde.

MERGE (c:Cliente {id:'CLI001'}) SET c.nome='Agro Vale do Cerrado Ltda', c.tipo='produtor_pj',
  c.documento='**.111.222/0001-**', c.uf='GO', c.municipio='Rio Verde', c.porte='grande',
  c.situacao='recuperacao_judicial', c.dias_atraso_max=98, c.cliente_desde=date('2019-03-11');
MERGE (c:Cliente {id:'CLI002'}) SET c.nome='Fazenda Santa Luzia', c.tipo='produtor_pf',
  c.documento='***.456.789-**', c.uf='GO', c.municipio='Jataí', c.porte='medio',
  c.situacao='adimplente', c.dias_atraso_max=0, c.cliente_desde=date('2021-08-02');
MERGE (c:Cliente {id:'CLI003'}) SET c.nome='Agropecuária Horizonte S/A', c.tipo='produtor_pj',
  c.documento='**.333.444/0001-**', c.uf='MT', c.municipio='Sorriso', c.porte='grande',
  c.situacao='atraso', c.dias_atraso_max=34, c.cliente_desde=date('2020-01-20');
MERGE (c:Cliente {id:'CLI004'}) SET c.nome='Sítio Boa Esperança', c.tipo='produtor_pf',
  c.documento='***.221.887-**', c.uf='GO', c.municipio='Rio Verde', c.porte='pequeno',
  c.situacao='adimplente', c.dias_atraso_max=0, c.cliente_desde=date('2022-05-14');
MERGE (c:Cliente {id:'CLI005'}) SET c.nome='Terra Nova Agronegócios Ltda', c.tipo='produtor_pj',
  c.documento='**.555.666/0001-**', c.uf='MT', c.municipio='Lucas do Rio Verde', c.porte='grande',
  c.situacao='adimplente', c.dias_atraso_max=0, c.cliente_desde=date('2018-11-30');
MERGE (c:Cliente {id:'CLI006'}) SET c.nome='Fazenda Ipê Amarelo', c.tipo='produtor_pf',
  c.documento='***.909.112-**', c.uf='BA', c.municipio='Luís Eduardo Magalhães', c.porte='medio',
  c.situacao='adimplente', c.dias_atraso_max=0, c.cliente_desde=date('2020-07-19');
MERGE (c:Cliente {id:'CLI007'}) SET c.nome='Cerrado Insumos Distribuidora', c.tipo='revenda',
  c.documento='**.777.888/0001-**', c.uf='GO', c.municipio='Rio Verde', c.porte='medio',
  c.situacao='adimplente', c.dias_atraso_max=0, c.cliente_desde=date('2019-09-05');
MERGE (c:Cliente {id:'CLI008'}) SET c.nome='Agroindústria Rio Claro S/A', c.tipo='produtor_pj',
  c.documento='**.999.000/0001-**', c.uf='MS', c.municipio='Dourados', c.porte='grande',
  c.situacao='inadimplente', c.dias_atraso_max=142, c.cliente_desde=date('2017-02-28');
MERGE (c:Cliente {id:'CLI009'}) SET c.nome='Fazenda Três Irmãos', c.tipo='produtor_pf',
  c.documento='***.554.332-**', c.uf='MT', c.municipio='Sorriso', c.porte='medio',
  c.situacao='atraso', c.dias_atraso_max=21, c.cliente_desde=date('2021-04-08');
MERGE (c:Cliente {id:'CLI010'}) SET c.nome='Sementes Planalto Ltda', c.tipo='produtor_pj',
  c.documento='**.246.813/0001-**', c.uf='BA', c.municipio='Barreiras', c.porte='pequeno',
  c.situacao='adimplente', c.dias_atraso_max=0, c.cliente_desde=date('2023-01-16');

// --- Vínculos societários (fonte: QSA / Receita Federal) --------------
// SOC001 é o vetor forte: liga CLI001 (em RJ) a CLI002 (ainda adimplente).

MATCH (c:Cliente {id:'CLI001'}), (s:Socio {id:'SOC001'}) MERGE (c)-[:TEM_SOCIO {participacao:0.60}]->(s);
MATCH (c:Cliente {id:'CLI001'}), (s:Socio {id:'SOC002'}) MERGE (c)-[:TEM_SOCIO {participacao:0.40}]->(s);
MATCH (c:Cliente {id:'CLI002'}), (s:Socio {id:'SOC001'}) MERGE (c)-[:TEM_SOCIO {participacao:1.00}]->(s);
MATCH (c:Cliente {id:'CLI005'}), (s:Socio {id:'SOC003'}) MERGE (c)-[:TEM_SOCIO {participacao:0.70}]->(s);
MATCH (c:Cliente {id:'CLI003'}), (s:Socio {id:'SOC003'}) MERGE (c)-[:TEM_SOCIO {participacao:0.30}]->(s);
MATCH (c:Cliente {id:'CLI008'}), (s:Socio {id:'SOC004'}) MERGE (c)-[:TEM_SOCIO {participacao:1.00}]->(s);

// --- Grupos econômicos ------------------------------------------------

MATCH (c:Cliente {id:'CLI003'}), (g:GrupoEconomico {id:'GRP001'}) MERGE (c)-[:PERTENCE_A]->(g);
MATCH (c:Cliente {id:'CLI005'}), (g:GrupoEconomico {id:'GRP001'}) MERGE (c)-[:PERTENCE_A]->(g);
MATCH (c:Cliente {id:'CLI006'}), (g:GrupoEconomico {id:'GRP002'}) MERGE (c)-[:PERTENCE_A]->(g);
MATCH (c:Cliente {id:'CLI010'}), (g:GrupoEconomico {id:'GRP002'}) MERGE (c)-[:PERTENCE_A]->(g);

// --- Região e cultura -------------------------------------------------

MATCH (c:Cliente {id:'CLI001'}), (r:Regiao {id:'REG-GO-SUD'}) MERGE (c)-[:OPERA_EM {hectares:4200}]->(r);
MATCH (c:Cliente {id:'CLI002'}), (r:Regiao {id:'REG-GO-SUD'}) MERGE (c)-[:OPERA_EM {hectares:1100}]->(r);
MATCH (c:Cliente {id:'CLI004'}), (r:Regiao {id:'REG-GO-SUD'}) MERGE (c)-[:OPERA_EM {hectares:380}]->(r);
MATCH (c:Cliente {id:'CLI007'}), (r:Regiao {id:'REG-GO-SUD'}) MERGE (c)-[:OPERA_EM {hectares:0}]->(r);
MATCH (c:Cliente {id:'CLI003'}), (r:Regiao {id:'REG-MT-MED'}) MERGE (c)-[:OPERA_EM {hectares:6800}]->(r);
MATCH (c:Cliente {id:'CLI005'}), (r:Regiao {id:'REG-MT-MED'}) MERGE (c)-[:OPERA_EM {hectares:5200}]->(r);
MATCH (c:Cliente {id:'CLI009'}), (r:Regiao {id:'REG-MT-MED'}) MERGE (c)-[:OPERA_EM {hectares:900}]->(r);
MATCH (c:Cliente {id:'CLI006'}), (r:Regiao {id:'REG-BA-OES'}) MERGE (c)-[:OPERA_EM {hectares:2400}]->(r);
MATCH (c:Cliente {id:'CLI010'}), (r:Regiao {id:'REG-BA-OES'}) MERGE (c)-[:OPERA_EM {hectares:450}]->(r);
MATCH (c:Cliente {id:'CLI008'}), (r:Regiao {id:'REG-MS-SUL'}) MERGE (c)-[:OPERA_EM {hectares:3100}]->(r);

MATCH (c:Cliente {id:'CLI001'}), (k:Cultura {id:'CUL-SOJA'})    MERGE (c)-[:PLANTA {hectares:4200}]->(k);
MATCH (c:Cliente {id:'CLI002'}), (k:Cultura {id:'CUL-SOJA'})    MERGE (c)-[:PLANTA {hectares:1100}]->(k);
MATCH (c:Cliente {id:'CLI004'}), (k:Cultura {id:'CUL-SOJA'})    MERGE (c)-[:PLANTA {hectares:380}]->(k);
MATCH (c:Cliente {id:'CLI003'}), (k:Cultura {id:'CUL-ALGODAO'}) MERGE (c)-[:PLANTA {hectares:6800}]->(k);
MATCH (c:Cliente {id:'CLI005'}), (k:Cultura {id:'CUL-MILHO'})   MERGE (c)-[:PLANTA {hectares:5200}]->(k);
MATCH (c:Cliente {id:'CLI009'}), (k:Cultura {id:'CUL-SOJA'})    MERGE (c)-[:PLANTA {hectares:900}]->(k);
MATCH (c:Cliente {id:'CLI006'}), (k:Cultura {id:'CUL-ALGODAO'}) MERGE (c)-[:PLANTA {hectares:2400}]->(k);
MATCH (c:Cliente {id:'CLI010'}), (k:Cultura {id:'CUL-SOJA'})    MERGE (c)-[:PLANTA {hectares:450}]->(k);
MATCH (c:Cliente {id:'CLI008'}), (k:Cultura {id:'CUL-MILHO'})   MERGE (c)-[:PLANTA {hectares:3100}]->(k);

// --- Canal de venda (revenda) ----------------------------------------

MATCH (a:Cliente {id:'CLI004'}), (b:Cliente {id:'CLI007'}) MERGE (a)-[:COMPRA_VIA {volume_safra:180000.0}]->(b);
MATCH (a:Cliente {id:'CLI002'}), (b:Cliente {id:'CLI007'}) MERGE (a)-[:COMPRA_VIA {volume_safra:420000.0}]->(b);

// --- Imóveis (fonte: SICAR) ------------------------------------------

MERGE (i:Imovel {id:'CAR-GO-0001'}) SET i.area_ha=4200, i.embargo_ibama=false, i.reserva_legal_ok=true;
MERGE (i:Imovel {id:'CAR-GO-0002'}) SET i.area_ha=380,  i.embargo_ibama=true,  i.reserva_legal_ok=false;
MERGE (i:Imovel {id:'CAR-MT-0003'}) SET i.area_ha=6800, i.embargo_ibama=false, i.reserva_legal_ok=true;
MATCH (c:Cliente {id:'CLI001'}), (i:Imovel {id:'CAR-GO-0001'}) MERGE (c)-[:POSSUI]->(i);
MATCH (c:Cliente {id:'CLI004'}), (i:Imovel {id:'CAR-GO-0002'}) MERGE (c)-[:POSSUI]->(i);
MATCH (c:Cliente {id:'CLI003'}), (i:Imovel {id:'CAR-MT-0003'}) MERGE (c)-[:POSSUI]->(i);
MATCH (i:Imovel {id:'CAR-GO-0001'}), (r:Regiao {id:'REG-GO-SUD'}) MERGE (i)-[:LOCALIZADO_EM]->(r);
MATCH (i:Imovel {id:'CAR-GO-0002'}), (r:Regiao {id:'REG-GO-SUD'}) MERGE (i)-[:LOCALIZADO_EM]->(r);
MATCH (i:Imovel {id:'CAR-MT-0003'}), (r:Regiao {id:'REG-MT-MED'}) MERGE (i)-[:LOCALIZADO_EM]->(r);

// --- Recebíveis -------------------------------------------------------

MERGE (r:Recebivel {id:'REC001'}) SET r.valor=890000.0, r.valor_aberto=890000.0,
  r.data_emissao=date('2025-10-15'), r.data_vencimento=date('2026-06-05'), r.dias_atraso=98,
  r.status='vencido', r.garantia_tipo='penhor_safra', r.garantia_valor=600000.0, r.estagio_juridico='habilitado_rj';
MERGE (r:Recebivel {id:'REC002'}) SET r.valor=310000.0, r.valor_aberto=310000.0,
  r.data_emissao=date('2025-11-02'), r.data_vencimento=date('2026-07-10'), r.dias_atraso=63,
  r.status='vencido', r.garantia_tipo='aval', r.garantia_valor=310000.0, r.estagio_juridico='notificado';
MERGE (r:Recebivel {id:'REC003'}) SET r.valor=145000.0, r.valor_aberto=0.0,
  r.data_emissao=date('2025-09-20'), r.data_vencimento=date('2026-05-20'), r.dias_atraso=0,
  r.status='recuperado', r.garantia_tipo='cpr', r.garantia_valor=145000.0, r.estagio_juridico='nenhum';
MERGE (r:Recebivel {id:'REC004'}) SET r.valor=520000.0, r.valor_aberto=520000.0,
  r.data_emissao=date('2026-01-12'), r.data_vencimento=date('2026-09-30'), r.dias_atraso=0,
  r.status='aberto', r.garantia_tipo='aval', r.garantia_valor=520000.0, r.estagio_juridico='nenhum';
MERGE (r:Recebivel {id:'REC005'}) SET r.valor=98000.0, r.valor_aberto=98000.0,
  r.data_emissao=date('2026-02-03'), r.data_vencimento=date('2026-10-15'), r.dias_atraso=0,
  r.status='aberto', r.garantia_tipo='nenhuma', r.garantia_valor=0.0, r.estagio_juridico='nenhum';
MERGE (r:Recebivel {id:'REC006'}) SET r.valor=760000.0, r.valor_aberto=760000.0,
  r.data_emissao=date('2025-08-11'), r.data_vencimento=date('2026-04-22'), r.dias_atraso=142,
  r.status='vencido', r.garantia_tipo='penhor_safra', r.garantia_valor=400000.0, r.estagio_juridico='protestado';
MERGE (r:Recebivel {id:'REC007'}) SET r.valor=230000.0, r.valor_aberto=230000.0,
  r.data_emissao=date('2026-01-25'), r.data_vencimento=date('2026-08-30'), r.dias_atraso=21,
  r.status='vencido', r.garantia_tipo='cpr', r.garantia_valor=230000.0, r.estagio_juridico='nenhum';
MERGE (r:Recebivel {id:'REC008'}) SET r.valor=410000.0, r.valor_aberto=410000.0,
  r.data_emissao=date('2026-02-18'), r.data_vencimento=date('2026-11-05'), r.dias_atraso=0,
  r.status='aberto', r.garantia_tipo='alienacao_fiduciaria', r.garantia_valor=410000.0, r.estagio_juridico='nenhum';
MERGE (r:Recebivel {id:'REC009'}) SET r.valor=175000.0, r.valor_aberto=175000.0,
  r.data_emissao=date('2026-03-07'), r.data_vencimento=date('2026-10-20'), r.dias_atraso=0,
  r.status='aberto', r.garantia_tipo='aval', r.garantia_valor=175000.0, r.estagio_juridico='nenhum';
MERGE (r:Recebivel {id:'REC010'}) SET r.valor=64000.0, r.valor_aberto=64000.0,
  r.data_emissao=date('2026-04-02'), r.data_vencimento=date('2026-12-01'), r.dias_atraso=0,
  r.status='aberto', r.garantia_tipo='nenhuma', r.garantia_valor=0.0, r.estagio_juridico='nenhum';

MATCH (r:Recebivel {id:'REC001'}), (c:Cliente {id:'CLI001'}) MERGE (r)-[:DE]->(c);
MATCH (r:Recebivel {id:'REC002'}), (c:Cliente {id:'CLI001'}) MERGE (r)-[:DE]->(c);
MATCH (r:Recebivel {id:'REC003'}), (c:Cliente {id:'CLI002'}) MERGE (r)-[:DE]->(c);
MATCH (r:Recebivel {id:'REC004'}), (c:Cliente {id:'CLI002'}) MERGE (r)-[:DE]->(c);
MATCH (r:Recebivel {id:'REC005'}), (c:Cliente {id:'CLI004'}) MERGE (r)-[:DE]->(c);
MATCH (r:Recebivel {id:'REC006'}), (c:Cliente {id:'CLI008'}) MERGE (r)-[:DE]->(c);
MATCH (r:Recebivel {id:'REC007'}), (c:Cliente {id:'CLI003'}) MERGE (r)-[:DE]->(c);
MATCH (r:Recebivel {id:'REC008'}), (c:Cliente {id:'CLI005'}) MERGE (r)-[:DE]->(c);
MATCH (r:Recebivel {id:'REC009'}), (c:Cliente {id:'CLI009'}) MERGE (r)-[:DE]->(c);
MATCH (r:Recebivel {id:'REC010'}), (c:Cliente {id:'CLI010'}) MERGE (r)-[:DE]->(c);

// Avais — AVA001 é o vetor que liga CLI001 (em RJ) a CLI003
MATCH (r:Recebivel {id:'REC002'}), (a:Avalista {id:'AVA001'}) MERGE (r)-[:GARANTIDO_POR]->(a);
MATCH (r:Recebivel {id:'REC007'}), (a:Avalista {id:'AVA001'}) MERGE (r)-[:GARANTIDO_POR]->(a);
MATCH (r:Recebivel {id:'REC004'}), (a:Avalista {id:'AVA002'}) MERGE (r)-[:GARANTIDO_POR]->(a);
MATCH (r:Recebivel {id:'REC009'}), (a:Avalista {id:'AVA003'}) MERGE (r)-[:GARANTIDO_POR]->(a);

MATCH (r:Recebivel), (s:Safra {id:'SAF-2526'}) WHERE r.id IN ['REC004','REC005','REC007','REC008','REC009','REC010']
  MERGE (r)-[:REFERENTE_A]->(s);
MATCH (r:Recebivel), (s:Safra {id:'SAF-2425'}) WHERE r.id IN ['REC001','REC002','REC003','REC006']
  MERGE (r)-[:REFERENTE_A]->(s);

// --- Eventos (o radar) ------------------------------------------------
// Fontes: DataJud/DJE, PGFN, IBAMA, INMET/Conab

MERGE (e:Evento {id:'EVT001'}) SET e.tipo='pedido_rj', e.data=date('2026-09-10'),
  e.fonte='DJE-GO', e.severidade=1.0, e.descricao='Distribuição de pedido de Recuperação Judicial';
MERGE (e:Evento {id:'EVT002'}) SET e.tipo='protesto', e.data=date('2026-07-28'),
  e.fonte='Cartório 2º Ofício', e.severidade=0.7, e.descricao='Protesto de duplicata';
MERGE (e:Evento {id:'EVT003'}) SET e.tipo='execucao_fiscal', e.data=date('2026-06-15'),
  e.fonte='PGFN', e.severidade=0.6, e.descricao='Inscrição em dívida ativa da União';
MERGE (e:Evento {id:'EVT004'}) SET e.tipo='embargo_ambiental', e.data=date('2026-05-02'),
  e.fonte='IBAMA', e.severidade=0.55, e.descricao='Embargo por desmatamento em área consolidada';
MERGE (e:Evento {id:'EVT005'}) SET e.tipo='quebra_safra', e.data=date('2026-03-18'),
  e.fonte='Conab/INMET', e.severidade=0.5, e.descricao='Perda estimada de 22% por estiagem prolongada';
MERGE (e:Evento {id:'EVT006'}) SET e.tipo='alteracao_qsa', e.data=date('2026-08-05'),
  e.fonte='Receita Federal', e.severidade=0.4, e.descricao='Saída de sócio majoritário do quadro societário';

MATCH (e:Evento {id:'EVT001'}), (c:Cliente {id:'CLI001'}) MERGE (e)-[:SOBRE]->(c);
MATCH (e:Evento {id:'EVT002'}), (c:Cliente {id:'CLI008'}) MERGE (e)-[:SOBRE]->(c);
MATCH (e:Evento {id:'EVT003'}), (c:Cliente {id:'CLI008'}) MERGE (e)-[:SOBRE]->(c);
MATCH (e:Evento {id:'EVT004'}), (c:Cliente {id:'CLI004'}) MERGE (e)-[:SOBRE]->(c);
MATCH (e:Evento {id:'EVT005'}), (c:Cliente {id:'CLI003'}) MERGE (e)-[:SOBRE]->(c);
MATCH (e:Evento {id:'EVT006'}), (c:Cliente {id:'CLI001'}) MERGE (e)-[:SOBRE]->(c);

// --- Exposição total materializada -----------------------------------

MATCH (c:Cliente)
OPTIONAL MATCH (r:Recebivel)-[:DE]->(c) WHERE r.status IN ['aberto','vencido','em_acordo']
WITH c, coalesce(sum(r.valor_aberto), 0.0) AS exp
SET c.exposicao_total = exp;
