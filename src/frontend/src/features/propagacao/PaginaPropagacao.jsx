import { useEffect, useState } from 'react';
import { useParams, useOutletContext, useSearchParams, Link } from 'react-router-dom';
import { carregarPropagacao } from '../../lib/notificacoes';

const STEPS = ['Evento detectado', 'Contágio propagado', 'Risco recalculado', 'Recuperação priorizada'];
const vg = (p) => p.toFixed(2).replace('.', ',');

export default function PaginaPropagacao(){
  const { id } = useParams();
  const [sp] = useSearchParams();
  const ctx = useOutletContext() || {};

  // O mapa vem do motor: propaga a partir de `id` e desenha quem acendeu.
  // Antes esta tela era o único ponto do app com o grafo escrito à mão.
  const [dados, setDados] = useState(null);
  useEffect(() => {
    let vivo = true;
    carregarPropagacao(id).then(d => vivo && setDados(d));
    return () => { vivo = false; };
  }, [id]);

  if (!dados) return (
    <main className="page">
      <div className="graph-empty">Propagando risco de <strong>{id}</strong> pela rede…</div>
    </main>
  );

  const { gatilho, acesos, controle } = dados;

  const foco = sp.get('foco');
  const focoGatilho = !foco || foco === gatilho.id;   // sem foco, ou foco no próprio gatilho → mostra tudo
  const focoAceso = acesos.find(a => a.id === foco);

  const gx = 80, gy = 160, ax = 372;
  const posY = (i) => (acesos.length > 1 ? 42 + i * (236 / (acesos.length - 1)) : 160);

  return (
    <main className="page">
      <div className="page-head">
        <div>
          <div className="eyebrow">04 / Momento-chave</div>
          <h1 className="title">O evento muda o mapa</h1>
          <p className="subtitle">{gatilho.nome} — {gatilho.evento}. O Lastro não pinta a carteira inteira: acende apenas quem tem caminho de contágio até o evento.</p>
        </div>
        <div className="status-pill"><span className="status-dot" style={{ background:'var(--danger)' }}/> LIVE · propagação</div>
      </div>

      <section className="prop-stage">
        <div className="flow-steps">
          {STEPS.map((s, i) => (
            <div className="flow-step" key={s}>
              <span className="flow-num">{String(i + 1).padStart(2, '0')}</span>{s}
              {i < STEPS.length - 1 && <span className="flow-sep"/>}
            </div>
          ))}
        </div>

        <div className="prop-body">
          <svg viewBox="0 0 460 320" className="prop-graph">
            {acesos.map((a, i) => {
              const y = posY(i); const forte = a.peso >= .6;
              const destaque = a.id === foco; const apagado = !focoGatilho && !destaque;
              return <line key={'l' + i} x1={gx} y1={gy} x2={ax} y2={y}
                style={{ stroke: destaque ? '#fff' : 'var(--accent)', opacity: apagado ? .12 : (destaque ? 1 : (forte ? .9 : .5)) }}
                strokeWidth={Math.max(1.5, a.peso * 4) + (destaque ? 1 : 0)} strokeDasharray={forte ? '0' : '5 6'} />;
            })}
            <circle cx={gx} cy={gy} r="26" style={{ fill:'var(--danger)' }} />
            {focoGatilho && <circle cx={gx} cy={gy} r="30" fill="none" style={{ stroke:'#fff', opacity:.9 }} strokeWidth="2" />}
            <text x={gx} y={gy + 4} textAnchor="middle" style={{ fill:'#fff', font:"600 12px 'IBM Plex Sans'" }}>{gatilho.id.replace('CLI', '')}</text>
            <text x={gx} y={gy + 46} textAnchor="middle" style={{ fill:'var(--text)', font:"500 11px 'IBM Plex Sans'" }}>{gatilho.id}</text>
            {acesos.map((a, i) => {
              const y = posY(i); const destaque = a.id === foco; const apagado = !focoGatilho && !destaque;
              return (
                <g key={'n' + i} style={{ opacity: apagado ? .28 : 1 }}>
                  <text x={ax} y={y - 24} textAnchor="middle" style={{ fill:'var(--muted)', font:"500 9px 'IBM Plex Mono'" }}>peso {vg(a.peso)}</text>
                  <circle cx={ax} cy={y} r={destaque ? 20 : 18} style={{ fill:'var(--alert)' }} />
                  {destaque && <circle cx={ax} cy={y} r="24" fill="none" style={{ stroke:'#fff' }} strokeWidth="2" />}
                  <text x={ax} y={y + 4} textAnchor="middle" style={{ fill:'#11100F', font:"600 10px 'IBM Plex Sans'" }}>{a.id.replace('CLI', '')}</text>
                </g>
              );
            })}
            {controle && (
              <g style={{ opacity: focoGatilho ? 1 : .35 }}>
                <text x="150" y="278" textAnchor="middle" style={{ fill:'var(--success)', font:"500 9px 'IBM Plex Mono'" }}>controle</text>
                <circle cx="150" cy="300" r="14" style={{ fill:'var(--success)' }} />
                <text x="150" y="304" textAnchor="middle" style={{ fill:'#fff', font:"600 9px 'IBM Plex Sans'" }}>{controle.id.replace('CLI', '')}</text>
              </g>
            )}
          </svg>

          <div className="prop-panel">
            {focoAceso && <div className="prop-foco">Destacando <strong>{focoAceso.id}</strong> · {focoAceso.via} · peso {vg(focoAceso.peso)}</div>}
            <div className="prop-list">
              {acesos.map((a, i) => (
                <div className={`prop-line ${a.id === foco ? 'on' : ''}`} key={i}>
                  <span className="reason-dot"/><span><strong>{a.id}</strong> · {a.via}</span>
                  <span className="peso">{vg(a.peso)}</span>
                </div>
              ))}
            </div>
            {controle && (
              <div className="prop-control"><strong>Controle: {controle.id} continua verde.</strong> Sem vínculo com o evento — prova que o sistema distingue contágio real de ruído.</div>
            )}
            <div className="prop-note"><strong>Explicação ≠ score solto</strong>Cada alerta nasce com o caminho do vínculo e a fonte que sustenta o evento — nunca um número sem porquê.</div>
            <div className="prop-actions">
              {ctx.setSelecionado && <button className="secondary-btn" onClick={() => ctx.setSelecionado(focoAceso ? focoAceso.id : gatilho.id)}>Ver dossiê{focoAceso ? ` de ${focoAceso.id}` : ' do gatilho'}</button>}
              <Link className="secondary-btn" to="/">Voltar ao grafo</Link>
            </div>
          </div>
        </div>

        <div className="prop-foot">Cena de demo recomendada: evento → propagação → scoring → dossiê → fila.</div>
      </section>
    </main>
  );
}
