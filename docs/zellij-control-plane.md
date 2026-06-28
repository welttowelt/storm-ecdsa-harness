# Zellij Control Plane

This document describes the current STORM board shape: one named Zellij
multiplexer session that replaces loose manual terminals plus mailbox-only
coordination.

The public repo publishes the shape, template files, and discipline. A live
operator should run it from a private controller directory. Do not copy private
state, provider details, raw logs, unreleased candidates, local paths, or
credentials into this repo.

## Why The Board Exists

The manual-session model worked for early experiments but had weak operational
invariants:

- many terminals could be alive without one obvious boss lane,
- workers could sit idle because nobody saw they were waiting,
- policy text could be long, stale, or hidden from the worker who needed it,
- mailbox entries were durable but not enough for live steering,
- resumed sessions were hard to identify,
- provider governance and validation could drift away from route ownership.

The Zellij board fixes this by making the control plane visible and named. The
board is not a solver. It is the operating desk around the solver.

## Invariants

- One named session, usually `STORM BOSS`.
- One private controller root with every pane started from the same directory.
- One visible policy file that states submit, compute, spend, and worker-island
  gates.
- One worker registry that shows role, state, and owner without leaking
  endpoints in public material.
- One dispatch ledger with `pending`, `sent`, `busy`, `ack`, `closed`, and
  `nack` status.
- Every autonomous worker has a role goal, output contract, stop condition, and
  `no_submit_ack=yes`.
- Paid compute, job killing, worker-island launches, and submit actions require
  explicit local policy gates. Default is closed.
- Scanner or prefilter output never becomes win language before trusted local
  validation and a fresh frontier check.

## Tab Model

| Tab | Purpose | Typical panes |
| --- | --- | --- |
| `boss` | Orchestration, priorities, policy, frontier, sentinels. | `control`, `policy-dispatch`, `frontier`, `sentinels` |
| `auditor` | Bluesky, Redsky, RCI, PUA/PIP audits and process hardening. | audit playbook, queue, docs |
| `pua-pip` | Repeated-failure discipline and assumption inversion. | goal lane, queue |
| `research` | Paper-to-source and theory-to-packet conversion. | researcher, skills, packet template |
| `local-benchmark` | Trusted local validation for gate-pass candidates only. | validator, benchmark checkout |
| `wallbreaker` | Integrators who connect specialist output into one executable attempt or hard NACK. | lead, shadow, queue, playbook |
| `pods-manager` | Provider inventory, canaries, spend visibility, cleanup plans. | policy, worker list, skills |
| `waffle-lab` | Two long-context Claude engineer workers for integration and adversarial alternates. | brief, queue, playbook |
| `research-vault` | One long-context Claude researcher for large-context digestion. | brief, playbook |
| `workers` | Generic local or remote worker landing area. | worker panes |

The boss lane should not be busy with low-value work. It owns the priority
stack: urgent decisions, blocked important workers, frontier/policy drift, and
handoffs that require judgment. Work that can wait should be assigned out or
parked.

## File Layout

The starter pack lives under
[`templates/zellij-control-plane/`](../templates/zellij-control-plane/):

```text
bin/
  env.sh
  start-zellij
  apply-zellij-layout
  steer-fleet
  role-loop
  launch-codex-roles
  launch-claude-roles
  check-gates
  policy-brief
  dispatch
  list-workers
layouts/
  fleet.kdl
state/
  fleet-policy.env.example
  dispatch-ledger.tsv.example
  skill-registry.tsv.example
workers.tsv.example
docs/
  role-goals.md
  control-plane.md
  lane-playbooks.md
  audit-process.md
  wallbreaker-worker.md
  claude-worker-loops.md
templates/
  research-packet.md
  route-attempt.md
```

In a real private controller, keep generated state, logs, transcripts, worker
hosts, and credentials outside the public repo or ignored by the private repo.

## Setup

Copy the template into a private directory:

```bash
cp -R templates/zellij-control-plane ../private-storm-controller
cd ../private-storm-controller
cp state/fleet-policy.env.example state/fleet-policy.env
cp workers.tsv.example workers.tsv
```

Edit `state/fleet-policy.env` before launching. Defaults should be closed:

```bash
FLEET_NO_SUBMIT=1
FLEET_NO_SUBMIT_ACK=yes
FLEET_SUBMIT_GATE=closed
FLEET_COMPUTE_GATE=closed
FLEET_SPEND_GATE=closed
FLEET_WORKER_ISLAND_GATE=closed
```

Start or resume the board:

