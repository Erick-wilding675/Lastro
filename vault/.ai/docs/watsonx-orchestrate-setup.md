# Montagem dos agentes no watsonx Orchestrate

**O que é este arquivo:** o roteiro de execução para tirar os quatro agentes do
[`docs/agentes.md`](agentes.md) do papel e colocá-los rodando no watsonx
Orchestrate, chamando a API do Lastro. O `agentes.md` diz *o que* cada agente é;
este diz *como* montar.

**Pré-requisito já resolvido:** credencial do watsonx criada (Erick, 12/09).

---

## O bloqueio real, antes de qualquer clique

O Orchestrate roda na nuvem da IBM. Ele **não enxerga `localhost:8000`**. Enquanto
o backend estiver só na sua máquina, nenhum agente vai conseguir chamar tool
nenhuma. Resolver isso é o passo 1, e é o único que pode travar tudo.

A segunda armadilha: o FastAPI gera OpenAPI **3.1**, e o Orchestrate só aceita
**3.0**. Baixar o `/openapi.json` da API e subir direto no Orchestrate falha. Por
isso os specs em `src/backend/openapi/` foram escritos à mão em 3.0.3, já com
`operationId` em snake_case e bloco `servers` de uma URL só, que é o que o
importador exige.

---

## Passo 1 — expor o backend numa URL pública

Com o backend de pé (`uvicorn app.main:app --reload`, respondendo em
`http://localhost:8000/docs`), abra **outro terminal**:

```bash
# opção A — Cloudflare, sem cadastro, mais rápido
winget install --id Cloudflare.cloudflared
cloudflared tunnel --url http://localhost:8000

# opção B — ngrok, se você já tem conta
ngrok http 8000
```

Os dois imprimem uma URL `https://...`. Copie. Valide antes de seguir:

```bash
curl https://SUA-URL/health
curl https://SUA-URL/agentes/dossie/CLI002
```

Se o `/health` não voltar `{"status":"ok","neo4j":"conectado"}`, o problema é
AuraDB, não Orchestrate. Volta pro passo do banco.

> A URL do tunnel muda toda vez que você reinicia o processo. Se cair, você
> refaz o passo 2 e reimporta as tools. Deixe o terminal aberto até o fim do
> pitch.

## Passo 2 — carimbar a URL nos specs

```bash
cd src/backend/openapi
python set-server.py https://SUA-URL
```

O script sobrescreve o bloco `servers` dos quatro arquivos. Ele recusa `http` e
qualquer coisa que não seja `https`, porque o Orchestrate também recusa.

## Passo 3 — importar as tools

**Pela interface:** no Orchestrate, vá em **Agent Builder → Tools → Add tool →
Import**, escolha **OpenAPI**, suba o arquivo e marque as operações que quer
expor. Repita para os quatro arquivos.

**Pela ADK (mais rápido se você já tem o CLI):**

```bash
pip install ibm-watsonx-orchestrate
orchestrate env add -n hacka -u <URL_DA_INSTANCIA>
orchestrate env activate hacka

orchestrate tools import -k openapi -f 01-coletor.openapi.json
orchestrate tools import -k openapi -f 02-risco-agro.openapi.json
orchestrate tools import -k openapi -f 03-decisao-scoring.openapi.json
orchestrate tools import -k openapi -f 04-sintetizador.openapi.json
```

Cada `operationId` vira uma tool. Você deve terminar com cinco:
`registrar_evento`, `obter_contexto_cliente`, `propagar_contagio`,
`recalcular_scoring`, `obter_dossie_cliente`.

Como a API do MVP não tem autenticação (decisão registrada em
`architecture.md`, seção Segurança), não precisa criar connection nem app-id.

## Passo 4 — criar os quatro agentes

Em **Agent Builder → Create agent**, um por um. Para cada agente: nome,
descrição, as tools da tabela e, no campo de instruções/comportamento, o
**prompt base** correspondente do `agentes.md`, copiado como está — ele já
carrega os guardrails.

