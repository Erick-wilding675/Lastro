# Data Model

**Status:** revisado pós-pivô (13/09) — reconciliado contra o schema Cypher
efetivamente implementado (`src/db/cypher/01-schema-e-seed.cypher` e
`02-queries-motor.cypher`). Substitui as duas versões anteriores: o schema de
matching pessoa↔projeto ("Talent Graph") e o rascunho intermediário sob o
codinome "Rizoma", que já descrevia o domínio certo mas com nomes de relação
que não bateram com o que foi implementado.

**Produto:** Lastro
**Versão:** 2.0 — pós-hackathon, alinhado ao código
**Data:** 2026-09-13
**Paradigma:** Grafo — Neo4j (AuraDB, tier gratuito). Ver [ARD.md](ARD.md), ARD-01.

---

## Princípio

O schema existe para tornar **consultável o que a planilha esconde**: não
"quanto o cliente X deve", mas "quem mais cai junto com o cliente X, e por
quê". Toda aresta aqui é um vetor de contágio potencial ou uma dimensão de
decisão de recuperação — nada é modelado por completude (Hard Rule 5 em
[`../ai.md`](../ai.md)).

---

## Nós

### `Cliente`

| Campo | Exemplo real (seed) | Descrição |
|---|---|---|
| `id` | `CLI001` | PK |
| `nome` | "Agro Vale do Cerrado Ltda" | Razão social ou nome do produtor |
| `tipo` | `produtor_pj` / `produtor_pf` / `revenda` | Topologia do canal |
| `documento` | mascarado | CPF/CNPJ |
| `uf`, `municipio` | "GO", "Rio Verde" | Localização |
| `porte` | `pequeno` / `medio` / `grande` | Calibra expectativa de exposição |
| `situacao` | `adimplente` / `atraso` / `inadimplente` / `recuperacao_judicial` | Estado de crédito atual |
| `dias_atraso_max` | 98 | Maior atraso entre os recebíveis abertos |
| `cliente_desde` | `date('2019-03-11')` | Tempo de relacionamento — entra no índice de prioridade de recuperação |
| `exposicao_total` | calculado | **Derivado**: soma de `valor_aberto` dos recebíveis não quitados do cliente (materializado ao fim do seed para performance de UI) |
| `score`, `rating`, `score_decomposto`, `score_calculado_em` | calculado | Escritos por Q2 (ver [`matching-model.md`](matching-model.md)) |

### `Recebivel`

| Campo | Exemplo real | Descrição |
|---|---|---|
| `id` | `REC001` | PK |
| `valor`, `valor_aberto` | 890000.0 | Valor de face e saldo devedor atual |
| `data_emissao`, `data_vencimento` | datas | Base do aging |
| `dias_atraso` | 98 | |
| `status` | `aberto` / `vencido` / `recuperado` | Ciclo de vida |
| `garantia_tipo` | `nenhuma` / `aval` / `penhor_safra` / `cpr` / `alienacao_fiduciaria` | Determina o haircut aplicado no score (Q2) |
| `garantia_valor` | 600000.0 | Valor de face da garantia, antes do haircut |
| `estagio_juridico` | `nenhum` / `notificado` / `protestado` / `habilitado_rj` | Filtro duro de estratégia elegível (Q4) |

### `Socio`, `Avalista`, `GrupoEconomico`, `Regiao`, `Cultura`, `Safra`, `Imovel`, `Evento`

