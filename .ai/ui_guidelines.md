# Diretrizes de UI

<!--
  Tokens de design e regras de componentes, verificados contra o código real
  em src/frontend/src/lib/tokens.js e src/frontend/src/styles/global.css.
-->

**Status:** revisado pós-pivô (13/09) — reescrito para o produto real
(Lastro) e conferido contra a implementação, substituindo a versão pré-pivô
que descrevia "Talent Graph" com Carbon Design System.

> Design spec completo: [`docs/design-doc.md`](docs/design-doc.md)

## Marca

- **Nome do produto:** Lastro
- **Identidade:** CSS próprio, sem biblioteca de componentes de terceiros —
  o app **não usa Carbon Design System** (confirmado em `global.css`: todo
  componente é uma classe própria, sem import de lib de UI). Sóbrio, escuro
  por padrão, com um único acento vívido (violeta) reservado para o que é
  "vivo"/calculado pelo motor — o mesmo princípio de antes, aplicado ao
  domínio de crédito: a sensação é "mapa de exposição vivo", não "dashboard
  corporativo".
- Os temas (claro/escuro) são objetos JS em `src/frontend/src/lib/tokens.js`
  (`temas.dark`, `temas.light`), aplicados como CSS custom properties
  inline pelo `Layout.jsx` — não há troca de classe/`[data-theme]`, é
  `style={{'--bg':t.background, ...}}` no elemento raiz.

---

## Tokens de Cor

Fonte de verdade: `src/frontend/src/lib/tokens.js`.

**Tema escuro (padrão):**

| Token | Hex | Papel |
|---|---|---|
| `background` | `#11100F` | Fundo — o "vazio" atrás do grafo de carteira |
| `layer1` | `#1F1E1C` | Painel lateral, cards, topbar |
| `layer2` | `#2C2B2A` | Conteúdo aninhado (nav tabs, chips) |
| `glass` | `rgba(17,16,15,.72)` | Superfícies com `backdrop-filter: blur()` — topbar, drawer, notificações |
| `borderGlass` | `rgba(246,244,239,.08)` | Borda sobre superfície de vidro |
| `textoPrimario` | `#F6F4EF` | Texto principal |
| `textoSecundario` | `#7A818B` | Texto secundário, metadados |
| `bordaSutil` | `#3F3E3C` | Bordas padrão dos cards |
| `acento` | `#A12AEB` | Violeta da marca — o único acento vívido; reservado para o que o motor calculou (score, recomendação, caminho de exposição) |
| `acentoSoft` | `rgba(161,42,235,.16)` | Fundo suave do acento (badges, chips ativos) |
| `alerta` | `#E8A33D` | Âmbar — rating C, avisos |
| `alertaSoft` | `rgba(232,163,61,.13)` | |
| `perigo` | `#D9534F` | Vermelho — rating D, red flags críticas |
| `perigoSoft` | `rgba(217,83,79,.13)` | |
| `sucesso` | `#4FA97B` | Verde — rating A, cliente sem exposição herdada |
| `sucessoSoft` | `rgba(79,169,123,.13)` | |
| `sombra` | `0 22px 60px rgba(0,0,0,.28)` | Sombra de superfícies elevadas (drawer, notificações) |

**Tema claro** (suportado, toggle na topbar — `StatusConexao`/tema não é o
padrão de abertura): mesma estrutura de tokens com `background: #F6F4EF`,
`textoPrimario: #11100F`, `acento` mantido `#A12AEB` — ver `tokens.js` para
os valores completos de cada token no claro.

**`corPorRating(rating, tema)`** — a função que pinta cada nó do grafo e cada
indicador de rating: `A → sucesso`, `B → textoSecundario` (neutro), `C →
alerta`, `D → perigo`. É o mapeamento canônico de cor por risco em todo o
app — qualquer novo componente que exiba rating deve usar essa função, não
reimplementar a tabela.

---

## Tipografia

| Papel | Fonte | Peso | Uso |
|---|---|---|---|
| Wordmark | Sora | 600 (SemiBold) | "Lastro" na topbar (`.wordmark`) |
| Corpo / UI | IBM Plex Sans | 400–700 | Todo o texto de interface (`:root { font-family }`) |
| Dado técnico / mono | IBM Plex Mono | 400–500 | Scores, timestamps, pesos de contágio, caminho de exposição (`.reason-path`, `.kpi-meta`, `.timeline-date`) — reforça "isto é dado calculado, não prosa" |

Fontes carregadas via Google Fonts no topo de `global.css`
(`IBM+Plex+Mono`, `IBM+Plex+Sans`, `Sora`).

---

## Geometria (valores reais observados no CSS, não uma escala de tokens formal)

