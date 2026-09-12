import { useEffect, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { api } from "../../lib/api";
import { cores, corPorRating } from "../../lib/tokens";

/**
 * Mapa de exposição da carteira.
 * Tamanho do nó = exposição em R$. Cor = rating.
 * Aresta sólida = vínculo confirmado. Tracejada = contágio calculado.
 */
export default function GrafoCarteira({ onSelecionar }) {
  const [dados, setDados] = useState({ nodes: [], links: [] });
  const ref = useRef();

  useEffect(() => {
    api.grafo().then((d) =>
      setDados({
        nodes: d.nodes ?? [],
        links: (d.links ?? []).map((l) => ({ ...l })),
      })
    );
  }, []);

  return (
    <ForceGraph2D
      ref={ref}
      graphData={dados}
      backgroundColor={cores.background}
      nodeLabel={(n) => `${n.nome} — rating ${n.rating ?? "?"}`}
      nodeVal={(n) => Math.max(2, (n.exposicao ?? 0) / 100000)}
      nodeColor={(n) => corPorRating(n.rating)}
      linkColor={() => cores.acento}
      linkDirectionalParticles={2}
      linkWidth={(l) => (l.peso ?? 0.3) * 3}
      onNodeClick={(n) => onSelecionar?.(n.id)}
    />
  );
}
