# Validation: <#issue título | Casca do projeto>

> Autor: verifier (contexto limpo) · Data: <data> · Commit: <sha> · Iteração: <N>/3
> Modo: feature (Art. 12.1) / casca (Art. 12.2)

## Veredito: PASS / FAIL

## Critérios de aceite (modo feature)
| AC | Teste(s) | O teste verifica o AC de fato? | Resultado |
|----|----------|--------------------------------|-----------|
| AC-1 | | Sim / Não (motivo) | PASS / FAIL |

## Casca (modo casca)
| Item do ARCHITECTURE.md | Evidência | Resultado |
|-------------------------|-----------|-----------|
| Módulo `:core:testing` existe e compila | | PASS / FAIL |
| `domain` sem dependência Android | | |
| Comando `<x>` do CLAUDE.md executa | | |
| CI verde no PR | | |

## Execução (saída real)
```
<testes> → <resumo da saída>
<lint> → <resumo>
<ktlint / detekt> → <resumo>
<build> → <resumo>
```

## Definition of Done
<copiar aqui o checklist do Art. 12.1 (feature) ou do Art. 12.2 (casca), marcando cada item com evidência>

## Lacunas (se FAIL) → viram passos de correção
1. <o quê> · <onde> · <AC ou regra violada>
