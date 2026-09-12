# Pipeline de ingestão — fontes públicas reais → grafo

Alimenta o esquema de [`src/db/cypher/01-schema-e-seed.cypher`](../cypher/01-schema-e-seed.cypher)
com dado real, e **declara explicitamente o que não dá para alimentar**. O mapa
do que é real, parcial, bloqueado, interno ou necessariamente sintético está em
[`COBERTURA.md`](COBERTURA.md), que é gerado do próprio código.

## Como rodar

```bash
cd src/db/ingestao
pip install -r requirements.txt

# 1. a carteira é o filtro de tudo
cp carteira.example.csv carteira.csv     # e preencha com os clientes reais

# 2. dados internos do ERP (sem eles o grafo sai sem exposição — ver abaixo)
mkdir -p data/interno                     # layouts no docstring de
                                          # ingestao/fontes/interno_krilltech.py

# 3. credencial do AuraDB (reusa src/backend/.env se já existir)
cp .env.example .env

# 4. rodar
python -m ingestao fontes                 # o que existe e o que cada fonte faz
python -m ingestao extract                # baixa o bruto para data/raw/
python -m ingestao transform              # normaliza para data/staging/
python -m ingestao load                   # MERGE no Neo4j
python -m ingestao all                    # as três em sequência
python -m ingestao cobertura              # regenera COBERTURA.md

python -m ingestao extract --fonte conab --fonte ibama   # limita a fontes
```

`extract` e `transform` nunca tocam o banco. `load` é a única etapa que escreve,
e é idempotente: rodar duas vezes não duplica nada.

## O desenho, em uma frase

**O pipeline é puxado pela carteira, não pela fonte.** Ele não ingere o Brasil:
parte dos clientes que a Krilltech já tem e os enriquece nas bases públicas. É o
que torna viável (o arquivo da PGFN tem 1,3 GB) e defensável em LGPD — só se
consulta quem já é contraparte.

```
carteira.csv ─┐
              ├─► extract ──► data/raw/      (arquivo como a fonte publica)
data/interno/─┘       │
                      ▼
                  transform ──► data/staging/ (CSV normalizado, auditável)
                      │                        toda linha tem fonte + confianca
                      ▼
                    load ─────► Neo4j          MERGE idempotente
```

As três etapas são separadas porque falham por motivos diferentes: `extract` por
rede e mudança de URL, `transform` por mudança de layout, `load` por credencial e
constraint. Num script único, qualquer erro vira "não funcionou".

## Fontes, verificadas ao vivo em 12/09/2026

| Fonte | O que entrega | Liga ao cliente? |
|---|---|---|
| **PGFN** dívida ativa | execução fiscal, dívida ativa, CDA protestada, valor em R$ | ✅ publica CPF/CNPJ |
| **IBAMA** áreas embargadas | embargo ambiental vigente, imóvel, bioma | ✅ publica CPF/CNPJ |
| **Receita/QSA** (via BrasilAPI) | razão social, endereço, porte, CNAE, sócios | 🟡 CPF do sócio mascarado |
| **Conab** série de grãos | quebra de safra medida contra baseline de 5 safras | ❌ nível UF |
| **IBGE** malha territorial | microrregião oficial (o recorte de `:Regiao`) | ✅ pelo município |
| **IBGE/PAM** SIDRA 5457 | rendimento por município, quebra microrregional | ❌ nível município |
| **INMET** séries históricas | déficit de chuva na janela out–mar | ❌ nível UF |
| **CNJ/DataJud** | densidade de RJ e execução fiscal por microrregião | ❌ **não expõe as partes** |
| **SICAR** | código do CAR, área total, reserva legal | ⛔ bloqueado (captcha, sem CPF/CNPJ) |
| **Krilltech ERP** | recebíveis, garantias, avalistas, grupos, lavoura | 🔒 interno |

## As três conclusões que mudam o discurso

**1. O gatilho da demo não tem fonte pública automatizável.** O DataJud tem os
pedidos de RJ — 1.291 no TJGO, 161 no último ano — e, por desenho da Portaria
CNJ 160/2020, **não tem as partes**. `(:Evento{tipo:'pedido_rj'})-[:SOBRE]->(:Cliente)`
sai de DJE (PDF por comarca), de API comercial paga, ou da intimação que a
própria Krilltech recebe como credora. De fonte pública aberta, não sai.

**2. Os dois vetores de maior peso do motor são os de pior cobertura pública.**
Grupo econômico (0,90) não tem base pública no Brasil; avalista em comum (0,85)
é contrato privado. Sócio em comum (0,70) existe na QSA, mas com CPF mascarado,
então a identidade do sócio entre duas empresas é casamento por nome + 6 dígitos
— vai ao grafo com `confianca=0.85` e sustenta investigação, não decisão.

**3. Em troca, o canal sistêmico deixa de ser plantado e passa a ser medido.** O
`EVT007` que o seed inventava para justificar o peso 0,75 agora sai da série da
Conab. Exemplo real desta execução: GO / milho 2ª safra está em 5,0 t/ha contra
média de 5,64 das 5 safras anteriores — queda de 11,3%, severidade 0,43. E o
contraexemplo importa igual: GO / soja está 1% **acima** do baseline, apesar de
ter caído de 4,2 para 3,9 no ano — comparar com o ano anterior diria "queda de
7%", comparar com o baseline mostra que 4,2 foi safra excepcional.

