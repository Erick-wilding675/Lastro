# Playbooks por papel — como o agente atende cada pessoa do time

<!--
  Este diretório é o task tracker vivo do Lastro durante o hackathon.
  Não é documentação de leitura: é instrução de execução para o agente.
-->

## Para o agente (IBM Bob, Claude Code, qualquer um): protocolo

Quando alguém abrir uma sessão e se identificar por papel — *"sou um dos
analistas de sistemas"*, *"sou dev fullstack"*, *"sou o tech lead"* — faça
**nesta ordem, sem pular**:

1. Leia [estado-atual.md](estado-atual.md). É o que já está pronto e o que
   está travado. Nunca refaça o que já existe lá.
2. Leia o playbook do papel (tabela abaixo).
3. Identifique **a próxima entrega imediata** daquela pessoa. É uma só. Se
   duas pessoas têm o mesmo papel, pergunte qual das duas trilhas ela pegou
   (A1/A2, D1/D2) — nunca deixe as duas fazendo a mesma coisa.
4. Execute com ela: gere arquivo, comando, query, o que for. Não devolva
   conselho genérico, devolva o artefato.
5. Ao terminar, **atualize [estado-atual.md](estado-atual.md)**: marque o que
   ficou pronto e o que destravou. Esse arquivo é a memória compartilhada do
   time; se ele não for atualizado, o próximo agente trabalha cego.

| A pessoa diz | Leia |
|---|---|
| "analista de sistemas", "vou fazer os agentes", "watsonx", "schema no neo4j" | [analista-de-sistemas.md](analista-de-sistemas.md) |
| "dev fullstack", "backend", "frontend", "API", "React" | [dev-fullstack.md](dev-fullstack.md) |
| "tech lead", "pitch", "canvas", "apresentação" | [tech-lead-pitch.md](tech-lead-pitch.md) |

## Regras que valem para todos os papéis

- **Prazo real: 15:00 de 12/09** para submeter o Project Canvas no formulário.
  Não são 19h. Tudo que não estiver pronto às 14:30 não entra.
- **Pitch é de 3 minutos.** Qualquer artefato precisa caber nessa narrativa
  ou não é prioridade.
- O contexto completo do projeto está em [../ai.md](../ai.md). As regras
  inegociáveis estão nas Hard Rules de lá.
- **Nunca mostre risco sem o caminho que o gerou.** Vale para código, tela,
  slide e fala.
- Dúvida de escopo não se resolve inventando: pergunta ao Erick e segue para
  a próxima tarefa da fila enquanto espera.
