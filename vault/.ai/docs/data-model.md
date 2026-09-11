# Data Model

<!--
  As entidades que o sistema armazena, seus campos/tipos, e como se
  relacionam. Segundo documento da fase de modelagem (Step 3b). Depende do
  SRS e dos use cases. Aqui é onde o Talent Model e o Project Genome (da
  Tese) viram schema.
-->

**Status:** Aprovado por Erick em 10/09 (proposta de schema + as 4 decisões de modelagem abaixo, aprovadas em bloco). **Adendo do Step 4 (11/09):** relação `RECOMENDADO_PARA` adicionada — ver seção de Relações e Regras de Dados.

**Projeto:** Talent Graph
**Versão:** 0.1 — Rascunho
**Data:** 2026-09-10
**Paradigma:** Grafo — Neo4j (AuraDB, tier gratuito). Ver [ARD.md](ARD.md), ARD-01.

> **Fonte:** `TeseTalent_Graph_IBM.pdf`, seções II (Talent Model) e III (Project Model) — as cinco dimensões de cada modelo já estão definidas lá; este arquivo vira o schema Neo4j (nós, relações, propriedades) para o MVP.

---

## Decisões de modelagem (Step 3b, aprovadas em bloco por Erick em 10/09)

Estas quatro decisões resolvem lacunas que a Tese deixa deliberadamente conceituais (ela não assume um banco específico) e que só faziam sentido depois do ARD-01 (Neo4j):

1. **Fonte/confiança nas propriedades escalares do `Projeto`:** **não** replicadas campo a campo. Justificativa: o Step 2 já decidiu que, no build do MVP, a criação de projeto acontece **só por elicitação direta** (extração documental fica conceitual, só para o pitch — ver SRS.md, FR-08 correlato e a resposta de Erick ao Step 2, item 3). Como existe apenas uma origem possível no MVP em execução, todo `Projeto` carrega uma única propriedade `fonte: "elicitação_direta"` no nó inteiro — rastreabilidade real (fonte + confiança por campo) é reservada para onde a Tese realmente exige comparação de força de evidência: as relações `TEM_COMPETENCIA` e `REQUER_COMPETENCIA`, que alimentam o Matching Model e cujo score depende exatamente dessa força (Tese, Nível 1, item 1).
2. **Isolamento da nota de avaliação:** só na camada de aplicação/orquestração, não no banco. O MVP não implementa autenticação multi-papel (NFR-04, Fora de Escopo no SRS — Alta Gestão e Talento são só narrativa de pitch, ver use-cases.md UC-06/07). Na prática, existe um único papel autenticado rodando o sistema (Gestor de Projetos), então a "restrição de acesso" da Tese (item 11) vira uma regra de **apresentação**: a UI e os agentes de explicação nunca renderizam a relação `AVALIADO_EM` fora do fluxo de decisão de formação de squad — nunca é exposta como um "registro de fato" comum. Fica registrado aqui como simplificação deliberada de escopo, não como a governança final (ver [harness.md](../harness.md), Governança — "a definir: modelo de autenticação/autorização do MVP").
3. **Requisitos e Escopo / Tecnologia e Decisões de Arquitetura são descritivas, não entram na matemática do Matching:** confirmado. Nem o Resumo Técnico nem a Tese listam essas duas dimensões entre os componentes de Nível 1 (Competências, Papéis, Interesse, Experiência Contextual, Disponibilidade) ou Nível 2 (Cobertura, Complementaridade, Distribuição de Experiência, Disponibilidade Agregada, Colaboração). Elas existem no grafo só como propriedades do nó `Projeto`, para popular a UI e a narrativa do pitch — não são lidas por nenhum agente de matching.
4. **Squad é um conceito derivado, não um nó próprio.** Não existe otimização de portfólio no MVP (Nível 3 fora do escopo) e cada `Projeto` tem exatamente um squad ativo por vez — logo "o squad do projeto X" é só o conjunto de relações `PARTICIPOU_DE` ativas apontando para aquele `Projeto`, sem necessidade de um nó `Squad` redundante para manter sincronizado. A animação de "matching em movimento" (UC-02) é um problema de **apresentação/orquestração** — o grafo armazena o resultado final (relações + os scores decompostos que a explicação usa), o frontend anima a revelação dimensão por dimensão a partir desses dados já calculados.

