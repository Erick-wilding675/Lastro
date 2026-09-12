import { useState } from "react";
import GrafoCarteira from "./features/grafo/GrafoCarteira";
import PainelCliente from "./features/painel/PainelCliente";
import { cores } from "./lib/tokens";

export default function App() {
  const [selecionado, setSelecionado] = useState(null);
  return (
    <div style={{ display: "flex", height: "100vh", background: cores.background }}>
      <main style={{ flex: 1 }}>
        <GrafoCarteira onSelecionar={setSelecionado} />
      </main>
      <PainelCliente clienteId={selecionado} />
    </div>
  );
}
