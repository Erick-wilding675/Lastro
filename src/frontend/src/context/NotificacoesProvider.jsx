import { createContext, useContext, useEffect, useState } from 'react';
import { carregarNotificacoes } from '../lib/notificacoes';

const Ctx = createContext(null);
export const useNotificacoes = () => useContext(Ctx);

const PRIMEIRA = 3500;   // primeiro alerta chega logo, pra dar vida à demo
const INTERVALO = 9000;  // e um novo a cada ~9s
const MAX = 8;

export default function NotificacoesProvider({ children }){
  const [lista, setLista] = useState([]);

  useEffect(() => {
    let vivo = true;
    let iv = null;
    let t0 = null;

    // A fila agora vem do motor (POST /motor/ciclo): cada alerta é um vínculo
    // de contágio que o grafo realmente encontrou. O gotejar continua — é o que
    // faz a rede parecer viva na demo — mas o conteúdo deixou de ser fixo.
    carregarNotificacoes().then(fila => {
      if (!vivo) return;
      let i = 0;
      const push = () => {
        if (i >= fila.length) { if (iv) clearInterval(iv); return; }  // uma passada só, sem loop
        const base = fila[i]; i += 1;
        const hora = new Date().toLocaleTimeString('pt-BR', { hour:'2-digit', minute:'2-digit' });
        setLista(l => [{ ...base, uid:`${base.cliente}-${i}-${Date.now()}`, hora, lida:false }, ...l].slice(0, MAX));
      };
      t0 = setTimeout(() => { push(); iv = setInterval(push, INTERVALO); }, PRIMEIRA);
    });

    return () => { vivo = false; if (t0) clearTimeout(t0); if (iv) clearInterval(iv); };
  }, []);

  const naoLidas = lista.filter(n => !n.lida).length;
  const marcarLidas = () => setLista(l => l.map(n => ({ ...n, lida:true })));
  const limpar = () => setLista([]);

  return <Ctx.Provider value={{ lista, naoLidas, marcarLidas, limpar }}>{children}</Ctx.Provider>;
}
