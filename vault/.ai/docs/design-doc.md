# Design Doc — Sistema Visual & Spec de Componentes

<!--
  A identidade visual e os specs de componentes — este passo exige decisões
  de look & feel do usuário. Também é onde o material de pitch (Step 5) pode
  se apoiar. Preenchido no Step 5 do kickoff.
-->

**Status:** Rascunho — Step 5 respondido por Erick em 11/09. Aguardando aprovação.

**Projeto:** Talent Graph
**Versão:** 0.1 — Rascunho
**Data:** 2026-09-11

---

## Identidade Visual

- **Tema:** "Sala de controle de um organismo de dados" — escuro por padrão, sóbrio, com um único acento vívido (violeta) reservado para o que é gerado por IA. Nada de dashboard corporativo genérico — consistente com a regra de narrativa do [ai.md](../ai.md), Hard Rule 10.
- **Base do design system:** Carbon (IBM) — confirmado por Erick. Reforça a narrativa técnica pro pitch ("construído dentro do ecossistema IBM") e dá componentes prontos e acessíveis pros formulários/painéis. **Híbrido, por decisão explícita**: o grafo de força e o modal de vidro (glassmorphism) não têm equivalente direto no Carbon — são componentes customizados que convivem com Carbon nos formulários, tiles e no painel lateral.
- Tokens de cor e tipografia completos: ver [../ui_guidelines.md](../ui_guidelines.md).
- Paleta: fornecida por Erick (Síntese Labs) — Brown Core, Sand, Graphite, Violeta da marca, Warm Black; Dark Plum aposentado como superfície. Tema escuro é o padrão do produto.

---

## Telas

1. **Tela Inicial (grafo vivo)** — `/` — todo o Talent Graph + Project Genome de uma vez, interação só de clicar/arrastar.
2. **Modal Cadastrar Projeto** — overlay sobre `/` — elicitação direta, card de vidro fosco sobre o grafo desfocado.
3. **Matching em Movimento** — overlay sobre `/` — animação da formação do squad, dimensão por dimensão.
4. **Painel Lateral — Detalhe do Projeto** — drawer sobre `/` — 3 abas (Genoma, Squad, Anotações).
5. **Memória Organizacional** — `/memoria` — linha do tempo, colaborações recorrentes, evolução de cobertura de competências.

Wireframes de baixa fidelidade completos em [wireframes.md](wireframes.md).

---

## Componentes

Ver [../ui_guidelines.md](../ui_guidelines.md) → Inventário de Componentes (C-01 a C-08): grafo de força, modal de vidro, painel lateral de 3 abas, nó fantasma + badge de alerta, card de recomendação, formulário de elicitação, gráfico de evolução, wordmark.

---

## Identidade de Pitch

**Wordmark:** "Talent Graph" em **Sora** (mesma fonte da Síntese Labs), peso 600, caixa título — não all-caps. Acompanhado de um glifo simples: **três pontos conectados por linhas finas** (um mini-grafo de 3 nós) em Violeta da marca, à esquerda do texto. Referencia o produto de forma literal, é barato de produzir num SVG simples, e funciona reduzido a um ícone único (favicon/slide de abertura).

**Uso no pitch:**
- Slide de abertura: wordmark + glifo centralizados sobre fundo Warm Black — mesma linguagem visual do produto, para que a demo ao vivo não pareça uma peça separada do material de pitch.
- IBM Plex Sans para o corpo dos slides (texto corrido, bullets) — mesma fonte da UI, reforça consistência entre o que a banca vê no pitch e o que vê na demo.
- IBM Plex Mono para qualquer trecho técnico mostrado nos slides (ex.: um exemplo de Cypher, um trecho do schema) — assinatura visual de "isso é um sistema técnico de verdade", reforça o critério de Viabilidade Técnica & Execução (25% da nota).

---

## Protótipos

Nenhum ainda — os wireframes ASCII em [wireframes.md](wireframes.md) são a referência até o time fullstack começar a implementar os componentes reais.

---

## Questões de Design em Aberto

| # | Questão | Owner | Status |
|---|---|---|---|
| 1 | Vetor final do glifo de 3 nós do wordmark (ângulos, espessura de linha exatos) | Equipe de design/fullstack | Open — execução, não bloqueia o build |
| 2 | `--support-warning` (âmbar) foi proposto por mim, fora da paleta original — confirmar ou substituir | Erick | Open |
| 3 | Tema claro documentado nos tokens mas não é prioridade de implementação — confirmar se fica de fora do MVP mesmo | Erick + equipe fullstack | Open |