---

## Entidades (Nós)

### Pessoa (Talent Model)

<!-- Cinco dimensões da Tese: Competências, Preferências e Interesses, Papéis, Disponibilidade, Histórico de Colaboração. -->

| Campo | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | uuid | PK | Identificador único (dataset seed). |
| nome | string | obrigatório | Nome do talento fictício. |
| disponibilidade_atual | enum: `livre` / `parcial` / `indisponível` | obrigatório | Filtro de elegibilidade (Tese, Nível 1 — disponibilidade funciona como filtro, não como comparação). |
| tipo_disponibilidade | enum: `execução` / `mista` | default `execução` | Distingue quem acumula coordenação além de projetos (Tese, Talent Model item 10 — "disponibilidade mista"). |
| projetos_simultaneos | int | ≥ 0 | Quantidade de projetos ativos no momento — suporta o filtro de disponibilidade. |

**Relacionamentos:** `TEM_COMPETENCIA`, `PARTICIPOU_DE`, `PREFERE_PAPEL`, `TEM_INTERESSE`, `COLABOROU_COM`, `AVALIADO_EM` — ver seção Relações.

### Projeto (Project Model / Project Genome)

<!-- Cinco dimensões da Tese: Problema e Contexto, Requisitos e Escopo, Competências e Papéis Necessários, Tecnologia e Decisões de Arquitetura, Complexidade e Estágio. -->

