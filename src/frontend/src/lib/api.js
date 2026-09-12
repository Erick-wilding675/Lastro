import { USE_DEMO, demoDossies, demoEventos, demoFila, demoKpis, demoLinks, demoNodes } from './demoData';
const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
async function req(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) throw new Error(`${res.status} em ${path}`);
  return res.json();
}
const wait = (v) => new Promise(r => setTimeout(() => r(v), 180));
export const api = {
  kpis: async () => USE_DEMO ? wait(demoKpis) : req('/carteira/kpis'),
  grafo: async () => USE_DEMO ? wait({nodes:demoNodes,links:demoLinks}) : req('/carteira/grafo'),
  cliente: async (id) => USE_DEMO ? wait(demoDossies[id] ?? demoDossies.CLI001) : req(`/carteira/cliente/${id}`),
  propagar: async (origem) => USE_DEMO ? wait({origem,ok:true}) : req(`/contagio/propagar/${origem}`, {method:'POST'}),
  recalcularScore: () => req('/scoring/recalcular', {method:'POST'}),
  redFlags: () => req('/scoring/red-flags'),
  recomendar: (cliente) => USE_DEMO ? wait(demoDossies[cliente]) : req(`/recuperacao/recomendar/${cliente}`, {method:'POST'}),
  priorizar: async () => USE_DEMO ? wait({fila:demoFila}) : req('/recuperacao/priorizar?capacidade=5'),
  executar: async (cliente) => USE_DEMO ? wait({ok:true,cliente}) : req(`/recuperacao/executar/${cliente}`, {method:'POST'}),
  radar: async () => USE_DEMO ? wait({eventos:demoEventos}) : req('/eventos/radar?dias=90'),
  dossie: async (cliente) => USE_DEMO ? wait(demoDossies[cliente] ?? demoDossies.CLI001) : req(`/agentes/dossie/${cliente}`),
};
