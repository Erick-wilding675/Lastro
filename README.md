# Lastro

**Risco de crédito relacional para o agro.** Construído em ~12h no Hackathon
PMI-DF 2026 (case Krilltech, 11–12/09/2026, Brasília); mantido aqui como
peça de portfólio público desde então.

> Quando um produtor rural cliente entra em Recuperação Judicial, a empresa
> credora fica legalmente impedida de executar garantia ou protestar por
> **180 dias** (*stay period*). Depois do pedido, não há o que fazer — todo
> o valor está em saber antes. O Lastro trata a carteira como uma **rede**,
> não uma lista: propaga risco pelos vínculos entre clientes e mostra **por
> qual vínculo** a exposição chega, a tempo de agir.
>
> **A tese em uma frase:** produtor rural não quebra sozinho — o componente
> de rede é o que nenhum bureau de crédito entrega.

---

## Índice

- [O problema](#o-problema)
- [O que o sistema faz](#o-que-o-sistema-faz)
- [Arquitetura](#arquitetura)
- [Pipeline de dados](#pipeline-de-dados)
- [Agentes de IA e o harness (GIRO)](#agentes-de-ia-e-o-harness-giro)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Quickstart](#quickstart)
- [Deploy](#deploy)
- [Documentação](#documentação)
- [Roadmap](#roadmap)

---

## O problema

A Krilltech (agtech brasileira, produto Arbolin Biogenesis) vende tecnologia
de alta produtividade direto ao produtor rural, a prazo, com pagamento
casado à safra. Entre entregar e receber há uma janela em que o risco só
cresce — e o setor inteiro piorou: **1.990 pedidos de RJ no agro em 2025**
(+56,4% sobre 2024, Serasa Experian), inadimplência de produtor PF saltando
de **2,7% para 7,3%** em 12 meses (Banco Central), **8,8%** de inadimplência
no 1T2026 — recorde da série.

O ponto cego: a carteira é gerida como lista de vencimentos, mas o risco no
agro é correlacionado. Vários clientes podem compartilhar o mesmo avalista,
grupo econômico, sócios, microrregião e safra — invisível numa planilha.
Quando o alerta chega pelo aging, o dinheiro já parou, e a lei fecha a
janela: deferida a RJ, começa o *stay period* de 180 dias em que nenhuma
execução ou protesto é possível.

Detalhe completo do diagnóstico, público-alvo e modelo de negócio no
[Project Canvas](.ai/docs/project-canvas.md) (entregável obrigatório do
hackathon).

## O que o sistema faz

1. **Representa a carteira como grafo** (Neo4j) — clientes, recebíveis,
   sócios, avalistas, grupos econômicos, região, cultura, safra e eventos
   viram nós e arestas.
2. **Propaga exposição por dois canais que não se confundem:**
   - **Estrutural** — o risco de um atinge o outro por vínculo jurídico ou
     patrimonial: mesmo grupo econômico (peso 0,90), avalista em comum
     (0,85), sócio em comum (0,70).
   - **Sistêmico** — ninguém contamina ninguém, todos sofrem a mesma causa:
     mesma região + cultura + safra (0,75), mesma revenda (0,65), só
     cultura (0,40). Só entra com peso cheio **quando há evento regional
     confirmando o choque** (quebra de safra, alerta ZARC, queda de
     cotação) — sem evento, entra reduzido. A região não é culpada por
     associação; é medida por causa comum documentada.
3. **Calcula score 0–1000 e rating A–D**, decomposto em cinco componentes
   (comportamento de pagamento, eventos jurídicos/fiscais, cobertura de
   garantia com *haircut* por tipo, exposição herdada da rede, risco
   agro/ambiental) — nunca um número isolado, sempre com o caminho que o
   produziu.
4. **Prioriza a recuperação** do que já venceu: estratégia recomendada por
   devedor (renegociação, barter, acordo parcelado, protesto, execução...),
   com valor recuperável estimado, prazo e custo, respeitando a capacidade
   real do time de cobrança.
5. **Mantém um radar de eventos contínuo** — cada ocorrência entra com
   fonte e data; eventos relevantes disparam repropagação e recálculo, não
   só do cliente do evento, mas de quem está ligado a ele.

O sistema **recomenda, nunca decide sozinho** — nenhuma ação de cobrança,
protesto ou judicial dispara automaticamente; e **nunca prescreve
instrumento jurídico** — diagnostica fragilidade de garantia, a decisão de
política de crédito é da Krilltech. Ver as 11 Hard Rules em
[`.ai/ai.md`](.ai/ai.md).

## Arquitetura

```
Frontend (React)  ◀──REST──▶  Backend (FastAPI)  ◀──driver──▶  Neo4j AuraDB
grafo de força,                único ponto que fala             carteira como rede
drawer do cliente,             com o banco (ARD-04)
fila de recuperação                    ▲
                                        │ chamada como "tool" (OpenAPI)
                           IBM watsonx Orchestrate
                           4 agentes de IA
```

**A regra que não se quebra:** o watsonx Orchestrate nunca fala com o
driver do Neo4j — ele chama a API do backend. Se aparecer credencial de
banco dentro de um agente, é erro de arquitetura, não atalho. Detalhe
completo em [`.ai/architecture.md`](.ai/architecture.md) e
[`.ai/docs/ARD.md`](.ai/docs/ARD.md) (Architecture Decision Records).

**Stack:**

| Camada                    | Tecnologia                                                                  |
| ------------------------- | --------------------------------------------------------------------------- |
| Grafo                     | Neo4j AuraDB (free tier)                                                    |
| Backend                   | Python + FastAPI — monólito modular, ver[`src/README.md`](src/README.md) |
| Frontend                  | React + Vite +`react-force-graph-2d`                                      |
| Orquestração de agentes | IBM watsonx Orchestrate                                                     |
| Engenharia                | IBM Bob / Claude Code                                                       |

## Pipeline de dados

Dois caminhos alimentam o grafo, e o repositório é honesto sobre qual é
qual — **nenhum dado real de produtor entra aqui** (Hard Rule #8):

1. **Seed sintético** ([`src/db/cypher/01-schema-e-seed.cypher`](src/db/cypher/01-schema-e-seed.cypher)) —
   cenário de demonstração plantado: um cliente pede RJ e acende quatro
   vizinhos por quatro vetores diferentes de contágio, mais um cliente de
   controle que permanece verde (prova de que o sistema não pinta a
   carteira toda de vermelho).
2. **Pipeline de ingestão real** ([`src/db/ingestao/`](src/db/ingestao/)) —
   pega a carteira de um cliente (nunca "ingere o Brasil inteiro" — puxado
   pela carteira, não pela fonte, o que é o que torna viável e defensável
   em LGPD) e a enriquece contra fontes públicas: PGFN (dívida ativa),
   IBAMA (embargos ambientais), Receita/QSA (sócios, CNAE), Conab/IBGE-PAM
   (quebra de safra contra baseline histórico), INMET (déficit de chuva),
   DataJud/CNJ (densidade de RJ e execução por microrregião), SICAR. Três
   estágios independentes — `extract → transform → load` — porque cada um
   falha por um motivo diferente (rede, layout, credencial), e um script
   único transformaria qualquer erro em "não funcionou". Toda linha
   carrega `fonte` e `confiança`; o que não tem fonte não vira propriedade.
   Documentação extensa, incluindo o mapa de cobertura por fonte real, em
   [`src/db/ingestao/README.md`](src/db/ingestao/README.md) e
   [`COBERTURA.md`](src/db/ingestao/COBERTURA.md).

`src/db/cypher/03-completar-lacunas.cypher` fecha as lacunas que sobram
quando seed sintético e ingestão real convivem no mesmo grafo — documentado
inclusive quais achados públicos **não existem** (ex.: o próprio pedido de
RJ não tem fonte pública que exponha as partes; sai de DJE ou da intimação
que a credora recebe).

## Agentes de IA e Harness

Quatro agentes no watsonx Orchestrate, desenhados por um princípio único:
**agente onde há ambiguidade, função onde há conta.** Propagação de
exposição, score, matriz de red flags e priorização são 100% determinísticos
(Cypher/backend) — reproduzíveis, auditáveis, não alucinam. LLM entra só
onde há texto livre ou necessidade de redação:

| Agente                  | Papel                                                                                   |
| ----------------------- | --------------------------------------------------------------------------------------- |
| Coletor & Parser        | Transforma fonte pública/documento não estruturado em evento com fonte e data         |
| Risco Agro & Climático | Cruza CAR, ZARC, safra e histórico regional; alimenta o canal sistêmico               |
| Decisão & Scoring      | Orquestra o recálculo na ordem certa (contágio → score); nunca calcula sozinho       |
| Sintetizador            | Redige o parecer de risco a partir do dossiê já calculado — nenhum número inventado |

Detalhe completo, prompts base e guardrails em
[`.ai/docs/agentes.md`](.ai/docs/agentes.md).

Tanto os agentes que **operam** o Lastro (acima) quanto os agentes de IA que
**constroem/mantêm** este repositório (Claude, IBM Bob) seguem o mesmo
framework de governança — o **Harness GIRO**, método da Síntese
Labs aplicado a este projeto: toda decisão de rota é rastreável até uma
regra declarada, toda saída de IA é recomendação sujeita a confirmação
humana, nunca fato consolidado sem fonte. Ver [`.ai/harness.md`](.ai/harness.md).

Esse é também o motivo de este repositório ter uma pasta `.ai/` versionada
junto do código: não é overhead de processo, é o contexto vivo que faz um
assistente de IA retomar o projeto meses depois sem reconstruir do zero o
que já foi decidido — a mesma retroalimentação que o harness pede do
produto, aplicada à manutenção do próprio repositório.

## Estrutura do repositório

```
.
├── .ai/                 contexto de produto e engenharia para IA — comece por .ai/ai.md
├── pitch/                Project Canvas, pitch deck e roteiro do hackathon
├── tasks/                task tracker (Local Markdown, histórico do sprint)
├── src/                  código — monólito modular, ver src/README.md
│   ├── backend/          Python + FastAPI (ver src/backend/README.md)
│   ├── db/               schema Cypher + pipeline de ingestão (ver src/db/README.md)
│   └── frontend/         React (ver src/frontend/README.md)
├── Makefile              setup, run, seed, lint — ver `make help`
└── .env.example           mapa de variáveis de ambiente do sistema completo
```

Monólito modular: um deployable (o backend), módulos com fronteira de
domínio clara (`carteira`, `contagio`, `scoring`, `recuperacao`, `eventos`,
`agentes`).

## Quickstart

Requer Python 3.11+, Node 20+, e uma instância Neo4j AuraDB (free tier
serve). Com `make` disponível (Git Bash, WSL, ou `choco install make` no
Windows):

```bash
git clone <este-repositório> && cd Hackathon
cp .env.example .env                # preencha NEO4J_URI/USER/PASSWORD
make setup                          # cria .venv na raiz + instala backend/ingestão/frontend
make seed                           # aplica schema + seed sintético no Neo4j
make backend                        # terminal 1 — http://localhost:8000/docs
make frontend                       # terminal 2 — http://localhost:5173
```

Sem `make`? Todo alvo do Makefile é só um comando de shell — abra o arquivo
e rode direto. Sem `.venv` ativado à mão no VS Code: `.vscode/settings.json`
já aponta o interpretador Python para `.venv/`, então o terminal integrado
ativa sozinho ao abrir a pasta.

O frontend usa a API real por padrão; se ela não responder, a tela cai
sozinha nos dados sintéticos do case e avisa — o indicador no topo passa de
"Motor conectado" para "Modo demonstração". `VITE_DEMO_MODE=true` força o
modo sintético.

Outros alvos úteis: `make ingest` (pipeline de ingestão real),
`make docker-backend` (build da imagem), `make lint` (ruff no backend),
`make clean`. `make help` lista tudo.

## Deploy

Backend: container Docker no [Render](https://render.com) (`render.yaml`,
`rootDir: src/backend`, plano free). Frontend: estático na
[Vercel](https://vercel.com) (`vercel.json`, builda `src/frontend`). Custo
direto de infraestrutura do protótipo ≈ R$ 0 — Neo4j AuraDB free, créditos
IBM do hackathon, fontes públicas gratuitas.

## Documentação

Toda a documentação de produto, arquitetura e processo vive em
[`.ai/`](.ai/ai.md) — pense nela como um segundo vault, mantido junto do
código, não como um wiki à parte que descola da realidade:

| Tópico                                     | Arquivo                                                                                                                  |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Entrada única (contexto para IA e humanos) | [`.ai/ai.md`](.ai/ai.md)                                                                                                |
| Project Canvas (entregável do hackathon)   | [`.ai/docs/project-canvas.md`](.ai/docs/project-canvas.md)                                                              |
| SRS — requisitos                           | [`.ai/docs/SRS.md`](.ai/docs/SRS.md)                                                                                    |
| Data model (grafo, motor de contágio)      | [`.ai/docs/data-model.md`](.ai/docs/data-model.md)                                                                      |
| Motor de exposição e scoring              | [`.ai/docs/matching-model.md`](.ai/docs/matching-model.md)                                                              |
| Arquitetura e decisões (ARD)               | [`.ai/architecture.md`](.ai/architecture.md) · [`.ai/docs/ARD.md`](.ai/docs/ARD.md)                                   |
| Agentes de IA                               | [`.ai/docs/agentes.md`](.ai/docs/agentes.md) · [montagem no watsonx Orchestrate](.ai/docs/watsonx-orchestrate-setup.md) |
| Harness                                     | [`.ai/harness.md`](.ai/harness.md)                                                                                      |
| UI / design system                          | [`.ai/ui_guidelines.md`](.ai/ui_guidelines.md) · [`.ai/docs/design-doc.md`](.ai/docs/design-doc.md)                   |
| Índice completo de documentos              | [`.ai/docs/documents-hub.md`](.ai/docs/documents-hub.md)                                                                |
| Material de pitch                           | [`pitch/README.md`](pitch/README.md)                                                                                    |

## Roadmap

**Estado atual:** MVP funcional entregue no hackathon (12/09/2026) — motor
de exposição em dois canais, score 0–1000 com rating A–D, matriz de red
flags, 4 agentes desenhados para o watsonx Orchestrate e aplicação web com
mapa de exposição e dossiê do cliente.

**Próximos 30/60/90 dias**, se o projeto sair do protótipo (detalhado no
[Project Canvas](.ai/docs/project-canvas.md)): conectar a base real da
Krilltech e calibrar os pesos de contágio com o histórico próprio da
empresa; automatizar a coleta em rotina; calibrar a probabilidade de
inadimplência com resultado observado.

---

Construído por: **Equipe Alfa - Hackathon PMI-DF 2026**.
**Erick Mendes** - Tech Lead; Engenheiro de IA; Pitch.
**Lanna Soares** - Analista de Sistemas; Arquiteta de Dados.
**Eduardo Fernandes** - Analista de Sistemas; Engenheiro de Dados.
**Sofia Carvalho** - Dev Full-Stack; Wireframes; DevOps.
**Pedro Mello** - Dev Backend; Business Intelligence; DevOps.

Licença em [`LICENSE`](LICENSE).
