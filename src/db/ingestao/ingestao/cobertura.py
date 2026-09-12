"""Gera a matriz de cobertura a partir das declarações das fontes.

O mapa é GERADO, não escrito à mão, e por um motivo: um documento separado
envelhece no primeiro dia em que alguém conserta um parser e não atualiza a
tabela. Aqui a declaração de cobertura vive ao lado do código que a implementa,
então `python -m ingestao cobertura` sempre diz a verdade sobre o que o pipeline
faz hoje.
"""
from collections import Counter

from ingestao import config
from ingestao.registry import FONTES

ROTULO = {
    "real": "✅ real",
    "parcial": "🟡 parcial",
    "bloqueado": "⛔ bloqueado",
    "interno": "🔒 interno (ERP)",
    "sintetico": "🔴 sintético",
}

ORDEM = ["sintetico", "bloqueado", "interno", "parcial", "real"]


def _tabela_resumo() -> list[str]:
    contagem = Counter(c.situacao for f in FONTES for c in f.cobertura)
    total = sum(contagem.values())
    linhas = ["| Situação | Alvos | % |", "|---|---:|---:|"]
    for s in ORDEM:
        n = contagem.get(s, 0)
        linhas.append(f"| {ROTULO[s]} | {n} | {100 * n / total:.0f}% |")
    linhas.append(f"| **total** | **{total}** | |")
    return linhas


def markdown() -> str:
    from datetime import date

    out = [
        "# Matriz de cobertura — o que o pipeline alimenta de verdade",
        "",
        "> **GERADO** por `python -m ingestao cobertura`. Não edite à mão: as",
        "> declarações vivem em `ingestao/fontes/*.py`, ao lado do parser que as",
        f"> implementa. Última geração: {date.today().isoformat()}.",
        "",
        "Legenda:",
        "",
        "- **✅ real** — fonte pública preenche o alvo, com vínculo direto ao cliente.",
        "- **🟡 parcial** — a fonte existe mas não fecha sozinha: nível agregado,",
        "  casamento probabilístico ou campo ausente. Entra com `confianca < 1`.",
        "- **⛔ bloqueado** — é pública mas não consumível por máquina hoje",
        "  (captcha, chave restrita, sem a chave de ligação). Exige passo manual.",
        "- **🔒 interno (ERP)** — não existe fonte pública, e nem deveria: é dado",
        "  comercial da Krilltech.",
        "- **🔴 sintético** — não há fonte pública nem dado interno. Tem de ser",
        "  inventado — e isso tem de aparecer na tela.",
        "",
        "## Resumo",
        "",
        *_tabela_resumo(),
        "",
        "## Por fonte",
        "",
    ]

    for f in FONTES:
        automacao = ("extract + transform" if f.extract and f.transform
                     else "só declaração (sem código de coleta)")
        out += [
            f"### {f.nome}",
            "",
            f"- **id:** `{f.id}` · **órgão:** {f.orgao} · **periodicidade:** {f.periodicidade}",
            f"- **endpoint:** {f.url}",
            f"- **automação:** {automacao}",
        ]
        if f.passo_manual:
            out.append(f"- **passo manual necessário:** {f.passo_manual}")
        out += ["", "| Alvo no grafo | Situação | Conf. | Nota |", "|---|---|---:|---|"]
        for c in sorted(f.cobertura, key=lambda x: ORDEM.index(x.situacao)):
            nota = c.nota.replace("|", "\\|")
            out.append(f"| `{c.alvo}` | {ROTULO[c.situacao]} | {c.confianca:.2f} | {nota} |")
        out.append("")

    out += [
        "## O que isso significa para o pitch",
        "",
        "Os dois vetores de MAIOR peso do motor de contágio são os de pior",
        "cobertura pública:",
        "",
        "| Vetor | Peso | De onde vem de verdade |",
        "|---|---:|---|",
        "| Mesmo grupo econômico | 0,90 | 🔒 cadastro da Krilltech — **não existe base pública de grupo econômico no Brasil** |",
        "| Avalista em comum | 0,85 | 🔒 contrato de aval, dado privado |",
        "| Sócio em comum (QSA) | 0,70 | 🟡 Receita, com CPF mascarado — casamento por nome + 6 dígitos |",
        "| Mesma região e cultura | 0,75 | 🟡 região real (IBGE) + choque real (Conab), mas cultura do cliente é interna |",
        "",
        "E o gatilho da demo — `pedido_rj` sobre um cliente específico — é o",
        "único elo que **nenhuma** fonte pública automatizável entrega: o DataJud",
        "tem os 1.291 pedidos de RJ do TJGO e, por desenho da Portaria CNJ",
        "160/2020, não tem as partes.",
        "",
        "A leitura honesta: **o Lastro é um sistema cuja espinha é o dado interno",
        "da Krilltech, enriquecido por fonte pública no contexto de risco.** O que",
        "o público entrega bem — e entrega de verdade, medido, não plantado — é",
        "dívida ativa com CNPJ (PGFN), embargo ambiental com CNPJ (IBAMA), quebra",
        "de safra (Conab), déficit de chuva (INMET), recorte territorial (IBGE) e",
        "pressão judicial regional (DataJud). Isso é contexto de primeira linha.",
        "Não é a carteira.",
        "",
    ]
    return "\n".join(out)


def escrever() -> None:
    destino = config.RAIZ / "COBERTURA.md"
    destino.write_text(markdown(), encoding="utf-8")
    print(f"  escrito: {destino}")
