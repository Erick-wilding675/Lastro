import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import PaginaGrafo from './features/grafo/PaginaGrafo';
import FilaRecuperacao from './features/fila/FilaRecuperacao';
import PainelGeral from './features/painel-geral/PainelGeral';
export default function App(){return <Routes><Route element={<Layout/>}><Route path="/" element={<PaginaGrafo/>}/><Route path="/fila" element={<FilaRecuperacao/>}/><Route path="/painel" element={<PainelGeral/>}/></Route></Routes>}
