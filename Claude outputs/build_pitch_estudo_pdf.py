#!/usr/bin/env python3
"""Gera o PDF de estudo do pitch (Lastro) a partir do markdown em prosa corrida."""
import re
import sys
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable
)
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import BaseDocTemplate, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "vault/.ai/docs/pitch-estudo-completo.md"
)
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(
    "/mnt/user-data/outputs/Lastro-Estudo-do-Pitch.pdf"
)

INK = HexColor("#1A1A1A")
ACCENT = HexColor("#502003")   # Brown Core
RULE = HexColor("#D8CFC2")

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TitleLastro", parent=styles["Title"],
    fontName="Times-Bold", fontSize=25, leading=30,
    textColor=ACCENT, alignment=TA_CENTER, spaceAfter=4,
)
subtitle_style = ParagraphStyle(
    "SubtitleLastro", parent=styles["Normal"],
    fontName="Times-Italic", fontSize=12, leading=16,
    textColor=INK, alignment=TA_CENTER, spaceAfter=18,
)
h2_style = ParagraphStyle(
    "H2Lastro", parent=styles["Heading2"],
    fontName="Times-Bold", fontSize=15, leading=19,
    textColor=ACCENT, spaceBefore=20, spaceAfter=10,
)
body_style = ParagraphStyle(
    "BodyLastro", parent=styles["Normal"],
    fontName="Times-Roman", fontSize=11.5, leading=17.5,
    textColor=INK, alignment=TA_JUSTIFY, spaceAfter=12,
)
intro_style = ParagraphStyle(
    "IntroLastro", parent=body_style,
    fontName="Times-Italic", textColor=HexColor("#3A3A3A"),
)
footer_style = ParagraphStyle(
    "FooterLastro", parent=styles["Normal"],
    fontName="Times-Italic", fontSize=8.5, textColor=HexColor("#8A8A8A"),
)


def parse(md_text: str):
    lines = md_text.strip("\n").split("\n")
    blocks = []
    para_lines = []
    mode = "intro"  # first H1 + immediate paragraph(s) are treated as intro

    def flush():
        nonlocal para_lines
        if para_lines:
            text = " ".join(l.strip() for l in para_lines).strip()
            if text:
                blocks.append((mode if mode == "intro" and not blocks else "p", text))
            para_lines = []

    title = None
    for raw in lines:
        line = raw.rstrip()
        if line.startswith("# "):
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            flush()
            mode = "h2"
            blocks.append(("h2", line[3:].strip()))
            mode = "p"
            continue
        if line.strip() == "":
            flush()
            continue
        para_lines.append(line)
    flush()
    return title, blocks


def build(md_path: Path, out_path: Path):
    title, blocks = parse(md_path.read_text(encoding="utf-8"))

    story = []
    story.append(Paragraph("LASTRO", title_style))
    story.append(Paragraph(
        "A narrativa completa do pitch, para estudo e memorização",
        subtitle_style,
    ))
    story.append(HRFlowable(width="100%", thickness=0.8, color=RULE, spaceAfter=16))

    first_p_done = False
    for kind, text in blocks:
        if kind == "h2":
            story.append(Paragraph(text, h2_style))
        else:
            style = intro_style if not first_p_done else body_style
            story.append(Paragraph(text, style))
            first_p_done = True

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Times-Italic", 8.5)
        canvas.setFillColor(HexColor("#8A8A8A"))
        canvas.drawString(2.2 * cm, 1.3 * cm, "Lastro — documento de estudo do pitch")
        canvas.drawRightString(A4[0] - 2.2 * cm, 1.3 * cm, f"{doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(out_path), pagesize=A4,
        leftMargin=2.6 * cm, rightMargin=2.6 * cm,
        topMargin=2.4 * cm, bottomMargin=2.2 * cm,
        title="Lastro — Documento de Estudo do Pitch",
        author="Lastro",
    )
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"OK: {out_path}")


if __name__ == "__main__":
    build(SRC, OUT)
