const pptxgen = require("pptxgenjs");

// ---------- palette (Lastro design system) ----------
const WARM_BLACK = "11100F";
const SAND = "F6F4EF";
const GRAPHITE = "5B6472";
const VIOLETA = "A12AEB";
const BROWN = "502003";
const WHITE = "FFFFFF";
const MUTED = "8A8A8A";
const MUTED_LIGHT = "C9C2B4";
const RATING_A = "2E7D5B";
const RATING_B = "3F7CAC";
const RATING_C = "D08C3A";
const RATING_D = "B23A3A";

const FONT_HEAD = "Cambria";
const FONT_BODY = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
const W = 13.33, H = 7.5;

function bg(slide, color) {
  slide.background = { color };
}

function graphMotif(slide, opts) {
  // small recurring node-and-edge motif
  const { x, y, color = VIOLETA, scale = 1, alpha = 100 } = opts;
  const pts = [
    [0, 0], [0.55 * scale, -0.35 * scale], [0.95 * scale, 0.15 * scale],
    [0.35 * scale, 0.45 * scale],
  ];
  for (let i = 0; i < pts.length - 1; i++) {
    slide.addShape("line", {
      x: x + pts[i][0], y: y + pts[i][1],
      w: pts[i + 1][0] - pts[i][0], h: pts[i + 1][1] - pts[i][1],
      line: { color, width: 1.25, transparency: 100 - alpha },
    });
  }
  pts.forEach(([dx, dy], i) => {
    const r = i === 0 ? 0.09 : 0.065;
    slide.addShape("ellipse", {
      x: x + dx - r / 2, y: y + dy - r / 2, w: r, h: r,
      fill: { color, transparency: 100 - alpha }, line: { type: "none" },
    });
  });
}

function pageNumber(slide, n, dark) {
  slide.addText(String(n).padStart(2, "0"), {
    x: W - 0.9, y: H - 0.55, w: 0.6, h: 0.3, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, fontSize: 9, color: dark ? MUTED_LIGHT : MUTED,
    align: "right",
  });
}

function kicker(slide, text, opts = {}) {
  slide.addText(text.toUpperCase(), {
    x: opts.x ?? 0.7, y: opts.y ?? 0.5, w: opts.w ?? 8, h: 0.4,
    isTextBox: true, margin: 0,
    fontFace: FONT_BODY, fontSize: 12.5, color: opts.color ?? VIOLETA,
    bold: true, charSpacing: 2,
  });
}

// =========================================================
// Slide 1 — Capa
// =========================================================
{
  const s = pres.addSlide();
  bg(s, WARM_BLACK);
  graphMotif(s, { x: 10.6, y: 1.2, scale: 2.6, color: VIOLETA, alpha: 70 });
  graphMotif(s, { x: 1.0, y: 5.6, scale: 1.6, color: BROWN === "" ? VIOLETA : "7A4FA0", alpha: 40 });

  s.addText("LASTRO", {
    x: 0, y: 2.55, w: W, h: 1.3, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, fontSize: 66, bold: true, color: WHITE,
    align: "center", charSpacing: 4,
  });
  s.addText("Inteligência de risco relacional e recuperação de capital no agro", {
    x: W / 2 - 5, y: 3.85, w: 10, h: 0.5, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, italic: true, fontSize: 16, color: MUTED_LIGHT,
    align: "center",
  });
  s.addShape("line", {
    x: W / 2 - 1.1, y: 4.55, w: 2.2, h: 0, line: { color: VIOLETA, width: 1.5 },
  });
  s.addText("Hackathon PMI-DF 2026  ·  Case Krilltech", {
    x: W / 2 - 5, y: 4.75, w: 10, h: 0.4, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, fontSize: 13, color: WHITE, align: "center",
  });
  s.addText("Apresentação: Erick Mendes  ·  Equipe Lastro", {
    x: W / 2 - 5, y: 5.15, w: 10, h: 0.4, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, fontSize: 11.5, color: MUTED_LIGHT, align: "center",
  });
  s.addNotes(
    "Abertura. Não falar nada ainda: deixar o wordmark no ar por 1-2 segundos antes de começar a tese."
  );
}

// =========================================================
// Slide 2 — A tese
// =========================================================
{
  const s = pres.addSlide();
  bg(s, WARM_BLACK);
  kicker(s, "A tese", { color: VIOLETA });

  s.addText(
    "Depois do pedido de Recuperação Judicial, não existe boa decisão.",
    {
      x: 0.9, y: 1.5, w: 11.5, h: 1.5, isTextBox: true, margin: 0,
      fontFace: FONT_HEAD, fontSize: 33, bold: true, color: WHITE, lineSpacing: 40,
    }
  );
  s.addText("Só existe decisão antes.", {
    x: 0.9, y: 2.95, w: 11.5, h: 0.9, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, fontSize: 33, bold: true, color: VIOLETA,
  });

  // stay period timeline
  const ty = 4.7, tx = 0.9, tw = 8.4;
  s.addShape("line", { x: tx, y: ty, w: tw, h: 0, line: { color: MUTED, width: 1.5 } });
  s.addShape("ellipse", { x: tx - 0.07, y: ty - 0.07, w: 0.14, h: 0.14, fill: { color: WHITE }, line: { type: "none" } });
  s.addShape("ellipse", { x: tx + tw - 0.07, y: ty - 0.07, w: 0.14, h: 0.14, fill: { color: VIOLETA }, line: { type: "none" } });
  s.addText("Pedido de RJ", {
    x: tx - 0.7, y: ty + 0.15, w: 2.4, h: 0.35, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, fontSize: 11, color: WHITE,
  });
  s.addText("180 dias de stay period (prorrogável)", {
    x: tx + tw / 2 - 2.2, y: ty - 0.55, w: 4.4, h: 0.35, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, fontSize: 11.5, color: MUTED_LIGHT, align: "center",
  });
  s.addText("Garantia e protesto ficam suspensos", {
    x: tx + tw - 2.6, y: ty + 0.15, w: 3.3, h: 0.35, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, fontSize: 11, color: VIOLETA, align: "right",
  });
  s.addText("Lei 11.101/2005, estendida ao produtor rural pessoa física pela Lei 14.112/2020", {
    x: 0.9, y: 6.7, w: 10, h: 0.35, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, italic: true, fontSize: 9.5, color: MUTED,
  });
  pageNumber(s, 2, true);
  s.addNotes(
    "Quando um cliente da Krilltech pede RJ, começa o stay period: 180 dias em que a empresa fica impedida de executar garantia ou protestar. Pausa de 2 segundos depois desta frase."
  );
}

