# Diretrizes de UI

<!--
  Tokens de design e regras de componentes, para o agente construir a UI de
  forma consistente. Espelha o design-doc. Preenchido no Step 5 do kickoff —
  e só se o MVP do hackathon tiver uma UI própria (a confirmar).
-->

**Status:** Rascunho — Step 5 respondido por Erick em 11/09. Aguardando aprovação.

> Design spec completo: [docs/design-doc.md](docs/design-doc.md)

## Marca

- **Nome do projeto:** Talent Graph
- **Identidade:** Carbon Design System (IBM) híbrido com componentes próprios pro grafo — sóbrio, escuro por padrão, com um único acento vívido (violeta) reservado para o que é "vivo"/gerado por IA no sistema. A sensação deve ser "sala de controle de um organismo de dados", não "dashboard corporativo".
- **Paleta de origem:** Síntese Labs (fornecida por Erick em 11/09) — ver Tokens de Cor.

---

## Tokens de Cor

**Paleta base (Síntese Labs, fornecida por Erick):**

| Nome | Hex | Papel original |
|---|---|---|
| Brown Core | `#502003` | Marca/engenharia |
| Sand | `#F6F4EF` | Fundo primário (light) |
| Graphite | `#5B6472` | Texto secundário |
| Violeta da marca | `#A12AEB` | IA/software |
| Warm Black | `#11100F` | Fundo dark mode |
| Dark Plum | `#241A25` | Aposentado como superfície — não pinta nada no site, mas segue documentado na paleta |

**Tema escuro (padrão do produto):**

```css
:root {
  /* Superfícies — Dark Plum está aposentado; a escala abaixo é derivada de
     Warm Black com tintas crescentes de Sand, calculada (não arbitrária),
     pra manter o undertone quente da marca em vez de cair num cinza-azulado
     genérico de dark theme. */
  --background:      #11100F; /* Warm Black — tela inicial, o "vazio" atrás do grafo */
  --layer-01:         #1F1E1C; /* Warm Black + 6% Sand — painel lateral, cards */
  --layer-02:         #2C2B2A; /* Warm Black + 12% Sand — conteúdo aninhado dentro do layer-01 (abas) */
  --layer-glass:       rgba(17, 16, 15, 0.55); /* Warm Black a 55% + backdrop-filter: blur(20px) — modal de vidro fosco (UC-02) */
  --border-glass:      rgba(246, 244, 239, 0.08); /* Sand a 8% — borda do card de vidro */

  /* Texto */
  --text-primary:     #F6F4EF; /* Sand — texto principal sobre fundo escuro */
  --text-secondary:   #7A818B; /* Graphite + 20% Sand, calculado — ver nota de contraste abaixo */
  --border-subtle:    #5B6472; /* Graphite puro — bordas, ícones, texto grande (não body text) */

  /* Marca / acento */
  --brand-core:        #502003; /* Brown Core — reservado para o wordmark/pitch, não para UI de produto */
  --accent-ai:         #A12AEB; /* Violeta da marca — o único acento vívido; reservado pro que é gerado por IA */

  /* Semântico — novo, fora da paleta original, proposto nesta etapa */
  --support-warning:   #E8A33D; /* âmbar quente — combina com o undertone de Sand/Brown Core; usado só pra sinalizar lacuna (badge) */
}
```

> **Nota de contraste (medido, não assumido — Hard Rule 7 do [ai.md](ai.md)):** Graphite puro (`#5B6472`) sobre Warm Black dá contraste ≈3.18:1 — passa o mínimo de 3:1 do WCAG AA pra texto grande/bordas/ícones, mas **não** passa 4.5:1 pra texto de corpo normal. Por isso `--text-secondary` usa uma variante clareada (`#7A818B`, Graphite + 20% Sand), que mede ≈4.83:1 — Graphite puro (`--border-subtle`) fica reservado pra bordas, divisores e texto grande. Violeta (`#A12AEB`) sobre Warm Black mede ≈3.66:1 — ótimo pra botões, ícones e bordas de acento, mas evitar como cor de texto de corpo pequeno direto sobre o fundo escuro.

> **`--support-warning` é uma proposta minha, fora da paleta que você mandou** — a paleta da marca não tem uma cor semântica de alerta, e o badge de lacuna (wireframes.md) precisa de uma. Escolhi um âmbar quente pra não destoar do restante (que é todo em tons quentes — Sand, Brown Core, Warm Black). Pode trocar se quiser.

**Tema claro (não é o padrão, mas documentado caso precise):**

```css
[data-theme="light"] {
  --background:      #F6F4EF; /* Sand */
  --layer-01:         #FFFFFF;
  --layer-02:         #EDEAE2; /* Sand escurecido levemente */
  --text-primary:     #11100F; /* Warm Black */
  --text-secondary:   #5B6472; /* Graphite puro — sobre Sand, contraste já é alto o suficiente */
  --border-subtle:    #5B6472;
  --accent-ai:         #A12AEB;
  --support-warning:   #C97A1F; /* âmbar escurecido — mantém contraste sobre fundo claro */
}
```

**Estados visuais do grafo (ver [docs/wireframes.md](docs/wireframes.md), "Padrão visual compartilhado"):**

