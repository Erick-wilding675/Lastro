# Playbook — Analista de Sistemas

> **Agente: leia [estado-atual.md](estado-atual.md) antes de responder.**
> São duas pessoas neste papel. Pergunte qual trilha ela pegou: **A1 (grafo e
> dados)** ou **A2 (agentes e orquestração)**. Nunca deixe as duas na mesma.

Você é dono da inteligência do Lastro: o grafo que sustenta o motor e os
agentes que raciocinam em cima dele. O que você entrega é o que a banca vai
chamar de "Viabilidade Técnica" — 25% da nota.

---

## Trilha A1 — Grafo e dados

### Próxima entrega imediata
**Instância AuraDB no ar, populada, com as 5 queries validadas.** Tudo no
projeto está bloqueado por isso. Meta: 40 minutos.

### Passo a passo

1. Criar a instância em [console.neo4j.io](https://console.neo4j.io) — AuraDB
   **Free**. Guardar a senha no momento da criação: ela **não é exibida de
   novo**. Capacidade do free tier (200k nós / 400k relacionamentos) é folga
   enorme para o nosso seed.
2. Abrir o Neo4j Browser da instância. Colar `src/db/cypher/01-schema-e-seed.cypher`:
   primeiro o **Bloco A** (constraints e índices), depois o **Bloco B** (seed).
   O seed usa `MERGE`, então pode rodar de novo sem duplicar.
3. Sanidade: `MATCH (n) RETURN labels(n)[0] AS tipo, count(*) ORDER BY count(*) DESC`.
   Esperado: 10 Cliente, 10 Recebivel, 8 EstrategiaRecuperacao, 6 Evento,
   4 Socio, 4 Regiao, 3 Avalista, 3 Cultura, 3 Imovel, 2 GrupoEconomico, 2 Safra.
4. Rodar as 5 queries de `02-queries-motor.cypher` na ordem. A Q1 usa parâmetro:
   no Browser, `:param origem => 'CLI001'` antes de rodar.
5. Entregar as credenciais para o D1 preencher `src/backend/.env`:
   `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.

### Definition of done
Q1 com `origem=CLI001` devolve **4 clientes** com caminhos diferentes, e Q2
classifica CLI001 como rating **D**. Se der isso, o motor está de pé.

### Depois disso, na ordem
1. Enriquecer o seed se a demo pedir mais volume (mais clientes no mesmo cluster).
2. Escrever a query de "memória de recuperação" (relação `EXECUTADA`) para o
   sistema mostrar aprendizado ao longo das safras.
3. Ajudar o D1 a validar os endpoints contra o banco real.

---

## Trilha A2 — Agentes e orquestração

### Próxima entrega imediata
**Os 4 agentes criados no watsonx Orchestrate, chamando a API do backend como
tool.** Meta: 90 minutos. Pode começar antes do backend estar no ar usando os
contratos abaixo, que não mudam.

### Os 4 agentes (espelham a arquitetura de referência da seção 6 do desafio)

| Agente | O que faz | Tool que chama |
|---|---|---|
| **Coletor & Parser** | Recebe CNPJ/CPF, consulta bases públicas, faz parsing de DJE e certidões em PDF, e registra o que achou como evento | `POST /eventos/registrar` |
| **Risco Agro & Climático** | Cruza CAR, ZARC e histórico de quebra de safra da região com o cliente | `GET /agentes/contexto/{cliente}` |
| **Motor de Decisão & Scoring** | Dispara o recálculo de score e rating da carteira | `POST /scoring/recalcular` |
| **Sintetizador de Relatórios** | Redige o Relatório Padronizado de Risco em linguagem natural para o decisor da Krilltech | `GET /agentes/dossie/{cliente}` |

### Regra de arquitetura que não se quebra
Nenhum agente recebe credencial do Neo4j. O Orchestrate fala **só** com a API
(ARD-04). Se você se pegar colando string de conexão do banco dentro de um
agente, parou: está indo pelo caminho errado.

### O prompt do Sintetizador (use como base)
O dossiê já chega pronto em `GET /agentes/dossie/{cliente}`: score decomposto,
contágio com caminho, recomendações e recebíveis. O agente só precisa redigir.
Exija dele: (a) citar **por qual vínculo** o cliente acendeu, (b) dizer o que
fazer e em que prazo, (c) nunca afirmar número que não veio do dossiê.

### Definition of done
Rodando o Sintetizador para `CLI002`, sai um parecer que diz, em português de
gente, que o cliente está adimplente **mas** compartilha sócio com uma empresa
que acabou de pedir RJ, e recomenda ação preventiva.

### Depois disso
1. Encadear os 4 agentes num fluxo único no Orchestrate (Coletor → Risco Agro →
   Scoring → Sintetizador), que é a demo dos agentes no pitch.
2. Gravar um vídeo curto ou tirar prints do fluxo rodando — é prova de execução
   para a banca, e não depende da internet do auditório na hora do pitch.

---

## O que **não** fazer

- Não invente dimensão nova no grafo sem falar com o Erick. O schema está
  fechado em `vault/.ai/docs/data-model.md`.
- Não deixe o agente inventar número. Todo dado que ele cita vem de uma tool.
- Não gaste tempo com autenticação, multi-tenant ou permissão: está fora de
  escopo declarado e ninguém vai avaliar isso.
