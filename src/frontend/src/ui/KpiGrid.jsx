import { formatarPercentual, formatarReais, formatarNumero } from '../lib/formato';
const cards=[
  ['exposicao_total_rs','Exposição total','reais'],
  ['vencido_rs','Vencido','reais'],
  ['pct_carteira_vencida','% carteira vencida','percentual'],
  ['exposicao_risco_critico_rs','Exposição em risco crítico','reais',true],
];
export default function KpiGrid({kpis}){return <div className="kpi-grid">{cards.map(([key,label,fmt,highlight])=>{const v=kpis?.[key];const txt=fmt==='reais'?formatarReais(v):fmt==='percentual'?formatarPercentual(v):formatarNumero(v);return <div key={key} className={`kpi ${highlight?'highlight':''}`}><div className="kpi-label">{label}</div><div className="kpi-value">{txt}</div><div className="kpi-meta">{key}</div></div>})}</div>}
