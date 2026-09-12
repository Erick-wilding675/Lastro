import { NavLink } from 'react-router-dom';
const abas=[['/','Grafo da carteira'],['/fila','Fila de recuperação'],['/painel','Painel geral']];
export default function NavTabs(){return <nav className="nav-tabs">{abas.map(([to,label])=><NavLink key={to} className={({isActive})=>`nav-tab ${isActive?'active':''}`} to={to} end={to==='/' }>{label}</NavLink>)}</nav>}
