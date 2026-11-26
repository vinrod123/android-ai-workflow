## O quê e por quê
<resumo>

Closes #<issue>

## Artefatos
- Ticket: `workflow/specs/<issue>-<slug>/ticket.md`
- Plano: `workflow/specs/<issue>-<slug>/plan.md`
- Validação: `workflow/specs/<issue>-<slug>/validation.md`

## Rastreabilidade
| AC | Teste(s) |
|----|----------|
| AC-1 | |

## Checklist (Definition of Done: CONSTITUTION.md Art. 12)
- [ ] Todos os ACs com teste e passando
- [ ] Build, lint, ktlint e detekt passando
- [ ] Testes não alterados depois do P2
- [ ] Código respeita o ARCHITECTURE.md (camadas, MVI, módulos)
- [ ] Review do tech-lead sem bloqueantes
- [ ] Security sem Crítico/Alto aberto (se aplicável); designer ok (se houver UI)
- [ ] Verifier: PASS

> O merge deste PR é feito **por um humano** (P3 / F4).