| Nó | Campos principais (seed) | Papel |
|---|---|---|
| `Socio` | id, nome, documento | Vínculo societário (fonte: QSA/Receita) — **vetor estrutural** de peso 0,70 |
| `Avalista` | id, nome, tipo (`pf`/`pj`), documento | Avalista comum a recebíveis de clientes diferentes — **vetor estrutural** de peso 0,85 |
| `GrupoEconomico` | id, nome | Clientes do mesmo grupo — **vetor estrutural** de peso 0,90 |
| `Regiao` | id, nome, uf | Base do canal sistêmico (clima, logística, preço regional) |
| `Cultura` | id, nome, ciclo_dias | Base do canal sistêmico (preço da commodity) |
| `Safra` | id, ano_agricola, status | Janela de caixa do recebível |
| `Imovel` | id, area_ha, embargo_ibama, reserva_legal_ok | Fonte SICAR/IBAMA — embargo vira red flag direta |
| `Evento` | id, tipo, data, fonte, severidade, descricao | O radar: `pedido_rj`, `protesto`, `execucao_fiscal`, `embargo_ambiental`, `quebra_safra`, `alteracao_qsa`, `alerta_zarc`, `queda_preco` — sempre com fonte e data |

### `EstrategiaRecuperacao`

| Campo | Exemplo real | Descrição |
|---|---|---|
| `id` | `EST-RENEG` | PK |
| `nome` | "Renegociação" | Nome de exibição — não é enum fechado no schema, é texto livre no catálogo |
| `custo_medio`, `prazo_medio_dias`, `taxa_sucesso_historica` | 1200.0 / 45 / 0.62 | Alimenta o índice de priorização (Q4) |
| `preserva_relacao` | `true`/`false` | Bônus de 30% no índice quando a estratégia preserva a relação comercial |
| `estagios_elegiveis` | `['nenhum','notificado']` | Filtro duro contra `Recebivel.estagio_juridico` |

Catálogo real do seed: Renegociação, Barter, Cobrança amigável, Acordo
parcelado, Reforço de garantia, Protesto, Execução judicial, Habilitação no
plano de RJ.

---

## Relações

Nomes e direções **confirmados linha a linha** contra o seed e as 5 queries
do motor — nada nesta tabela é hipótese.

| Relação | De → Para | Propriedades | Papel |
|---|---|---|---|
| `DE` | Recebivel → Cliente | — | De quem é o recebível (nota: sentido é Recebível→Cliente, não o inverso) |
| `GARANTIDO_POR` | Recebivel → Avalista | — | **Contágio estrutural**: mesmo avalista em recebíveis de clientes diferentes (peso 0,85) |
| `PERTENCE_A` | Cliente → GrupoEconomico | — | **Contágio estrutural** (peso 0,90) |
| `TEM_SOCIO` | Cliente → Socio | `participacao` | **Contágio estrutural**: sócio comum a dois clientes, 2 hops via o nó `Socio` (peso 0,70) |
| `OPERA_EM` | Cliente → Regiao | `hectares` | Base do canal sistêmico (junto com `PLANTA`, peso 0,75 com choque / 0,30 sem) |
| `PLANTA` | Cliente → Cultura | `hectares` | Base do canal sistêmico — sozinho, peso 0,40 |
| `COMPRA_VIA` | Cliente → Cliente (revenda) | `volume_safra` | Canal sistêmico: mesma revenda (peso 0,65) |
| `POSSUI` | Cliente → Imovel | — | Base para red flag de embargo IBAMA |
| `LOCALIZADO_EM` | Imovel → Regiao | — | Liga o imóvel (CAR/SICAR) à região |
| `REFERENTE_A` | Recebivel → Safra | — | Janela de caixa |
| `SOBRE` | Evento → Cliente | — | O radar aponta para quem o evento afeta; é a base de risco jurídico/agro do score e das red flags |
| `EXPOSTO_A` | Cliente (origem) → Cliente (vizinho) | `peso`, `caminho` (lista), `canais`, `calculado_em` | **Derivada** — calculada por Q1 a cada `POST /contagio/propagar/{origem}`. Guarda o caminho inteiro, não só o peso final: é a explicação materializada |
| `RECOMENDADA` | Cliente → EstrategiaRecuperacao | `valor_recuperavel_estimado`, `prazo_estimado`, `indice`, `calculado_em`, `executada_em`, `executada_por` | Materializa a recomendação (Q4). Quando um humano decide agir, `executada_em`/`executada_por` são setados na **mesma** aresta — não existe uma relação `EXECUTADA` separada; é a trilha de auditoria da decisão (Hard Rule 2) |

