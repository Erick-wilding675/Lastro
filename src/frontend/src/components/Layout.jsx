import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import NavTabs from './NavTabs';
import SinoNotificacoes from './SinoNotificacoes';
import DrawerCliente from '../ui/DrawerCliente';
import Brand from '../ui/Brand';
import { temas } from '../lib/tokens';
import '../styles/global.css';
export default function Layout(){
  const [selecionado,setSelecionado]=useState(null); const [tema,setTema]=useState('dark');
  const t=temas[tema];
  return <div className="app app-shell" style={{'--bg':t.background,'--layer1':t.layer1,'--layer2':t.layer2,'--glass':t.glass,'--border':t.bordaSutil,'--text':t.textoPrimario,'--muted':t.textoSecundario,'--accent':t.acento,'--accent-soft':t.acentoSoft,'--alert':t.alerta,'--alert-soft':t.alertaSoft,'--danger':t.perigo,'--danger-soft':t.perigoSoft,'--success':t.sucesso,'--success-soft':t.sucessoSoft,'--shadow':t.sombra,'background':t.background,'color':t.textoPrimario}}>
    <header className="topbar"><Brand/><NavTabs/><div className="top-actions"><SinoNotificacoes/><div className="status-pill"><span className="status-dot"/> Motor conectado</div><button className="theme-toggle" title="Alternar tema" onClick={()=>setTema(x=>x==='dark'?'light':'dark')}>{tema==='dark'?'☼':'☾'}</button></div></header>
    <Outlet context={{setSelecionado,selecionado,tema}} />
    <DrawerCliente clienteId={selecionado} onClose={()=>setSelecionado(null)}/>
  </div>
}