// =========================================================
// Slide 3 — Diagnóstico
// =========================================================
{
  const s = pres.addSlide();
  bg(s, SAND);
  kicker(s, "O diagnóstico", { color: BROWN });
  s.addText("O “antes” está ficando mais curto", {
    x: 0.7, y: 0.95, w: 11, h: 0.6, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, fontSize: 24, bold: true, color: WARM_BLACK,
  });

  const stats = [
    { big: "1.990", sub: "pedidos de RJ no agro em 2025", tag: "+56,4% sobre 2024", src: "Serasa Experian" },
    { big: "2,7%→7,3%", sub: "inadimplência do produtor rural PF", tag: "em 12 meses", src: "Banco Central" },
    { big: "8,8%", sub: "inadimplência rural no 1T2026", tag: "recorde da série", src: "Serasa Experian" },
  ];
  const cardW = 3.6, gap = 0.45, startX = (W - (cardW * 3 + gap * 2)) / 2, cardY = 2.15, cardH = 3.5;
  stats.forEach((st, i) => {
    const x = startX + i * (cardW + gap);
    s.addShape("roundRect", {
      x, y: cardY, w: cardW, h: cardH, rectRadius: 0.08,
      fill: { color: WHITE }, line: { color: "E6DFD2", width: 1 },
      shadow: { type: "outer", color: "000000", opacity: 0.08, blur: 8, offset: 3, angle: 90 },
    });
    s.addText(st.big, {
      x: x + 0.25, y: cardY + 0.4, w: cardW - 0.5, h: 1.0, isTextBox: true, margin: 0,
      fontFace: FONT_HEAD, bold: true, fontSize: 32, color: VIOLETA, align: "center",
    });
    s.addText(st.sub, {
      x: x + 0.25, y: cardY + 1.45, w: cardW - 0.5, h: 0.9, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, fontSize: 13, color: WARM_BLACK, align: "center", lineSpacing: 16,
    });
    s.addText(st.tag, {
      x: x + 0.25, y: cardY + 2.35, w: cardW - 0.5, h: 0.4, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, bold: true, fontSize: 11.5, color: BROWN, align: "center",
    });
    s.addText(st.src, {
      x: x + 0.25, y: cardY + cardH - 0.5, w: cardW - 0.5, h: 0.35, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, italic: true, fontSize: 9.5, color: MUTED, align: "center",
    });
  });

  s.addText(
    "A Krilltech vende a prazo, direto ao produtor, em 18 estados. A carteira dela está exatamente nessa população.",
    {
      x: 0.9, y: 6.15, w: 11.5, h: 0.6, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, italic: true, fontSize: 13, color: GRAPHITE, align: "center",
    }
  );
  pageNumber(s, 3, false);
  s.addNotes(
    "1.990 pedidos de RJ no agro em 2025, 56,4% a mais que 2024. Inadimplência do produtor PF de 2,7% para 7,3% em 12 meses. A Krilltech vende direto ao produtor em 18 estados: a carteira dela está exatamente nessa população. E ela enxerga essa carteira como lista, quando o risco é compartilhado."
  );
}