O projeto não define uma escala de `--radius-*`/`--space-*` em CSS custom
properties — os valores estão hardcoded por componente em `global.css`.
Padrões observados, para manter consistência em componentes novos:

| Uso | Valor |
|---|---|
| Cards, KPI, list-shell | `border-radius: 16–18px` |
| Chips, badges, botões pequenos | `border-radius: 8–12px`, pílulas em `999px` |
| Drawer lateral | largura `min(430px, calc(100vw - 28px))` |
| Padding de página | `22px` (desktop), `14px` (≤980px), topbar `0 12px` (≤560px) |
| `backdrop-filter: blur()` | `14–22px`, conforme a superfície (chip de legenda vs. drawer) |

---

## Inventário de Componentes

Mapeado contra as classes reais em `global.css` e os arquivos em
`src/frontend/src/`:

| Componente | Arquivo | Classe raiz | Onde aparece |
|---|---|---|---|
| Topbar (wordmark + nav + status + sino) | `components/Layout.jsx`, `NavTabs.jsx`, `StatusConexao.jsx` | `.topbar` | Todas as telas |
| Faixa de KPIs | `features/kpis/FaixaKpis.jsx`, `ui/KpiGrid.jsx` | `.kpi-grid`, `.kpi` | `/`, `/painel` |
| Grafo de força da carteira | `features/grafo/GrafoCarteira.jsx`, `PaginaGrafo.jsx` | `.graph-shell`, `.graph-legend`, `.legend-chip` | `/` |
| Drawer do cliente | `ui/DrawerCliente.jsx` | `.drawer`, `.score`, `.reason-list`, `.recommendation` | Sobre qualquer tela, ao selecionar um cliente |
| Fila de recuperação (lista) | `features/fila/FilaRecuperacao.jsx` | `.list-shell`, `.list-row` (com `.critical`/`.warning`/`.normal`) | `/fila` |
| Tela de propagação | `features/propagacao/PaginaPropagacao.jsx` | `.prop-stage`, `.flow-steps`, `.prop-body` | `/evento/:id` |
| Timeline de eventos | (dentro do drawer/painel) | `.timeline`, `.timeline-item` | Drawer, painel geral |
| Sino de notificações | `components/SinoNotificacoes.jsx`, `context/NotificacoesProvider.jsx` | `.bell-wrap`, `.notif-panel` | Topbar, todas as telas |
| Indicador de conexão | `components/StatusConexao.jsx`, `lib/conexao.js` | `.status-pill`, `.status-dot` | Topbar — "Motor conectado" vs. "Modo demonstração" |
| Wordmark | `ui/Brand.jsx` | `.wordmark`, `.brand-mark` | Topbar |

---

## Telas

| Rota | Tela | Componentes-chave |
|---|---|---|
| `/` | Grafo de força da carteira (tela inicial) | Grafo, faixa de KPIs, drawer sob demanda |
| `/evento/:id` | Propagação animada de exposição | `.prop-stage`, grafo + painel lado a lado |
| `/fila` | Fila de recuperação priorizada | `.list-shell` |
| `/painel` | Painel geral de KPIs | `.kpi-grid`, timeline |

Ver descrição completa de cada tela em [`docs/wireframes.md`](docs/wireframes.md).

---

## Padrões de Interação

| Padrão | Comportamento |
|---|---|
| Abertura do drawer do cliente | Desliza da direita (`.drawer`), largura `min(430px, 100vw-28px)`; fundo escurecido por `.drawer-backdrop` |
| Indicador de conexão | "Motor conectado" (ponto verde) quando `GET /health` responde; cai para "Modo demonstração" com aviso visível quando a API não responde — nunca finge que o dado sintético é real |
| Legenda do grafo | Chips clicáveis (`.legend-toggle`) filtram/realçam o canal de exposição (estrutural × sistêmico) na tela de propagação |
| Notificações | Painel suspenso (`.notif-panel`) com badge de não lidas (`.bell-badge`), classificado por tipo (`critico`, `contagio`) |
| Tema | Escuro por padrão; toggle para claro disponível na topbar (`.theme-toggle`) |

---

## Responsividade

Dois breakpoints reais em `global.css`:

- `@media (max-width: 980px)`: nav tabs somem, KPI grid cai para 2 colunas,
  lista vira 1 coluna, grafo reduz para 70vh.
- `@media (max-width: 560px)`: KPI grid vira 1 coluna, título reduz para
  24px, topbar comprime, status pill e submarca do wordmark somem.

Acessibilidade formal (leitores de tela, navegação por teclado completa)
não foi prioridade do MVP de 12h — é item de roadmap, não implementado hoje.
