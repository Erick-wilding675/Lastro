# Estado atual — quadro vivo

**Última atualização:** 12/09, ~00h, antes da reunião de alinhamento.
**Quem atualiza:** qualquer agente, ao concluir uma entrega. Mantenha honesto.

---

## Pronto (não refazer)

| Item | Onde | Nota |
|---|---|---|
| Especificação completa do produto | `vault/.ai/docs/` | Reescrita para o case KRILLTECH |
| Decisões de arquitetura ARD-01 a ARD-05 | `vault/.ai/docs/ARD.md` | Neo4j, FastAPI, React, integração via API, explicação materializada |
| Design system (paleta, tipografia, tokens) | `vault/.ai/ui_guidelines.md` | Tema escuro, paleta Síntese, wordmark Sora |
| Schema + seed do grafo | `src/db/cypher/01-schema-e-seed.cypher` | Cenário de demo plantado (CLI001 pede RJ e acende 4 vizinhos) |
| As 5 queries do motor | `src/db/cypher/02-queries-motor.cypher` | Contágio, score 0-1000, red flags, recomendação, KPIs |
| Estrutura do monólito modular | `src/` | Backend 6 módulos + frontend com grafo e painel |

## Em aberto — atribuições definidas na reunião

| Item | Dono | Papel | Bloqueia |
|---|---|---|---|
| Schema no AuraDB (instância + seed + validar as 5 queries) | **Lanna** | Analista (trilha A1) | Tudo que roda |
| Fontes diretas dos dados em mãos (Receita/QSA, DataJud/DJE, PGFN, SICAR/IBAMA, Conab/ZARC/INMET) | **Eduardo** | Analista | Credibilidade do pipeline no pitch |
| Wireframes | **Sofia** | Dev | Frontend e a cena do pitch |
| Mapear KPIs | **Pedro** | Dev | Números na tela e no canvas |
| Agentes definidos (documento) | **Erick** | Tech lead | Demo dos agentes |
| **Project Canvas** (entregável obrigatório) | **Erick** | Tech lead | Submissão às 15:00 |
| **Pitch de 3 min** | **Erick** | Tech lead | Avaliação 15:20 |

> Agente: ao atender alguém, use o nome para achar a linha acima. Se a pessoa
> não estiver na tabela, pergunte o papel e siga o playbook correspondente.

## Revisão do time (12/09) — ✅ JÁ APLICADA no código e nos docs

1. **Pesos do contágio separados em dois canais.** Estrutural (grupo 0,90;
   avalista 0,85; sócio 0,70) e sistêmico (região+cultura+safra 0,75; mesma
   revenda 0,65; só cultura 0,40). O canal sistêmico só entra com peso cheio
   **se houver evento regional confirmando o choque** (quebra de safra, alerta
   ZARC, queda de preço); sem evento, entra reduzido.
2. **Haircut por tipo de garantia** antes de calcular cobertura: alienação
   fiduciária 1,00; aval 0,70; CPR 0,60; penhor de safra 0,50; nenhuma 0,00.
3. **GIRO sai do discurso.** A substância fica como "trilha de auditoria da
   decisão de crédito", uma linha, sem virar pilar.
4. **Alienação fiduciária deixa de ser recomendação de destaque.** O sistema
   diagnostica fragilidade de garantia; qual instrumento adotar é política de
   crédito da Krilltech, não recomendação nossa.
5. **Linguagem:** nada de "prever quem vai quebrar". O sistema mede *exposição
   compartilhada* e mostra *por qual vínculo*. E nada de criticar o processo
   atual da empresa.

## Decisões tomadas que o time precisa saber

- O produto se chama **Lastro**.
- O desafio **não exige código** — Canvas e pitch são os obrigatórios; app,
  agentes, código e painéis são "entregáveis competitivos". Decisão do Erick:
  fazemos MVP funcional mesmo assim, porque é o que diferencia em Viabilidade
  Técnica (25% da nota). Mas **o Canvas tem prioridade absoluta sobre o build.**
- Painel de KPIs sai como artefato separado, não dentro do sistema.
- Números aparecem na tela (R$, dias, score). A regra antiga de "nada de número
  cru" era do projeto anterior e foi derrubada.

## Cenário da demo (todo mundo conta a mesma história)

`CLI001 — Agro Vale do Cerrado` pede Recuperação Judicial. O Lastro propaga o
risco e acende quatro clientes que ninguém ligava a ele:

| Cliente | Acende por | Peso |
|---|---|---|
| CLI005 Terra Nova | mesmo grupo econômico (estrutural) | 0,90 |
| CLI003 Agropecuária Horizonte | avalista em comum — Marcos Ferreira Duarte (estrutural) | 0,85 |
| CLI004 Sítio Boa Esperança | mesma região e cultura **com quebra de safra confirmada pela Conab** (sistêmico), e ainda tem embargo IBAMA | 0,75 |
| CLI002 Fazenda Santa Luzia | sócio em comum no QSA — João Batista Moreira (estrutural) **e** mesma região/cultura (sistêmico) | 0,75 |

`CLI006 Fazenda Ipê Amarelo` é o controle: outra região, outra cultura, nenhum
vínculo. Continua verde. É isso que prova que o sistema não está pintando a
carteira toda de vermelho.

**A fala que fecha a objeção da banca:** o Sudoeste Goiano só acende porque existe
um evento da Conab registrando quebra de safra na região. Sem esse evento, o peso
cai de 0,75 para 0,30 e a vizinhança não dispara. A região não é culpada por
associação — ela é medida por causa comum documentada.
