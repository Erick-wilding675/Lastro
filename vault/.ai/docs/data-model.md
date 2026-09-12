# Data Model

**Status:** Reescrito em 11/09 para o domínio do case KRILLTECH (risco relacional e recuperação de recebíveis). Substitui o schema de formação de squads. **Este é o documento que o time de dados/backend implementa primeiro.**

**Projeto:** Rizoma
**Versão:** 1.0 — Pivô de domínio
**Data:** 2026-09-11
**Paradigma:** Grafo — Neo4j (AuraDB, tier gratuito). Ver [ARD.md](ARD.md), ARD-01 (decisão preservada no pivô).

---

## Princípio

O schema existe para tornar **consultável o que a planilha esconde**: não "quanto o cliente X deve", mas "quem mais cai junto com o cliente X, e por quê". Toda aresta aqui é um vetor de contágio potencial ou uma dimensão de decisão de recuperação — nada é modelado por completude.

---

## Nós

### `Cliente`

| Campo | Tipo | Descrição |
|---|---|---|
| id | uuid | PK |
| nome | string | Razão social ou nome do produtor |
| tipo | enum: `produtor_pf` / `produtor_pj` / `revenda` / `distribuidor` | Topologia do canal |
| documento | string | CPF/CNPJ (mascarado no seed) |
| uf, municipio | string | Localização — liga em `Regiao` |
| porte | enum: `pequeno` / `medio` / `grande` | Calibra expectativa de exposição |
| situacao | enum: `adimplente` / `atraso` / `inadimplente` / `recuperacao_judicial` / `renegociado` | Estado de crédito atual |
| dias_atraso_max | int | Maior atraso entre os recebíveis abertos |
| exposicao_total | float | R$ em aberto — **derivado**, materializado para performance de UI |
| cliente_desde | date | Tempo de relacionamento — entra na dimensão de valor comercial |

### `Recebivel`

| Campo | Tipo | Descrição |
|---|---|---|
| id | uuid | PK |
| valor | float | Valor de face |
| valor_aberto | float | Saldo devedor atual |
| data_emissao, data_vencimento | date | Base do aging |
| dias_atraso | int | Derivado |
| safra | string | Ex.: "2025/26" — casa a cobrança com o ciclo de caixa do produtor |
| status | enum: `aberto` / `vencido` / `renegociado` / `recuperado` / `perdido` / `em_acordo` | Ciclo de vida |
| garantia_tipo | enum: `nenhuma` / `aval` / `penhor_safra` / `cpr` / `hipoteca` / `seguro` | Determina estratégias elegíveis |
| garantia_valor | float | Cobertura |
| estagio_juridico | enum: `nenhum` / `notificado` / `protestado` / `judicial` / `habilitado_rj` | Filtro duro de estratégia |

### `Avalista`, `GrupoEconomico`, `Regiao`, `Cultura`, `Safra`

| Nó | Campos principais | Papel no contágio |
|---|---|---|
| `Avalista` | id, nome, documento, tipo (`pf`/`pj`), exposicao_agregada | **Vetor forte** — um avalista comum a vários devedores concentra risco silenciosamente |
| `GrupoEconomico` | id, nome | **Vetor forte** — quebra de um membro contamina o grupo |
| `Regiao` | id, nome, uf, microrregiao | **Vetor médio** — clima, logística e preço são regionais |
| `Cultura` | id, nome, ciclo_dias | **Vetor médio** — margem de soja/milho move a carteira inteira junto |
| `Safra` | id, ano_agricola, cultura_ref | Janela de caixa: define **quando** cobrar faz sentido |

### `EstrategiaRecuperacao`

| Campo | Tipo | Descrição |
|---|---|---|
| id | uuid | PK |
| nome | enum: `renegociacao` / `barter` / `cobranca_amigavel` / `acordo_parcelado` / `protesto` / `judicial` / `securitizacao` / `habilitacao_rj` | Catálogo de ações |
| custo_medio | float | Custo operacional/jurídico por caso |
| prazo_medio_dias | int | Tempo típico até o caixa voltar |
| taxa_sucesso_historica | float | Alimentada pela memória de recuperação |
| preserva_relacao | bool | Barter e renegociação preservam; judicial e protesto queimam |
| estagios_elegiveis | list\<enum\> | Quais `estagio_juridico` aceitam esta estratégia |

---

## Relações

| Relação | De → Para | Propriedades | Papel |
|---|---|---|---|
| `DEVE` | Cliente → Recebivel | — | Exposição direta |
| `GARANTIDO_POR` | Recebivel → Avalista | `tipo_garantia` | **Contágio forte**: avalista compartilhado |
| `PERTENCE_A` | Cliente → GrupoEconomico | — | **Contágio forte** |
| `SOCIO_EM_COMUM` | Cliente → Cliente | `qtd_socios_comuns` | **Contágio forte**: vínculo societário oculto |
| `COMPRA_VIA` | Cliente → Cliente (revenda) | `volume_safra` | Contágio médio: quebra de canal |
| `OPERA_EM` | Cliente → Regiao | `hectares` | Contágio médio: clima/logística |
| `PLANTA` | Cliente → Cultura | `hectares`, `safra_ref` | Contágio médio: preço da commodity |
| `REFERENTE_A` | Recebivel → Safra | — | Janela de caixa |
| `EXPOSTO_A` | Cliente → Cliente | `peso`, `caminho`, `calculado_em` | **Derivada** — aresta de contágio calculada pelo motor. Guarda o caminho que a produziu, para explicação |
| `RECOMENDADA` | Cliente → EstrategiaRecuperacao | `score_decomposto`, `valor_recuperavel_estimado`, `prazo_estimado`, `calculado_em` | Herdeira direta de `RECOMENDADO_PARA` (ARD-05): materializa a explicação, não recalcula |
| `EXECUTADA` | Cliente → EstrategiaRecuperacao | `data`, `resultado`, `valor_recuperado`, `prazo_real` | **Memória de recuperação** — é isto que faz o sistema aprender |

