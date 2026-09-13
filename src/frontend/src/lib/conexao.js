// Estado da ligação com o backend, compartilhado por toda a interface.
//
// Existe porque a tela precisa dizer a verdade sobre a própria origem do dado.
// O pill "Motor conectado" do topo era fixo no HTML: dizia "conectado" mesmo
// com a API fora do ar. Num pitch isso é pior do que não ter indicador nenhum.
//
// MODOS
//   verificando — primeira chamada ainda não voltou
//   api         — dado vindo do backend
//   demo        — a API não respondeu e a tela caiu no dado sintético
//   demo-fixo   — VITE_DEMO_MODE=true, escolha explícita de quem subiu a app

let estado = { modo: 'verificando', detalhe: '' };
const ouvintes = new Set();

export function obterConexao() { return estado; }

export function assinarConexao(fn) {
  ouvintes.add(fn);
  fn(estado);
  return () => ouvintes.delete(fn);
}

export function definirConexao(modo, detalhe = '') {
  if (estado.modo === modo && estado.detalhe === detalhe) return;
  estado = { modo, detalhe };
  ouvintes.forEach(fn => fn(estado));
}

export const ROTULO_CONEXAO = {
  verificando: { texto: 'Conectando ao motor…', cor: 'var(--muted)' },
  api:         { texto: 'Motor conectado',      cor: 'var(--success)' },
  demo:        { texto: 'Modo demonstração',    cor: 'var(--alert)' },
  'demo-fixo': { texto: 'Demonstração (fixa)',  cor: 'var(--accent)' },
};
