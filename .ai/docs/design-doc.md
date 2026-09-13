# Design Doc — Sistema Visual & Spec de Componentes

<!--
  Identidade visual, princípios de design e specs de componentes, revisados
  contra a implementação real em src/frontend após o pivô de domínio (11/09).
  Este documento descreve o frontend como ele existe, não uma proposta.
-->

**Status:** Revisado pós-pivô — descreve o frontend como implementado.

**Projeto:** Lastro
**Versão:** 1.1 — reflete `src/frontend/src`
**Data:** 2026-09-13

---

## Princípios de Design

Estes princípios não são aspiracionais — cada um corresponde a uma decisão de
código específica, citada abaixo.

1. **Nenhum número aparece sem explicação.** Hard Rule 3 do [ai.md](../ai.md):
   "exposição sempre explica o caminho — nunca mostrar risco 0,8 sem dizer por
   qual vínculo esse risco chegou". É a regra que mais molda a UI: o drawer do
   cliente (`DrawerCliente.jsx`) tem uma seção inteira, "Por que acendeu", que
   lista o `caminho` percorrido no grafo antes de qualquer recomendação; a
   tela de propagação (`PaginaPropagacao.jsx`) fecha com a nota literal
   "Explicação ≠ score solto — cada alerta nasce com o caminho do vínculo e a
   fonte que sustenta o evento, nunca um número sem porquê". Não é um tooltip
   opcional: é o primeiro conteúdo que carrega.
2. **A rede é a protagonista visual, não uma lista disfarçada.** A tela
   inicial (`/`) é um grafo de força (`react-force-graph-2d`) com todos os
   clientes como nós — não uma tabela com um mapa "de apoio" no canto. A cena
   de demo (`/evento/:id`) também é desenhada como propagação num grafo (SVG
   próprio em `PaginaPropagacao.jsx`), não como uma lista de "clientes
   afetados". Onde existe lista (fila de recuperação), ela é a exceção
   deliberada para priorização, não o padrão.
3. **O sistema nunca finge estar online quando não está.** Consequência direta
   da Hard Rule 7 ("prefira falha ruidosa a degradação silenciosa"). Antes, o
   pill do topo dizia "Motor conectado" fixo no HTML — verdade ou não. Hoje
   `StatusConexao.jsx` + `lib/conexao.js` mostram o estado real da conexão em
   tempo real, e a origem do dado (API real vs. sintético) nunca é escondida
   do usuário. Ver seção "Estados de conexão" abaixo — é o princípio mais
   consequente deste documento, porque é o único que protege o pitch ao vivo
   de uma queda de rede.
4. **Números são a linguagem, mas nunca números crus.** A Hard Rule 9 revogou
   a regra antiga de "nada de número na UI" — mas todo valor monetário ou
   percentual passa por `formatarReais`/`formatarPercentual`
   (`lib/formato.js`) antes de chegar à tela, e todo dado técnico (peso de
   vínculo, score, timestamp, caminho no grafo) usa IBM Plex Mono para se
   diferenciar visualmente de prosa. Número sem unidade ou sem fonte
   diferenciada não passa em review.
5. **Um único acento vívido, reservado para o que é IA/recomendação.** Tema
   escuro sóbrio por padrão; violeta (`--accent`, `#A12AEB`) é a única cor que
   "chama" — usada em wordmark, foco, seleção, e no badge `ai` do drawer.
   Reforça a Hard Rule 10 ([ai.md](../ai.md)): Lastro não é "um sistema de
   cobrança ou um score", é processo de inteligência de risco — a estética não
   pode parecer dashboard financeiro genérico.

---

## Identidade Visual

- **Tema:** "sala de controle de um organismo de dados" — escuro por padrão,
  sóbrio, com o único acento vívido reservado para o que é lido como
  IA/recomendação (Princípio 5).
- **Base do design system:** CSS customizado (`src/frontend/src/styles/global.css`),
  não um design system de terceiro. O grafo de força e os painéis em
  glassmorphism (`backdrop-filter: blur(...)`) não têm equivalente pronto em
  bibliotecas de componente genéricas — decisão consciente de construir os
  primitivos (`.kpi`, `.drawer`, `.list-row`, `.timeline`, `.prop-*`) direto
  em CSS, sem dependência de UI kit.
- **Tokens de cor e tema:** `src/frontend/src/lib/tokens.js` define `temas.dark`
  e `temas.light` como objetos JS (não CSS estático) — `Layout.jsx` injeta o
  tema ativo como CSS custom properties (`--bg`, `--accent`, `--danger`...) na
  raiz `.app`, e todo o resto do CSS consome essas variáveis. Alternar tema é
  literalmente trocar o objeto e re-renderizar; não há build separado por
  tema.

### Paleta (via `tokens.js`)

