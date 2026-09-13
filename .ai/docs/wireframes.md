# Wireframes

<!--
  Layout de cada tela real do frontend do Lastro. Espelha o código em
  src/frontend/src/ — não é mais um rascunho de baixa fidelidade, é a
  descrição do que está implementado.
-->

**Status:** revisado pós-pivô (13/09) — reescrito para o Lastro, espelha
`src/frontend/src/` linha a linha.

**Projeto:** Lastro
**Versão:** 1.0 — reflete a implementação
**Stack de UI:** React (Vite) + `react-force-graph-2d` para o grafo de força.
Questão antiga sobre "qual biblioteca de grafo usar" está resolvida.

---

## Dispositivos-alvo

| Dispositivo | Suportado | Notas |
|---|---|---|
| Web — desktop | Sim | Alvo principal; `global.css` tem breakpoints para até 560px. |
| Mobile | Parcial | Existem media queries (980px, 560px) que colapsam KPIs e escondem a navegação/nav-tabs, mas não é o alvo de design. |

---

## Inventário de Telas

| Tela | Rota | Componente | UC (`use-cases.md`) | Propósito |
|---|---|---|---|---|
| Grafo da carteira | `/` | `PaginaGrafo` → `GrafoCarteira` | UC-01 | Tela inicial: a carteira inteira como grafo de força, coloração por rating A–D. |
| Propagação de contágio | `/evento/:id` | `PaginaPropagacao` | UC-02, UC-03 | A cena central da demo: um cliente pede RJ (ou tem outro evento crítico) e o mapa mostra quem acende e por qual vínculo. |
| Fila de recuperação | `/fila` | `FilaRecuperacao` | UC-04, UC-05 | Lista priorizada por capacidade real do time, com ação "marcar executada". |
| Painel geral | `/painel` | `PainelGeral` | UC-07 | Leitura executiva: KPIs da carteira + timeline de eventos dos últimos 90 dias. |
| Drawer do cliente | overlay sobre qualquer rota | `DrawerCliente` | UC-02, UC-06 | Dossiê de risco de um cliente — score, exposição com caminho, recomendação. Abre ao clicar em qualquer nó/linha que exponha um cliente. |

Todas as quatro rotas compartilham o mesmo `Layout` (topbar + outlet + drawer),
definido em `src/frontend/src/components/Layout.jsx` e roteado em `App.jsx`.

---

## Padrão visual compartilhado

### Tema e paleta (ver `.ai/ui_guidelines.md` para a fonte completa)

Tema escuro por padrão, alternável para claro pelo botão ☼/☾ na topbar
(`Layout.jsx`, `useState('dark')`). Cores por variável CSS (`--accent`,
`--danger`, `--alert`, `--success`, `--muted`...) injetadas via `style` inline
a partir de `src/frontend/src/lib/tokens.js`.

### Coloração por rating (`corPorRating`, em `lib/tokens.js`)

| Rating | Cor | Leitura |
|---|---|---|
| A | `--success` (verde) | Baixo risco |
| B | `--muted` (neutro) | Risco moderado |
| C | `--alert` (âmbar) | Atenção |
| D | `--danger` (vermelho), com glow e contorno extra no canvas | Crítico |

### Aresta de contágio vs aresta neutra (`GrafoCarteira.jsx`, `linkColor`/`linkLineDash`)

| Estado da aresta | Estilo | Significado |
|---|---|---|
| `caminho` presente | Sólida, cor `--accent`, partículas direcionais animadas | Vínculo que efetivamente propagou exposição (contágio real) |
| `caminho` ausente | Tracejada, cinza (`--muted` a ~45% opacidade), sem partícula | Vínculo estrutural no grafo que não fez parte da propagação atual |

Esse par sólido-animado / tracejado-neutro é o mecanismo central de "nunca
mostrar risco sem caminho" (Hard Rule #3 de `.ai/ai.md`).

### Indicador de conexão (`StatusConexao.jsx` + `lib/conexao.js`, em toda tela)

Pill no canto superior direito, com 4 estados possíveis (`ROTULO_CONEXAO` em
`lib/conexao.js`), cada um com cor própria:

| Modo | Texto do pill | Cor | Quando ocorre |
|---|---|---|---|
| `verificando` | "Conectando ao motor…" | `--muted` | Primeira chamada ainda não voltou. |
| `api` | "Motor conectado" | `--success` | Backend respondeu; dado é real. |
| `demo` | "Modo demonstração" | `--alert` | API não respondeu; caiu no dado sintético (`lib/demoData.js`). |
| `demo-fixo` | "Demonstração (fixa)" | `--accent` | `VITE_DEMO_MODE=true` — escolha explícita de quem subiu a app. |

Substitui o pill fixo antigo que dizia "Motor conectado" mesmo com o backend
fora do ar — decisão deliberada de design (ver `.ai/docs/design-doc.md`): a
tela nunca finge que um número é real quando não é.

---

## Wireframes

