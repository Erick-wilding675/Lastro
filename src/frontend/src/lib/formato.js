const moeda = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
const inteiro = new Intl.NumberFormat("pt-BR");
export function formatarReais(valor) { return valor == null ? "—" : moeda.format(valor); }
export function formatarNumero(valor) { return valor == null ? "—" : inteiro.format(valor); }
export function formatarPercentual(valor) { return valor == null ? "—" : `${Number(valor).toFixed(1).replace('.', ',')}%`; }