| Campo | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | uuid | PK | Identificador único do projeto. |
| fonte | constante `"elicitação_direta"` | obrigatório | Ver Decisão de modelagem #1 — única origem possível no MVP em execução. |
| problema | string | obrigatório | O que o projeto pretende resolver (dimensão Problema e Contexto). |
| publico_alvo | string | obrigatório | Para quem o problema é relevante. |
| dominio | string | obrigatório | Domínio/mercado do projeto — mesma taxonomia usada em `TEM_INTERESSE`. |
| evidencia_problema | string | opcional | Pesquisa, demanda observada ou hipótese não validada. |
| funcionalidades_essenciais | list\<string\> | obrigatório | Dimensão Requisitos e Escopo — descritiva (Decisão #3). |
| funcionalidades_desejaveis | list\<string\> | opcional | idem |
| fora_de_escopo | list\<string\> | opcional | idem |
| criterios_sucesso | list\<string\> | opcional | idem |
| stack_tecnologica | string | opcional | Dimensão Tecnologia e Decisões de Arquitetura — descritiva (Decisão #3). |
| decisoes_arquitetura | string | opcional | idem |
| complexidade_tecnica | enum/escala | obrigatório | Eixo 1 de 3 (Tese, item 9). |
| complexidade_produto | enum/escala | obrigatório | Eixo 2 de 3. |
| complexidade_mercado | enum/escala | obrigatório | Eixo 3 de 3 — "o quanto o contexto competitivo/regulatório impõe dificuldade adicional". |
| estagio | enum: `ideação` / `validação de hipótese` / `construção de MVP` / `validação com usuários reais` / `tração inicial` / `escala` | obrigatório | Tese, item 9 — muda ao longo do tempo. |

**Relacionamentos:** `REQUER_COMPETENCIA`, `REQUER_PAPEL` — ver seção Relações. **Não** registra quem já trabalhou no projeto (isso vive só em `PARTICIPOU_DE`/`COLABOROU_COM` do lado de `Pessoa` — Hard Rule 3 do [ai.md](../ai.md), evita a duplicação que a própria Tese identifica como erro).

### Competencia (taxonomia compartilhada)

| Campo | Tipo | Descrição |
|---|---|---|
| id | uuid | PK |
| nome | string | Ex.: "Python", "Arquitetura de Software", "Educação" (técnica / metodológica / domínio — Tese, Talent Model item 4). |
| categoria | enum: `técnica` / `metodológica` / `domínio` | Mesma taxonomia usada por Pessoa e Projeto. |

### Papel (taxonomia compartilhada)

| Campo | Tipo | Descrição |
|---|---|---|
| id | uuid | PK |
| nome | string | Ex.: "Engenheiro de Dados", "Product Owner". |

### Dominio (taxonomia compartilhada — interesses/preferências)

| Campo | Tipo | Descrição |
|---|---|---|
| id | uuid | PK |
| nome | string | Mesma taxonomia usada em `Projeto.dominio` e em `TEM_INTERESSE`. |

---

## Relações

| Relação | De → Para | Propriedades | Dimensão da Tese |
|---|---|---|---|
| `TEM_COMPETENCIA` | Pessoa → Competencia | `fonte` (projeto realizado em conjunto / artefato público / perfil autodeclarado / conversa direta / inferência de IA), `confianca` | Competências (item 4) + Evidência e Fonte (item 5) |
| `REQUER_COMPETENCIA` | Projeto → Competencia | `indispensavel` (bool), `fonte`, `confianca` | Competências e Papéis Necessários (item 7) |
| `PARTICIPOU_DE` | Pessoa → Projeto | `papel`, `periodo_inicio`, `periodo_fim`, `resultado` | Dupla função: evidência de competência **e** histórico de colaboração no mesmo registro (Tese, item 6 — "não é mais necessário duplicar") |
| `PREFERE_PAPEL` | Pessoa → Papel | `origem: "preferência declarada"` | Papéis — papel desejado, nunca exercido (peso menor que papel comprovado) |
| `REQUER_PAPEL` | Projeto → Papel | `indispensavel_desde_inicio` (bool) | Competências e Papéis Necessários (item 7) |
| `TEM_INTERESSE` | Pessoa → Dominio | — | Preferências e Interesses |
| `COLABOROU_COM` | Pessoa → Pessoa | `projeto_id`, `papeis`, `periodo`, `resultado` | Histórico de Colaboração — **registro de fato**, visível a qualquer pessoa com acesso ao Talent Model (Tese, item 11.a) |
| `AVALIADO_EM` | Pessoa → Pessoa | `projeto_id`, `nota`, `autor_id` | Histórico de Colaboração — **nota de avaliação**, acesso restrito por regra de apresentação (Decisão de modelagem #2; Tese, item 11.b) |
| `RECOMENDADO_PARA` | Pessoa → Projeto | `score_decomposto` (por dimensão de Nível 1/2) | **Adendo Step 4 (ARD-05):** materializa o resultado do Matching Model — não é recalculado a cada consulta. Base técnica da Memória Organizacional (UC-05) e da explicação que a UI consome sem expor números crus (NFR-02). |

---

## Diagrama Entidade-Relacionamento

```
                 TEM_COMPETENCIA {fonte, confiança}
   ┌─────────┐ ─────────────────────────────────▶ ┌──────────────┐
   │ PESSOA  │                                     │ COMPETENCIA  │
   │ id  PK  │ ◀───────────────────────────────── │ id  PK        │
   └─────────┘   REQUER_COMPETENCIA {indispensável, fonte, confiança}
     │  │  │                                       ┌──────────────┐
     │  │  └── PREFERE_PAPEL ──────────────────▶  │ PAPEL        │
     │  │                                          │ id  PK        │
     │  │      REQUER_PAPEL {indispensável_inicio} └──────────────┘
     │  │                        (Projeto ──────────────▲)
     │  │
     │  └── TEM_INTERESSE ───────────────────────▶ ┌──────────────┐
     │                                              │ DOMINIO      │
     │      PARTICIPOU_DE {papel, período, resultado}└──────────────┘
     └──────────────────────────────────────────▶ ┌──────────────┐
                                                    │ PROJETO      │
     COLABOROU_COM {projeto_id, papéis, período,   │ id  PK        │
     resultado}  (Pessoa ──▶ Pessoa, registro de   └──────────────┘
     fato — visível a todos)

     AVALIADO_EM {projeto_id, nota, autor_id}
     (Pessoa ──▶ Pessoa, nota de avaliação — acesso restrito,
     nunca renderizada fora do fluxo de decisão de squad)
```

---

## Enumerações & Tipos Compartilhados

| Tipo | Valores / forma | Usado por |
|---|---|---|
| Competência (taxonomia compartilhada) | técnica / metodológica / domínio | `Pessoa` (via `TEM_COMPETENCIA`), `Projeto` (via `REQUER_COMPETENCIA`) |
| Papel (taxonomia compartilhada) | livre, definida pelo seed (ex.: Engenheiro de Dados, PO) | `Pessoa` (via `PARTICIPOU_DE`/`PREFERE_PAPEL`), `Projeto` (via `REQUER_PAPEL`) |
| Domínio (taxonomia compartilhada) | livre, definida pelo seed (ex.: educação, saúde, jurídico) | `Projeto.dominio`, `Pessoa` (via `TEM_INTERESSE`) |
| Fonte | projeto realizado em conjunto / artefato público / perfil autodeclarado / conversa ou observação direta / inferência de IA | `TEM_COMPETENCIA`, `REQUER_COMPETENCIA` |
| Estágio do projeto | ideação / validação de hipótese / construção de MVP / validação com usuários reais / tração inicial / escala | `Projeto.estagio` |

---

## Regras de Dados

- Toda relação `TEM_COMPETENCIA`/`REQUER_COMPETENCIA` carrega **fonte** e **confiança** — nunca uma competência isolada sem proveniência (ver [../harness.md](../harness.md), Rastreabilidade).
- `COLABOROU_COM` (registro de fato) é sempre uma relação separada de `AVALIADO_EM` (nota de avaliação) — nunca a mesma relação com um campo opcional, porque isso violaria a regra de visibilidade diferenciada (Tese, item 11).
- `Projeto` nunca registra `PARTICIPOU_DE` no sentido inverso nem duplica quem trabalhou nele — essa informação vive só do lado de `Pessoa` (Hard Rule 3, [ai.md](../ai.md)).
- Toda sugestão de IA que ainda não foi confirmada (ex.: uma competência inferida) carrega `confianca` compatível com essa origem — nunca é indistinguível de um dado confirmado por evidência forte (Tese, item 13 do Talent Model).
- Dataset seed: artificial e enriquecido o suficiente para produzir squads quase perfeitos na demo (ver system-description.md, Objetivos & Sucesso) — isso é responsabilidade de geração de dados, não do schema, mas o schema acima precisa suportar toda a variação de `fonte`/`confianca` que o seed for gerar.

---

## Questões em Aberto

| # | Questão | Owner | Status |
|---|---|---|---|
| 1 | Volume e distribuição exata do dataset seed (quantas Pessoas, quantos Projetos simulados, quantas Competências/Papéis na taxonomia) | Erick + equipe de dados | Open — Step 4 ou início do build |
| 2 | Granularidade da taxonomia de Competência/Papel/Domínio — nível de detalhe sem criar falsa precisão | Erick + equipe de agentes | Open — Step 4 |
| 3 | ~~Formato exato de persistência da explicação decomposta?~~ Resolvido no Step 4 (ARD-05) — materializada como `RECOMENDADO_PARA {score_decomposto}`. | Erick + Claude | Resolvido 11/09 |
| 4 | Onde a regra de apresentação da Decisão #2 (nunca renderizar `AVALIADO_EM` fora do fluxo de decisão) é efetivamente implementada — camada de API, camada de agente, ou ambas? | Erick + equipe fullstack | Open — Step 4 |