---

## Diagrama

```
        PERTENCE_A                              GARANTIDO_POR
 (GrupoEconomico)◀────(Cliente)────DE────(Recebivel)────────▶(Avalista)
        ▲                 │  │                                    ▲
        │ contágio 0.90   │  └─TEM_SOCIO──▶(Socio)◀──TEM_SOCIO────┘ (outro Cliente)
        │                 │        contágio 0.70      contágio 0.85 (via Recebivel⇄Avalista)
        │                 ├─OPERA_EM──▶(Regiao)◀──LOCALIZADO_EM──(Imovel)◀──POSSUI──(Cliente)
        │                 ├─PLANTA────▶(Cultura)         (canal sistêmico: 0.75 c/ evento, 0.30 s/, ou 0.40 só cultura)
        │                 ├─COMPRA_VIA▶(Cliente revenda)◀─COMPRA_VIA─(outro Cliente)   (contágio 0.65)
        │                 │
        │                 ├─EXPOSTO_A {peso, caminho, canais}──▶(outro Cliente)   [derivada, por Q1]
        │                 └─RECOMENDADA {indice, executada_em}──▶(EstrategiaRecuperacao)   [materializada, por Q4]
        │
   (Evento)──SOBRE──▶(Cliente)   [o radar — fonte, data, severidade]
```

---

## O motor de contágio (Q1)

A aresta `EXPOSTO_A` é calculada, não informada — ver a query completa em
[`../../src/db/cypher/02-queries-motor.cypher`](../../src/db/cypher/02-queries-motor.cypher).
Quando um `Cliente` de origem é acionado (`POST /contagio/propagar/{origem}`),
o motor varre os seis padrões abaixo em paralelo (`UNION`) e mantém o **maior**
peso por vizinho, com todos os caminhos concatenados:

**Canal estrutural** — o risco de um contamina o outro por vínculo jurídico ou
patrimonial, sempre peso cheio:

| Caminho | Peso |
|---|---|
| Mesmo `GrupoEconomico` (`PERTENCE_A`) | 0,90 |
| Mesmo `Avalista` (via `Recebivel-GARANTIDO_POR`) | 0,85 |
| Mesmo `Socio` (via `TEM_SOCIO`, fonte QSA) | 0,70 |

```cypher
// Mesmo grupo econômico — o vínculo mais direto (peso 0,90)
MATCH (c:Cliente)-[:PERTENCE_A]->(g:GrupoEconomico)<-[:PERTENCE_A]-(c2:Cliente)
WHERE c <> c2
RETURN c.nome, c2.nome, g.nome;

// Avalista em comum — o vínculo passa por DOIS recebíveis, não por Cliente
// direto: um avalista garante o título, não a carteira inteira (peso 0,85)
MATCH (c:Cliente)<-[:DE]-(:Recebivel)-[:GARANTIDO_POR]->(a:Avalista)
      <-[:GARANTIDO_POR]-(:Recebivel)-[:DE]->(c2:Cliente)
WHERE c <> c2
RETURN c.nome, c2.nome, a.nome;

// Sócio em comum, fonte QSA (peso 0,70)
MATCH (c:Cliente)-[:TEM_SOCIO]->(s:Socio)<-[:TEM_SOCIO]-(c2:Cliente)
WHERE c <> c2
RETURN c.nome, c2.nome, s.nome;
```

**Canal sistêmico** — ninguém contamina ninguém, todos sofrem a mesma causa
(seca, praga, queda de cotação). O peso cheio de região+cultura só vale **se
houver `Evento` do tipo `quebra_safra`/`alerta_zarc`/`queda_preco` nos últimos
365 dias apontando (`SOBRE`) para algum cliente da mesma região**; sem esse
evento, cai para 0,30:

| Caminho | Com choque confirmado | Sem evento regional |
|---|---|---|
| Mesma `Regiao` (`OPERA_EM`) **e** mesma `Cultura` (`PLANTA`) | 0,75 | 0,30 |
| Mesma revenda (`COMPRA_VIA`) | 0,65 | 0,65 |
| Mesma `Cultura` apenas | 0,40 | 0,40 |

