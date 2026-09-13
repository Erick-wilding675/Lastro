// Cliente da API do Lastro.
//
// DUAS DECISÕES QUE VALE ENTENDER ANTES DE MEXER:
//
// 1. A API é a fonte padrão. Antes era o contrário — `VITE_DEMO_MODE !== 'false'`
//    fazia a demo ser o padrão, então quem clonava o repo e subia o backend
//    continuava vendo dado sintético e achava que tinha conectado. Agora só
//    `VITE_DEMO_MODE=true` força a demo; o resto usa o backend.
//
// 2. Se o backend não responder, a tela cai no dado sintético em vez de
//    quebrar — e AVISA, pelo estado de conexão (ver `conexao.js`). Rede de
//    hackathon cai; o pitch não pode cair junto. Mas cair sem avisar seria
//    mentir sobre a origem do número, e isso não.
import { definirConexao } from './conexao';
import { demoDossies, demoEventos, demoFila, demoKpis, demoLinks, demoNodes } from './demoData';

const BASE = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/+$/, '');
export const DEMO_FIXO = import.meta.env.VITE_DEMO_MODE === 'true';

async function req(caminho, opcoes = {}) {
  const res = await fetch(`${BASE}${caminho}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opcoes,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status} em ${caminho}`);
  return res.json();
}

/** Chama a API; se ela não responder, devolve a reserva sintética. */
async function comReserva(chamada, reserva) {
  if (DEMO_FIXO) return reserva;
  try {
    const dados = await chamada();
    definirConexao('api');
    return dados;
  } catch (erro) {
    definirConexao('demo', erro.message);
    return reserva;
  }
}

// --- ordem de execução do motor -------------------------------------------
// O score usa o contágio como componente e a fila usa a recomendação. Ler
// /carteira/grafo antes de /motor/ciclo devolve um grafo sem nenhuma aresta de
// contágio — não por erro, por ordem. Em vez de espalhar essa dependência pelos
// componentes, toda leitura espera o ciclo aqui, uma vez só por sessão.
let cicloEmCurso = null;

export function garantirCiclo(origem) {
  if (origem || !cicloEmCurso) {
    const caminho = origem ? `/motor/ciclo?origem=${encodeURIComponent(origem)}` : '/motor/ciclo';
    cicloEmCurso = comReserva(() => req(caminho, { method: 'POST' }), { propagacoes: [], reserva: true });
  }
  return cicloEmCurso;
}

const aposCiclo = async (chamada, reserva) => {
  await garantirCiclo();
  return comReserva(chamada, reserva);
};

export const api = {
  health: () =>
    fetch(`${BASE}/health`)
      .then(r => r.json().then(c => ({ ...c, http: r.status })))
      .catch(e => ({ status: 'sem_conexao', detalhe: e.message })),

  ciclo: (origem) => garantirCiclo(origem),

  kpis: () => aposCiclo(() => req('/carteira/kpis'), demoKpis),

  grafo: () => aposCiclo(() => req('/carteira/grafo'), { nodes: demoNodes, links: demoLinks }),

  cliente: (id) => aposCiclo(() => req(`/carteira/cliente/${id}`), demoDossies[id] ?? demoDossies.CLI001),

  // Propagar reinicia o ciclo: o clique no nó é o gatilho da cena da demo, e o
  // score de todo mundo muda junto com o contágio.
  propagar: (origem) => garantirCiclo(origem),

  recalcularScore: () => comReserva(() => req('/scoring/recalcular', { method: 'POST' }), { clientes: [] }),

  redFlags: () => aposCiclo(() => req('/scoring/red-flags'), { matriz: [] }),

  recomendar: (cliente) =>
    comReserva(() => req(`/recuperacao/recomendar/${cliente}`, { method: 'POST' }),
               { cliente, estrategias: demoDossies[cliente]?.recomendacoes ?? [] }),

  priorizar: (capacidade = 5) =>
    aposCiclo(() => req(`/recuperacao/priorizar?capacidade=${capacidade}`),
              { fila: demoFila.slice(0, capacidade) }),

  executar: (cliente, responsavel = 'operador') =>
    comReserva(() => req(`/recuperacao/executar/${cliente}?responsavel=${encodeURIComponent(responsavel)}`,
                         { method: 'POST' }),
               { cliente, executada_por: responsavel }),

  radar: (dias = 90) => aposCiclo(() => req(`/eventos/radar?dias=${dias}`), { eventos: demoEventos }),

  dossie: (cliente) =>
    aposCiclo(() => req(`/agentes/dossie/${cliente}`), demoDossies[cliente] ?? demoDossies.CLI001),

  contexto: (cliente) => aposCiclo(() => req(`/agentes/contexto/${cliente}`), {}),
};