```bash
./bin/start-zellij
zellij attach "STORM BOSS"
```

Inside the board:

```bash
./bin/check-gates --brief
./bin/launch-codex-roles
./bin/launch-claude-roles
./bin/role-loop enqueue --idle
./bin/steer-fleet dispatch
```

Codex workers use the unsupervised launcher shape requested for private fleet
operations:

```bash
codex --cd "$STORM_FLEET_ROOT" --sandbox danger-full-access --ask-for-approval never "<role prompt>"
```

Claude workers use:

```bash
claude --dangerously-skip-permissions --effort max --model opus --name "<session name>" "<role prompt>"
```

Those flags are powerful. The policy gate and role prompt must carry the actual
limits: no submit, no secret leakage, no provider commands without an opened
gate, and no unbounded spend.

## Policy Visibility

The policy pane should be short. It should answer:

- Is submit closed or open?
- Is `no_submit_ack=yes` explicit?
- Is paid compute closed or open?
- What is the current spend cap, if any?
- Is worker-island launch authority closed or open?
- Who owns the next decision?

Do not bury this behind paragraphs. Long policy belongs in docs; the board pane
is for the active gates.

## Dispatch Flow

Use the dispatch ledger for live handoffs:

```text
id  status   target              owner  title
1   pending  wallbreaker-lead    boss   connect source-proof and GPU notes
2   sent     auditor             boss   redsky current route packet
3   closed   validator           boss   official local validation clean
```

Good dispatches include:

- target role,
- owner,
- one bounded ask,
- evidence expected,
- stop condition,
- whether policy gates allow the action.

The boss should repeatedly ask: "who is waiting on me, who is idle but
important, and what would move the frontier evidence today?"

## Information Flow

Specialists do not own the whole attack. They produce packets:

- research -> source mapping, hashes, q/T economics, proof obligations,
- source-proof -> invariants, counterexamples, closed-ledger checks,
- provider manager -> canary state, spend runway, cleanup state,
- validator -> trusted dirty state and score evidence,
- auditor -> Bluesky/Redsky/RCI/PIP findings and implemented fixes.

Wallbreakers consume those packets and must output exactly one of:

- `route_attempt`: source-bound attempt ready for proof or cheap validation,
- `worker_attempt`: bounded compute/worker plan with stop condition,
- `hard_nack`: reason the lane is dead and what ledger closes it.

The boss consumes wallbreaker and validator output, then decides whether to
reassign, close, escalate, or park.

## Role Goals

Every agent pane should receive a `/goal` with:

- role identity,
- active objective,
- required inputs to read,
- loop discipline: Bluesky, Redsky, RCI, PUA, PIP,
- output artifact,
- policy boundaries,
- evidence metrics,
- no-submit acknowledgement.

See
[`templates/zellij-control-plane/docs/role-goals.md`](../templates/zellij-control-plane/docs/role-goals.md)
for reusable goal blocks.

Claude and some specialist panes need recurring LOOP packets in addition to
initial goals, because they can finish one task and become passive while the
board still needs their role. Use:

```bash
./bin/role-loop list
./bin/role-loop enqueue --idle
./bin/steer-fleet dispatch
```

The loop contract is bounded: one route attempt, worker attempt, hard NACK,
readiness packet, or explicit wait reason with `no_submit_ack=yes`.
Use a short per-role cooldown so completed workers are re-pulled regularly
without immediate duplicate spam.

## Migration From Mailbox-Only Operations

1. Keep the mailbox as the durable handoff record.
2. Create the Zellij board as the live status surface.
3. Convert old loose sessions into named roles in `workers.tsv`.
4. Convert old mailbox threads into dispatch rows or closed ledgers.
5. Assign one owner per active route.
6. Put the policy gate in `state/fleet-policy.env`.
7. Keep public notes fixture-only until validation and release checks pass.

The important change is ownership. The board should make it obvious when the
ball is with the boss, a wallbreaker, the auditor, a validator, or the provider
manager.

## Public Boundary

Public docs and templates may include:

- role names,
- generic commands,
- placeholder worker rows,
- fixture examples,
- policy variable names,
- no-submit discipline,
- audit methods.

Public docs and templates must not include:

- provider endpoints,
- account identifiers,
- payment details,
- credentials or credential names,
- raw logs,
- unreleased nonces,
- active candidate diffs,
- local absolute paths,
- live mailbox exports,
- runtime state from a private board.

Run before publishing:

```bash
scripts/redaction-check.sh
scripts/check-public-harness.sh
```
