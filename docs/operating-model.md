# Operating Model

Storm is an operator layer for agentic benchmark research. It assumes the
base benchmark and challenge already exist, then adds coordination discipline
around agents, evidence, compute, and publication.

The production name for this operating model is the STORM harness in production.
The live controller stays private; this repo publishes the same workflow as
docs, templates, fixture data, and release checks.

## Production Controller

In production, STORM is not only a dashboard or prompt pack. It is the local
controller that:

- refreshes public frontier state before every route decision,
- reads and ACKs a shared worker mailbox,
- keeps one active route unless a route packet says otherwise,
- runs source checks, canaries, benchmark validators, and submission-note gates,
- dispatches CPU/GPU work only after validator and kill-gate checks pass,
- labels every scanner hit as `Prefilter` until trusted validation returns
  clean `0/0/0`,
- routes strategic-goal packets back through the mailbox so workers converge.

The current controller shape uses one named Zellij board as the live control
surface. Mailbox entries still exist for durable handoffs, but the board is the
place where the boss lane sees policy, dispatch, frontier status, idle workers,
wallbreaker pressure, validation, and provider governance at once. This avoids
the old failure mode where many manual terminal sessions existed but no pane
owned the next decision.

See [docs/zellij-control-plane.md](zellij-control-plane.md) for the public
template and setup sequence.

## Roles

- Research lead: ranks routes, refreshes the frontier, writes route packets, and
  kills weak lanes.
- Engineering specialist: receives narrow tasks with a validator and kill gate.
- Deep researcher: answers hard proof or architecture questions only.
- Skeptic / RCI reviewer: tries to falsify every route before compute spend.
- External pressure-test worker: gives a bounded critique, one sharp question,
  one creative alternative, and a falsifiable decision.
- Boss / orchestrator: maintains the priority stack, watches for blocked or
  idle important lanes, routes decisions, and refuses busywork that does not
  move a route toward proof, validation, compute, or closure.
- Wallbreaker: connects specialist output into one executable route attempt,
  worker attempt, or hard NACK, then challenges shallow results until evidence
  improves.
- Provider manager: owns compute inventory, canaries, spend policy visibility,
  and cleanup plans, but receives no submit authority.

Roles can be run by separate agents or by one agent explicitly switching hats.
Each claim is pressure-tested before it becomes state.

## Cycle Order

1. Refresh the live benchmark/current target.
2. Read the shared mailbox and log ACK/read receipts.
3. Scan the mailbox tail for directed operator asks before posting steering.
   Every direct ask must be ACKed, NACKed, or explicitly deferred with the next
   bounded check.
4. Review the active route packet and evidence label.
5. Run cheap local validation, source inspection, or canary checks.
6. Run skeptic/RCI pass.
7. Dispatch compute only with a validated compute request.
8. Harvest results and downgrade all raw hits to `Prefilter`.
9. Run trusted validation on score-relevant survivors.
10. Open submit gate only after official local validation and fresh score check.

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
- redacted read receipts,
- fixture or public leaderboard data.

They must not show endpoints, ports, credentials, raw logs, unreleased nonces, or
private diffs.