## Duas decisões de modelagem que o motor precisa saber

### `:EventoRegional` é um rótulo separado de `:Evento`

Conab, INMET, PAM e DataJud produzem eventos de **região**, não de cliente. Eles
entram como `(:EventoRegional)-[:SOBRE_REGIAO]->(:Regiao)` — nunca como
`(:Evento)-[:SOBRE]->(:Cliente)`.

Se fossem o mesmo rótulo, a Q2 (score) e a Q3 (red flags) contariam uma seca
como fato sobre o cliente, e a matriz de red flags acenderia a carteira inteira
por causa de um evento climático. Para o canal sistêmico da Q1 consumir isso, a
travessia passa a ser explícita:

```cypher
MATCH (origem)-[:OPERA_EM]->(r:Regiao)<-[:OPERA_EM]-(v:Cliente),
      (origem)-[:PLANTA]->(cu:Cultura)<-[:PLANTA]-(v)
OPTIONAL MATCH (ev:EventoRegional)-[:SOBRE_REGIAO]->(r)
  WHERE ev.tipo IN ['quebra_safra','estiagem','alerta_zarc','queda_preco']
    AND ev.data >= date() - duration({days: 365})
```

Hoje a Q1 busca `(ev:Evento)-[:SOBRE]->(:Cliente)-[:OPERA_EM]->(r)`, que é o
jeito do seed. **Os dois funcionam**; o de cima é que é verdadeiro quanto à
origem do dado.

### Campo sem fonte não vira propriedade

O loader descarta campo vazio em vez de gravar `0` ou `''`. A QSA não publica
percentual de participação, então `TEM_SOCIO` sai **sem** `participacao` — não
com `participacao: 0.0`. Ausência e zero são coisas diferentes, e o componente de
score trata as duas de formas opostas: ausência ele ignora, zero ele usa como
medição.

## Sem `data/interno/`, o que o grafo perde

Recebível, garantia, avalista, grupo econômico, dias de atraso e o que o produtor
plantou são **todos** internos. Sem eles o grafo sai com clientes, regiões,
culturas e eventos públicos — mas sem exposição em R$, e portanto sem score, sem
matriz de red flags e sem recomendação de estratégia. O motor inteiro depende do
ERP. O pipeline público é o contexto de risco, não a carteira.

Se o time decidir gerar sintético para o que falta, o sintético tem de entrar com
`fonte='SINTÉTICO — demo'` e nunca herdar `'Krilltech — ERP'`. O
`01-schema-e-seed.cypher` é exatamente isso: sintético declarado.

## Limites conhecidos que não estão resolvidos

- **Carga irregular do DataJud.** O módulo conta por agregação (`size: 0` +
  `track_total_hits`), então não há mais truncamento — mas a alimentação da base
  pelos tribunais é irregular **por classe e por vara**. Caso real: TJSP, classe
  129, município de São Paulo tem `2022:13 · 2023:6 · 2024:0 · 2025:44 ·
  2026:118`. Uma vara de RJ em São Paulo não teve zero pedidos em 2024 — o ano
  não foi alimentado. Lido de forma ingênua isso virava "34x acima da média". O
  módulo detecta o ano vazio e **se recusa a medir**, gravando o motivo em
  `staging/analise_datajud.csv`. O que sobra é sinal: Porto Alegre com execução
  fiscal 3,27x acima da média dos 4 anos anteriores.
- **`dataAjuizamento` corrompido na origem.** Há processos datados de 2206, 4201
  e 8007 (visto em TJSP e TJRS). A query tem teto em "hoje" — sem ele, um
  processo de 2206 cai na janela dos últimos 365 dias.
- **Baseline do INMET.** Cada safra out–mar atravessa dois arquivos anuais e o
  ano mais antigo baixado nunca tem seu out–dez, então N safras completas exigem
  N+2 anos de ZIP. Com o padrão (5 anos) saem 3 safras completas, 2 de baseline,
  abaixo do mínimo de 3 — e o módulo corretamente **não emite evento**, gravando
  o motivo em `staging/analise_chuva.csv`. Para o INMET valer use
  `LASTRO_INMET_ANOS=6` ou mais (~500 MB).
- **Granularidade de Conab e INMET.** Publicam por UF. Um evento em `GO` se liga
  a todas as microrregiões do estado, inclusive as que não quebraram. A
  propriedade `granularidade='uf'` no evento marca isso no grafo.
- **Estação INMET → microrregião.** A estação tem lat/long, não município. O
  join espacial contra a malha do IBGE não está implementado;
  `staging/estacoes_inmet.csv` guarda lat/long para viabilizá-lo depois.
- **`queda_preco` nunca dispara.** O motor lista esse gatilho no canal
  sistêmico, mas a série histórica de grãos da Conab não traz preço (está em
  outra base, SIMA, não coberta aqui).

## Nada de dado real no repositório

`.gitignore` exclui `data/raw/`, `data/staging/`, `data/interno/`, `carteira.csv`
e `.env`. Só os layouts e os exemplos com placeholder são versionados —
Hard Rule #8.