| Agente | Tools | Prompt base |
|---|---|---|
| Lastro Coletor & Parser | `registrar_evento` | agentes.md § [1] |
| Lastro Risco Agro & Climático | `obter_contexto_cliente` | agentes.md § [2] |
| Lastro Decisão & Scoring | `propagar_contagio`, `recalcular_scoring` | agentes.md § [3] |
| Lastro Sintetizador | `obter_dossie_cliente` | agentes.md § [4] |

Três coisas que valem repetir dentro do campo de instruções, porque é onde o
guardrail vira comportamento e não intenção:

1. **Nenhum agente recebe credencial do Neo4j** (ARD-04). Se você se pegar
   colando string de conexão em algum campo, parou tudo: está errado.
2. **Nenhum número é inventado.** Todo valor citado sai da resposta da tool.
3. **No Decisão & Scoring, a ordem importa:** `propagar_contagio` primeiro,
   `recalcular_scoring` depois. O risco herdado da rede é componente do score.

Escolha do modelo (questão 3 em aberto no `agentes.md`): use o modelo padrão da
instância para os três primeiros e o maior disponível no Sintetizador, que é o
único que precisa escrever bem. Não é hora de comparar modelos.

## Passo 5 — agente supervisor (só se sobrar tempo)

Crie um agente `Lastro` sem tool própria, com os quatro acima como
colaboradores, e a instrução de rotear: documento ou CNPJ vai pro Coletor,
pergunta sobre safra e região vai pro Risco Agro, evento novo dispara
Decisão & Scoring, pedido de parecer vai pro Sintetizador.

Isso é o desenho completo do fluxo de orquestração do `agentes.md`. Mas a demo
do pitch roda **um** agente, então isso é bônus, não caminho crítico.

## Passo 6 — testar com o cenário da demo

No preview de chat do Sintetizador:

```
Escreva o parecer de risco do cliente CLI002.
```

O parecer está certo se ele:

- cita os **dois** vínculos do CLI002 (sócio em comum João Batista Moreira, e
  região/cultura com quebra de safra confirmada pela Conab);
- não inventa nem arredonda número nenhum;
- não afirma que o cliente vai quebrar, fala em exposição e probabilidade;
- não recomenda instrumento jurídico;
- fecha devolvendo a decisão ao comitê de crédito.

Se ele inventar número, o problema quase sempre é a tool não ter sido chamada.
Confira no rastro de execução se `obter_dossie_cliente` apareceu.

Antes de testar, garanta que o grafo está no estado do cenário:
`POST /contagio/propagar/CLI001` e depois `POST /scoring/recalcular`.

## Passo 7 — lastro para o pitch

Os outros três agentes aparecem no Canvas e na fala com print ou gravação, não
ao vivo (decisão do `agentes.md`, seção "Como demonstrar no pitch"). Tire print
de cada um dos quatro na tela de configuração, mostrando nome, tool acoplada e
instrução. Quatro prints resolvem.

---

## Se o tempo apertar, esta é a ordem

1. Tunnel + `set-server.py` + importar o `04-sintetizador`.
2. Criar o agente Sintetizador e fazer o CLI002 rodar. **Aqui já existe demo.**
3. Importar os outros três specs e criar os agentes, mesmo sem testar a fundo.
4. Prints.
5. Supervisor.

Parar depois do 2 já dá a resposta pra pergunta "onde entra IA de verdade
nisso?". Parar antes do 2 não dá.

---

## Questões que este documento fecha

| # (agentes.md) | Questão | Resposta |
|---|---|---|
| 1 | Coletor consulta bases ao vivo na demo? | Não. O `registrar_evento` grava evento já parseado. Demo não depende de API pública de terceiro. |
| 3 | Qual modelo em cada agente | Padrão da instância nos três primeiros, o maior disponível no Sintetizador. |

A questão 2 (vocabulário final de tipos de evento, dono Eduardo) já está
congelada no `enum` do `01-coletor.openapi.json`. Se ele mudar, muda lá e
reimporta.
