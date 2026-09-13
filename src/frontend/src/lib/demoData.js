export const demoKpis = {
  clientes: 10,
  exposicao_total_rs: 2400000,
  vencido_rs: 480000,
  recuperado_rs: 920000,
  pct_carteira_vencida: 20,
  clientes_rating_D: 2,
  exposicao_risco_critico_rs: 480000,
};

export const demoNodes = [
  { id:'CLI001', nome:'Agro Vale do Cerrado Ltda', rating:'D', score:210, exposicao:320000 },
  { id:'CLI002', nome:'Fazenda Santa Luzia', rating:'B', score:680, exposicao:190000 },
  { id:'CLI003', nome:'Agropecuária Horizonte S/A', rating:'C', score:490, exposicao:360000 },
  { id:'CLI004', nome:'Sítio Boa Esperança', rating:'B', score:720, exposicao:85000 },
  { id:'CLI005', nome:'Terra Nova Agronegócios Ltda', rating:'B', score:640, exposicao:410000 },
  { id:'CLI006', nome:'Fazenda Ipê Amarelo', rating:'A', score:910, exposicao:150000 },
  { id:'CLI007', nome:'Cerrado Insumos Distribuidora', rating:'B', score:760, exposicao:210000 },
  { id:'CLI008', nome:'Agroindústria Rio Claro S/A', rating:'D', score:300, exposicao:250000 },
  { id:'CLI009', nome:'Fazenda Três Irmãos', rating:'C', score:530, exposicao:180000 },
  { id:'CLI010', nome:'Sementes Planalto Ltda', rating:'A', score:840, exposicao:70000 },
];

export const demoLinks = [
  {source:'CLI001',target:'CLI002',peso:.80,caminho:['CLI001','QSA','João Batista Moreira','CLI002']},
  {source:'CLI001',target:'CLI003',peso:.85,caminho:['CLI001','Avalista','Marcos Ferreira Duarte','CLI003']},
  {source:'CLI003',target:'CLI005',peso:.90,caminho:['CLI003','Grupo Terra Nova','CLI005']},
  {source:'CLI001',target:'CLI004',peso:.45,caminho:['CLI001','Sudoeste Goiano','Soja','CLI004']},
  {source:'CLI007',target:'CLI001',peso:.32},
  {source:'CLI003',target:'CLI009',peso:.36},
  {source:'CLI006',target:'CLI010',peso:.18},
  {source:'CLI008',target:'CLI009',peso:.42},
];

export const demoDossies = {
  CLI001: {
    cliente:{nome:'Agro Vale do Cerrado Ltda',score:210,rating:'D',situacao:'recuperacao_judicial'},
    contagio:[{de:'Origem do evento',peso:1,caminho:['Pedido de Recuperação Judicial','stay period ativo']}],
    recomendacoes:[{estrategia:'Habilitação no plano de RJ',recuperavel:72000,prazo:900},{estrategia:'Mapeamento de garantias',recuperavel:165000,prazo:30}],
  },
  CLI002: {
    cliente:{nome:'Fazenda Santa Luzia',score:680,rating:'B',situacao:'adimplente'},
    contagio:[{de:'CLI001 · Agro Vale do Cerrado',peso:.80,caminho:['sócio em comum','QSA','João Batista Moreira']}],
    recomendacoes:[{estrategia:'Renegociação preventiva',recuperavel:118000,prazo:45},{estrategia:'Cobrança amigável',recuperavel:91000,prazo:20}],
  },
  CLI003: {
    cliente:{nome:'Agropecuária Horizonte S/A',score:490,rating:'C',situacao:'atraso'},
    contagio:[{de:'CLI001 · Agro Vale do Cerrado',peso:.85,caminho:['avalista em comum','Marcos Ferreira Duarte']}],
    recomendacoes:[{estrategia:'Acordo parcelado',recuperavel:176000,prazo:90},{estrategia:'Renegociação',recuperavel:205000,prazo:45}],
  },
  CLI005: {
    cliente:{nome:'Terra Nova Agronegócios Ltda',score:640,rating:'B',situacao:'adimplente'},
    contagio:[{de:'CLI003 · Agropecuária Horizonte',peso:.90,caminho:['mesmo grupo econômico','Grupo Terra Nova']}],
    recomendacoes:[{estrategia:'Renegociação preventiva',recuperavel:172000,prazo:45}],
  },
  CLI004: {
    cliente:{nome:'Sítio Boa Esperança',score:720,rating:'B',situacao:'adimplente'},
    contagio:[{de:'CLI001 · Agro Vale do Cerrado',peso:.45,caminho:['mesma região','Soja','embargo ambiental no imóvel']}],
    recomendacoes:[{estrategia:'Monitoramento + contato',recuperavel:48000,prazo:20}],
  },
  CLI006: {
    cliente:{nome:'Fazenda Ipê Amarelo',score:910,rating:'A',situacao:'adimplente'},
    contagio:[],
    recomendacoes:[{estrategia:'Nenhuma ação',recuperavel:0,prazo:0}],
  },
};

export const demoEventos = [
  {evento_id:'EVT-001',cliente_nome:'Agro Vale do Cerrado Ltda',cliente:'CLI001',descricao:'Pedido de Recuperação Judicial',data:'12/09/2026'},
  {evento_id:'EVT-002',cliente_nome:'Agropecuária Horizonte S/A',cliente:'CLI003',descricao:'Atraso ultrapassou 30 dias',data:'03/09/2026'},
  {evento_id:'EVT-003',cliente_nome:'Sítio Boa Esperança',cliente:'CLI004',descricao:'Embargo ambiental identificado',data:'27/08/2026'},
  {evento_id:'EVT-004',cliente_nome:'Terra Nova Agronegócios Ltda',cliente:'CLI005',descricao:'Alteração societária recente',data:'15/08/2026'},
  {evento_id:'EVT-005',cliente_nome:'Agroindústria Rio Claro S/A',cliente:'CLI008',descricao:'Execução fiscal registrada',data:'02/08/2026'},
];

export const demoFila = [
  {cliente:'CLI003',nome:'Agropecuária Horizonte S/A',melhor:{estrategia:'Renegociação',recuperavel:205000,prazo:45}},
  {cliente:'CLI005',nome:'Terra Nova Agronegócios Ltda',melhor:{estrategia:'Renegociação preventiva',recuperavel:172000,prazo:45}},
  {cliente:'CLI002',nome:'Fazenda Santa Luzia',melhor:{estrategia:'Renegociação preventiva',recuperavel:118000,prazo:45}},
  {cliente:'CLI004',nome:'Sítio Boa Esperança',melhor:{estrategia:'Monitoramento + contato',recuperavel:48000,prazo:20}},
  {cliente:'CLI008',nome:'Agroindústria Rio Claro S/A',melhor:{estrategia:'Acordo parcelado',recuperavel:96000,prazo:90}},
];

// A decisão de usar (ou não) estes dados mora em `api.js` — aqui só o conteúdo.
// Servem como reserva quando o backend não responde, e como demo forçada
// com VITE_DEMO_MODE=true. O padrão é a API real.
