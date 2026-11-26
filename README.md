# Android Workflow: kit de agentes para Claude Code

Workflow com 12 papéis, dois cenários e gates humanos, governado por uma constituição única.

> **Comece por [`CONSTITUTION.md`](CONSTITUTION.md).** Todo o resto deriva dela.

## Os dois cenários

| | Comando | Quando |
|---|---|---|
| **A: Fundação** | `/bootstrap` | Uma vez por projeto. Alinha o backlog com a PO, o tech-lead define a casca, o developer constrói, o devops implanta. Num projeto existente roda em modo mapeamento (documenta a casca que já existe). |
| **B: Feature** | `/feature <issue>` | Por story. O developer refina, o planner faz o check final e o plano, o test-engineer monta os testes RED, o developer implementa, depois reviews, verifier e merge humano. |

## Instalar num projeto Android
1. **Crie o projeto manualmente** no Android Studio e o repositório no GitHub (o workflow não faz isso).
2. Copie para a raiz do projeto:
   ```
   CONSTITUTION.md
   CLAUDE.md                 ← o tech-lead preenche no /bootstrap
   .claude/agents/
   .claude/skills/bootstrap/
   .claude/skills/feature/
   .claude/hooks/git_guard.py
   .claude/settings.json     ← se já existir, mescle "permissions" e "hooks"
   workflow/templates/
   .github/pull_request_template.md
   .github/ISSUE_TEMPLATE/feature.md
   ```
3. Pré-requisitos: `gh` autenticado (`gh auth status`), `python` no PATH (para o guard), Gradle wrapper funcionando.
4. Rode `/bootstrap`. Depois do merge da casca (F4), use `/feature <issue>` na ordem do backlog.

## Gates humanos
| Cenário A | Cenário B |
|-----------|-----------|
| F1 Backlog alinhado | P0 Story aprovada (só fora do backlog) |
| F2 Casca aprovada | P1 Plano aprovado |
| F3 Implantação aprovada | P2 Contrato RED (obrigatório) |
| F4 Merge da casca | P3 Merge |

## Estrutura
| Caminho | O que é |
|---------|---------|
| `CONSTITUTION.md` | Lei máxima: princípios, cenários, papéis, gates, arquitetura e stack, testes, segurança, DoR/DoD |
| `CLAUDE.md` | Comandos e dados do projeto; importa a constituição |
| `.claude/skills/bootstrap/` | `/bootstrap`: a sessão principal conduz o Cenário A |
| `.claude/skills/feature/` | `/feature`: a sessão principal conduz o Cenário B |
| `.claude/agents/` | 11 subagentes: product-owner, tech-lead, developer, planner, test-engineer, devops, designer, security-reviewer, verifier, refactorer, docs-writer |
| `.claude/hooks/git_guard.py` | Bloqueia merge, force push, approve e commit em branch protegida |
| `workflow/templates/` | STATUS (fundação e feature), BACKLOG, ARCHITECTURE, DEPLOY-PLAN, ticket, plan, ui-spec, security-report, validation |
