# .ai/

Contexto vivo para qualquer assistente de IA (Claude, IBM Bob, etc.)
trabalhando neste repositório, e documentação de produto do Lastro.

**Comece por [`ai.md`](ai.md)** — é o ponto de entrada único, com o mapa de
navegação completo para o resto desta pasta (`docs/`, `playbooks/`,
`workflows/`, `config/`, `templates/`, `tools/`).

```
.ai/
├── ai.md                    entrada — tese, hard rules, mapa de navegação
├── architecture.md          visão geral de arquitetura e fluxos-chave
├── harness.md                GIRO — governança dos agentes de IA que constroem e operam o Lastro
├── coding_conventions.md
├── ui_guidelines.md         design system
├── config/system.md         instruções-mestre para agentes de IA
├── docs/                    especificação completa do produto (SRS, ARD, data model, etc.)
├── playbooks/                protocolo de atendimento por papel (histórico do hackathon)
├── workflows/                 kickoff, task tracker, execução paralela de agentes
├── templates/
└── tools/
```

Esta pasta era um vault do Obsidian (`vault/.ai/`) até a reorganização
pós-hackathon; hoje vive na raiz do repositório como `.ai/` — ainda pode ser
aberta como vault no Obsidian se preferir (`.obsidian/` continua local,
apenas fora do git).
