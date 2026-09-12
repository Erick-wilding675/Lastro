"""Registro das fontes. A ORDEM É DEPENDÊNCIA, não preferência.

`qsa` precisa vir antes de `ibge_regioes` porque é a Receita que devolve o
código do município. `ibge_regioes` precisa vir antes de `ibge_pam` e de
`datajud` porque os dois situam o dado por microrregião, e o de-para
município→microrregião sai dele. O resto é independente.
"""
from ingestao.fontes import (
    conab_safra,
    cvm_cias,
    datajud,
    ibama_embargos,
    ibge_pam,
    ibge_regioes,
    inmet_clima,
    interno_krilltech,
    pgfn_dau,
    qsa_cnpj,
    sicar_car,
    sintetico,
)

FONTES = [
    interno_krilltech.FONTE,  # primeiro: é o núcleo; sem ele não há exposição
    qsa_cnpj.FONTE,           # resolve código de município para os seguintes
    cvm_cias.FONTE,           # situação de insolvência da companhia registrada
    ibge_regioes.FONTE,       # resolve microrregião para os seguintes
    ibge_pam.FONTE,
    conab_safra.FONTE,
    inmet_clima.FONTE,
    pgfn_dau.FONTE,
    ibama_embargos.FONTE,
    datajud.FONTE,
    sicar_car.FONTE,          # sem extract/transform: declara a lacuna
    sintetico.FONTE,          # por ultimo: le o staging de todos os outros
]

POR_ID = {f.id: f for f in FONTES}


def resolver(ids: list[str] | None):
    """Nomes de fonte -> objetos Fonte, preservando a ordem de dependência."""
    if not ids:
        return [f for f in FONTES if f.extract or f.transform]
    desconhecidas = [i for i in ids if i not in POR_ID]
    if desconhecidas:
        raise SystemExit(f"Fonte desconhecida: {', '.join(desconhecidas)}.\n"
                         f"Disponiveis: {', '.join(POR_ID)}")
    return [f for f in FONTES if f.id in ids]
