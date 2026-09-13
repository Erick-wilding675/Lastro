import { useOutletContext } from 'react-router-dom';
import GrafoCarteira from './GrafoCarteira';
import FaixaKpis from '../kpis/FaixaKpis';
import StatusConexao from '../../components/StatusConexao';
export default function PaginaGrafo(){const{setSelecionado,tema}=useOutletContext();return <main className="page"><div className="page-head"><div><div className="eyebrow">01 / Carteira viva</div><h1 className="title">Grafo da carteira</h1><p className="subtitle">Veja a exposição como rede: o risco se desloca por sócios, avalistas, grupos, região e cultura antes de aparecer no atraso.</p></div><StatusConexao/></div><FaixaKpis/><GrafoCarteira onSelecionar={setSelecionado} tema={tema}/></main>}
