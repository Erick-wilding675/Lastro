// Tokens do design system — ver vault/.ai/ui_guidelines.md
export const cores = {
  background: "#11100F",   // Warm Black
  layer1: "#1F1E1C",
  layer2: "#2C2B2A",
  textoPrimario: "#F6F4EF", // Sand
  textoSecundario: "#7A818B",
  bordaSutil: "#5B6472",   // Graphite
  acento: "#A12AEB",       // Violeta da marca — o que é gerado por IA
  alerta: "#E8A33D",
};

// Cor do nó por rating: A/B saudável, C atenção, D crítico.
export const corPorRating = (rating) =>
  ({ A: "#4FA97B", B: "#7A818B", C: cores.alerta, D: "#D9534F" }[rating] ?? cores.bordaSutil);
