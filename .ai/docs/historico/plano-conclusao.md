# Plano de Conclusão — Lastro pós-hackathon

**O que é este documento:** o fechamento concreto do pitch. Depois de mostrar
que o motor funciona (a demo), o pitch fecha dizendo **quanto custa, quem
precisa construir e em quanto tempo** para levar o Lastro da demonstração de
12h até uso ativo pelo comitê de crédito da Krilltech. Números em ordem de
grandeza, tratados como hipótese declarada e defensável, no mesmo espírito dos
pesos do motor de contágio: nada aqui é fingido como precisão que o time não
tem.

Horizonte: **6 meses**, do fim do hackathon até a virada para uso ativo em
produção (saindo de modo sombra). Ancorado no roadmap de 30/60/90 dias já
presente no Project Canvas (bloco LINHA DO TEMPO), aqui detalhado com equipe e
custo.

---

## Equipe necessária

| Papel | Dedicação | Duração | Responsabilidade |
|---|---|---|---|
| Tech Lead / Arquiteto de Soluções | Integral | 6 meses | Arquitetura, integração com sistemas da Krilltech, ponte técnica com o comitê de crédito |
| Engenheiro de Dados / Backend (x2) | Integral | 6 meses | Motor de contágio e scoring em produção, ingestão das bases públicas, APIs |
| Engenheiro Frontend | Integral | 4 meses, depois manutenção | Mapa de exposição, dossiê do cliente, painel do comitê |
| Analista de Dados e Fontes Públicas | Integral 2 meses, depois parcial | 6 meses | Pipeline de QSA, DataJud, SICAR, Conab/ZARC/INMET; qualidade e atualização dos dados |
| Especialista de Domínio (crédito agro) | Consultoria pontual | Ao longo dos 6 meses | Validação dos pesos do motor com conhecimento de mercado, calibração dos componentes do score |
| Ponto focal da Krilltech (comitê de crédito) | Meio período | A partir do mês 2 | Validação do modo sombra, feedback sobre alertas, decisão de virada para produção |

A base técnica do MVP construído no hackathon (schema Neo4j, motor de dois
canais, scoring, os quatro agentes) é reaproveitada integralmente: o trabalho
dos 6 meses é conectar à base real, automatizar a coleta e calibrar, não
reconstruir do zero.

---

## Cronograma de execução

**Mês 1 — Conexão e fundação**
Ingestão da base real de recebíveis e clientes da Krilltech. Mapeamento de
vínculos societários via QSA da Receita Federal. Ajuste do schema aos dados
reais (tipos de garantia, estágios jurídicos, culturas efetivamente operadas).

**Meses 2 e 3 — Automação e modo sombra**
Coleta contínua das bases públicas (DataJud, Receita, SICAR/IBAMA, PGFN,
Conab/ZARC/INMET) rodando em rotina, sem intervenção manual. Calibração
inicial dos pesos do motor de contágio com o especialista de domínio e o
ponto focal da Krilltech. Entrada em **modo sombra**: o sistema roda ao lado
do processo atual, sem poder de decisão, e todo alerta é registrado para
comparação posterior.

**Meses 4 e 5 — Validação**
Comparação sistemática entre o que o Lastro sinalizou e o que de fato
aconteceu na carteira. Calibração da probabilidade de inadimplência em
horizontes de 6, 12 e 24 meses com resultado observado. Ajuste fino dos
componentes do score e dos pesos de contágio a partir dessa comparação.

**Mês 6 — Virada para produção**
Handoff para uso ativo pelo comitê de crédito, com os alertas do Lastro
passando a ser insumo formal de decisão. Treinamento das equipes de crédito e
comercial. Documentação final e definição do plano de expansão para revendas
e cooperativas.

---

## Orçamento estimado

Valores de referência de mercado para squads de dados e machine learning no
Brasil, ordem de grandeza, não cotação fechada.

| Item | Custo mensal | Duração | Subtotal |
|---|---|---|---|
| Tech Lead / Arquiteto | R$ 18.000 | 6 meses | R$ 108.000 |
| Engenheiros de Dados/Backend (x2) | R$ 12.000 cada | 6 meses | R$ 144.000 |
| Engenheiro Frontend | R$ 10.000 | 4 meses | R$ 40.000 |
| Analista de Dados e Fontes Públicas | R$ 8.000 | 3 meses (equivalente) | R$ 24.000 |
| Especialista de Domínio (consultoria pontual) | — | 6 meses | R$ 15.000 |
| **Subtotal equipe** | | | **R$ 331.000** |
| Neo4j AuraDB (tier profissional) | R$ 2.500 | 6 meses | R$ 15.000 |
| Hospedagem backend/frontend | R$ 1.000 | 6 meses | R$ 6.000 |
| Consumo de LLM por evento (watsonx ou equivalente) | R$ 1.500 | 6 meses | R$ 9.000 |
| Ferramentas e licenças | — | — | R$ 5.000 |
| **Subtotal infraestrutura** | | | **R$ 35.000** |
| **Total estimado (6 meses até produção)** | | | **≈ R$ 366.000** |

**Leitura do investimento:** o próprio cenário de demonstração já identifica
R$ 1.258.000 em exposição que hoje está classificada como saudável. Recuperar
uma fração desse valor, ou evitar que ele vire perda total, já paga o
investimento do primeiro semestre de operação. O ponto de equilíbrio real
depende do volume de recebíveis em risco na carteira completa da Krilltech,
que só é conhecido depois do mês 1 (conexão à base real) — e é exatamente por
isso que o roadmap coloca a conexão à base real como primeiro marco, antes de
qualquer promessa de retorno mais precisa.

---

## O que este plano não é

Não é uma proposta comercial fechada, nem um contrato. É a resposta honesta à
pergunta que toda banca de hackathon faz sem dizer em voz alta: "e se vocês
ganharem, isso vira alguma coisa de verdade?" A resposta é sim, com equipe,
prazo e ordem de grandeza de custo definidos, e com o primeiro semestre
desenhado para não fazer nenhuma promessa de resultado antes de validar em
modo sombra contra a base real.
