# Lastro — Índice de Contexto para IA

<!--
  PONTO DE ENTRADA ÚNICO para qualquer assistente de IA (IBM Bob, Claude, etc.)
  trabalhando neste repositório. AGENTS.md e CLAUDE.md, na raiz do repo, só
  redirecionam para cá.
-->

## ⛔ ANTES DE QUALQUER COISA: quem está falando com você?

Se a pessoa se identificar por papel — *"sou analista de sistemas"*, *"sou dev
fullstack"*, *"sou o tech lead"* — **pare de ler este arquivo e vá para
[playbooks/README.md](playbooks/README.md)**. Lá está o protocolo de atendimento
por papel e a próxima entrega imediata de cada um. Isso é o task tracker do time
durante o hackathon.

Volte aqui depois, para contexto de produto.

---

> **⚠️ PIVÔ DE DOMÍNIO EM 11/09.** O case oficial foi revelado: problema real da
> **KRILLTECH** (agtech brasileira nascida de parceria com UnB e EMBRAPA, produto
> Arbolin Biogenesis) — aumento de inadimplência, pedidos repentinos de
> Recuperação Judicial e recuperação de capital lenta. O projeto deixou de ser
> sobre formação de squads e passou a ser sobre **risco relacional de crédito e
> recuperação de recebíveis no agro**. Se encontrar referência a "Talent Graph",
> "squad" ou "Project Genome", é resíduo da versão anterior: trate como
> desatualizado e sinalize.

**Nome do produto:** Lastro.

---

## O projeto, em uma olhada

**Sistema:** Lastro — processo contínuo de **gestão de risco relacional e
recuperação de capital**. Representa a carteira de recebíveis como uma rede, não
uma lista; antecipa inadimplência propagando risco pelos vínculos entre clientes;
e prioriza a recuperação do que já venceu, sempre explicando o caminho.

**A tese, em uma frase:** quando um cliente pede RJ, começa um *stay period* de
180 dias em que a Krilltech fica legalmente impedida de executar garantia ou
protestar. Depois do pedido não há o que fazer. Todo o valor está em saber antes.

**O diferencial técnico:** produtor rural não quebra sozinho. Quebra por grupo
econômico, avalista comum, sócios em comum (QSA da Receita), revenda, região,
cultura e safra. O grafo propaga esse risco multi-hop e acende os vizinhos
expostos antes de virarem inadimplência — consulta que em SQL vira junção
recursiva ilegível e em Cypher é uma query.

**Prazos reais:** submissão do Project Canvas até **15:00 de 12/09**. Pitch de
**3 minutos** a partir das 15:20. Entregáveis obrigatórios: Canvas e pitch.
Aplicações, agentes, código e painéis são *entregáveis competitivos* — decisão do
Erick é entregá-los mesmo assim, sem nunca deixar o Canvas em segundo plano.

**Stack:** IBM watsonx Orchestrate (4 agentes) + IBM Bob + Neo4j AuraDB +
Python/FastAPI + React. Código em `src/` (monólito modular — ver `src/README.md`).

---

## Mapa de Navegação

| Tópico | Arquivo |
|---|---|
| **Playbooks por papel (task tracker)** | [playbooks/README.md](playbooks/README.md) |
| **Estado atual do time** | [playbooks/estado-atual.md](playbooks/estado-atual.md) |
| Descrição do sistema e diagnóstico | [docs/system-description.md](docs/system-description.md) |
| Data model (grafo, motor de contágio) | [docs/data-model.md](docs/data-model.md) |
| Matching Model (contágio, níveis 1–3, agentes) | [docs/matching-model.md](docs/matching-model.md) |
| Project Canvas | [docs/project-canvas.md](docs/project-canvas.md) |
| Arquitetura | [architecture.md](architecture.md) |
| Decisões de arquitetura (ARD-01 a 05) | [docs/ARD.md](docs/ARD.md) |
| Harness — GIRO | [harness.md](harness.md) |
| Regras e critérios do hackathon | [docs/edital-e-avaliacao.md](docs/edital-e-avaliacao.md) |
| UI / design system | [ui_guidelines.md](ui_guidelines.md) + [docs/design-doc.md](docs/design-doc.md) |
| Índice de documentos | [docs/documents-hub.md](docs/documents-hub.md) |

---

## Hard Rules

1. **O modelo recomenda, nunca decide sozinho.** Nada dispara cobrança, protesto
   ou ação judicial automaticamente.
2. **GIRO não é opcional** — ver [harness.md](harness.md).
3. **Contágio sempre explica o caminho.** Nunca mostrar "risco 0,8" sem dizer por
   qual vínculo esse risco chegou. O caminho é a explicação.
4. **O watsonx Orchestrate nunca fala com o driver do Neo4j.** Ele chama a API do
   backend (ARD-04). Credencial de banco dentro de agente é erro de arquitetura.
5. **Toda aresta do grafo existe para responder uma pergunta de decisão.** Não
   modele por completude.
6. **Meça antes de afirmar; corrija-se em voz alta quando a medição contradisser.**
7. **Prefira falha ruidosa a degradação silenciosa.**
8. **Nenhum dado real de produtor entra no repositório.** O seed é sintético e
   mascarado.
9. **Números são a linguagem aqui.** R$ em risco, dias de atraso, score 0–1000,
   prazo de retorno. A regra antiga de "nada de número cru na UI" era do projeto
   anterior e está revogada.
10. **Nunca descreva o Lastro como "um sistema de cobrança" ou "um score".** É um
    processo contínuo de inteligência de risco e recuperação; a priorização da
    carteira é uma saída, não a identidade.
11. **O Canvas tem prioridade sobre o build.** O build é competitivo; o Canvas é
    obrigatório e tem prazo duro.
