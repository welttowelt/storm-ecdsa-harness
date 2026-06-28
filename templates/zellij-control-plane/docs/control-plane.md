# Control Plane

The board is the live operating surface for a private STORM controller. It does
not replace durable route packets or mailbox entries; it makes the current
decision state visible.

## Boss Duties

- Keep the priority stack current.
- Watch blocked important lanes before low-value busywork.
- Keep `policy-dispatch` short and current.
- Reassign idle important workers.
- Run `./bin/role-loop enqueue --idle` before treating an empty dispatch ledger
  as healthy.
- Demand route packets, validators, stop conditions, and evidence labels.
- Route specialist output to wallbreakers.
- Route wallbreaker packets to validator or closure.
- Keep `no_submit_ack=yes` explicit while submit is closed.

## Policy Duties

Default is closed:

- submit closed,
- paid compute closed,
- spend closed,
- worker-island closed.

Opening a gate should name owner, cap, stop condition, and cleanup condition.
Do not place credentials or account/payment details in command lines, docs, or
dispatch rows.

## Evidence Duties

Use labels consistently:

- `Historical clue`
- `Source fact plus inference`
- `Paper score`
- `Partial run`
- `Prefilter`
- `Local full run`
- `Promoted`

Only trusted local validation plus fresh current-target check can move a result
toward submit discussion.

## Role Loops

Claude and some specialists do not keep a visible Codex-style `Pursuing goal`
state. The board uses recurring LOOP dispatches instead:

```bash
./bin/role-loop list
./bin/role-loop due --idle
./bin/role-loop enqueue --idle
./bin/steer-fleet dispatch
```

This keeps idle Claude engineers, the Claude researcher, auditor, PUA/PIP,
researcher, source-proof, validator, provider manager, and wallbreakers pulling
back into one bounded artifact instead of silently going passive.
