# Convenções de Código

<!--
  Os padrões que um agente DEVE seguir ao escrever código neste repositório.
  Preenchido a partir das escolhas de arquitetura, depois do Step 4.
-->

**Status:** Não iniciado — depende da Architecture (Step 4).

## {{Linguagem / Framework}}

- **Versão:** {{}}
- **Lints / formatação:** {{ferramenta + config}}
- **Padrão de estado / arquitetura:** {{}}
- **Modelos / validação:** {{}}
- **Tratamento de erros:** {{}}

### Exemplo

```{{lang}}
{{um exemplo curto e canônico do estilo preferido}}
```

---

## Dados / Banco de Dados

- {{migrations, IDs, naming, regras de indexação}}

---

## Testes

- **Unitário:** {{o quê + ferramentas}}
- **Integração:** {{}}

---

## Git

- Nomenclatura de branch: prefixos `feat/`, `fix/`, `chore/`, `infra/`
- Mensagens de commit: conventional commits — `feat(escopo): resumo`
- Sem segredos commitados; usar `.env.example` com placeholders
- Agentes em paralelo trabalham em worktrees separados sob `.worktrees/` (git-ignored), um branch cada — ver [workflows/parallel-agents.md](workflows/parallel-agents.md)

---

## Segurança

- Sem segredos no código-fonte — apenas variáveis de ambiente / secret managers
- {{queries parametrizadas / validação de input / regras de autorização / tratamento de PII — especialmente relevante aqui, dado que o Talent Model lida com dados pessoais}}

---

## Nomenclatura

- Arquivos: {{convenção}}
- Tipos / classes: {{convenção}}
- {{outras regras}}
