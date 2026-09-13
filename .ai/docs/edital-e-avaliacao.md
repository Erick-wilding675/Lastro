# Edital e Critérios de Avaliação — Hackathon PMI-DF 2026

<!--
  Resumo do Edital 01/2026 do Student Club PMI-DF, transformado em checklist
  rastreável. Fonte: Edital_01_2026_HackathonPMIDF_VF.pdf, na raiz do repositório.
-->

**Status:** Resumo transcrito do edital — não é uma decisão de projeto, é um input fixo e externo.

---

## Cronograma e formato

- **Evento:** 11 e 12 de setembro de 2026, presencial em Brasília (DF).
- **Dia 1 — 11/09:** 19h às 21h. **O case é revelado às 19h.** Check-in: pelo menos 1 integrante até 19h30, todos até 20h (sob pena de eliminação).
- **Dia 2 — 12/09:** 9h às 19h. Check-in: pelo menos 1 integrante até 9h30, todos até 10h. Sessão de capacitação obrigatória (pelo menos 1 integrante), sob pena de desclassificação.
- **Total:** 12h de desenvolvimento (2h + 10h).
- Participação integral obrigatória — sem frequência parcial em turnos ou dias isolados.

## Equipe

- Equipes de 4 a 5 integrantes, todos com inscrição individual confirmada no Sympla, nome de grupo no formato `SIGLA-Xxxxxx`.
- Requisitos: 18 anos ou mais, regularmente matriculado em IES.
- 20 equipes validadas (critério de desempate em caso de excesso de inscritos: ordem cronológica de envio).

## Critérios de avaliação

Nota final = média aritmética simples das notas dos jurados.

| Critério | Peso | O que a banca observa | Ordem de desempate |
|---|---|---|---|
| **Diagnóstico do Problema & Impacto** | 25% | Clareza na definição do problema, dor real do usuário, uso de dados para embasar a escolha, quem é impactado | 1º |
| **Viabilidade Técnica & Execução** | 25% | Lógica de funcionamento, fluxo do projeto, protótipo/MVP que demonstre viabilidade de forma clara | 2º |
| **Arquitetura de Negócios & Custos** | 20% | Consistência do modelo de sustentação, entendimento dos custos envolvidos, viabilidade de longo prazo | 3º |
| **Implementação & Gestão de Mudanças** | 15% | Próximos passos, premissas e restrições do projeto, principais riscos e propostas para lidar com eles | 4º |
| **Pitch de Defesa & Articulação** | 15% | Qualidade da apresentação oral, clareza do valor gerado, segurança e articulação ao responder a banca | 5º |

## Checklist — o que o Lastro precisa entregar em cada critério

<!-- Preenchido/marcado progressivamente conforme os documentos de escopo avançam. -->

- [ ] **Diagnóstico do Problema & Impacto** — cobre-se em [system-description.md](system-description.md) (Problema & Valor) — **a definir no Step 1**
- [ ] **Viabilidade Técnica & Execução** — cobre-se em [../architecture.md](../architecture.md) + protótipo funcional — **a definir no Step 4**
- [ ] **Arquitetura de Negócios & Custos (20%)** — ⚠️ **nenhum documento do método padrão cobre isso hoje.** O fluxo de 7 documentos do `ai-template` (System Description → SRS → Use Cases → Data Model → Wireframes → Architecture → Design Doc) não inclui modelo de negócio/custos. Precisa de um documento próprio — a decidir se vira uma seção nova em `system-description.md` ou um arquivo dedicado `docs/business-model.md`.
- [ ] **Implementação & Gestão de Mudanças** — cobre-se em [ARD.md](ARD.md) (riscos, premissas, decisões) e no Task Tracker (`tasks/`)
- [ ] **Pitch de Defesa & Articulação** — cobre-se em [design-doc.md](design-doc.md) / material de apresentação (a construir mais perto da hora)

## Regras que restringem a construção

- Sem cópia ou reprodução, ainda que parcial, de outras fontes ou competições — desclassificação em caso de identificação.
- No ato da inscrição, a equipe cede direitos de imagem, nome, voz e de todo conteúdo desenvolvido durante o evento ao PMI-DF e às empresas parceiras.
- Código de conduta: [PMI Code of Ethics](https://www.pmi.org/about/ethics/guidelines).

## Contato / dúvidas oficiais

- student.club@pmidf.org
