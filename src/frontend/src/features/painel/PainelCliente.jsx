import { useEffect, useState } from "react";
import { api } from "../../lib/api";
import { cores } from "../../lib/tokens";

/** Painel lateral: dossiê do cliente, com o contágio explicado pelo caminho. */
export default function PainelCliente({ clienteId }) {
  const [dossie, setDossie] = useState(null);

  useEffect(() => {
    if (clienteId) api.dossie(clienteId).then(setDossie);
  }, [clienteId]);

  if (!clienteId) return null;
  if (!dossie) return <aside style={estilo}>Carregando…</aside>;

  return (
    <aside style={estilo}>
      <h2 style={{ color: cores.textoPrimario }}>{dossie.cliente?.nome}</h2>
      <p style={{ color: cores.textoSecundario }}>
        Score {dossie.cliente?.score} · Rating {dossie.cliente?.rating}
      </p>

      <h3 style={{ color: cores.textoPrimario }}>Por que acendeu</h3>
      <ul>
        {(dossie.contagio ?? [])
          .filter((c) => c.de)
          .map((c, i) => (
            <li key={i} style={{ color: cores.textoSecundario }}>
              {c.de} · peso {c.peso} · {(c.caminho ?? []).join("; ")}
            </li>
          ))}
      </ul>

      <h3 style={{ color: cores.textoPrimario }}>Recomendação</h3>
      <ul>
        {(dossie.recomendacoes ?? [])
          .filter((r) => r.estrategia)
          .map((r, i) => (
            <li key={i} style={{ color: cores.textoSecundario }}>
              {r.estrategia} · R$ {r.recuperavel} · {r.prazo} dias
            </li>
          ))}
      </ul>
    </aside>
  );
}

const estilo = {
  width: "38%",
  padding: 24,
  background: cores.layer1,
  borderLeft: `1px solid ${cores.bordaSutil}`,
  overflowY: "auto",
};