| Token | Escuro | Claro | Uso |
|---|---|---|---|
| `background` | `#11100F` (warm black) | `#F6F4EF` (sand) | fundo da aplicação |
| `layer1` / `layer2` | `#1F1E1C` / `#2C2B2A` | `#FFFFFF` / `#EDEAE2` | superfícies elevadas (cards, drawer, toolbar) |
| `textoPrimario` / `textoSecundario` | `#F6F4EF` / `#7A818B` | `#11100F` / `#5B6472` | texto principal / muted |
| `acento` | `#A12AEB` (violeta) | mesmo | recomendação de IA, wordmark, foco, seleção |
| `alerta` | `#E8A33D` | `#C97A1F` | rating C, "modo demonstração" |
| `perigo` | `#D9534F` | `#B74642` | rating D, badge de risco crítico |
| `sucesso` | `#4FA97B` | `#2E7A56` | rating A, "motor conectado" |

`corPorRating(rating, tema)` em `tokens.js` mapeia o rating de crédito direto
para cor: `A → sucesso`, `B → textoSecundario` (neutro), `C → alerta`,
`D → perigo`. É o único lugar do código que traduz rating em cor — qualquer
tela que pinte um cliente por rating chama essa função, não reimplementa a
lógica.

- **Tipografia:** Sora 600 (wordmark, `.wordmark`), IBM Plex Sans (corpo,
  padrão de `:root`), IBM Plex Mono (dados, timestamps, `peso 0.XX`, caminhos
  de grafo — qualquer número/caminho técnico usa mono para se diferenciar de
  prosa, Princípio 4). As três vêm do Google Fonts, carregadas no topo de
  `global.css`.

---

## Estados de conexão: a UI nunca finge estar online

Esta é a decisão de design mais importante do documento (Princípio 3), então
merece seção própria em vez de ficar enterrada em "componentes".

**O problema que isso resolve:** rede de hackathon cai. Se a tela quebrasse
quando a API caísse, o pitch ao vivo cairia junto. Mas se a tela simplesmente
mostrasse dado sintético sem avisar, estaria mentindo sobre a origem do
número — o que viola a Hard Rule 7 tão gravemente quanto quebrar.

**Como funciona (`lib/api.js` + `lib/conexao.js` + `StatusConexao.jsx`):**

- Toda chamada de API passa por `comReserva()`, em `lib/api.js`: tenta o
  backend real e, se a chamada falhar, devolve dado sintético de
  `lib/demoData.js` — mas antes disso chama `definirConexao('demo',
  erro.message)`, publicando o motivo real da queda para quem observa o
  estado.
- `lib/conexao.js` mantém esse estado global (padrão observer, sem lib
  externa) e o componente `StatusConexao.jsx` — montado no topbar via
  `Layout.jsx` — assina esse estado e renderiza o pill correspondente.
- Existem **quatro estados reais**, não dois:

| Modo | Gatilho | Texto exibido | Cor |
|---|---|---|---|
| `verificando` | primeira chamada ainda não voltou | "Conectando ao motor…" | `--muted` |
| `api` | chamada ao backend teve sucesso | "Motor conectado" | `--success` (verde) |
| `demo` | backend respondeu com erro/timeout; UI caiu no dado sintético | "Modo demonstração" | `--alert` (âmbar) |
| `demo-fixo` | `VITE_DEMO_MODE=true` no ambiente — escolha explícita de quem subiu o app | "Demonstração (fixa)" | `--accent` (violeta) |

- No modo `demo`, o `title` (tooltip) do pill mostra o motivo real do erro:
  `API indisponível (${detalhe}) — exibindo dados sintéticos`. Não é um
  estado genérico de "offline": carrega a causa.
- **Correção histórica relevante:** antes, `VITE_DEMO_MODE !== 'false'` fazia
  a demonstração ser o *padrão* — quem clonava o repo e subia o backend
  continuava vendo dado sintético e achava, por engano, que tinha conectado.
  Isso foi invertido: hoje só `VITE_DEMO_MODE=true` força a demo; qualquer
  outra configuração tenta o backend real primeiro.

Nenhuma outra tela do produto reimplementa essa lógica — todas as chamadas de
dados passam pelo módulo `api.js`, então o comportamento de fallback e aviso é
uniforme em toda a aplicação, não um detalhe de uma tela específica.

---

## Telas (rotas reais, `App.jsx`)

1. **`/` — Grafo da carteira** (`PaginaGrafo.jsx`) — tela inicial. Grafo de
   força (`GrafoCarteira.jsx`, `react-force-graph-2d`) com todos os clientes
   como nós, coloridos por rating via `corPorRating`; toolbar com legenda por
   rating (`legend-chip`); clicar um nó abre o drawer do cliente.
2. **`/evento/:id` — Propagação** (`PaginaPropagacao.jsx`) — a cena da demo:
   anima o ciclo do motor (`POST /motor/ciclo?origem=...`) mostrando os passos
   numerados (`flow-step`), o grafo reagindo, e a lista de clientes que
   acenderam com o peso do vínculo (`prop-line`, `.peso` em mono). Fecha com
   a nota "Explicação ≠ score solto" — a materialização do Princípio 1 nesta
   tela.
3. **`/fila` — Fila de recuperação** (`FilaRecuperacao.jsx`) — lista
   priorizada (`GET /recuperacao/priorizar`) em formato de tabela
   (`.list-shell`/`.list-row`), com indicador lateral por severidade
   (crítico/alerta/normal via `box-shadow: inset`).
