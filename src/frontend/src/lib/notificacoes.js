// Notificações e mapa de propagação — derivados do motor, com reserva sintética.
//
// Estas duas telas eram as únicas que nunca falavam com o backend: o sino
// piscava uma lista fixa e a tela /evento/:id desenhava um mapa escrito à mão.
// Agora ambas leem o resultado real de POST /motor/ciclo, que devolve, para
// cada origem, os vizinhos que acenderam e por qual vínculo.
//
// As constantes abaixo continuam existindo como RESERVA: se a API não
// responder, a cena da demo (CLI001 pede RJ e acende 4 vizinhos) continua de
// pé. Os pesos aqui espelham os do motor — se mudar lá, mude aqui.
import { api } from './api';

export const filaNotificacoesReserva = [
  { tipo:'critico',  cliente:'CLI001', titulo:'CLI001 · Pedido de Recuperação Judicial', via:'DJE · stay period ativo' },
  { tipo:'contagio', cliente:'CLI002', origem:'CLI001', titulo:'CLI002 acendeu na rede', via:'Sócio em comum · QSA',        peso:.80 },
  { tipo:'contagio', cliente:'CLI003', origem:'CLI001', titulo:'CLI003 acendeu na rede', via:'Avalista em comum',           peso:.85 },
  { tipo:'contagio', cliente:'CLI005', origem:'CLI001', titulo:'CLI005 acendeu na rede', via:'Mesmo grupo econômico',       peso:.90 },
  { tipo:'contagio', cliente:'CLI004', origem:'CLI001', titulo:'CLI004 acendeu na rede', via:'Mesma região e cultura',      peso:.45 },
];

export const propagacaoPorEventoReserva = {
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

/** Um exposto do motor vira uma linha de tela. `caminhos` é a lista de vias
 *  que ligam origem e vizinho; a primeira é a de maior peso. */
const paraAceso = (e) => ({
  id: e.cliente,
  nome: e.nome,
  via: e.caminhos?.[0] ?? e.canais?.join(' · ') ?? 'vínculo na rede',
  peso: Number(e.risco_exposicao ?? 0),
});

const porPesoDesc = (a, b) => b.peso - a.peso;

/** Constrói o mapa de propagação de um gatilho a partir do motor real. */
export async function carregarPropagacao(origemId) {
  const reserva = propagacaoPorEventoReserva[origemId] ?? propagacaoPorEventoReserva.CLI001;
  try {
    const ciclo = await api.ciclo(origemId);
    const prop = ciclo.propagacoes?.find(p => p.origem === origemId) ?? ciclo.propagacoes?.[0];
    if (!prop?.expostos?.length) return reserva;

    const acesos = prop.expostos.map(paraAceso).sort(porPesoDesc);
    const [grafo, radar] = await Promise.all([api.grafo(), api.radar(90)]);
    const nos = grafo.nodes ?? [];
    const no = nos.find(n => n.id === prop.origem);
    const evento = (radar.eventos ?? []).find(e => e.cliente === prop.origem);

    // O controle não é decorativo: é a prova de que o motor não pinta a
    // carteira inteira de vermelho. Escolhe quem NÃO acendeu e está melhor —
    // mas só entre produtores. A revenda tem score alto por não ter recebível
    // nenhum, e "olha, o canal de distribuição continua verde" não responde
    // nada: o contraste que vale é com um produtor comparável ao gatilho.
    const acesosIds = new Set([prop.origem, ...acesos.map(a => a.id)]);
    const naoAcesos = nos.filter(n => !acesosIds.has(n.id));
    const porScore = (a, b) => (b.score ?? 0) - (a.score ?? 0);
    const produtores = naoAcesos.filter(n => String(n.tipo ?? '').startsWith('produtor'));
    const controle = (produtores.length ? produtores : naoAcesos).sort(porScore)[0];

    return {
      gatilho: {
        id: prop.origem,
        nome: prop.nome ?? no?.nome ?? prop.origem,
        evento: evento?.descricao ?? 'deterioração detectada na carteira',
      },
      acesos,
      controle: controle ? { id: controle.id, nome: controle.nome } : null,
    };
  } catch {
    return reserva;
  }
}

/** Constrói a fila do sino a partir do que o motor acabou de propagar. */
export async function carregarNotificacoes() {
  try {
    const ciclo = await api.ciclo();
    const propagacoes = ciclo.propagacoes ?? [];
    if (!propagacoes.length) return filaNotificacoesReserva;

    const radar = await api.radar(90);
    const eventos = radar.eventos ?? [];
    const fila = [];

    for (const prop of propagacoes) {
      const evento = eventos.find(e => e.cliente === prop.origem);
      fila.push({
        tipo: 'critico',
        cliente: prop.origem,
        titulo: `${prop.origem} · ${evento?.descricao ?? 'deterioração detectada'}`,
        via: evento ? `${evento.fonte} · ${evento.tipo.replaceAll('_', ' ')}` : 'carteira interna',
      });
      for (const aceso of prop.expostos.map(paraAceso).sort(porPesoDesc)) {
        fila.push({
          tipo: 'contagio',
          cliente: aceso.id,
          origem: prop.origem,
          titulo: `${aceso.id} acendeu na rede`,
          via: aceso.via,
          peso: aceso.peso,
        });
      }
    }
    return fila;
  } catch {
    return filaNotificacoesReserva;
  }
}