```cypher
// Região + cultura em comum, com a checagem de evento que decide o peso —
// 0,75 com choque confirmado, 0,30 sem evento regional no período
MATCH (c:Cliente)-[:OPERA_EM]->(r:Regiao)<-[:OPERA_EM]-(c2:Cliente),
      (c)-[:PLANTA]->(cu:Cultura)<-[:PLANTA]-(c2)
WHERE c <> c2
OPTIONAL MATCH (ev:Evento)-[:SOBRE]->(:Cliente)-[:OPERA_EM]->(r)
  WHERE ev.tipo IN ['quebra_safra','alerta_zarc','queda_preco']
    AND ev.data >= date() - duration({days: 365})
WITH c, c2, r, cu, count(ev) > 0 AS choque
RETURN c.nome, c2.nome, r.nome, cu.nome,
       CASE WHEN choque THEN 0.75 ELSE 0.30 END AS peso;

// Mesma revenda — quebra do canal de venda, não do produtor (peso 0,65)
MATCH (c:Cliente)-[:COMPRA_VIA]->(rev:Cliente)<-[:COMPRA_VIA]-(c2:Cliente)
WHERE c <> c2
RETURN c.nome, c2.nome, rev.nome;
```

Essa condicional é o que impede a carteira inteira de acender quando um
cliente quebra por motivo próprio — a microrregião só fica vermelha quando
existe uma causa comum documentada, com fonte. No seed, é exatamente o
`EVT007` (quebra de safra confirmada pela Conab no Sudoeste Goiano) que faz
`CLI004` acender com peso 0,75 em vez de 0,30.

> **Por que isso exige grafo:** a consulta é multi-hop com pesos por tipo de
> aresta, reconstrução de caminho e um `UNION` de seis padrões — em SQL vira
> junção recursiva ilegível; em Cypher é uma query só (Q1).

---

## Decisões de modelagem

- **`Recebivel` é nó, não propriedade de `Cliente`.** Garantia, estágio
  jurídico e vencimento variam por título, não por cliente — o canal
  `GARANTIDO_POR` e o score (Q2) precisam de granularidade por título: um
  `Cliente` com cinco recebíveis pode ter um protestado e quatro em dia, e
  colapsar isso em campos do cliente perderia exatamente o que o motor
  precisa somar e filtrar. Hard Rule 5: toda aresta existe para responder uma
  pergunta de decisão, e "de quem é este título específico" é uma pergunta
  diferente de "quanto este cliente deve no total".

- **`GARANTIDO_POR` liga `Recebivel` a `Avalista`, não `Cliente` a
  `Avalista`.** Um avalista garante um título específico, não a carteira
  inteira de um devedor — por isso o caminho de "avalista em comum" atravessa
  necessariamente dois nós `Recebivel`
  (`(origem)<-[:DE]-(:Recebivel)-[:GARANTIDO_POR]->(a)<-[:GARANTIDO_POR]-(:Recebivel)-[:DE]->(v)`).
  Uma relação direta Cliente→Avalista inflaria o canal estrutural sempre que
  qualquer título do cliente tivesse aval, mesmo um já quitado.

- **O canal sistêmico só ganha peso cheio com `Evento` confirmado.** Sem essa
  condicional, todo vizinho de região e cultura acenderia junto assim que um
  cliente quebrasse por motivo idiossincrático (má gestão, por exemplo), o
  que contradiz a tese do produto: "produtor rural não quebra sozinho" não
  significa "todo vizinho quebra junto". A janela de 365 dias e a lista
  fechada de tipos de evento (`quebra_safra`, `alerta_zarc`, `queda_preco`)
  existem para manter esse peso auditável e não um chute — e para que a
  microrregião só fique vermelha quando existe uma causa comum documentada,
  com fonte (Hard Rule 3: exposição sempre explica o caminho).