// =========================================================
// Slide 4 — Lista vs Rede
// =========================================================
{
  const s = pres.addSlide();
  bg(s, SAND);
  kicker(s, "O problema de base", { color: BROWN });
  s.addText("A carteira não se comporta como uma lista", {
    x: 0.7, y: 0.95, w: 11.5, h: 0.6, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, fontSize: 24, bold: true, color: WARM_BLACK,
  });

  // left column: lista (faded)
  const colW = 5.15, colY = 2.15, colH = 3.7, gap = 0.7;
  const lx = (W - (colW * 2 + gap)) / 2;
  const rx = lx + colW + gap;

  s.addShape("roundRect", {
    x: lx, y: colY, w: colW, h: colH, rectRadius: 0.08,
    fill: { color: "EDE9E0" }, line: { color: "DED6C7", width: 1 },
  });
  s.addText("Hoje: carteira como lista", {
    x: lx + 0.35, y: colY + 0.3, w: colW - 0.7, h: 0.4, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, bold: true, fontSize: 14, color: GRAPHITE,
  });
  // faded list icon: horizontal bars
  for (let i = 0; i < 5; i++) {
    s.addShape("roundRect", {
      x: lx + 0.35, y: colY + 0.95 + i * 0.42, w: colW - 0.9, h: 0.22, rectRadius: 0.04,
      fill: { color: "D6CDBB" }, line: { type: "none" },
    });
  }
  s.addText("Cada cliente avaliado sozinho. O risco só aparece quando já virou vencido.", {
    x: lx + 0.35, y: colY + 3.05, w: colW - 0.7, h: 0.6, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, fontSize: 11.5, color: GRAPHITE, italic: true,
  });

  s.addShape("roundRect", {
    x: rx, y: colY, w: colW, h: colH, rectRadius: 0.08,
    fill: { color: WHITE }, line: { color: VIOLETA, width: 1.5 },
    shadow: { type: "outer", color: "000000", opacity: 0.1, blur: 10, offset: 3, angle: 90 },
  });
  s.addText("Com o Lastro: carteira como rede", {
    x: rx + 0.35, y: colY + 0.3, w: colW - 0.7, h: 0.4, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, bold: true, fontSize: 14, color: WARM_BLACK,
  });
  graphMotif(s, { x: rx + 0.7, y: colY + 1.75, scale: 3.0, color: VIOLETA, alpha: 100 });
  s.addText("Vínculos entre clientes propagam o risco antes do vencimento.", {
    x: rx + 0.35, y: colY + 3.05, w: colW - 0.7, h: 0.6, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, fontSize: 11.5, color: WARM_BLACK, italic: true,
  });

  s.addText(
    "Krilltech: agtech de Brasília, parceria UnB e Embrapa, produto Arbolin Biogenesis · 210 clientes · 18 estados · 23 culturas",
    {
      x: 0.7, y: 6.25, w: 12, h: 0.4, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, fontSize: 10.5, color: MUTED, align: "center",
    }
  );
  pageNumber(s, 4, false);
  s.addNotes(
    "A Krilltech promete otimizar a produtividade da lavoura do cliente através da Arbolin Biogenesis. O Lastro dá a mesma inteligência sobre a saúde financeira de quem compra dela."
  );
}

// =========================================================
// Slide 5 — Motor de dois canais
// =========================================================
{
  const s = pres.addSlide();
  bg(s, SAND);
  kicker(s, "Como o Lastro funciona", { color: BROWN });
  s.addText("Dois canais de exposição, naturezas diferentes", {
    x: 0.7, y: 0.95, w: 11.7, h: 0.6, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, fontSize: 24, bold: true, color: WARM_BLACK,
  });

  const colW = 5.5, colY = 2.05, gap = 0.6;
  const lx = (W - (colW * 2 + gap)) / 2;
  const rx = lx + colW + gap;
  const rowH = 0.62;

  function channelCard(x, title, subtitle, color, rows) {
    const h = 0.95 + rows.length * rowH + 0.35;
    s.addShape("roundRect", {
      x, y: colY, w: colW, h, rectRadius: 0.08,
      fill: { color: WHITE }, line: { color: "E6DFD2", width: 1 },
      shadow: { type: "outer", color: "000000", opacity: 0.08, blur: 8, offset: 3, angle: 90 },
    });
    s.addShape("roundRect", {
      x: x + 0.3, y: colY + 0.3, w: 0.14, h: 0.6, rectRadius: 0.03,
      fill: { color }, line: { type: "none" },
    });
    s.addText(title, {
      x: x + 0.55, y: colY + 0.28, w: colW - 0.9, h: 0.35, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, bold: true, fontSize: 14.5, color: WARM_BLACK,
    });
    s.addText(subtitle, {
      x: x + 0.55, y: colY + 0.62, w: colW - 0.9, h: 0.3, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, italic: true, fontSize: 10, color: MUTED,
    });
    rows.forEach((r, i) => {
      const ry = colY + 1.05 + i * rowH;
      s.addText(r.label, {
        x: x + 0.35, y: ry, w: colW - 1.7, h: rowH - 0.06, isTextBox: true, margin: 0,
        fontFace: FONT_BODY, fontSize: 11.5, color: WARM_BLACK, valign: "middle",
      });
      s.addShape("roundRect", {
        x: x + colW - 1.25, y: ry + 0.06, w: 0.9, h: rowH - 0.22, rectRadius: 0.05,
        fill: { color: color, transparency: 88 }, line: { color, width: 0.75 },
      });
      s.addText(r.weight, {
        x: x + colW - 1.25, y: ry + 0.06, w: 0.9, h: rowH - 0.22, isTextBox: true, margin: 0,
        fontFace: FONT_BODY, bold: true, fontSize: 11.5, color, align: "center", valign: "middle",
      });
    });
    return h;
  }

  channelCard(lx, "Canal estrutural", "risco contamina por vínculo jurídico ou patrimonial", BROWN, [
    { label: "Mesmo grupo econômico", weight: "0,90" },
    { label: "Avalista em comum", weight: "0,85" },
    { label: "Sócio em comum (QSA)", weight: "0,70" },
  ]);
  channelCard(rx, "Canal sistêmico", "ninguém contamina; todos sofrem a mesma causa externa", VIOLETA, [
    { label: "Região + cultura*", weight: "0,75" },
    { label: "Mesma revenda", weight: "0,65" },
    { label: "Mesma cultura", weight: "0,40" },
  ]);

  s.addText(
    "* Peso cheio só com evento regional confirmando o choque (quebra de safra, alerta ZARC, queda de preço em até 365 dias). Sem evento, cai para 0,30.",
    {
      x: 0.7, y: 6.15, w: 12, h: 0.5, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, italic: true, fontSize: 10, color: MUTED,
    }
  );
  s.addText("Toda exposição guarda o caminho que a gerou. O caminho é a explicação.", {
    x: 0.7, y: 6.65, w: 12, h: 0.4, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, bold: true, fontSize: 11.5, color: WARM_BLACK,
  });
  pageNumber(s, 5, false);
  s.addNotes(
    "Estrutural: grupo econômico, avalista, sócio em comum. Sistêmico: região e cultura só pesam cheio se houver evento regional confirmando o choque - isso é o que impede a carteira inteira de acender."
  );
}