---

## Diagrama

```
            GARANTIDO_POR                    PERTENCE_A
  (Avalista)◀──────────(Recebivel)      (GrupoEconomico)
      ▲                     ▲                   ▲
      │ contágio forte      │ DEVE              │ contágio forte
      │                     │                   │
      └──────────────  (CLIENTE)  ──────────────┘
                         │ │ │ │
        SOCIO_EM_COMUM ◀─┘ │ │ └─▶ OPERA_EM ─▶ (Regiao)
        (outro Cliente)    │ └───▶ PLANTA ───▶ (Cultura)
                           │
                           ├─▶ EXPOSTO_A {peso, caminho} ─▶ (outro Cliente)   [derivada]
                           ├─▶ RECOMENDADA {score_decomposto} ─▶ (Estrategia)  [materializada]
                           └─▶ EXECUTADA {resultado, valor_recuperado} ─▶ (Estrategia)  [memória]
```

---

## O motor de contágio

A aresta `EXPOSTO_A` é calculada, não informada. Quando um `Cliente` muda para `recuperacao_judicial` ou `inadimplente`, o motor percorre o grafo a partir dele e atribui peso decrescente por tipo e distância do vínculo:

**Canal estrutural** — o risco de um contamina o outro por vínculo jurídico ou
patrimonial:

| Caminho | Peso |
|---|---|
| Mesmo `GrupoEconomico` | 0,90 |
| Mesmo `Avalista` | 0,85 |
| Mesmo `Socio` (via `TEM_SOCIO`, fonte QSA) | 0,70 |

**Canal sistêmico** — ninguém contamina ninguém, todos sofrem a mesma causa
(seca, praga, queda de cotação). Só entra com peso cheio **se houver evento
regional confirmando o choque** (`quebra_safra`, `alerta_zarc`, `queda_preco`
nos últimos 365 dias); sem evento, entra reduzido:

| Caminho | Com choque confirmado | Sem evento regional |
|---|---|---|
| Mesma `Regiao` + mesma `Cultura` | 0,75 | 0,30 |
| Mesma revenda (`COMPRA_VIA`) | 0,65 | 0,65 |
| Mesma `Cultura` apenas | 0,40 | 0,40 |

Essa condicional é o que impede a carteira inteira de acender quando um cliente
quebra por motivo próprio. A microrregião só fica vermelha quando existe uma
causa comum documentada, com fonte.

Pesos multiplicam a cada hop adicional (decaimento), e o caminho percorrido é gravado em `EXPOSTO_A.caminho` — é isso que permite dizer ao gestor **"este cliente acendeu porque compartilha avalista com o produtor que entrou em RJ ontem"**, em vez de mostrar um número sem origem. Pesos são hipótese inicial, auditável e ajustável (mesmo princípio da Tese: peso é hipótese, não verdade).

> **Por que isso exige grafo:** a consulta é multi-hop com pesos por tipo de aresta e reconstrução de caminho. Em SQL vira junção recursiva ilegível; em Cypher é uma query. É a justificativa técnica do Neo4j no pitch (Viabilidade Técnica, 25%).

---

## Regras de Dados

- Toda informação carrega **fonte e confiança** quando vier de inferência de IA ou de documento extraído — nunca vira fato consolidado silenciosamente. É o que sustenta a trilha de auditoria da decisão de crédito.
- **Cobertura de garantia usa haircut por tipo** antes de qualquer cálculo:
  alienação fiduciária 1,00; aval 0,70; CPR 0,60; penhor de safra 0,50; nenhuma
  0,00. Penhor de safra evapora com a seca e entra no concurso da RJ; alienação
  fiduciária é extraconcursal e sobrevive. O schema guarda `garantia_tipo` e
  `garantia_valor` justamente para permitir essa ponderação.
- `EXPOSTO_A` e `RECOMENDADA` são **derivadas e datadas** (`calculado_em`): nunca são tratadas como fato do mundo, e sim como o que o sistema calculou naquele momento.
- `EXECUTADA` é imutável — é o registro histórico que alimenta `taxa_sucesso_historica`. Corrigir um resultado cria um novo registro, não sobrescreve.
- Dados pessoais de produtores são mascarados no dataset seed; nenhum documento real entra no repositório.

---

## Questões em Aberto

| # | Questão | Owner | Status |
|---|---|---|---|
| 1 | Krilltech vende via revenda? Se não, `COMPRA_VIA` sai do schema | Erick / empresa | Open |
| 2 | Pesos iniciais do contágio — calibrar com quem conhece o agro, ou manter hipótese uniforme documentada | Erick | Open |
| 3 | Volume do seed: quantos clientes, recebíveis e clusters para a demo ficar convincente sem pesar o AuraDB free | Erick + dados | Open |
| 4 | `Safra` como nó ou como propriedade — hoje está como nó para permitir janela de caixa por safra; confirmar na implementação | Backend | Open |
