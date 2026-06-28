# Claude Worker Loops

The Claude lanes are for long-context work where a narrow task needs a large
window and persistence.

## Waffle Lab Engineers

Two engineer panes work like wallbreakers:

- one lead integration lane,
- one adversarial alternate/falsifier lane.

They should not stop at a first failure. After a NACK, they must either test a
materially different hypothesis, produce a hard blocker, or ask for one missing
artifact that would change the decision.

Claude does not expose a Codex-style persistent `Pursuing goal` state to the
board. Keep Claude alive with recurring LOOP dispatches:

```bash
./bin/role-loop list
./bin/role-loop enqueue --idle
./bin/steer-fleet dispatch
```

An idle Claude pane with no pending packet is a pullback trigger. The next loop
must test a materially different hypothesis, produce a concrete hard blocker,
or ask for one missing artifact that would change the decision.
The template uses a short per-role cooldown
(`STORM_ROLE_LOOP_IDLE_MIN_SECONDS`, default `300`) so a worker is not requeued
immediately after it just produced an artifact.

## Research Vault

The researcher pane digests large context step by step:

1. Pick one bounded batch.
2. Extract source mappings and claims.
3. Run Bluesky on upside.
4. Run Redsky on proof and economics.
5. Write a source-bound packet or closure.
6. Only then move to the next batch.

## Required Output

- artifact name,
- source/base,
- claim,
- evidence label,
- proof obligations,
- validator or falsifier,
- next owner,
- `no_submit_ack=yes`.

## Specialist Pullback

Use the same `role-loop` mechanism for specialist panes after they finish a
task and become passive:

- auditor,
- PUA/PIP,
- researcher,
- source-proof,
- validator,
- provider manager,
- wallbreaker lead and shadow.

Each loop must close the dispatch or leave an explicit wait reason.
