// Dados da demo do sistema de notificações.
// Cada item da fila representa um NOVO relacionamento de contágio detectado
// a partir do evento-gatilho (CLI001 pede Recuperação Judicial).
export const filaNotificacoes = [
  { tipo:'critico',  cliente:'CLI001', titulo:'CLI001 · Pedido de Recuperação Judicial', via:'DJE · stay period ativo' },
  { tipo:'contagio', cliente:'CLI002', origem:'CLI001', titulo:'CLI002 acendeu na rede', via:'Sócio em comum · QSA',        peso:.80 },
  { tipo:'contagio', cliente:'CLI003', origem:'CLI001', titulo:'CLI003 acendeu na rede', via:'Avalista em comum',           peso:.85 },
  { tipo:'contagio', cliente:'CLI005', origem:'CLI001', titulo:'CLI005 acendeu na rede', via:'Mesmo grupo econômico',       peso:.90 },
  { tipo:'contagio', cliente:'CLI004', origem:'CLI001', titulo:'CLI004 acendeu na rede', via:'Mesma região e cultura',      peso:.45 },
];

// Descreve o mapa de propagação de cada evento-gatilho, usado pela tela /evento/:id
export const propagacaoPorEvento = {
  CLI001: {
    gatilho: { id:'CLI001', nome:'Agro Vale do Cerrado Ltda', evento:'Pedido de Recuperação Judicial' },
    acesos: [
      { id:'CLI005', nome:'Terra Nova Agronegócios Ltda', via:'Mesmo grupo econômico',  peso:.90 },
      { id:'CLI003', nome:'Agropecuária Horizonte S/A',   via:'Avalista em comum',      peso:.85 },
      { id:'CLI002', nome:'Fazenda Santa Luzia',          via:'Sócio em comum · QSA',   peso:.80 },
      { id:'CLI004', nome:'Sítio Boa Esperança',          via:'Mesma região e cultura', peso:.45 },
    ],
    controle: { id:'CLI006', nome:'Fazenda Ipê Amarelo' },
  },
};
