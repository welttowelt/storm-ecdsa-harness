# Operating Model

Stormforge is an operator layer for agentic benchmark research. It assumes the
base benchmark and challenge already exist, then adds coordination discipline
around agents, evidence, compute, and publication.

## Roles

- Research lead: ranks routes, refreshes the frontier, writes route packets, and
  kills weak lanes.
- Engineering specialist: receives narrow tasks with a validator and kill gate.
- Deep researcher: answers hard proof or architecture questions only.
- Skeptic / RCI reviewer: tries to falsify every route before compute spend.
- External pressure-test worker: gives a bounded critique, one sharp question,
  one creative alternative, and a falsifiable decision.

Roles can be run by separate agents or by one agent explicitly switching hats.
The important property is that each claim is pressure-tested before it becomes
state.

## Cycle Order

1. Refresh the live benchmark/current target.
2. Read the shared mailbox and log ACK/read receipts.
3. Review active route packet and evidence label.
4. Run cheap local validation or source inspection.
5. Run skeptic/RCI pass.
6. Dispatch compute only with a validated compute request.
7. Harvest results and downgrade all raw hits to `Prefilter`.
8. Open submit gate only after official local validation and fresh score check.

## Evidence Labels

- `Promoted`: public leaderboard accepted the submission.
- `Local full run`: local official benchmark completed.
- `Partial run`: local component or bounded run completed.
- `Prefilter`: scanner or predicate found a possible survivor.
- `Paper score`: estimated score before official validation.
- `Historical clue`: useful prior note or older route.
- `Source fact plus Inference`: source or public data plus explicit reasoning.

## Compute Gate

Do not spend paid compute just because a machine is idle. A compute request needs:

- current source/base,
- route ID,
- exact predicate or proof target,
- expected edge,
- validator command,
- owner,
- kill condition,
- maximum budget,
- disjoint work ranges if sharded,
- public-credit policy if it wins.

Raw scanner hits are not winners. They stay `Prefilter` until local official
validation passes.

## Submit Gate

Submit only when all are true:

- fresh frontier recheck,
- official local validation passes with `0/0/0`,
- score beats the live frontier,
- diff is legal and narrow,
- public note is ready,
- submit flag is explicitly enabled.

## Public Status Surfaces

Dashboards and shared boards are status surfaces only. They may show:

- route name,
- evidence label,
- worker status,
- aggregate counts,
- sanitized read receipts,
- fixture or public leaderboard data.

They must not show endpoints, ports, credentials, raw logs, unreleased nonces, or
private diffs.