// =========================================================
// Slide 6 — A demonstração (grafo de contágio)
// =========================================================
{
  const s = pres.addSlide();
  bg(s, WARM_BLACK);
  kicker(s, "A demonstração", { color: VIOLETA });
  s.addText("Um clique. Quatro clientes acendem. Um continua verde.", {
    x: 0.7, y: 0.9, w: 12, h: 0.55, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, fontSize: 22, bold: true, color: WHITE,
  });

  const centerX = 3.1, centerY = 4.35;
  const nodes = [
    { x: 7.7, y: 2.05, r: 0.62, color: RATING_A, label: "Terra Nova", sub: "grupo econômico · A", w: "R$ 410 mil" },
    { x: 9.9, y: 3.15, r: 0.5, color: RATING_B, label: "Fazenda Santa Luzia", sub: "sócio comum + região · B", w: "R$ 520 mil" },
    { x: 9.75, y: 5.35, r: 0.46, color: RATING_C, label: "Agropecuária Horizonte", sub: "avalista comum · C", w: "R$ 230 mil" },
    { x: 7.55, y: 5.85, r: 0.42, color: RATING_C, label: "Sítio Boa Esperança", sub: "região/cultura (Conab) · C", w: "R$ 98 mil" },
  ];
  nodes.forEach((n) => {
    s.addShape("line", {
      x: Math.min(centerX, n.x), y: Math.min(centerY, n.y),
      w: Math.abs(n.x - centerX), h: Math.abs(n.y - centerY),
      line: { color: VIOLETA, width: 1.25, dashType: "sysDot" },
      flipV: n.y < centerY,
    });
  });
  // center node (RJ)
  s.addShape("ellipse", {
    x: centerX - 0.85, y: centerY - 0.85, w: 1.7, h: 1.7,
    fill: { color: RATING_D }, line: { color: WHITE, width: 2 },
  });
  s.addText("Agro Vale\ndo Cerrado", {
    x: centerX - 0.85, y: centerY - 0.45, w: 1.7, h: 0.7, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, bold: true, fontSize: 11, color: WHITE, align: "center", valign: "middle",
  });
  s.addText("pediu RJ · rating D", {
    x: centerX - 1.3, y: centerY + 0.95, w: 2.6, h: 0.35, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, fontSize: 10, color: MUTED_LIGHT, align: "center",
  });

  nodes.forEach((n) => {
    s.addShape("ellipse", {
      x: n.x - n.r, y: n.y - n.r, w: n.r * 2, h: n.r * 2,
      fill: { color: n.color }, line: { color: WHITE, width: 1.5 },
    });
    const labelAbove = n.y < centerY;
    s.addText(`${n.label}\n${n.sub}\n${n.w}`, {
      x: n.x - 1.35, y: labelAbove ? n.y - n.r - 1.0 : n.y + n.r + 0.08,
      w: 2.7, h: 0.9, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, fontSize: 9.5, color: WHITE, align: "center", lineSpacing: 12,
    });
  });

  // control node
  s.addShape("ellipse", {
    x: 1.55 - 0.4, y: 6.35 - 0.4, w: 0.8, h: 0.8,
    fill: { color: RATING_A }, line: { color: WHITE, width: 1.5 },
  });
  s.addText("Ipê Amarelo\ncontrole · A · sem vínculo", {
    x: 1.55 - 1.5, y: 6.35 + 0.42, w: 3.0, h: 0.6, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, fontSize: 9.5, color: MUTED_LIGHT, align: "center",
  });

  s.addText("R$ 1.258.000", {
    x: 0.6, y: 1.65, w: 3.4, h: 0.7, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, bold: true, fontSize: 27, color: VIOLETA,
  });
  s.addText("de exposição identificada antes do vencimento", {
    x: 0.6, y: 2.35, w: 3.0, h: 0.6, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, fontSize: 11, color: MUTED_LIGHT,
  });
  pageNumber(s, 6, true);
  s.addNotes(
    "Um clique e a Agro Vale do Cerrado propaga o risco. Quatro clientes acendem, nenhum em atraso hoje. Terra Nova por grupo, Horizonte por avalista, Santa Luzia por sócio comum, Boa Esperança por região com quebra confirmada pela Conab. O Ipê Amarelo continua verde: outra região, outra cultura, nenhum vínculo. O sistema não pinta a carteira toda de vermelho."
  );
}

