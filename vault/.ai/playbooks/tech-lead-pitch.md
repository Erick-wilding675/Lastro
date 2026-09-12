# Playbook — Tech Lead & Pitch (Erick)

> **Agente: leia [estado-atual.md](estado-atual.md) antes de responder.**

Você tem dois produtos para entregar e eles não são o código: o **Project
Canvas** (submissão às 15:00, obrigatório) e o **pitch de 3 minutos**. O time
constrói; você garante que o que foi construído seja entendido em três minutos
por uma banca que nunca viu o sistema.

---

## Próxima entrega imediata
**Project Canvas fechado.** É o único artefato com prazo duro e formulário.
Meta: pronto às 13:30, revisado às 14:30, submetido antes das 15:00.

### Os 10 blocos exigidos (seção 7.1 do desafio)
Não invente estrutura: a banca checa contra esta lista.

1. Problema & Diagnóstico
2. Público-Alvo / Beneficiários
3. Lógica de Funcionamento da Solução
4. Score & Classificação de Rating (0–1000, A a D)
5. Matriz de Red Flags
6. Recomendação de Decisão Operacional
7. Monitoramento Contínuo (Early Warning System)
8. Arquitetura de Negócios & Custos
9. Premissas, Restrições e Riscos
10. Próximos Passos

O template visual é o Project Model Canvas que a organização mandou. Os 10
conteúdos acima têm que aparecer nele.

---

## O roteiro do pitch — 3 minutos, quatro movimentos

**0:00–0:30 — A tese.**
"Quando um cliente da Krilltech pede Recuperação Judicial, começa um stay
period de 180 dias em que a empresa fica legalmente proibida de executar
garantia ou protestar. Quando o nome suja, já é tarde. Todo o valor está em
saber antes."

**0:30–1:15 — O diagnóstico com número.**
1.990 pedidos de RJ no agro em 2025, 56,4% acima de 2024. Inadimplência de
produtor rural saindo de 2,7% para 7,3% em doze meses. A Krilltech vende
direto a produtor rural em 18 estados: a carteira dela está exatamente na
população que está quebrando. E ela enxerga essa carteira como uma lista,
quando ela se comporta como uma rede.

**1:15–2:15 — A demo (é aqui que ganha).**
Uma tela, um clique. Agro Vale do Cerrado pede RJ. O Lastro acende quatro
clientes que ninguém ligava a ele: um por sócio em comum no quadro societário
da Receita, um por avalista compartilhado, um pelo grupo econômico, um pela
região e cultura. E mostra **por qual vínculo** cada um acendeu. Um quinto
cliente continua verde, porque não tem vínculo nenhum — o sistema não pinta a
carteira toda de vermelho.

**2:15–3:00 — A decisão e o fecho.**
Para cada cliente aceso, o sistema recomenda ação com prazo e valor
recuperável. A recomendação mais forte é converter a garantia para alienação
fiduciária, que é extraconcursal e sobrevive à RJ, enquanto ainda dá tempo.
Fecho: "a Krilltech promete otimizar a produtividade da lavoura do cliente.
O Lastro dá a ela a mesma inteligência sobre a saúde financeira de quem
compra. É o mesmo negócio, fechando o ciclo."

### Regras do pitch
- 3 minutos, 1 minuto de feedback de um jurado, **sem tréplica**. Não sobra
  espaço para se corrigir: ensaie com cronômetro.
- Os 4 melhores reapresentam às 16:40. Prepare-se para repetir.
- Leve a demo gravada além da ao vivo. Internet de auditório derruba pitch.

---

## Perguntas que a banca vai fazer, e a resposta curta

**"De onde vêm esses vínculos?"** Quadro de Sócios e Administradores da Receita
Federal, avalista dos próprios contratos da Krilltech, e CAR para o imóvel.
Tudo fonte pública ou dado que a empresa já tem.

**"E se o dado não existir?"** O sistema degrada com transparência: mostra que
a dimensão está sem fonte em vez de inventar score. Toda informação carrega
fonte e confiança.

**"Isso não é só um score de crédito?"** Não. Score olha o cliente sozinho.
O Lastro olha a rede: dois clientes com o mesmo score e balanço idêntico têm
risco diferente se um deles divide avalista com quem acabou de quebrar.

**"Quanto custa rodar?"** Infra de grafo em tier inicial e consumo de LLM por
evento, não por varredura. Um único recebível relevante recuperado antes de
virar perda paga o ano.

**"Por que grafo e não banco relacional?"** A pergunta é multi-hop com peso por
tipo de vínculo e reconstrução do caminho. Em SQL vira junção recursiva
ilegível; em Cypher é uma query. E o caminho é a explicação.

---

## Sua função de tech lead durante a janela

- **Proteja o Canvas.** Se às 13:30 o Canvas não estiver pronto, tire alguém do
  build e traga para o Canvas. O código é competitivo; o Canvas é obrigatório.
- **Congele o build às 14:00.** Nada de feature nova depois disso: só ensaio e
  revisão. Demo que quebra no pitch custa mais do que feature que não existiu.
- **Escolha uma cena e defenda.** O pitch tem uma demo, não quatro. Qualquer
  coisa que não serve àquela cena é distração.