4. **`/painel` — Painel geral** (`PainelGeral.jsx`) — KPIs agregados da
   carteira (`KpiGrid.jsx`, consumindo `GET /carteira/kpis`) e visão
   consolidada de exposição.

O **drawer do cliente** (`ui/DrawerCliente.jsx`) é global, montado uma vez em
`Layout.jsx` e aberto por `context.setSelecionado` a partir de qualquer tela —
não é uma rota própria, é overlay sobre a tela atual. Clicar um nó no grafo,
uma linha na fila, ou um card de destaque na propagação sempre leva ao mesmo
componente, com a mesma estrutura de explicação.

---

## Componentes-chave

- **Drawer do cliente** (`DrawerCliente.jsx`) — busca `GET /agentes/dossie/{cliente}`
  ao abrir. Mostra, nesta ordem: score grande (`.score strong`, 34px) + badge
  de rating; seção **"Por que acendeu"** com um card por vínculo de contágio,
  cada um com o `de` (origem) e o `caminho` percorrido no grafo formatado em
  mono (`caminho.join('  →  ')`) e o peso do vínculo — a materialização visual
  direta do Princípio 1; seção **"Recomendação da IA"** com badge `ai`
  violeta, estratégia, valor recuperável e prazo; e um bloco fixo "Princípio
  do Lastro" lembrando que o vínculo nunca some da tela. A ordem não é
  acidental: a explicação vem antes da recomendação, nunca depois.
- **KPI grid** (`ui/KpiGrid.jsx`) — 4 cards fixos: exposição total, vencido,
  % carteira vencida, exposição em risco crítico (com destaque visual
  `.kpi.highlight`). Todo valor passa por `formatarReais`/`formatarPercentual`
  de `lib/formato.js` — nunca um número cru sem unidade (Princípio 4).
- **Indicador de conexão** (`StatusConexao.jsx` + `lib/conexao.js`) — ver
  seção "Estados de conexão" acima.
- **Sino de notificações** (`SinoNotificacoes.jsx` + `NotificacoesProvider.jsx`) —
  painel flutuante (`.notif-panel`, glass) com eventos recentes, ponto colorido
  por tipo (`critico` vermelho, `contagio` violeta).
- **Toggle de tema** — botão `☼`/`☾` no topbar (`Layout.jsx`), troca
  `temas.dark`/`temas.light` em runtime via estado local (`useState`). A troca
  é imediata (re-render das CSS custom properties na raiz `.app`), sem
  transição de página. Não persiste entre reloads — ver Questões em Aberto.

---

## Padrões de Interação

| Padrão | Comportamento |
|---|---|
| Clique em nó do grafo | Abre o drawer do cliente (overlay à direita, `DrawerCliente.jsx`), buscando o dossiê sob demanda — não pré-carregado |
| Clique em linha da fila de recuperação | Mesmo drawer, mesmo componente — reforça que "explicação" é um contrato único em toda a aplicação, não uma feature por tela |
| Cena de propagação (`/evento/:id`) | Animação do grafo reagindo ao ciclo do motor; foco opcional via querystring (`?foco=`) realça um nó específico e apaga os demais (`opacity`), sem navegação nova |
| Indicador de conexão | Atualiza em tempo real conforme o estado publicado por `conexao.js`; tooltip (`title`) mostra o motivo do fallback quando em modo demo |
| Toggle de tema | Clique alterna `dark`/`light` instantaneamente; estado local, não persiste |
| Sino de notificações | Clique abre painel flutuante sobreposto (glass), sem navegação |

---

## Identidade de Pitch

**Wordmark:** "Lastro" em Sora 600, caixa título. Acompanhado de um glifo de
três pontos conectados (`.brand-mark`, replicado em CSS puro com `::before`/
`::after` como as linhas) em violeta — o mesmo mini-grafo de 3 nós usado no
produto, não um logo separado para o pitch.

**Uso no pitch:**
- Slide de abertura com wordmark + glifo sobre fundo `#11100F`, mesma
  linguagem visual da UI — a demo ao vivo não destoa do material.
- IBM Plex Sans no corpo dos slides; IBM Plex Mono para qualquer trecho
  técnico (Cypher, JSON de resposta) — mesma assinatura visual da aplicação.

---

## Protótipos

Não há wireframe de baixa fidelidade separado — o design foi direto para
componente React versionado em `src/frontend/src`. `wireframes.md` documenta
as telas reais para referência de navegação, não como estágio anterior ao
código.

---

## Questões de Design em Aberto

| # | Questão | Status |
|---|---|---|
| 1 | Toggle de tema não persiste escolha (volta para escuro a cada reload) | Aberto — candidato a `localStorage` |
| 2 | Vetor final do glifo de 3 nós do wordmark fora do CSS (para uso em favicon/slide) | Aberto — hoje só existe como CSS, não como SVG exportável |
| 3 | Tema claro implementado nos tokens mas pouco testado visualmente fora do toggle manual | Aberto |