### Grafo da carteira — `/`

**Propósito:** primeira tela do sistema, a carteira inteira como organismo
vivo. `PaginaGrafo.jsx` monta cabeçalho + `FaixaKpis` (tiras de KPI) +
`GrafoCarteira` (o grafo em si, ocupando o resto da viewport).

**Ação primária:** clicar num nó cliente → dispara `POST /contagio/propagar/{id}`
e reabre o grafo atualizado (`GrafoCarteira.click`), e abre o `DrawerCliente`
com o dossiê daquele cliente.

**Interação:** pan/zoom do `react-force-graph-2d`; filtro por rating via os
4 chips da legenda (A/B/C/D, clicáveis, `graph-toolbar`); auto-fit da câmera
ao trocar o filtro (`zoomToFit`).

```
+----------------------------------------------------------------+
| 01 / Carteira viva                                              |
| Grafo da carteira                          [Motor conectado ●]  |
| Veja a exposição como rede...                                   |
+----------------------------------------------------------------+
| [KPI][KPI][KPI][KPI]  ← FaixaKpis                                |
+----------------------------------------------------------------+
| [A/baixo risco][B/mediano][C/atenção][D/crítico]  [IA/contágio] | ← legenda clicável
|                                                                  |
|        (CLI005:A)                                               |
|             \                                                   |
|   (CLI003:C)—(CLI001:D) ~~~ contágio ~~~ (CLI002:B)              |
|             /              (partículas animadas na aresta viva) |
|        (CLI004:C)         (CLI006:A, isolado — controle)         |
|                                                                  |
|  raio do nó ∝ exposição; nó D com glow vermelho e contorno       |
+----------------------------------------------------------------+
```

Banner temporário "Propagando risco de `<origem>` pela rede…" aparece
enquanto a chamada de propagação está em voo (`graph-banner`).

---

### Propagação de contágio — `/evento/:id`

**Propósito:** a cena central do pitch. Mostra, a partir de um gatilho
(`id` = cliente que virou evento, ex. `CLI001`), quem acendeu e por qual
vínculo — carregado via `carregarPropagacao(id)` (`lib/notificacoes.js`).

**Ação primária:** clicar num cliente aceso (na lista ou via `?foco=CLI00X`
na URL) para focar aquele vínculo específico; "Ver dossiê" abre o
`DrawerCliente`; "Voltar ao grafo" retorna para `/`.

**Estrutura:** 4 passos fixos no topo (`Evento detectado → Contágio
propagado → Risco recalculado → Recuperação priorizada`), depois um SVG
desenhado à mão (não é o `ForceGraph2D` — layout radial fixo: gatilho à
esquerda, clientes acesos em leque à direita, nó de controle embaixo) e um
painel lateral com a lista de vínculos e pesos.

```
+----------------------------------------------------------------+
| 04 / Momento-chave                                               |
| O evento muda o mapa                        [● LIVE · propagação]|
| Agro Vale do Cerrado — pediu RJ...                                |
+----------------------------------------------------------------+
| [01 Evento detectado]→[02 Contágio propagado]→[03 Risco recalc.] |
|  →[04 Recuperação priorizada]                                    |
+----------------------------------------------------------------+
|  SVG 460x320                          |  peso 0,90               |
|   (CLI001)==forte==>(CLI005) peso .90 |  ● CLI005 · grupo econ.   |
|   (CLI001)--fraco-->(CLI003) peso .30 |  peso 0,85                |
|   (CLI001)==forte==>(CLI002) peso .75 |  ● CLI003 · avalista comum|
|                                        |  peso 0,75                |
|         (CLI006 controle, canto)      |  ● CLI002 · sócio+região  |
|                                        |------------------------- |
|                                        | Controle: CLI006 continua|
|                                        | verde — sem vínculo.     |
|                                        |------------------------- |
|                                        | Explicação ≠ score solto |
|                                        | [Ver dossiê] [Voltar]    |
+----------------------------------------------------------------+
```

Aresta sólida = peso ≥ 0,6 ("forte"); tracejada = peso menor. O nó em foco
(via `?foco=`) ganha anel branco e opacidade cheia; os demais apagam para
~28-35% — o mesmo padrão de "focar sem esconder o resto" usado no grafo
principal.

---

### Fila de recuperação — `/fila`

**Propósito:** lista de trabalho do time de recuperação, carregada de
`GET /recuperacao/priorizar?capacidade=5` — respeita a capacidade real do
time (Hard Rule: ação que ninguém executa é ação inexistente).

**Ação primária:** "Marcar executada" por linha → `POST /recuperacao/executar/{cliente}`,
remove a linha da fila localmente após sucesso. Clicar no nome do cliente
abre o `DrawerCliente`.

**Urgência por linha:** cor lateral (`box-shadow` inset) derivada do prazo
da melhor estratégia — `≤20 dias` = crítico (vermelho), `≤45` = atenção
(âmbar), senão neutro (`urgencia()` em `FilaRecuperacao.jsx`).

