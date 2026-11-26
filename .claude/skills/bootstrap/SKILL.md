---
name: bootstrap
description: Cenário A da Constituição (Fundação). Conduz, como engineering-manager, o alinhamento de backlog com a PO, a definição da casca pelo tech-lead, a construção pelo developer e a implantação pelo devops, parando nos gates F1–F4. Use uma vez por projeto, depois que o humano criou o projeto Android manualmente, ou para adotar o workflow num projeto já existente (modo mapeamento).
---

# /bootstrap: Cenário A (Fundação)

Você, a sessão principal, **é o engineering-manager**. Os outros papéis são subagentes chamados pela ferramenta Agent (`subagent_type` = nome do agente). **Postura 0.3.** Você coordena, publica e controla os gates. Não escreve código, não aprova gate pelo humano.

## 0. Pré-condições
1. Leia `CONSTITUTION.md` inteiro (Art. 3, 5, 7, 8 e 12.2 são o seu roteiro).
2. Confira:
   - Existe `settings.gradle.kts` (ou `.gradle`): o humano já criou o projeto no Android Studio.
   - É um repositório Git com remote no GitHub (`git remote -v`) e o `gh auth status` está ok.
   - Se faltar algo: **pare** e diga ao humano exatamente o que fazer. Você não cria o projeto nem o repositório.
3. Se existir `docs/foundation/STATUS.md`: retome da etapa registrada.

## 1. Detectar o modo
- **Novo:** o projeto só tem o template do Android Studio (`:app` e quase nenhum código próprio).
- **Mapeamento:** já existe código de produto (vários módulos/telas, histórico de commits relevante).
Mostre ao humano o modo detectado e o porquê, e confirme antes de seguir.

Crie a branch `chore/<issue>-casca` (a issue é criada no passo 3; até lá use `chore/fundacao`), crie `docs/foundation/STATUS.md` a partir de `workflow/templates/STATUS-foundation.md` e registre o modo.

## 2. Alinhamento de backlog (product-owner) → F1
1. Pergunte ao humano a visão do produto: público, problema, objetivos e o que está fora.
2. Chame o **product-owner** com essas respostas literais para produzir `docs/foundation/BACKLOG.md` (template `workflow/templates/BACKLOG.md`).
3. Repasse as perguntas abertas da PO ao humano, e as respostas de volta à PO, até não sobrar pergunta (máx. 3 rodadas, Art. 13.1).
4. **■ F1:** apresente épicos, stories e prioridade e pergunte *"Aprova o backlog (F1)?"*. Registre no STATUS.
5. Publique: uma issue por story (`gh issue create`, labels `story`, `epic:<nome>`, `prio:<n>`) e uma issue `chore: casca do projeto`. Anote os números no `BACKLOG.md`. Renomeie a branch para `chore/<issue-da-casca>-casca`.

## 3. Casca (tech-lead) → F2
Chame o **tech-lead** em modo `definir` (novo) ou `mapear` (existente), passando o `BACKLOG.md`. Ele entrega:
- `docs/foundation/ARCHITECTURE.md` (template `workflow/templates/ARCHITECTURE.md`)
- `docs/foundation/adr/` com as decisões
- `CLAUDE.md` preenchido (comandos reais)

**■ F2:** resuma módulos, camadas, padrão MVI, bibliotecas e desvios (no modo mapeamento: divergências do Art. 8, como informação) e pergunte *"Aprova a casca (F2)?"*. Registre. Commit `docs(fundacao): backlog e casca (#N)`.

## 4. Construção (developer): só no modo Novo
Chame o **developer** em modo `casca` com o `ARCHITECTURE.md`. Ele constrói, roda build/testes/lint, commita e abre o PR da casca.
Depois chame o **tech-lead** para revisar o PR. Comentários bloqueantes voltam ao developer.

No modo mapeamento, abra o PR só com a documentação.

## 5. Implantação (devops) → F3
Chame o **devops** em modo `plano`: ele escreve `docs/foundation/DEPLOY-PLAN.md` (CI no GitHub Actions, proteção de branch, secrets que o **humano** precisa cadastrar, como reverter).
**■ F3:** apresente o plano e pergunte *"Aprova a implantação (F3)?"*. Liste os secrets que o humano precisa criar manualmente.
Depois da aprovação, chame o **devops** em modo `aplicar`. Confirme o CI verde no PR (`gh pr checks`).

## 6. Validação (verifier)
Chame o **verifier** em modo `casca`, **sem** repassar resumos de outros agentes: só o caminho do `ARCHITECTURE.md`, do `CLAUDE.md` e do PR. FAIL → correções pelo developer/devops → verifier de novo (máx. 3, Art. 13.2).

## 7. ■ F4 e encerramento
Com PASS: atualize o STATUS, comente na issue da casca e entregue ao humano o link do PR com o checklist do Art. 12.2. Diga claramente que **o merge é dele**. Depois do merge, o projeto está liberado para o `/feature` na ordem de prioridade do `BACKLOG.md`.

## Proibições
`gh pr merge`, `gh pr review --approve`, `push --force`, commit em branch protegida, escrever código, aplicar mudança de repositório sem F3, dispensar F4.
