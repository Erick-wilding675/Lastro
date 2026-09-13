const moeda = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
const inteiro = new Intl.NumberFormat("pt-BR");
export function formatarReais(valor) { return valor == null ? "—" : moeda.format(valor); }
export function formatarNumero(valor) { return valor == null ? "—" : inteiro.format(valor); }
export function formatarPercentual(valor) { return valor == null ? "—" : `${Number(valor).toFixed(1).replace('.', ',')}%`; }

/** A API devolve data em ISO-8601 (2026-09-12); a tela mostra em pt-BR.
 *  A conversão fica aqui e não no backend de propósito: o mesmo endpoint serve
 *  o frontend e o watsonx Orchestrate, e locale é decisão de quem exibe. */
export function formatarData(valor) {
  if (!valor) return "—";
  const iso = String(valor).slice(0, 10);
  const [a, m, d] = iso.split("-");
  return a && m && d ? `${d}/${m}/${a}` : String(valor);
}
