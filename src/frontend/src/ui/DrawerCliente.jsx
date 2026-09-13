import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { formatarReais } from '../lib/formato';
export default function DrawerCliente({clienteId,onClose}){
  const [dossie,setDossie]=useState(null);
  useEffect(()=>{let vivo=true;if(clienteId) api.dossie(clienteId).then(d=>vivo&&setDossie(d)); return()=>{vivo=false}},[clienteId]);
  if(!clienteId)return null;
  return <><div className="drawer-backdrop" onClick={onClose}/><aside className="drawer">
    <div className="drawer-head"><div><div className="eyebrow">Dossiê de risco</div><div className="drawer-title">{dossie?.cliente?.nome ?? 'Carregando…'}</div><div className="drawer-sub">{dossie?.cliente ? `${(dossie.cliente.situacao ?? 'situação não informada').replaceAll('_',' ')} · cliente estratégico` : 'Consultando motor de decisão'}</div></div><button className="icon-btn" onClick={onClose}>×</button></div>
    <div className="drawer-scroll">
      {dossie ? <>
        <div className="score-row"><div className="score"><strong>{dossie.cliente.score ?? '—'}</strong><span>/1000</span></div><div className="badge risk">Rating {dossie.cliente.rating ?? '—'}</div></div>
        <div className="section"><h3>Por que acendeu</h3><div className="reason-list">{(dossie.contagio??[]).filter(c=>c.de).map((c,i)=><div className="reason" key={i}><div className="reason-top"><span className="reason-dot"/> {c.de}</div><div className="reason-path">{(c.caminho??[]).join('  →  ')}</div><div className="rec-metrics"><span className="metric-chip">peso {Number(c.peso??0).toFixed(2)}</span></div></div>)}</div></div>
        <div className="section"><h3>Recomendação da IA</h3><div className="recommendation"><div className="rec-title"><strong>{dossie.recomendacoes?.[0]?.estrategia ?? 'Análise em andamento'}</strong><span className="badge ai">IA</span></div><div className="rec-body">A recomendação considera elegibilidade jurídica, retorno esperado, prazo e preservação da relação comercial.</div><div className="rec-metrics"><span className="metric-chip">{formatarReais(dossie.recomendacoes?.[0]?.recuperavel)}</span><span className="metric-chip">{dossie.recomendacoes?.[0]?.prazo ?? '—'} dias</span></div></div><button className="primary-btn">Abrir plano de recuperação</button></div>
        <div className="section"><h3>Princípio do Lastro</h3><div className="reason"><div className="reason-top">Caminho sempre visível</div><div className="reason-path">O risco não aparece sozinho: este painel conserva o vínculo que explica a priorização.</div></div></div>
      </> : <div className="graph-empty">Carregando dossiê…</div>}
    </div>
  </aside></>
}
