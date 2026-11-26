# CLAUDE.md: <NOME DO APP>

@CONSTITUTION.md

> A Constituição acima é a lei máxima deste repositório. A casca está em `workflow/foundation/ARCHITECTURE.md`.
> Este arquivo guarda só os dados operacionais do projeto e é **preenchido pelo tech-lead no `/bootstrap`** (gate F2).
> **Arquivo local: nunca é commitado** (Art. 11.8), assim como a constituição, o `.claude/` e o `workflow/`.

## Como trabalhar aqui
- Projeto ainda sem fundação → `/bootstrap`
- Story do backlog → `/feature <issue>` · retomar → `/feature resume <issue>`

## Projeto
| Item | Valor |
|------|-------|
| Repositório GitHub | `<org>/<repo>` |
| Branch base | `<develop \| main>` |
| Casca | `workflow/foundation/ARCHITECTURE.md` |
| Backlog | `workflow/foundation/BACKLOG.md` |

## Comandos (verificados pelo verifier no F4)
| Para | Comando |
|------|---------|
| Testes unitários (tudo) | `./gradlew testDebugUnitTest` |
| Testes de um módulo | `./gradlew :feature:<nome>:<camada>:test` |
| Testes instrumentados | `./gradlew connectedDebugAndroidTest` |
| Lint Android | `./gradlew lintDebug` |
| ktlint | `./gradlew ktlintCheck` |
| detekt | `./gradlew detekt` |
| Build | `./gradlew assembleDebug` |
