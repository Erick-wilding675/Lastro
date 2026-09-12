import { useOutletContext } from 'react-router-dom';
import GrafoCarteira from './GrafoCarteira';
import FaixaKpis from '../kpis/FaixaKpis';
export default function PaginaGrafo(){const{setSelecionado,tema}=useOutletContext();return <main className="page"><div className="page-head"><div><div className="eyebrow">01 / Carteira viva</div><h1 className="title">Grafo da carteira</h1><p className="subtitle">Veja a exposição como rede: o risco se desloca por sócios, avalistas, grupos, região e cultura antes de aparecer no atraso.</p></div><div className="status-pill"><span className="status-dot"/> Demo KRILLTECH · dados sintéticos</div></div><FaixaKpis/><GrafoCarteira onSelecionar={setSelecionado} tema={tema}/></main>}
