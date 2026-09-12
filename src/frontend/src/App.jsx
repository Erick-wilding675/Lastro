import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import NotificacoesProvider from './context/NotificacoesProvider';
import PaginaGrafo from './features/grafo/PaginaGrafo';
import PaginaPropagacao from './features/propagacao/PaginaPropagacao';
import FilaRecuperacao from './features/fila/FilaRecuperacao';
import PainelGeral from './features/painel-geral/PainelGeral';

export default function App(){
  return (
    <NotificacoesProvider>
      <Routes>
        <Route element={<Layout/>}>
          <Route path="/" element={<PaginaGrafo/>}/>
          <Route path="/evento/:id" element={<PaginaPropagacao/>}/>
          <Route path="/fila" element={<FilaRecuperacao/>}/>
          <Route path="/painel" element={<PainelGeral/>}/>
        </Route>
      </Routes>
    </NotificacoesProvider>
  );
}
