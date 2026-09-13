# Lastro — frontend

React + Vite. Consome a API do backend (`src/backend`) e mostra a carteira
como rede: grafo de força, propagação de contágio, fila de recuperação e
painel geral de KPIs.

## Subir

```bash
npm install
cp .env.example .env   # VITE_API_URL aponta para o backend
npm run dev             # http://localhost:5173
```

## Estrutura

```
src/
├── App.jsx                    rotas (react-router-dom)
├── components/
│   ├── Layout.jsx              topbar + navegação + outlet
│   ├── NavTabs.jsx              abas de navegação
│   ├── SinoNotificacoes.jsx     sino de notificações (eventos/contágio)
│   └── StatusConexao.jsx        pill "Motor conectado" / "Modo demonstração"
├── context/
│   └── NotificacoesProvider.jsx contexto de notificações em tempo real
├── features/
│   ├── grafo/                   tela inicial — grafo de força da carteira
│   ├── propagacao/               tela de propagação de um evento (/evento/:id)
│   ├── fila/                     fila de recuperação priorizada (/fila)
│   ├── painel-geral/             KPIs consolidados (/painel)
│   └── kpis/                     faixa de KPIs reutilizável
├── ui/
│   ├── Brand.jsx                 wordmark + marca gráfica do Lastro
│   ├── DrawerCliente.jsx         drawer lateral — dossiê do cliente
│   └── KpiGrid.jsx               grid de cards de KPI
├── lib/
│   ├── api.js                    cliente HTTP da API do backend
│   ├── conexao.js                estado de conexão (api / demo / demo-fixo)
│   ├── demoData.js               dados sintéticos do case Krilltech (fallback)
│   ├── formato.js                formatação pt-BR (moeda, data, número)
│   ├── notificacoes.js           lógica de notificações
│   └── tokens.js                 design tokens (paleta clara/escura, cor por rating)
└── styles/global.css             estilos globais (design system, ver .ai/ui_guidelines.md)
```

## Rotas

| Rota | Tela | O que mostra |
|---|---|---|
| `/` | `PaginaGrafo` | Grafo de força da carteira inteira |
| `/evento/:id` | `PaginaPropagacao` | Animação de propagação de um evento/contágio |
| `/fila` | `FilaRecuperacao` | Fila de recuperação priorizada por capacidade |
| `/painel` | `PainelGeral` | KPIs consolidados da carteira |

## Modo demonstração (fallback sintético)

O app usa a API real por padrão (`VITE_API_URL`). Se ela não responder, a
tela cai sozinha nos dados sintéticos de `lib/demoData.js` e o
`StatusConexao` avisa — o pill no topo passa de "Motor conectado" para
"Modo demonstração". A tela nunca finge estar conectada quando não está:
ver `lib/conexao.js`.

`VITE_DEMO_MODE=true` força o modo sintético mesmo com o backend no ar
(`demo-fixo`) — útil para demonstrar a interface sem depender de rede ou de
uma instância do backend ligada.

## Design system

Tema escuro por padrão (paleta e tokens em `lib/tokens.js`), tipografia
Sora (wordmark) + IBM Plex Sans (corpo) + IBM Plex Mono (dados/timestamps).
Detalhes em [`.ai/ui_guidelines.md`](../../.ai/ui_guidelines.md).

## Deploy

`vercel.json` na raiz do repo builda este diretório
(`cd src/frontend && npm install && npm run build`, output
`src/frontend/dist`) — configurado para deploy na Vercel.
