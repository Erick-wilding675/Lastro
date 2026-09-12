const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function req(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) throw new Error(`${res.status} em ${path}`);
  return res.json();
}

export const api = {
  kpis: () => req("/carteira/kpis"),
  grafo: () => req("/carteira/grafo"),
  cliente: (id) => req(`/carteira/cliente/${id}`),
  propagar: (origem) => req(`/contagio/propagar/${origem}`, { method: "POST" }),
  recalcularScore: () => req("/scoring/recalcular", { method: "POST" }),
  redFlags: () => req("/scoring/red-flags"),
  recomendar: (cliente) => req(`/recuperacao/recomendar/${cliente}`, { method: "POST" }),
  priorizar: (capacidade = 5) => req(`/recuperacao/priorizar?capacidade=${capacidade}`),
  radar: (dias = 90) => req(`/eventos/radar?dias=${dias}`),
  dossie: (cliente) => req(`/agentes/dossie/${cliente}`),
};
