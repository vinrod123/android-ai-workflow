# Deploy Plan: implantação da casca

> Autor: devops · Status: Plano / Aprovado no F3 em <data> / Aplicado em <data>
> Regra: plan before apply. Nada daqui é aplicado antes do F3.

## O que muda
| # | Mudança | Onde | Reversível? | Como reverter |
|---|---------|------|-------------|---------------|
| 1 | Workflow de CI (build, testes unitários, lint, ktlint, detekt) em todo PR | `.github/workflows/ci.yml` | Sim | Remover o arquivo |
| 2 | Proteção da branch base (PR obrigatório, CI obrigatório, sem force push) | GitHub › Settings › Branches | Sim | `gh api -X DELETE .../protection` |

## Pipeline de CI
```
on: pull_request → setup JDK → cache do Gradle → <comandos do CLAUDE.md>
```

## Secrets que o HUMANO precisa cadastrar (o devops nunca vê os valores)
| Nome | Para quê | Quando é necessário |
|------|----------|---------------------|

## Evidência do plano (dry-run)
```
<saída de validação: actionlint, gh api GET da proteção atual etc.>
```

## Riscos
- <risco> → <mitigação>
