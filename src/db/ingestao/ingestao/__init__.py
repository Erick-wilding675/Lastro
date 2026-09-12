"""Pipeline de ingestão do Lastro — fontes públicas reais → grafo Neo4j.

Três etapas, separadas de propósito (extract / transform / load):

  extract    baixa o arquivo bruto da fonte, como ela publica, em data/raw/
  transform  normaliza para CSV de staging com schema estável, em data/staging/
  load       faz MERGE idempotente no Neo4j

A separação existe porque as três falham por motivos diferentes: extract falha
por rede e por mudança de URL na fonte; transform falha por mudança de layout;
load falha por credencial e constraint. Misturar as três num script só
transforma qualquer erro em "não funcionou".

Toda linha de staging carrega `fonte`, `coletado_em` e `confianca` — exigência
do data-model (trilha de auditoria da decisão de crédito). Nada entra no grafo
sem dizer de onde veio e com que confiança.
"""
