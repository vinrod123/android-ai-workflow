# Ticket: #<issue> <título>

> Story: product-owner · Refinamento: developer · Check: planner
> Status: Rascunho / Refinado / Pronto (DoR ok) / Aprovado no P1 em <data>

## Story
**Como** <persona>, **quero** <ação>, **para** <benefício>.

## Contexto
<por que agora, de onde veio, épico>

## Critérios de aceite
**AC-1: <caminho feliz>**
```gherkin
Dado <contexto>
Quando <ação>
Então <resultado observável>
```

**AC-2: <erro ou borda>**
```gherkin
Dado <contexto>
Quando <ação>
Então <resultado observável>
```

## Estados de borda (refinamento)
| Estado | Comportamento esperado | AC |
|--------|------------------------|----|
| Carregando | | |
| Vazio | | |
| Erro de rede | | |
| Offline | | |
| Sem permissão | | |
| Entrada inválida | | |
| Rotação / morte de processo | | |

## Requisitos não funcionais (mensuráveis)
- <ex.: primeira renderização com cache em até 500ms>

## Impacto no código (refinamento: o developer leu o código real)
| Módulo / arquivo | O que muda | Tem testes hoje? |
|------------------|------------|------------------|

## Dependências
- <API, outra story, textos, assets, feature flag>

## Fatiamento (obrigatório se o tamanho for C)
- <ticket filho 1> · <ticket filho 2>

## Fora de escopo
- <...>

## Perguntas abertas
- [ ] [negócio] <pergunta para o humano>
- [ ] [técnico] <pergunta para o developer>

## Definition of Ready (preenchido pelo planner)
- [ ] Story com valor claro
- [ ] ACs em Gherkin com ID, testáveis e observáveis
- [ ] Estados de borda cobertos
- [ ] Requisitos não funcionais mensuráveis
- [ ] Impacto no código identificado
- [ ] Dependências resolvidas
- [ ] ui-spec.md aprovado (se houver UI)
- [ ] Fora de escopo declarado
- [ ] Zero perguntas abertas
- [ ] Tamanho até L