```
+----------------------------------------------------------------+
| 02 / Recuperação                                                 |
| Fila de recuperação              [Capacidade atual · 5 ações]    |
+----------------------------------------------------------------+
| Cliente / contexto      | Estratégia   | Retorno/prazo | Ação    |
|--------------------------------------------------------------- |
|▐CLI002 Fazenda St.Luzia | Renegociação | R$ 42.000/45d |[Marcar  |
|  abrir dossiê e caminho |preserva relação             |executada]|
|▐CLI008 Agroind. Rio Cl. | Protesto     | R$ 18.500/15d |[Marcar  |
+----------------------------------------------------------------+
```

---

### Painel geral — `/painel`

**Propósito:** leitura executiva — `KpiGrid` com os KPIs de
`GET /carteira/kpis`, mais uma timeline (`GET /eventos/radar?dias=90`) dos
eventos que mudaram o cenário nos últimos 90 dias.

**Ação primária:** nenhuma transacional — tela de leitura. Cada item da
timeline mostra cliente, descrição/tipo do evento e data.

```
+----------------------------------------------------------------+
| 03 / Controle                                                    |
| Painel geral                [Leitura executiva · últimos 90 dias]|
+----------------------------------------------------------------+
| [KPI][KPI][KPI][KPI]  ← KpiGrid                                  |
+----------------------------------------------------------------+
| O que mudou                                          [Radar IA]  |
| ─● CLI001 — pedido de RJ distribuído          12/09/2026          |
| ─● CLI004 — quebra de safra confirmada Conab  10/09/2026          |
+----------------------------------------------------------------+
```

---

### Drawer do cliente — overlay sobre qualquer rota

**Propósito:** um único componente reaproveitado em toda tela que expõe um
cliente (grafo, propagação, fila) — dossiê carregado de `GET /agentes/dossie/{cliente}`.
Fundo com `backdrop-filter: blur` (glassmorphism), desliza da direita,
~430px de largura, o resto da tela permanece visível atrás.

**Conteúdo real (`DrawerCliente.jsx`):** nome do cliente + situação; score
grande (`/1000`) e badge de rating; seção "Por que acendeu" com um card por
vínculo de contágio (peso + caminho, ex. `CLI001 → SOC001 → CLI002`); seção
"Recomendação da IA" com a estratégia sugerida, valor recuperável formatado
em R$, prazo em dias e botão "Abrir plano de recuperação"; nota fixa de
princípio ("Caminho sempre visível").

**Ação primária:** varia por seção — nenhuma navegação, é um painel de
leitura + 1 CTA de recuperação.

```
+----------------------------------------------------------------+
|  [grafo/tela ao fundo, ainda visível]     | Dossiê de risco   [x]|
|                                            | Fazenda Santa Luzia   |
|                                            | adimplente · cliente  |
|                                            | estratégico            |
|                                            |------------------------|
|                                            |  620 /1000  [Rating B] |
|                                            |------------------------|
|                                            | Por que acendeu        |
|                                            | ● CLI001                |
|                                            |   CLI001 → SOC001 →    |
|                                            |   CLI002   peso 0.85   |
|                                            |------------------------|
|                                            | Recomendação da IA [IA]|
|                                            | Renegociação            |
|                                            | R$ 42.000 · 45 dias    |
|                                            | [Abrir plano de recup.]|
|                                            |------------------------|
|                                            | Princípio do Lastro    |
|                                            | Caminho sempre visível |
+----------------------------------------------------------------+
```

---

## Modelo de Navegação

```
  Grafo da carteira (/) ──┬─ clique num cliente ──▶ propaga + abre Drawer
                           │
                           ├─ evento crítico ──▶ Propagação (/evento/:id) ──┬─ foco num vínculo
                           │                                                 └─ Ver dossiê ──▶ Drawer
                           ├─ nav-tabs ──▶ Fila de recuperação (/fila) ──▶ Drawer (por linha)
                           │
                           └─ nav-tabs ──▶ Painel geral (/painel)  [leitura, sem navegação adicional]
```

---

## Decisões já resolvidas (substituem as "Questões em Aberto" antigas)

| # | Questão antiga | Resolução real |
|---|---|---|
| 1 | Números crus na UI eram proibidos (NFR antigo) | Revogado (Hard Rule #9 de `.ai/ai.md`): números aparecem direto — score, R$, dias, peso. A explicação nunca é um número sozinho, mas o número em si é a linguagem do produto. |
| 2 | Biblioteca de grafo de força | `react-force-graph-2d`, decidido e implementado (`GrafoCarteira.jsx`). |
| 3 | Biblioteca de charts para a leitura executiva | Não existe biblioteca de charts de terceiros no projeto. A leitura executiva é o Painel Geral (`/painel`): `KpiGrid` (componente próprio, sem lib) + timeline de eventos, ambos consumindo os mesmos endpoints do grafo principal. |