// =========================================================
// Slide 7 — Score, rating e decisão
// =========================================================
{
  const s = pres.addSlide();
  bg(s, SAND);
  kicker(s, "Score, rating e decisão", { color: BROWN });
  s.addText("Cinco componentes, uma fórmula auditável", {
    x: 0.7, y: 0.95, w: 11.5, h: 0.55, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, fontSize: 24, bold: true, color: WARM_BLACK,
  });

  s.addShape("roundRect", {
    x: 0.7, y: 1.75, w: 11.9, h: 0.6, rectRadius: 0.08,
    fill: { color: WARM_BLACK }, line: { type: "none" },
  });
  s.addText("score  =  1000  ×  ( 1 − média dos 5 componentes )", {
    x: 0.7, y: 1.75, w: 11.9, h: 0.6, isTextBox: true, margin: 0,
    fontFace: "Courier New", fontSize: 15, color: WHITE, align: "center", valign: "middle",
  });

  const comps = [
    "Comportamento\nde pagamento",
    "Eventos jurídicos\ne fiscais (180d)",
    "Cobertura de garantia\n(com haircut)",
    "Exposição herdada\nda rede",
    "Risco agro\ne ambiental",
  ];
  const cw = 2.15, cgap = 0.18, cx0 = (W - (cw * 5 + cgap * 4)) / 2, cy = 2.65;
  comps.forEach((c, i) => {
    const x = cx0 + i * (cw + cgap);
    s.addShape("roundRect", {
      x, y: cy, w: cw, h: 1.1, rectRadius: 0.07,
      fill: { color: WHITE }, line: { color: "E6DFD2", width: 1 },
    });
    s.addText(c, {
      x: x + 0.1, y: cy + 0.1, w: cw - 0.2, h: 0.9, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, fontSize: 10.5, color: WARM_BLACK, align: "center", valign: "middle", lineSpacing: 13,
    });
  });

  s.addText("Haircut por tipo de garantia: alienação fiduciária 1,00 · aval 0,70 · CPR 0,60 · penhor de safra 0,50 · nenhuma 0,00", {
    x: 0.7, y: 3.95, w: 11.9, h: 0.4, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, italic: true, fontSize: 10.5, color: GRAPHITE, align: "center",
  });

  // rating scale bar
  const ratings = [
    { label: "D", range: "0–399", color: RATING_D, w: 2.6 },
    { label: "C", range: "400–599", color: RATING_C, w: 2.6 },
    { label: "B", range: "600–799", color: RATING_B, w: 2.6 },
    { label: "A", range: "800–1000", color: RATING_A, w: 2.6 },
  ];
  const barY = 4.85, barX0 = (W - ratings.length * 2.6 - (ratings.length - 1) * 0.12) / 2;
  ratings.forEach((r, i) => {
    const x = barX0 + i * (r.w + 0.12);
    s.addShape("roundRect", {
      x, y: barY, w: r.w, h: 0.85, rectRadius: 0.06,
      fill: { color: r.color }, line: { type: "none" },
    });
    s.addText(`${r.label}  ·  ${r.range}`, {
      x, y: barY, w: r.w, h: 0.85, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, bold: true, fontSize: 14, color: WHITE, align: "center", valign: "middle",
    });
  });

  s.addShape("roundRect", {
    x: barX0, y: barY + 1.05, w: ratings.length * 2.6 + (ratings.length - 1) * 0.12, h: 0.75, rectRadius: 0.06,
    fill: { color: WHITE }, line: { color: RATING_D, width: 1.25 },
  });
  s.addText("Regra de knockout: cliente em Recuperação Judicial é rating D por definição — score travado em até 350", {
    x: barX0 + 0.2, y: barY + 1.05, w: ratings.length * 2.6 + (ratings.length - 1) * 0.12 - 0.4, h: 0.75,
    isTextBox: true, margin: 0,
    fontFace: FONT_BODY, bold: true, fontSize: 11, color: RATING_D, align: "center", valign: "middle",
  });
  pageNumber(s, 7, false);
  s.addNotes(
    "Score determinístico, não gerado por modelo. Haircut traduz o tipo de garantia em cobertura real. Knockout: cliente em RJ é D por definição, para o sinal mais grave não ser diluído pela média."
  );
}

// =========================================================
// Slide 8 — Os quatro agentes
// =========================================================
{
  const s = pres.addSlide();
  bg(s, SAND);
  kicker(s, "Onde entra IA de verdade", { color: BROWN });
  s.addText("Quatro agentes. Nenhum deles calcula o score.", {
    x: 0.7, y: 0.95, w: 11.7, h: 0.55, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, fontSize: 24, bold: true, color: WARM_BLACK,
  });

  const agents = [
    { n: "1", t: "Coletor & Parser", d: "lê base pública e PDF, devolve evento com fonte e data" },
    { n: "2", t: "Risco Agro & Climático", d: "cruza CAR, ZARC, cultura e safra com a região" },
    { n: "3", t: "Decisão & Scoring", d: "dispara o cálculo e interpreta o que mudou — não calcula" },
    { n: "4", t: "Sintetizador", d: "redige o parecer citando só números do dossiê" },
  ];
  const aw = 2.7, agap = 0.35, ax0 = (W - (aw * 4 + agap * 3)) / 2, ay = 2.5, ah = 2.7;
  agents.forEach((a, i) => {
    const x = ax0 + i * (aw + agap);
    s.addShape("roundRect", {
      x, y: ay, w: aw, h: ah, rectRadius: 0.08,
      fill: { color: WHITE }, line: { color: "E6DFD2", width: 1 },
      shadow: { type: "outer", color: "000000", opacity: 0.08, blur: 8, offset: 3, angle: 90 },
    });
    s.addShape("ellipse", {
      x: x + aw / 2 - 0.32, y: ay + 0.3, w: 0.64, h: 0.64,
      fill: { color: VIOLETA }, line: { type: "none" },
    });
    s.addText(a.n, {
      x: x + aw / 2 - 0.32, y: ay + 0.3, w: 0.64, h: 0.64, isTextBox: true, margin: 0,
      fontFace: FONT_HEAD, bold: true, fontSize: 20, color: WHITE, align: "center", valign: "middle",
    });
    s.addText(a.t, {
      x: x + 0.2, y: ay + 1.15, w: aw - 0.4, h: 0.5, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, bold: true, fontSize: 13, color: WARM_BLACK, align: "center",
    });
    s.addText(a.d, {
      x: x + 0.2, y: ay + 1.65, w: aw - 0.4, h: 0.95, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, fontSize: 10.5, color: GRAPHITE, align: "center", lineSpacing: 13,
    });
    if (i < agents.length - 1) {
      s.addShape("line", {
        x: x + aw + 0.03, y: ay + ah / 2, w: agap - 0.06, h: 0,
        line: { color: VIOLETA, width: 1.5, endArrowType: "triangle" },
      });
    }
  });

  s.addText("IA entra onde há texto e ambiguidade. Onde há conta, é query determinística — por isso o score não alucina.", {
    x: 0.7, y: 5.7, w: 11.9, h: 0.5, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, italic: true, fontSize: 12.5, color: BROWN, align: "center",
  });
  pageNumber(s, 8, false);
  s.addNotes(
    "A decisão mais importante da arquitetura é o que não virou agente: propagação, score e haircut são determinísticos. LLM entra só onde há texto livre."
  );
}

