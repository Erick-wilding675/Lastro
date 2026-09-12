export const temas = {
  dark: {
    background: "#11100F",
    layer1: "#1F1E1C",
    layer2: "#2C2B2A",
    glass: "rgba(17,16,15,.72)",
    borderGlass: "rgba(246,244,239,.08)",
    textoPrimario: "#F6F4EF",
    textoSecundario: "#7A818B",
    bordaSutil: "#3F3E3C",
    acento: "#A12AEB",
    acentoSoft: "rgba(161,42,235,.16)",
    alerta: "#E8A33D",
    alertaSoft: "rgba(232,163,61,.13)",
    perigo: "#D9534F",
    perigoSoft: "rgba(217,83,79,.13)",
    sucesso: "#4FA97B",
    sucessoSoft: "rgba(79,169,123,.13)",
    sombra: "0 22px 60px rgba(0,0,0,.28)",
  },
  light: {
    background: "#F6F4EF",
    layer1: "#FFFFFF",
    layer2: "#EDEAE2",
    glass: "rgba(255,255,255,.82)",
    borderGlass: "rgba(17,16,15,.08)",
    textoPrimario: "#11100F",
    textoSecundario: "#5B6472",
    bordaSutil: "#D8D5CE",
    acento: "#A12AEB",
    acentoSoft: "rgba(161,42,235,.12)",
    alerta: "#C97A1F",
    alertaSoft: "rgba(201,122,31,.12)",
    perigo: "#B74642",
    perigoSoft: "rgba(183,70,66,.11)",
    sucesso: "#2E7A56",
    sucessoSoft: "rgba(46,122,86,.11)",
    sombra: "0 18px 48px rgba(42,37,31,.12)",
  },
};

export const corPorRating = (rating, tema = "dark") => {
  const t = temas[tema];
  return ({ A: t.sucesso, B: t.textoSecundario, C: t.alerta, D: t.perigo }[rating] ?? t.bordaSutil);
};
