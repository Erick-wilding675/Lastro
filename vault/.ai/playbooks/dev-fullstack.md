# Playbook — Desenvolvedor Fullstack

> **Agente: leia [estado-atual.md](estado-atual.md) antes de responder.**
> São duas pessoas. Pergunte qual trilha: **D1 (backend e dados)** ou
> **D2 (frontend e a cena do pitch)**. Nunca as duas na mesma.

A estrutura do monólito modular já existe em `src/`. Você **não** vai criar
projeto do zero: vai fazer o que está lá rodar contra o banco real e ficar
apresentável. Leia `src/README.md` primeiro.

---

## Trilha D1 — Backend e dados

### Próxima entrega imediata
**API no ar, conectada no AuraDB, com os 6 módulos respondendo.** Meta: 60 min.

### Passo a passo

```bash
cd src/backend
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env     # credenciais vêm do analista A1
uvicorn app.main:app --reload
```

1. `GET /health` tem que responder `{"status":"ok","neo4j":"conectado"}`.
   Se falhar aqui, o problema é credencial ou URI, não código.
2. Validar na ordem que o motor exige: `POST /contagio/propagar/CLI001` →
   `POST /scoring/recalcular` → `GET /scoring/red-flags` →
   `POST /recuperacao/recomendar/CLI002` → `GET /carteira/kpis`.
3. `GET /carteira/grafo` é o que o frontend consome. Confira que volta `nodes`
   e `links` com `peso` e `caminho` preenchidos **depois** de rodar o contágio.

### Definition of done
`/docs` abre, e a sequência completa do motor roda sem erro devolvendo os
4 expostos de CLI001 com caminhos diferentes.

### Depois disso, na ordem
1. Endpoint de "o que mudou": `GET /eventos/radar?dias=90` alimentando um feed
   de alertas na tela.
2. Persistir a memória de recuperação (relação `EXECUTADA`) quando o gestor
   marca uma ação como executada — é o que sustenta a narrativa de aprendizado.
3. Deploy. Só depois de tudo funcionando local. Se faltar tempo, **demo local
   é aceitável** — ninguém vai avaliar URL pública.

---

## Trilha D2 — Frontend e a cena do pitch

### Próxima entrega imediata
**O grafo da carteira renderizando com dado real, e o painel abrindo ao clicar
num nó.** Meta: 90 min. Esta é a imagem que vende o produto em 3 minutos.

### Passo a passo

```bash
cd src/frontend
npm install
cp .env.example .env      # VITE_API_URL=http://localhost:8000
npm run dev
```

O esqueleto já tem: `GrafoCarteira.jsx` (force graph, tamanho do nó por
exposição, cor por rating), `PainelCliente.jsx` (dossiê com contágio explicado)
e `lib/api.js` com todos os endpoints mapeados. Tokens de cor em `lib/tokens.js`,
alinhados ao design system do vault.

### O que fazer, em ordem de valor para o pitch

1. **Grafo com dado real.** Nó grande = exposição alta, cor por rating.
2. **O clique que conta a história.** Clicar em CLI001 dispara
   `POST /contagio/propagar/CLI001` e as arestas de contágio aparecem
   **animando** dos vizinhos acesos. É o momento do pitch. Sem isso, é um
   grafo bonito; com isso, é uma demonstração.
3. **Painel lateral** mostrando "por que acendeu" com o caminho em texto
   (sócio em comum, avalista em comum) e a recomendação com R$ e prazo.
4. **Faixa de KPIs** no topo, vinda de `/carteira/kpis`: exposição total,
   vencido, % da carteira vencida, exposição em risco crítico.

### Definition of done
Dá para sentar na frente de alguém, clicar em um nó e a pessoa entender
sozinha o que aconteceu, sem você explicar.

### O que **não** fazer
- Não construa dashboard de KPI como tela principal. O grafo é a experiência;
  os números são faixa de apoio. Painel completo sai como artefato separado.
- Não gaste tempo em responsividade mobile, tema claro, login ou rotas extras.
  Nada disso é avaliado e tudo isso está fora de escopo declarado.
- Não invente dado no frontend para "ficar mais bonito". Se o número não veio
  da API, ele não aparece na tela.

---

## Regra comum às duas trilhas

Se travar mais de 15 minutos em alguma coisa, **pare e avise o Erick**. Numa
janela dessas, 15 minutos parado é 5% do tempo total do time.