| Estado | Token | Regra |
|---|---|---|
| Aresta confirmada (`PARTICIPOU_DE` ativa) | `--accent-ai`, traço sólido, opacidade 100% | Membro efetivamente alocado |
| Aresta recomendada com ressalva (lacuna) | `--accent-ai`, traço tracejado, opacidade ~45% | Candidato sugerido mesmo sem bater o limiar |
| Nó fantasma (posição não coberta) | contorno tracejado em `--border-subtle`, sem preenchimento | Lacuna — nenhuma `Pessoa` bate o critério |
| Badge de lacuna | `--support-warning`, ícone ▲ | Ancorado no canto do nó fantasma |

---

## Tipografia

| Papel | Fonte | Tamanho | Peso | Uso |
|---|---|---|---|---|
| Wordmark / logotipo | Sora | — | 600 (SemiBold) | "Talent Graph" no pitch, tela de abertura, favicon |
| Título de tela | IBM Plex Sans | 28px | 600 | Cabeçalhos de painel lateral, Memória Organizacional |
| Corpo | IBM Plex Sans | 15px | 400 | Texto de UI padrão |
| Rótulo / label pequeno | IBM Plex Sans | 13px | 500 | Labels de campo, tags |
| Dado técnico (dimensão, score, Cypher-like) | IBM Plex Mono | 13px | 400 | Anotações técnicas na animação de matching, detalhes de score na lista de substituição (ver wireframes.md, Questão em Aberto 1) |

**Wordmark:** "Talent Graph" em Sora 600, caixa título (não all-caps). Acompanhado de uma marca gráfica simples — três pontos conectados por linhas finas em `--accent-ai` (um mini-grafo de 3 nós), à esquerda do texto — referencia o produto literalmente, é barato de construir (SVG simples) e funciona como favicon reduzido a um único nó com um anel.

---

## Espaçamento & Geometria

```css
:root {
  --radius-sm: 4px;   /* inputs, tags */
  --radius-md: 8px;   /* cards, painel lateral */
  --radius-lg: 16px;  /* modal de vidro (UC-02) — mais arredondado, reforça o efeito "flutuante" */

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 16px;
  --space-4: 24px;
  --space-5: 32px;

  --blur-glass: 20px; /* backdrop-filter do modal de cadastro de projeto */
}
```

---

## Inventário de Componentes

| ID | Componente | Base | Telas |
|---|---|---|---|
| C-01 | Grafo de força | Custom (react-force-graph ou equivalente — ver wireframes.md, Questão 2) | Tela Inicial, Painel Lateral (aba Squad), Matching em Movimento |
| C-02 | Modal de vidro (glassmorphism) | Custom, sobre `Modal` do Carbon | Cadastrar Projeto |
| C-03 | Painel lateral (drawer, 3 abas) | `Modal` lateral do Carbon adaptado, ou custom | Detalhe do Projeto (Genoma / Squad / Anotações) |
| C-04 | Nó fantasma + badge de alerta | Custom (SVG) | Grafo, sempre que há lacuna |
| C-05 | Card de recomendação (lista de substituição) | `Tile` do Carbon | Painel Lateral, aba Squad |
| C-06 | Formulário de elicitação direta | `TextInput`, `Dropdown`, `TagInput` do Carbon | Modal Cadastrar Projeto |
| C-07 | Gráfico de evolução (cobertura de competências) | Biblioteca de charts a definir (ver wireframes.md, Questão 3) | Memória Organizacional |
| C-08 | Wordmark / logotipo | Custom (SVG + Sora) | Cabeçalho, slide de abertura do pitch |

---

## Telas

| Rota | Tela | Componentes-chave |
|---|---|---|
| `/` | Tela Inicial (grafo vivo) | C-01, C-08 |
| overlay | Modal Cadastrar Projeto | C-02, C-06 |
| overlay | Matching em Movimento | C-01 |
| drawer | Painel Lateral — Detalhe do Projeto | C-03, C-04, C-05 |
| `/memoria` | Memória Organizacional | C-07 |

---

## Padrões de Interação

| Padrão | Comportamento |
|---|---|
| Abertura do painel lateral | Desliza da direita, ~35–40% da largura; grafo permanece visível e navegável nos 60% restantes |
| Modal de vidro | Aparece sobre o grafo desfocado/dimmed (grafo continua em movimento por trás); fecha com [X] ou clique fora |
| Matching em movimento | Animação automática, sem interação do usuário; termina abrindo o painel lateral |
| Nó fantasma → badge | Hover/clique expande um mini-card com a explicação da lacuna + candidatos com ressalva |
| Tema | Escuro por padrão; claro é suportado nos tokens mas não é prioridade de build no MVP |

---

## Responsividade / Acessibilidade

- **Viewport:** só desktop web — sem breakpoints mobile (ver [docs/SRS.md](docs/SRS.md), Fora de Escopo).
- **Contraste:** ver Nota de contraste na seção Tokens de Cor — `--text-secondary` e não Graphite puro é o token correto pra texto de corpo sobre fundo escuro.
- **Alvo de clique:** mínimo 32px de altura em elementos interativos do painel lateral e modal (Carbon já segue isso por padrão nos componentes usados).
- Acessibilidade formal (leitores de tela, navegação por teclado completa) não é prioridade do MVP de 12h — mencionar como trabalho futuro se perguntado no pitch, não implementar agora.

---

## Questões de Design em Aberto

1. Ícone/glifo exato do mini-grafo de 3 nós do wordmark — vetor final fica pro Step de execução (Design Doc só define o conceito).
2. Confirmar se o tema claro chega a ser implementado no MVP ou fica só documentado nos tokens (ver Padrões de Interação — hoje a decisão é que não é prioridade).
