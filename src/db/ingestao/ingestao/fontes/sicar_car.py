"""SICAR / CAR — Cadastro Ambiental Rural. Fonte BLOQUEADA, declarada aqui.

Este módulo não baixa nada. Existe para que a lacuna fique no código e no
relatório de cobertura, e não só na cabeça de quem investigou.

O QUE O SICAR TERIA. É a única base que fecha imóvel rural com precisão:
código do CAR, perímetro, área total, área de reserva legal, APP, e situação
do cadastro. Preencheria `:Imovel.id` (código do CAR de verdade, não o número
de um termo de embargo), `:Imovel.area_ha` e `:Imovel.reserva_legal_ok` — os
três campos que o seed tem e o IBAMA não cobre.

POR QUE NÃO DÁ. A consulta pública (consultapublica.car.gov.br) exige captcha
por download e serve shapefile por estado, não por proprietário. E, mais
importante para o caso de uso: por força de decisão sobre dados pessoais, o
download público NÃO traz o CPF/CNPJ do proprietário. Então mesmo com o
shapefile na mão não existe a chave que liga o imóvel ao cliente — que é
exatamente o que o grafo precisa.

COMO RESOLVER DE VERDADE, em ordem de custo:
  1. O próprio cliente entrega o recibo do CAR. É rotina em crédito rural: o
     banco já pede o CAR para liberar custeio. A Krilltech pode pedir igual.
     Vira dado interno, com fonte documental — melhor que qualquer raspagem.
  2. Convênio/API institucional com o Serviço Florestal Brasileiro.
  3. Shapefile estadual + join espacial contra a geometria do embargo do IBAMA
     (que é pública e traz WKT_GEOM_AREA_EMBARGADA). Isso recupera o código do
     CAR dos imóveis EMBARGADOS, que é um subconjunto útil mas enviesado.

A opção 1 é a que está recomendada. As outras duas são trabalho de semanas para
cobrir o que um e-mail ao cliente resolve.
"""
from ingestao.fontes.base import Cobertura, Fonte

FONTE = Fonte(
    id="sicar",
    nome="SICAR — Cadastro Ambiental Rural",
    url="https://consultapublica.car.gov.br/",
    orgao="Serviço Florestal Brasileiro",
    periodicidade="contínua",
    extract=None,
    transform=None,
    passo_manual=(
        "Pedir ao cliente o recibo de inscrição no CAR (rotina em credito "
        "rural) e carregar como dado interno em data/interno/imoveis.csv. "
        "Alternativa institucional: convenio com o SFB."),
    cobertura=[
        Cobertura(":Imovel.id (codigo do CAR)", "bloqueado", 0.0,
                  "Consulta publica com captcha, shapefile por estado."),
        Cobertura(":Imovel.area_ha (area total)", "bloqueado", 0.0,
                  "So o SICAR tem area total. O IBAMA tem area EMBARGADA, que e "
                  "coisa diferente e menor."),
        Cobertura(":Imovel.reserva_legal_ok", "bloqueado", 0.0,
                  "Exclusivo do SICAR."),
        Cobertura("(:Imovel)-[:LOCALIZADO_EM]->(:Regiao)", "parcial", 0.9,
                  "Derivavel do municipio do imovel quando ele vem do IBAMA; "
                  "para os imoveis sem embargo, nao ha imovel no grafo."),
        Cobertura("Chave imovel -> cliente", "bloqueado", 0.0,
                  "O download publico do CAR NAO traz CPF/CNPJ do proprietario. "
                  "Sem essa chave o shapefile nao liga ao grafo, mesmo baixado."),
    ],
)
