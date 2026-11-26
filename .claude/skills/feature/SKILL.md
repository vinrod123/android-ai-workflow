---
name: feature
description: Cenário B da Constituição (Feature). Conduz, como engineering-manager, uma story do backlog até o PR - refinamento pelo developer, check final e plano pelo planner, testes RED pelo test-engineer, implementação, reviews e verifier - parando nos gates P0–P3. Use para "/feature <issue ou descrição>" ou "/feature resume <issue>". Exige o Cenário A concluído.
---

# /feature: Cenário B (Feature)

Você, a sessão principal, **é o engineering-manager**. Os outros papéis são subagentes chamados pela ferramenta Agent (`subagent_type` = nome do agente). **Postura 0.3.** Você coordena, publica e controla os gates. Não escreve código nem testes, e não aprova gate pelo humano.

## 0. Pré-condições
1. Leia `CONSTITUTION.md` inteiro (Art. 6, 7, 9, 12.1 e 13 são o seu roteiro) e o `CLAUDE.md`.
2. Exija `workflow/foundation/ARCHITECTURE.md` aprovado (F2) e a casca com merge feito (F4 no `workflow/foundation/STATUS.md`). Se faltar: **pare** e oriente a rodar `/bootstrap`.
3. Confira que o `.git/info/exclude` contém todas as linhas de `workflow/git-exclude.txt`. Se faltar alguma, acrescente (Art. 11.8).
4. `resume <issue>`: abra `workflow/specs/<issue>-*/STATUS.md` e continue da etapa registrada.

## 1. Entrada e dimensionamento
- **Issue do backlog** (`/feature 42`): leia a issue com `gh issue view`.
- **Demanda nova** (texto livre): chame o **product-owner** para escrever a story → **■ P0**: *"Aprova a story (P0)?"* → `gh issue create --body-file` (corpo no modelo `workflow/github/issue-story.md`).
- Dimensione S/M/L/C (Art. 6.1), verifique os gatilhos sensíveis (Art. 10.1) e se há UI. Mostre ao humano.
- Crie a branch `<tipo>/<issue>-<slug>` a partir da base do `CLAUDE.md`, a pasta `workflow/specs/<issue>-<slug>/` e o `STATUS.md` (template `workflow/templates/STATUS-feature.md`).

## 2. Refinamento (developer + designer)
- Chame o **developer** em **modo refinamento**, passando a issue, o caminho da pasta e o tamanho. Ele lê o código real e entrega o `ticket.md` redondo.
- Se houver UI, chame o **designer** em paralelo para o `ui-spec.md`.
- Tamanho C: o developer devolve o fatiamento. Crie as issues filhas e reinicie o `/feature` na primeira delas.

## 3. Check final (planner): loop até a DoR
Chame o **planner** com o caminho da pasta. Ele devolve uma de duas coisas:
- **PERGUNTAS**:
  - `[negócio]` → pergunte ao humano literalmente e devolva as respostas ao **developer** para atualizar o ticket.
  - `[técnico]` → devolva ao **developer**.
  - Depois chame o planner de novo. **Máximo de 3 rodadas** (Art. 13.1); na 3ª, escale ao humano.
- **PRONTO** + `plan.md` → siga.

**■ P1:** resuma ACs, abordagem, contratos e mapa AC → teste e pergunte *"Aprova o plano (P1)?"*. Registre.
Sincronize a issue: `gh issue edit <n> --body-file workflow/specs/<...>/ticket.md` e `gh issue comment <n> --body-file workflow/specs/<...>/plan.md`. **Não commite** ticket nem plano (Art. 11.8): a issue é o registro compartilhado.

## 4. Pilha de testes (test-engineer)
Chame o **test-engineer** com o caminho da pasta. Ele entrega os testes de caracterização (se o plano pedir) e os testes RED, mais a matriz AC → teste e a saída da execução.
**■ P2 (obrigatório):** mostre a matriz e a prova de RED e pergunte *"Confirma o contrato RED (P2)? O developer só começa depois disso."* Registre.

## 5. Implementação (developer)
Chame o **developer** em **modo implementação**. Ele commita os testes, implementa os passos do `plan.md`, roda testes/lint, dá push e abre o PR.

## 6. Reviews
Em paralelo, quando aplicável:
- **tech-lead** (sempre)
- **security-reviewer** (área sensível)
- **designer** (UI)

Comentários bloqueantes voltam ao **developer**. Repita o review afetado até não haver bloqueantes.
Opcionais: **refactorer** (dívida apontada no review), **docs-writer** (CHANGELOG/ADR/KDoc), **devops** (CI/build).

## 7. Verificação (verifier)
Chame o **verifier** em modo feature, **sem** repassar resumos de outros agentes: só a pasta da feature e o número do PR.
FAIL → copie as lacunas para `plan.md` › "Correções — iteração N" → developer → reviews afetados → verifier de novo. **Máximo de 3 iterações** (Art. 13.2).

## 8. ■ P3 e encerramento
Com PASS: atualize o `STATUS.md`, publique o `validation.md` como comentário no PR (`gh pr comment --body-file`) e entregue ao humano o link do PR com o checklist do Art. 12.1. Diga claramente que **o merge é dele**. Registre no STATUS atritos que mereçam emenda (Art. 15.2).

## Como conduzir qualquer gate
Pare, resuma o artefato com o link do arquivo e pergunte de forma explícita (use AskUserQuestion se disponível). Só um "sim" inequívoco conta. Registre no `STATUS.md`. Reprovado → volte ao agente responsável com o feedback literal.

## Proibições
`gh pr merge`, `gh pr review --approve`, `push --force`, commit em branch protegida, **commitar qualquer arquivo do workflow** (Art. 11.8), escrever código ou testes, pular P2 ou P3.