// =========================================================
// Slide 9 — Governança
// =========================================================
{
  const s = pres.addSlide();
  bg(s, WARM_BLACK);
  kicker(s, "Governança", { color: VIOLETA });
  s.addText("O que o Lastro nunca faz", {
    x: 0.7, y: 0.95, w: 11, h: 0.55, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, fontSize: 24, bold: true, color: WHITE,
  });

  const rules = [
    { t: "Recomenda, nunca decide", d: "Nenhuma cobrança, protesto ou ação judicial é disparada automaticamente." },
    { t: "Toda decisão tem trilha de auditoria", d: "Fonte, data e decomposição de cada número, sempre visíveis." },
    { t: "Nunca prescreve instrumento jurídico", d: "Mostra a fragilidade da garantia; a política de crédito é da Krilltech." },
    { t: "Nunca promete prever falência", d: "Mede exposição compartilhada e mostra por qual vínculo ela chega." },
  ];
  const rw = 5.6, rgap = 0.5, rx0 = (W - (rw * 2 + rgap)) / 2, ry0 = 2.15, rh = 1.75, rvgap = 0.35;
  rules.forEach((r, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = rx0 + col * (rw + rgap), y = ry0 + row * (rh + rvgap);
    s.addShape("roundRect", {
      x, y, w: rw, h: rh, rectRadius: 0.08,
      fill: { color: "1B1A17" }, line: { color: "2E2C27", width: 1 },
    });
    s.addShape("roundRect", {
      x: x + 0.3, y: y + 0.3, w: 0.12, h: rh - 0.6, rectRadius: 0.03,
      fill: { color: VIOLETA }, line: { type: "none" },
    });
    s.addText(r.t, {
      x: x + 0.55, y: y + 0.25, w: rw - 0.85, h: 0.45, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, bold: true, fontSize: 14.5, color: WHITE,
    });
    s.addText(r.d, {
      x: x + 0.55, y: y + 0.75, w: rw - 0.85, h: 0.9, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, fontSize: 11.5, color: MUTED_LIGHT, lineSpacing: 15,
    });
  });
  pageNumber(s, 9, true);
  s.addNotes(
    "O Lastro entrega a decisão pronta para o comitê tomar. Não recomendamos alienação fiduciária como se fosse óbvio: mostramos o número e deixamos a decisão de instrumento jurídico com a Krilltech."
  );
}

// =========================================================
// Slide 10 — Plano de conclusão: equipe
// =========================================================
{
  const s = pres.addSlide();
  bg(s, SAND);
  kicker(s, "Plano de conclusão · 1 de 3", { color: BROWN });
  s.addText("A equipe para sair do protótipo à produção", {
    x: 0.7, y: 0.95, w: 11.7, h: 0.55, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, fontSize: 23, bold: true, color: WARM_BLACK,
  });
  s.addText("Horizonte de 6 meses, do fim do hackathon até uso ativo pelo comitê de crédito", {
    x: 0.7, y: 1.5, w: 11.7, h: 0.4, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, italic: true, fontSize: 12, color: GRAPHITE,
  });

  s.addTable(
    [
      [
        { text: "Papel", options: { bold: true, color: WHITE, fill: { color: BROWN } } },
        { text: "Dedicação", options: { bold: true, color: WHITE, fill: { color: BROWN } } },
        { text: "Duração", options: { bold: true, color: WHITE, fill: { color: BROWN } } },
      ],
      ["Tech Lead / Arquiteto de Soluções", "Integral", "6 meses"],
      ["Engenheiros de Dados / Backend (2)", "Integral", "6 meses"],
      ["Engenheiro Frontend", "Integral", "4 meses + manutenção"],
      ["Analista de Dados e Fontes Públicas", "Integral → parcial", "6 meses"],
      ["Especialista de Domínio (crédito agro)", "Consultoria pontual", "6 meses"],
      ["Ponto focal da Krilltech (comitê)", "Meio período", "a partir do mês 2"],
    ],
    {
      x: 0.7, y: 2.15, w: 11.9, h: 3.9,
      fontFace: FONT_BODY, fontSize: 12.5, color: WARM_BLACK,
      border: { type: "solid", color: "E6DFD2", pt: 0.75 },
      fill: { color: WHITE },
      autoPage: false,
      rowH: 0.55,
      valign: "middle",
    }
  );

  s.addText("A base técnica do MVP (schema Neo4j, motor de dois canais, scoring, os 4 agentes) é reaproveitada por inteiro.", {
    x: 0.7, y: 6.25, w: 11.9, h: 0.5, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, italic: true, fontSize: 11, color: MUTED, align: "center",
  });
  pageNumber(s, 10, false);
  s.addNotes("Equipe necessária para os 6 meses até produção. A base técnica do hackathon é reaproveitada, não reconstruída.");
}

