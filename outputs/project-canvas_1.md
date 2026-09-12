# Project Model Canvas — Lastro

**Este é o entregável.** Texto pronto para transcrever em cada bloco do template
enviado pela organização. Cada campo é curto de propósito: canvas é página única,
e a banca lê em pé.

Fundamentação completa e respostas de defesa: [project-canvas-fundamentacao.md](project-canvas-fundamentacao.md).

---

## PITCH

Quando um cliente da Krilltech pede Recuperação Judicial, a empresa fica 180 dias
legalmente impedida de executar garantia ou protestar. O **Lastro** trata a carteira
como rede, não como lista: mede a exposição compartilhada entre clientes e mostra
**por qual vínculo** ela chega — a tempo de decidir limite, condição de pagamento e
prioridade de recuperação.

---

## JUSTIFICATIVAS *(passado)*

- **1.990 pedidos de RJ no agro em 2025, +56,4% sobre 2024** (Serasa Experian)
- **Inadimplência do produtor rural PF: 2,7% → 7,3% em 12 meses** (Banco Central)
- **8,8% de inadimplência rural no 1T2026 — recorde da série** (Serasa Experian)
- Lei 14.112/2020 estendeu a RJ ao produtor rural pessoa física
- Quebra de safra (El Niño/La Niña), queda de soja e milho, custo de insumo alto
- Efeito cascata chega ao fornecedor de tecnologia — a Krilltech
- A carteira é gerida como lista de vencimentos; o risco no agro é correlacionado

## OBJETIVO SMART

Entregar um sistema de inteligência de risco de crédito que, a partir do CNPJ ou
CPF do cliente, produza **score de 0 a 1000 com rating A–D**, matriz de red flags,
alerta antecipado de exposição compartilhada e recomendação de limite e condição
de pagamento — validado em demonstração funcional sobre carteira simulada,
entregue até **15:00 de 12/09/2026**.

## BENEFÍCIOS *(futuro)*

- Decidir **antes do stay period**, enquanto ainda existe opção
- Reduzir o tempo de retorno do capital já vencido
- Priorizar a carteira pelo que volta mais rápido, dentro da capacidade do time
- Exposição consolidada e previsibilidade de caixa para a diretoria
- Decisão auditável: fonte, data e decomposição em toda nota
- Sustentar a relação com o cliente bom no momento em que o setor aperta

---

## PRODUTO

- Grafo da carteira em Neo4j: cliente, recebível, sócio, avalista, grupo
  econômico, imóvel, região, cultura, safra e evento
- **Motor de exposição em dois canais**: estrutural e sistêmico
- Score 0–1000 com rating A–D e decomposição visível
- Matriz de red flags
- Recomendação de limite, condição de pagamento e estratégia de recuperação
- Radar de eventos (early warning) sobre bases públicas
- Aplicação web: mapa de exposição da carteira + dossiê do cliente
- Relatório Padronizado de Risco em linguagem natural

## REQUISITOS

- **Score 0–1000** — A: 800+ · B: 600+ · C: 400+ · D: <400 (alerta de RJ)
- **5 componentes**: comportamento de pagamento · eventos jurídicos e fiscais ·
  cobertura de garantia com *haircut* por tipo · exposição herdada da rede ·
  risco agro e ambiental
- **Exposição em dois canais**: estrutural (grupo 0,90 · avalista 0,85 · sócio
  0,70) e sistêmico (região+cultura 0,75 · revenda 0,65 · cultura 0,40), sendo
  que o sistêmico só atinge peso cheio com **evento regional confirmando o choque**
- **Red flags**: RJ distribuída · protesto · execução fiscal · exposição
  estrutural ≥0,80 · embargo ambiental · quebra de safra · cobertura de garantia
  frágil · alteração societária
- Toda exposição exibe **o caminho do vínculo** que a originou
- Todo dado carrega **fonte e data**; nenhuma ação é disparada automaticamente
- **4 agentes**: Coletor & Parser · Risco Agro & Climático · Decisão & Scoring ·
  Sintetizador de Relatórios

---

## STAKEHOLDERS EXTERNOS & FATORES EXTERNOS

**Stakeholders:** área de crédito e financeiro da Krilltech (usuário direto) ·
comitê de crédito e diretoria · time comercial · produtor rural cliente · cadeia
(revendas, distribuidores, cooperativas) · banca PMI-DF e IBM

**Fatores externos:** Lei 14.112/2020 · clima (El Niño/La Niña) · cotação de soja
e milho · disponibilidade e atualidade das bases públicas (Receita/QSA, DataJud,
PGFN, SICAR/IBAMA, Conab/ZARC/INMET) · política de crédito e jurídica da própria
Krilltech

