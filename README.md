# Android Workflow: kit de agentes para Claude Code

Workflow com 12 papéis, dois cenários e gates humanos, governado por uma constituição única.

> **Comece por [`CONSTITUTION.md`](CONSTITUTION.md).** Todo o resto deriva dela.

## Os dois cenários

| | Comando | Quando |
|---|---|---|
| **A: Fundação** | `/bootstrap` | Uma vez por projeto. A PO alinha o backlog, o tech-lead define a casca, o developer constrói, o devops implanta. Num projeto existente roda em modo mapeamento (documenta a casca que já existe). |
| **B: Feature** | `/feature <issue>` | Por story. A PO refina, o planner faz o check final e o plano, o test-engineer monta os testes RED, o developer implementa, depois vêm reviews, verifier e merge humano. |

## O repositório do app é só do app (Art. 11.8)

Nenhum arquivo deste kit é commitado no projeto Android. Eles ficam **só na sua máquina**, ignorados pelo `.git/info/exclude`, que é local e também não vai para o Git. O que o time precisa ver (ticket, plano, validação) é publicado como texto na issue e no PR do GitHub.

Nunca são commitados (lista em [`workflow/git-exclude.txt`](workflow/git-exclude.txt)):
```
CONSTITUTION.md   CLAUDE.md   CLAUDE.local.md   .claude/   workflow/
```
O `git_guard.py` bloqueia `git add` e `git commit` desses caminhos. Ele só atua em projetos Android (com `settings.gradle*` na raiz), então não interfere neste repositório do kit.

## Sem rastro de IA no GitHub do app (Art. 11.9)

Commits, PRs, reviews, issues e branches do app parecem escritos por uma pessoa do time:
- **Sem atribuição de IA.** O `.claude/settings.json` desliga o `Co-Authored-By` e o "Generated with Claude Code", e o `CLAUDE.md` reforça a regra.
- **Sem referência ao workflow.** Nada de arquivos `.md`, `workflow/`, `.claude/`, artigos, gates, `/feature` ou nomes de agente.
- **Publicação pelos modelos limpos** de `workflow/github/`, renderizados em `workflow/out/` (local), nunca pelo artefato cru.
- **O guard bloqueia o comando** se qualquer rastro aparecer no texto: inline, em heredoc ou no arquivo do `--body-file`.

## Instalar num projeto Android
1. **Crie o projeto manualmente** no Android Studio e o repositório no GitHub (o workflow não faz isso).
2. **Antes de copiar os arquivos**, ative a exclusão na raiz do projeto, para que um `git add .` seu nunca os pegue:
   ```powershell
   Get-Content <caminho-do-kit>\workflow\git-exclude.txt | Add-Content .git\info\exclude
   ```
3. Copie para a raiz do projeto:
   ```
   CONSTITUTION.md
   CLAUDE.md                 ← o tech-lead preenche no /bootstrap
   .claude/                  ← agents, skills, hooks e settings.json (se já existir um, mescle "permissions" e "hooks")
   workflow/                 ← git-exclude.txt, templates/ e github/
   ```
4. Confira que nada do workflow aparece como pendente de commit:
   ```powershell
   git status --porcelain
   ```
5. Pré-requisitos: `gh` autenticado (`gh auth status`), `python` no PATH (para o guard), Gradle wrapper funcionando.
6. Rode `/bootstrap`. Depois do merge da casca (F4), use `/feature <issue>` na ordem do backlog.

## Gates humanos
| Cenário A | Cenário B |
|-----------|-----------|
| F1 Backlog alinhado | P0 Story aprovada (só fora do backlog) |
| F2 Casca aprovada | P1 Plano aprovado |
| F3 Implantação aprovada | P2 Contrato RED (obrigatório) |
| F4 Merge da casca | P3 Merge |

## Estrutura do kit
| Caminho | O que é |
|---------|---------|
| `CONSTITUTION.md` | Lei máxima: princípios, cenários, papéis, gates, arquitetura e stack, testes, segurança, Git, DoR/DoD |
| `CLAUDE.md` | Comandos e dados do projeto; importa a constituição |
| `.claude/skills/bootstrap/` | `/bootstrap`: a sessão principal conduz o Cenário A |
| `.claude/skills/feature/` | `/feature`: a sessão principal conduz o Cenário B |
| `.claude/agents/` | 11 subagentes: product-owner, tech-lead, developer, planner, test-engineer, devops, designer, security-reviewer, verifier, refactorer, docs-writer |
| `.claude/hooks/git_guard.py` | Bloqueia merge, force push, approve, commit em branch protegida e qualquer arquivo do workflow no Git |
| `workflow/git-exclude.txt` | Lista oficial do que nunca é commitado no app |
| `workflow/templates/` | STATUS (fundação e feature), BACKLOG, ARCHITECTURE, DEPLOY-PLAN, ticket, plan, ui-spec, security-report, validation |
| `workflow/github/` | Modelos de corpo de issue e PR, usados com `--body-file` |
| `workflow/foundation/`, `workflow/specs/` | Criados no projeto durante o uso: os artefatos de cada cenário (locais) |