// =========================================================
// Slide 11 — Plano de conclusão: cronograma
// =========================================================
{
  const s = pres.addSlide();
  bg(s, SAND);
  kicker(s, "Plano de conclusão · 2 de 3", { color: BROWN });
  s.addText("Quatro fases até a virada para produção", {
    x: 0.7, y: 0.95, w: 11.7, h: 0.55, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, fontSize: 23, bold: true, color: WARM_BLACK,
  });

  const phases = [
    { m: "Mês 1", t: "Conexão e fundação", d: "Base real da Krilltech, mapeamento de vínculos via QSA" },
    { m: "Meses 2–3", t: "Automação e modo sombra", d: "Coleta contínua das bases públicas; sistema roda ao lado do processo atual" },
    { m: "Meses 4–5", t: "Validação", d: "Comparação sistemática dos alertas; calibração em 6, 12 e 24 meses" },
    { m: "Mês 6", t: "Virada para produção", d: "Uso ativo pelo comitê de crédito; treinamento das equipes" },
  ];
  const pw = 2.75, pgap = 0.3, px0 = (W - (pw * 4 + pgap * 3)) / 2, py = 2.4, ph = 3.6;
  const lineY = py + 0.35;
  s.addShape("line", { x: px0 + pw / 2, y: lineY, w: pw * 4 + pgap * 3 - pw, h: 0, line: { color: VIOLETA, width: 2 } });
  phases.forEach((p, i) => {
    const x = px0 + i * (pw + pgap);
    s.addShape("ellipse", {
      x: x + pw / 2 - 0.15, y: lineY - 0.15, w: 0.3, h: 0.3,
      fill: { color: VIOLETA }, line: { color: WHITE, width: 2 },
    });
    s.addShape("roundRect", {
      x, y: py + 0.75, w: pw, h: ph - 0.75, rectRadius: 0.07,
      fill: { color: WHITE }, line: { color: "E6DFD2", width: 1 },
      shadow: { type: "outer", color: "000000", opacity: 0.07, blur: 6, offset: 2, angle: 90 },
    });
    s.addText(p.m.toUpperCase(), {
      x: x + 0.2, y: py + 0.95, w: pw - 0.4, h: 0.3, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, bold: true, fontSize: 10.5, color: VIOLETA, charSpacing: 1,
    });
    s.addText(p.t, {
      x: x + 0.2, y: py + 1.25, w: pw - 0.4, h: 0.65, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, bold: true, fontSize: 13, color: WARM_BLACK, lineSpacing: 15,
    });
    s.addText(p.d, {
      x: x + 0.2, y: py + 1.95, w: pw - 0.4, h: 1.5, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, fontSize: 10, color: GRAPHITE, lineSpacing: 13,
    });
  });
  pageNumber(s, 11, false);
  s.addNotes("Trinta dias para conectar a base real. Sessenta para automatizar a coleta. Noventa para calibrar com resultado observado. Mês 6, virada para uso ativo.");
}