- **`EXPOSTO_A` e `RECOMENDADA` são derivadas e materializadas
  (`calculado_em`), não recalculadas a cada leitura.** Duas razões: custo (Q1
  e Q4 percorrem o grafo inteiro a partir da origem; não compensa rodar isso
  a cada render de tela) e auditoria (o valor gravado é o que o sistema
  calculou naquele momento, com aquela versão de pesos — se os pesos mudarem
  depois, o histórico anterior não se reescreve silenciosamente).

- **Não existe uma relação `EXECUTADA` separada.** A execução de uma
  recomendação grava `executada_em`/`executada_por` na própria aresta
  `RECOMENDADA` (ver `EXECUTAR` em
  `src/backend/app/modules/recuperacao/queries.py`). O caso é um só, do
  diagnóstico à ação; separar em duas arestas obrigaria juntar duas
  entidades toda vez que se quisesse responder "o que foi feito com esta
  recomendação", sem nenhum ganho de consulta em troca — e é isso que
  sustenta a Hard Rule 2 (toda decisão tem trilha de auditoria: quem decidiu
  e quando ficam gravados junto com o que foi decidido).

- **`Safra` é nó, não string solta em `Recebivel`.** Hoje carrega só
  `ano_agricola` e `status`, mas existir como nó permite `REFERENTE_A`
  consultar "todos os recebíveis desta safra" sem parsing de string e
  suporta extensão futura (janela de plantio, preço médio da safra) sem
  migrar o schema de `Recebivel`.

- **`Regiao` do seed e `Regiao` do IBGE foram fundidas, não convivem
  duplicadas.** O seed criou `REG-GO-SUD` antes da malha real do IBGE existir
  no grafo; quando as duas cargas passaram a conviver, o canal sistêmico
  parava de atravessar entre clientes que na vida real estão na mesma
  microrregião. `03-completar-lacunas.cypher` (Bloco A) funde os nós e só
  apaga o antigo depois de confirmar que ficou sem nenhuma aresta —
  preferindo falha visível a perda silenciosa (Hard Rule 7).

---

## Regras de dados

- Toda informação que vem de fonte pública ou de inferência de IA carrega
  **fonte e data** (`Evento.fonte`, `Evento.data`) — nunca vira fato
  consolidado silenciosamente.
- **Cobertura de garantia usa haircut por tipo** antes de qualquer cálculo de
  score (Q2): alienação fiduciária 1,00; aval 0,70; CPR 0,60; penhor de safra
  0,50; nenhuma 0,00. Penhor de safra evapora com a seca e entra no concurso
  da RJ; alienação fiduciária é extraconcursal e sobrevive.
- `EXPOSTO_A` e `RECOMENDADA` são **derivadas e datadas** (`calculado_em`):
  nunca são fato do mundo, são o que o sistema calculou naquele momento —
  recalcular é seguro (`MERGE`, idempotente).
- A execução de uma recomendação não cria nó/relação nova: grava
  `executada_em`/`executada_por` na própria `RECOMENDADA` (Hard Rule 1 — o
  sistema nunca age, só registra que uma pessoa agiu).
- Dados pessoais de produtores são mascarados no dataset seed; nenhum
  documento real entra no repositório (Hard Rule 8).

---

## Notas de implementação (confirmadas, não mais em aberto)

- Krilltech vende via revenda: `COMPRA_VIA` está implementado e alimenta o
  canal sistêmico (peso 0,65).
- Pesos do contágio: mantidos como hipótese uniforme declarada e auditável
  (ver [`matching-model.md`](matching-model.md)) — calibração com histórico
  real é item de roadmap pós-MVP ([`project-canvas.md`](project-canvas.md),
  bloco 10).
- Volume do seed: 10 clientes, 10 recebíveis, 7 eventos, cenário de
  demonstração plantado (`CLI001` dispara, `CLI002`–`CLI005` acendem por
  vetores diferentes, `CLI006` é o controle que permanece verde).
- `Safra` é nó (não propriedade), para permitir consulta de janela de caixa
  por safra independente do recebível.
