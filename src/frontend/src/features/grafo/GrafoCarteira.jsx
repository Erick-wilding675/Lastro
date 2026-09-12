import { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { api } from '../../lib/api';
import { corPorRating, temas } from '../../lib/tokens';

function raio(n){ return Math.max(5, Math.min(22, 5 + Math.sqrt((n.exposicao||0)/10000))); }

export default function GrafoCarteira({onSelecionar,tema}){
  const t = temas[tema];
  const [dados,setDados]=useState({nodes:[],links:[]}); const [propagando,setPropagando]=useState(false); const [origem,setOrigem]=useState(null); const ref=useRef();
  const carregar=()=>api.grafo().then(d=>setDados({nodes:d.nodes??[],links:(d.links??[]).map(l=>({...l}))}));
  useEffect(()=>{carregar()},[]);
  useEffect(()=>{const id=setTimeout(()=>ref.current?.zoomToFit?.(500,80),250);return()=>clearTimeout(id)},[dados]);
  const click=async n=>{setOrigem(n.id);setPropagando(true);try{await api.propagar(n.id);await carregar();}finally{setPropagando(false)}onSelecionar?.(n.id)};
  return <div className="graph-shell">
    <div className="graph-grid"/>
    <div className="graph-toolbar"><div className="graph-legend"><span className="legend-chip"><i className="legend-dot" style={{background:'var(--success)'}}/>A / baixo risco</span><span className="legend-chip"><i className="legend-dot" style={{background:'var(--alert)'}}/>C / atenção</span><span className="legend-chip"><i className="legend-dot" style={{background:'var(--danger)'}}/>D / crítico</span><span className="legend-chip"><i className="legend-dot" style={{background:'var(--accent)'}}/>IA / contágio</span></div></div>
    {propagando&&<div className="graph-banner">Propagando risco de <strong>{origem}</strong> pela rede…</div>}
    {dados.nodes.length===0&&<div className="graph-empty">Nenhum nó retornado pelo backend.</div>}
    <ForceGraph2D ref={ref} width={undefined} height={undefined} graphData={dados} backgroundColor="transparent" enablePanInteraction enableZoomInteraction nodeLabel={n=>`${n.nome} — ${n.id} · rating ${n.rating??'?'}`} nodeVal={raio} nodeColor={n=>corPorRating(n.rating,tema)} linkColor={l=>l.caminho?.length?t.acento:`${t.textoSecundario}73`} linkWidth={l=>l.caminho?.length?Math.max(2,(l.peso||.5)*4):1} linkLineDash={l=>l.caminho?.length?[]:[5,6]} linkDirectionalParticles={l=>l.caminho?.length?2:0} linkDirectionalParticleWidth={2} onNodeClick={click} nodeCanvasObject={(node,ctx,globalScale)=>{const r=raio(node);const c=corPorRating(node.rating,tema);ctx.beginPath();ctx.arc(node.x,node.y,r,0,2*Math.PI,false);ctx.fillStyle=c;ctx.shadowColor=c;ctx.shadowBlur=node.rating==='D'?16:8;ctx.fill();ctx.shadowBlur=0;if(node.rating==='D'){ctx.lineWidth=2;ctx.strokeStyle=c;ctx.stroke()}if(globalScale>1.55){const fs=Math.max(8,12/globalScale);ctx.font=`600 ${fs}px IBM Plex Sans`;ctx.textAlign='center';ctx.textBaseline='top';ctx.fillStyle=t.textoPrimario;ctx.fillText(node.id,node.x,node.y+r+4)}}}/>
  </div>
}