// =========================================================
// Slide 12 — Plano de conclusão: orçamento
// =========================================================
{
  const s = pres.addSlide();
  bg(s, SAND);
  kicker(s, "Plano de conclusão · 3 de 3", { color: BROWN });
  s.addText("Orçamento estimado e retorno esperado", {
    x: 0.7, y: 0.95, w: 11.7, h: 0.55, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, fontSize: 23, bold: true, color: WARM_BLACK,
  });

  // big stat left
  s.addShape("roundRect", {
    x: 0.7, y: 1.9, w: 4.6, h: 4.3, rectRadius: 0.08,
    fill: { color: WARM_BLACK }, line: { type: "none" },
  });
  s.addText("≈ R$ 366 mil", {
    x: 0.9, y: 2.3, w: 4.2, h: 0.9, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, bold: true, fontSize: 30, color: VIOLETA,
  });
  s.addText("investimento estimado para os 6 meses até produção (equipe + infraestrutura)", {
    x: 0.9, y: 3.15, w: 4.2, h: 0.9, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, fontSize: 12, color: WHITE, lineSpacing: 15,
  });
  s.addShape("line", { x: 0.9, y: 4.25, w: 4.0, h: 0, line: { color: "3A3833", width: 1 } });
  s.addText("R$ 1.258.000", {
    x: 0.9, y: 4.45, w: 4.2, h: 0.55, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, bold: true, fontSize: 19, color: WHITE,
  });
  s.addText("em exposição já identificada só no cenário de demonstração", {
    x: 0.9, y: 4.95, w: 4.2, h: 0.8, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, fontSize: 11, color: MUTED_LIGHT, lineSpacing: 14,
  });
  s.addText("Ordem de grandeza, hipótese declarada — não cotação fechada.", {
    x: 0.9, y: 5.75, w: 4.2, h: 0.4, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, italic: true, fontSize: 9, color: MUTED,
  });

  // breakdown "chart": hand-drawn horizontal bars (avoids a pptxgenjs
  // native-chart bug that emits an unmatched 3rd axId on 2D bar charts,
  // which real PowerPoint refuses to open even though other tools accept it)
  {
    const chX = 5.6, chY = 1.9, chW = 7.0, chH = 4.3;
    s.addText("Composição do investimento (R$ mil)", {
      x: chX, y: chY, w: chW, h: 0.4, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, bold: true, fontSize: 13, color: WARM_BLACK, align: "center",
    });
    const rows = [
      { label: "Equipe", value: 331 },
      { label: "Infraestrutura", value: 35 },
    ];
    const maxVal = 350;
    const labelW = 1.55, barAreaX = chX + labelW, barAreaW = chW - labelW - 0.9;
    const barH = 0.62, rowGap = 1.15, firstRowY = chY + 0.95;
    // baseline + simple scale ticks
    const baseY = firstRowY - 0.25;
    const axisBottomY = firstRowY + rowGap + barH + 0.35;
    s.addShape("line", {
      x: barAreaX, y: baseY, w: 0, h: axisBottomY - baseY,
      line: { color: "E6DFD2", width: 1 },
    });
    [0, 50, 100, 150, 200, 250, 300, 350].forEach((tick) => {
      const tx = barAreaX + (tick / maxVal) * barAreaW;
      s.addShape("line", {
        x: tx, y: baseY, w: 0, h: axisBottomY - baseY,
        line: { color: "F0EBE0", width: 0.75 },
      });
      s.addText(String(tick), {
        x: tx - 0.3, y: axisBottomY, w: 0.6, h: 0.3, isTextBox: true, margin: 0,
        fontFace: FONT_BODY, fontSize: 8.5, color: MUTED, align: "center",
      });
    });
    rows.forEach((r, i) => {
      const y = firstRowY + i * rowGap;
      s.addText(r.label, {
        x: chX, y: y + barH / 2 - 0.35, w: labelW - 0.15, h: 0.7, isTextBox: true, margin: 0,
        fontFace: FONT_BODY, bold: true, fontSize: 12, color: WARM_BLACK, align: "right", valign: "middle",
      });
      const bw = Math.max(0.15, (r.value / maxVal) * barAreaW);
      s.addShape("roundRect", {
        x: barAreaX, y, w: bw, h: barH, rectRadius: 0.05,
        fill: { color: VIOLETA }, line: { type: "none" },
      });
      s.addText(String(r.value), {
        x: barAreaX + bw + 0.1, y, w: 0.7, h: barH, isTextBox: true, margin: 0,
        fontFace: FONT_BODY, bold: true, fontSize: 12, color: WARM_BLACK, valign: "middle",
      });
    });
  }

  s.addText("Recuperar uma fração da exposição identificada já paga o investimento do primeiro semestre.", {
    x: 5.6, y: 6.25, w: 7.0, h: 0.5, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, italic: true, fontSize: 11, color: GRAPHITE,
  });
  pageNumber(s, 12, false);
  s.addNotes("Cerca de 366 mil reais para 6 meses de equipe e infraestrutura. A própria demo já mostra 1,258 milhão em exposição identificada: uma fração desse valor recuperado paga o semestre.");
}

// =========================================================
// Slide 13 — Fecho
// =========================================================
{
  const s = pres.addSlide();
  bg(s, WARM_BLACK);
  graphMotif(s, { x: 1.0, y: 1.2, scale: 2.2, color: VIOLETA, alpha: 55 });
  graphMotif(s, { x: 10.8, y: 5.6, scale: 1.8, color: VIOLETA, alpha: 40 });

  s.addText("O mesmo negócio.", {
    x: 0, y: 2.5, w: W, h: 0.85, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, bold: true, fontSize: 34, color: WHITE, align: "center",
  });
  s.addText("Fechando o ciclo.", {
    x: 0, y: 3.3, w: W, h: 0.85, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, bold: true, fontSize: 34, color: VIOLETA, align: "center",
  });
  s.addText(
    "A Krilltech otimiza a lavoura do cliente. O Lastro entrega a mesma inteligência sobre a saúde financeira de quem compra dela.",
    {
      x: W / 2 - 5, y: 4.35, w: 10, h: 0.8, isTextBox: true, margin: 0,
      fontFace: FONT_BODY, italic: true, fontSize: 13.5, color: MUTED_LIGHT, align: "center", lineSpacing: 18,
    }
  );
  s.addShape("line", { x: W / 2 - 1.1, y: 5.55, w: 2.2, h: 0, line: { color: VIOLETA, width: 1.5 } });
  s.addText("LASTRO", {
    x: 0, y: 5.8, w: W, h: 0.6, isTextBox: true, margin: 0,
    fontFace: FONT_HEAD, bold: true, fontSize: 22, color: WHITE, align: "center", charSpacing: 3,
  });
  s.addText("Obrigado · Equipe Lastro · Hackathon PMI-DF 2026", {
    x: 0, y: 6.5, w: W, h: 0.4, isTextBox: true, margin: 0,
    fontFace: FONT_BODY, fontSize: 11, color: MUTED, align: "center",
  });
  s.addNotes("Fecho. Não cortar esta fala mesmo se o tempo apertar.");
}

pres.writeFile({ fileName: process.argv[2] || "/mnt/user-data/outputs/Lastro-Pitch.pptx" })
  .then((f) => console.log("OK:", f))
  .catch((e) => { console.error(e); process.exit(1); });
