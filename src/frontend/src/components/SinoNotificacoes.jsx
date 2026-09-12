import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useNotificacoes } from '../context/NotificacoesProvider';

export default function SinoNotificacoes(){
  const { lista, naoLidas, marcarLidas } = useNotificacoes();
  const [aberto, setAberto] = useState(false);
  const wrap = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fora = e => { if (wrap.current && !wrap.current.contains(e.target)) setAberto(false); };
    document.addEventListener('mousedown', fora);
    return () => document.removeEventListener('mousedown', fora);
  }, []);

  const toggle = () => setAberto(a => { const nx = !a; if (nx) marcarLidas(); return nx; });
  const abrir = n => { setAberto(false); const gatilho = n.origem ?? n.cliente; navigate(`/evento/${gatilho}?foco=${n.cliente}`); };

  return (
    <div className="bell-wrap" ref={wrap}>
      <button className={`icon-btn bell ${naoLidas > 0 ? 'has-unread' : ''}`} title="Notificações" onClick={toggle}>
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/>
        </svg>
        {naoLidas > 0 && <span className="bell-badge">{naoLidas}</span>}
      </button>
      {aberto && (
        <div className="notif-panel">
          <div className="notif-head"><strong>Notificações</strong><span>{lista.length} recentes</span></div>
          <div className="notif-list">
            {lista.length === 0
              ? <div className="notif-empty">Sem eventos por enquanto…</div>
              : lista.map(n => (
                  <button key={n.uid} className="notif-item" onClick={() => abrir(n)}>
                    <span className={`notif-dot ${n.tipo}`}/>
                    <span className="notif-body">
                      <span className="notif-title">{n.titulo}</span>
                      <span className="notif-meta">{n.via}{n.peso ? ` · peso ${n.peso.toFixed(2).replace('.', ',')}` : ''}</span>
                    </span>
                    <span className="notif-hora">{n.hora}</span>
                  </button>
                ))}
          </div>
          <div className="notif-foot">Clique num alerta para ver o evento mudar o mapa</div>
        </div>
      )}
    </div>
  );
}
