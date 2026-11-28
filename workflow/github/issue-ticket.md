## Story
**Como** <persona>, **quero** <ação>, **para** <benefício>.

## Contexto
<por que agora, de onde veio>

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

## Estados da tela
| Estado | Comportamento esperado |
|--------|------------------------|
| Carregando | |
| Vazio | |
| Erro | |
| Offline | |

## Requisitos não funcionais
- <ex.: primeira renderização com cache em até 500ms>

## Dependências
- <API, textos, assets, outra story>

## Fora de escopo
- <...>