## EQUIPE

- **Erick** — engenheiro de IA · tech lead, agentes e pitch
- **Lanna** — analista de sistemas · grafo e dados (AuraDB)
- **Eduardo** — analista de sistemas · fontes de dados públicas
- **Sofia** — desenvolvedora · wireframes e frontend
- **Pedro** — desenvolvedor · KPIs e backend

---

## PREMISSAS

- A venda é a prazo, com pagamento casado à safra
- Existe controle de recebíveis extraível (planilha ou ERP)
- Vínculos entre clientes são inferíveis por documento, QSA e aval
- A capacidade do time de cobrança é limitada
- As bases públicas seguem acessíveis e com atualização periódica

## GRUPO DE ENTREGAS

1. **Grafo e dados** — schema, seed, ingestão
2. **Inteligência** — motor de exposição, scoring, red flags, recomendação
3. **Agentes** — os quatro, no watsonx Orchestrate
4. **Aplicação** — mapa de exposição e dossiê do cliente
5. **Governança** — trilha de auditoria da decisão de crédito
6. **Comunicação** — Project Canvas e pitch

## RESTRIÇÕES

- Janela do hackathon, submissão às 15:00 · pitch de 3 minutos
- Stack IBM: watsonx Orchestrate + IBM Bob
- Sem base real da Krilltech — dados sintéticos e mascarados
- Nenhum dado pessoal real no repositório
- O sistema **não prescreve instrumento jurídico**: diagnostica, e a decisão de
  política de crédito permanece com a empresa

---

## RISCOS

| Risco | Como tratamos |
|---|---|
| Base atual sem os vínculos mapeados | Enriquecimento por QSA é etapa do pipeline, não pré-requisito |
| Pesos parecerem arbitrários | Hipótese declarada e auditável, com o caminho sempre visível |
| Parecer "mais um score de crédito" | O componente de rede é o que bureau nenhum entrega |
| Falso positivo queimar relação comercial | Canal sistêmico exige evento confirmado; nada é automático |
| Dado público desatualizado | Fonte e data em cada evento; o sistema mostra a idade do dado |
| Demo falhar ao vivo | Gravação de backup do fluxo completo |

## LINHA DO TEMPO

- **Hoje** — MVP funcional, Project Canvas e pitch
- **30 dias** — conectar a base real da Krilltech e calibrar os pesos com o
  histórico próprio da empresa
- **60 dias** — coleta automatizada em rotina (DataJud, Receita, SICAR, INMET) e
  régua de alertas para o time de crédito
- **90 dias** — calibrar a probabilidade de inadimplência com resultado observado,
  em horizontes de 6, 12 e 24 meses
- **Depois** — abrir como serviço para revendas, distribuidores e cooperativas

## CUSTOS

- **Protótipo:** Neo4j AuraDB Free + créditos IBM do evento + fontes públicas
  gratuitas ≈ **R$ 0 de infraestrutura**; o custo real é hora de equipe
- **Operação:** grafo gerenciado em tier inicial; consumo de LLM **por evento**,
  não por varredura contínua
- **Sem custo de bureau** — as fontes do desafio são públicas e abertas
- **Retorno:** custo evitado, medido em capital que não virou perda
- **Equilíbrio:** um único recebível relevante recuperado antes de virar perda
  paga o ano de operação

---

## Conferência: onde cada exigência da seção 7.1 está no canvas

| Exigência (seção 7.1) | Bloco do canvas |
|---|---|
| 1. Problema & Diagnóstico | JUSTIFICATIVAS |
| 2. Público-Alvo / Beneficiários | STAKEHOLDERS EXTERNOS + BENEFÍCIOS |
| 3. Lógica de Funcionamento | PRODUTO + REQUISITOS |
| 4. Score & Classificação de Rating | REQUISITOS (primeiro item) |
| 5. Matriz de Red Flags | REQUISITOS (quarto item) |
| 6. Recomendação de Decisão Operacional | PRODUTO + BENEFÍCIOS |
| 7. Monitoramento Contínuo (Early Warning) | PRODUTO (radar de eventos) |
| 8. Arquitetura de Negócios & Custos | CUSTOS |
| 9. Premissas, Restrições e Riscos | PREMISSAS + RESTRIÇÕES + RISCOS |
| 10. Próximos Passos | LINHA DO TEMPO |

**Todos os 10 estão cobertos.** Se a banca perguntar por algum, aponte o bloco.
