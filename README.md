# Storm ECDSA Harness

Public repo: <https://github.com/welttowelt/storm-ecdsa-harness>

Fixture dashboard: <https://welttowelt.github.io/storm-ecdsa-harness/>

Storm is the public release of the STORM harness in production: an operator
control plane for coordinating public `ecdsa.fail` research workflows. It is the
layer around the solver: deciding what receives attention, forcing evidence
labels, routing workers, gating compute, recording ACKs, and keeping public
notes safe to share. The edge is multi-model collaboration: different workers
can contribute through mailbox or API handoffs, but every claim still has to
pass the same evidence, critique, and validation gates. It is not the original
benchmark harness and it does not contain private hunt state.

Purpose and limits: `ecdsa.fail` is a public resource-estimation benchmark for
the quantum cost of one `secp256k1` point-add circuit. This repo contains
workflow templates, evidence discipline, dashboard fixtures, and safety checks.
It does not provide target selection, key recovery, private compute endpoints,
raw scan logs, unreleased nonces, or live candidate diffs.

## STORM Harness In Production

The live STORM controller is private. It refreshes the public leaderboard,
reads the shared worker mailbox, creates route packets, dispatches CPU/GPU work,
runs official validation, and opens the submit gate only after a fresh score
check and explicit submit flag.

This public repo is the reusable release surface for that setup. It contains the
protocol, templates, fixture dashboard, operator cards, and redaction checks so
other OSS teams can copy the coordination layer without inheriting private
state.

See [docs/production-shape.md](docs/production-shape.md) for the exact
production-to-public mapping.

## Operator Edge

Agentic benchmark work fails quietly when teams trust memory, chase stale
routes, spend compute without a kill gate, or promote scanner hits into public
claims too early. Storm makes that operating layer explicit:

- **Current-target lock:** every cycle starts from refreshed public benchmark
  state, not chat memory.
- **Route packets:** every idea names the claim, evidence level, validator,
  owner, budget, and falsifier before it receives compute.
- **Multi-model workers:** Codex-, Claude-, and DeepSeek-style workers can plug
  in as research leads, engineering specialists, deep researchers, or external
  pressure-test reviewers.
- **Critique loop:** constructive reviews, skeptical reviews, source checks, and
  smallest-useful-fix passes run before compute or public claims.
- **Compute gate:** CPU/GPU work is allowed only when a route has a predicate,
  validator, owner, budget, and stop condition.
- **Submit gate:** no win language until fresh frontier recheck, official local
  validation, score win, legal diff, public note, and explicit submit flag.
- **Public boundary:** dashboards, examples, and notes stay fixture/public-only
  while private logs, endpoints, routes, and nonces stay out.

The repo is therefore not a faster circuit generator by itself. It is a way to
make a group of agents and humans behave like a disciplined research desk.

## Lineage

- Base challenge / benchmark lineage: Gautham Anant and the public
  `ecdsa.fail` challenge. The public framing is described in Sreeram Kannan's
  article: <https://www.linkedin.com/pulse/you-beat-google-sreeram-kannan-rqehc>.
- Early custom agent-harness inspiration: Gajesh Naik / Gajesh2007, including
  custom agent workflows, goal-mode style operation, model/subagent routing, and
  more agent-readable code organization.
- Storm contribution: the STORM harness control-plane layer:
  mailbox protocol, ACK/read receipts, route packets, worker roles, dashboard
  views, compute gates, submit gates, and redaction discipline.

See [docs/credits.md](docs/credits.md) and [CREDITS.yaml](CREDITS.yaml) for
explicit attribution. Credits are split into direct tools, public sources, and
group-discussion process inspiration so the repo does not imply copied code or
endorsement where there was only inspiration.

## What This Repo Contains

- A current-target-first operating model.
- A production-shape map for the live STORM controller.
- Worker role cards and handoff templates.
- Public operator cards under `operators/` for Kimi Storm, Deep Storm, and
  Codex Storm handoffs.
- Historical route packets under `routes/` with falsification status where
  known.
- Critique-before-compute audit loop.
- Evidence labels and validation gates.
- Route packet and compute request templates.
- External pressure-test worker prompt pattern.
- Safe filled examples for the templates.
- A fixture-only dashboard for operator status.
- A redaction checklist and automated redaction scan.
- Public-credit policy for community-derived ideas.
- Repo-local Codex skill bridges for ECDSA workflow agents.

## Skill Cards

The `skills/` directory contains operator prompt cards that can be copied into
agent instructions or used as a preflight before route work:

- `skills/nasqret-playbook.md`: build route slates before scaling compute.
- `skills/deepseek-pressure-test.md`: ask an external worker to try to kill a
  route before acting.
- `skills/tony-rci-audit.md`: turn critique into concrete findings, smallest
  useful fixes, and explicit gates.
- `skills/bluesky-audit.md`: find the best bounded path if an idea is real
  before deciding whether to invest.
- `skills/redsky-audit.md`: try to kill a route with stale-truth, evidence,
  validator, economics, and gate checks.
- `skills/pip-discipline.md`: use the English/PIP-derived evidence discipline
  after repeated failure, passive handoff, or unverified completion claims. This
  repo imports only the local prompt-card discipline, not plugin hooks,
  telemetry, feedback upload, or remote prompt loading.
- `skills/exact-support-miner.md`: turn public op-trace facts into ranked
  value-exact skip packets with proof and validation gates.
- `skills/frontier-lock.md`: refresh and record the current public frontier
  before route, compute, note, or submit decisions.
- `skills/validation-submit-gate.md`: keep evidence labels, trusted
  validation, and submit-gate claims separate.
- `skills/route-compute-gate.md`: require owner, predicate, validator, budget,
  and stop condition before CPU/GPU dispatch.
- `skills/multi-agent-handoff.md`: make cross-worker handoffs explicit with
  ACKs, validators, and kill gates.
- `skills/circuit-diff-mining.md`: mine recent promoted diffs into bounded
  candidate probes without stale knob copying.
- `skills/submission-forensics.md`: deep-audit public submissions, notes,
  promoted diffs, and adjacent frontier moves without private-state leakage or
  credit overclaiming.
- `skills/bluesky-route-salvage.md`: find the smallest falsifiable experiment
  that preserves upside before a route is killed.
- `skills/redsky-frontier-audit.md`: run adversarial frontier, legality,
  evidence-label, compute, and submit-gate checks.
- `skills/ecdsafail-cli-ops.md`: operate the `ecdsafail` CLI with worktree,
  credential, sync/reset, validation, and submit discipline.
- `skills/stormgate-prefilter.md`: keep prefilter, canary, survivor-label, and
  trusted-validation boundaries explicit.
- `skills/paper-gidney-constant-workspace-adder.md`: apply Gidney 2025
  constant-workspace adders only after a toy proof and one-callsite residual
  gate.
- `skills/paper-mbu-modular-arithmetic.md`: turn measured-workspace arithmetic
  cleanup into an explicit phase-correction proof obligation.
- `skills/paper-hrs-dirty-constant-adder.md`: use HRS dirty-ancilla adders as a
  disciplined borrowed-host route, not as zero scratch.
- `skills/paper-gidney-temporary-logical-and.md`: evaluate temporary logical-AND
  erase patterns for uncompute and Toffoli budgeting.
- `skills/paper-haner-ecdlp-circuits.md`: compare point-add route ideas against
  established ECDLP Q/T/depth tradeoffs.
- `skills/paper-schrottenloher-point-addition.md`: map 2026 secp256k1
  point-addition architecture ideas into local TLM invariants.
- `skills/paper-schrottenloher-dialog-codec-audit.md`: test
  Schrottenloher dialog-codec compression ideas against entropy bounds before
  lower-Q transcript edits.
- `skills/paper-luo-register-sharing-eea.md`: explore compact
  register-sharing EEA ideas without hiding decompression peaks.
- `skills/conditionally-clean-cascade-cut.md`: test the Nie-Zi-Sun /
  Khattar-Gidney conditionally-clean cascade route for exact peak-carry cuts.
- `skills/paper-conditionally-clean-ancillae.md`: use Khattar/Gidney
  conditionally clean ancillae only with a branch-clean proof.
- `skills/paper-reversible-pebbling-memory-management.md`: turn lower-Q
  cleanup/recompute ideas into explicit peak DAG and stale-drop gates.
- `skills/paper-square-active-volume.md`: rank reuse, uncompute, and codec
  timing candidates by the above-target active-volume rows they actually cover.
- `skills/paper-vandaele-optimal-comparator.md`: apply Vandaele 2026
  comparator/incrementer circuits only after proving the comparator is the
  peak source or pairing it with the co-peak carry floor.
- `skills/paper-remaud-ancilla-free-adder.md`: evaluate no-ancilla adder
  suffixes as lower-Q pressure relief with a strict Toffoli gate.
- `skills/paper-takahashi-no-ancilla-adder.md`: use classic no-ancilla addition
  as a suffix-only fallback baseline.
- `skills/paper-roetteler-ecdlp-resource-estimate.md`: ground prime-field ECDLP
  architecture ideas in gate-level point-add validation.
- `skills/paper-garn-kan-windowed-binary-ecdlp.md`: borrow exact exceptional-case
  and window/table discipline without direct field-porting.
- `skills/paper-wire-recycling-lifetime-graph.md`: apply wire-recycling,
  SQUARE, and Reqomp lifetime-graph discipline to free-pool aliasing and
  stale-dead-drop failures.
- `skills/paper-dirty-borrowing-entanglement.md`: require idle-source,
  original-state, and external-entanglement identity proofs before borrowed
  working qubits can support lower-Q cuts.
- `skills/paper-scalable-memory-recycling.md`: prevent lower-Q primitive
  swaps from silently changing dynamic headroom schedules; require schedule
  ledgers, frozen baseline replay, and explicit rebaked tables.
- `skills/paper-dead-gate-elimination.md`: regenerate and audit dead-drop
  index files after op-stream edits; never reuse stale `.idx` proof artifacts.

Codex-style agents can also discover the PIP and audit cards through the
repo-local bridges under `.agents/skills/`.

## How To Call The Skills

In Codex or another skill-aware agent, call a repo-local skill by name:

```text
Use frontier-lock.
Use bluesky-route-salvage on this route.
Use redsky-frontier-audit before compute.
Use ecdsafail-cli-ops and validation-submit-gate before submit.
```

The bridge names are:

- `nasqret-playbook`
- `deepseek-pressure-test`
- `pip-discipline`
- `exact-support-miner`
- `frontier-lock`
- `validation-submit-gate`
- `route-compute-gate`
- `multi-agent-handoff`
- `circuit-diff-mining`
- `submission-forensics`
- `bluesky-route-salvage`
- `redsky-frontier-audit`
- `ecdsafail-cli-ops`
- `stormgate-prefilter`
- `paper-gidney-constant-workspace-adder`
- `paper-mbu-modular-arithmetic`
- `paper-hrs-dirty-constant-adder`
- `paper-gidney-temporary-logical-and`
- `paper-haner-ecdlp-circuits`
- `paper-schrottenloher-point-addition`
- `paper-schrottenloher-dialog-codec-audit`
- `paper-luo-register-sharing-eea`
- `conditionally-clean-cascade-cut`
- `paper-conditionally-clean-ancillae`
- `paper-reversible-pebbling-memory-management`
- `paper-vandaele-optimal-comparator`
- `paper-remaud-ancilla-free-adder`
- `paper-takahashi-no-ancilla-adder`
- `paper-roetteler-ecdlp-resource-estimate`
- `paper-garn-kan-windowed-binary-ecdlp`
- `paper-wire-recycling-lifetime-graph`
- `paper-dirty-borrowing-entanglement`
- `paper-scalable-memory-recycling`
- `paper-dead-gate-elimination`

Useful global skills for ECDSA work, when installed in the agent environment:

- `redsky`: deep ECDSA.fail frontier-solving audit.
- `ecdsafail-cli`: detailed CLI syntax for benchmark, run, submit, notes, sync,
  reset, and skill install.

Common call chains:

- Exact skip mining: `frontier-lock` -> `exact-support-miner` ->
  `redsky-frontier-audit` -> `validation-submit-gate`.
- Frontier shift: `frontier-lock` -> `nasqret-playbook` ->
  `circuit-diff-mining`.
- New route: `frontier-lock` -> `bluesky-route-salvage` ->
  `redsky-frontier-audit` -> `route-compute-gate`.
- External critique: `deepseek-pressure-test` -> `redsky-frontier-audit`.
- Public submission audit: `frontier-lock` -> `submission-forensics` ->
  `circuit-diff-mining`.
- Prefilter/search work: `frontier-lock` -> `stormgate-prefilter` ->
  `route-compute-gate` -> `validation-submit-gate`.
- Submit attempt: `frontier-lock` -> `ecdsafail-cli-ops` ->
  `validation-submit-gate`.
- Worker handoff: `multi-agent-handoff` plus whichever route or validation card
  owns the task.
- Paper-driven lower-q adder work: `paper-gidney-constant-workspace-adder` ->
  `paper-mbu-modular-arithmetic` -> `q1152-structural-core` or
  `structural-qubit-cut`.
- Conditionally-clean cascade cut: `conditionally-clean-cascade-cut` ->
  `paper-conditionally-clean-ancillae` -> `fold-carry-rearchitecture` ->
  `exact-support-invariant-miner`.
- Free-pool or stale-dead-drop integration failure:
  `paper-wire-recycling-lifetime-graph` -> `redsky-frontier-audit` ->
  `validation-submit-gate`.
- Borrowed working-lane cut:
  `paper-dirty-borrowing-entanglement` ->
  `paper-wire-recycling-lifetime-graph` -> `paper-dead-gate-elimination`.
- Schedule-coupled lower-Q primitive:
  `paper-scalable-memory-recycling` -> `frontier-lock` ->
  `structural-qubit-cut` -> `validation-submit-gate`.
- Comparator peak pressure: `paper-vandaele-optimal-comparator` ->
  `q1152-structural-core` -> `exact-support-invariant-miner`.
- Peak host borrowing: `paper-conditionally-clean-ancillae` ->
  `fold-carry-rearchitecture` -> `exact-support-invariant-miner`.
- Zero-ancilla suffix fallback: `paper-remaud-ancilla-free-adder` ->
  `paper-takahashi-no-ancilla-adder` -> `route-compute-gate`.
- Paper-driven architecture work: `paper-haner-ecdlp-circuits` ->
  `paper-schrottenloher-point-addition` ->
  `paper-luo-register-sharing-eea` ->
  `paper-roetteler-ecdlp-resource-estimate`, then reduce the idea to one local
  invariant.

## Quickstart

Use this as a GitHub template or clone it directly:

```bash
git clone https://github.com/welttowelt/storm-ecdsa-harness.git
cd storm-ecdsa-harness
scripts/redaction-check.sh
scripts/redaction-check.sh --history
scripts/check-public-harness.sh
python3 -m http.server 8787 --directory dashboard
```

Then adapt the templates with fixture or public data only. Keep private hunt
state in a separate private repo or local folder.

Full guide: [docs/quickstart.md](docs/quickstart.md).

Safe filled examples: [examples/](examples/).

Audit loop: [docs/audit-loop.md](docs/audit-loop.md).

Prefilter gate pattern: [docs/stormgate.md](docs/stormgate.md).

Latest stormgate Redsky audit:
[docs/redsky-stormgate-audit-2026-06-20.md](docs/redsky-stormgate-audit-2026-06-20.md).

## What This Repo Does Not Contain

- Live `ecdsafail-hunt-ops` state.
- Private mailbox history.
- Real run logs, pod endpoints, keys, tokens, or account details.
- Unreleased candidate diffs or winning nonces.
- Active strategy notes from an ongoing hunt.

## Operating Model

Every cycle starts from public truth, not memory:

1. Refresh the live benchmark/current target.
2. Read mailbox entries and ACK directed handoffs.
3. Check route packets and evidence labels.
4. Run cheap validation before paid compute.
5. Dispatch compute only when a route has a predicate, owner, validator, kill
   gate, and bounded stop condition.
6. Treat scanner hits as `Prefilter` until official local validation passes.
7. Submit only after fresh frontier recheck, official local `0/0/0`, score win,
   legal narrow diff, public note, and explicit submit flag.

More detail: [docs/operating-model.md](docs/operating-model.md).

## Dashboard

The dashboard in `dashboard/` is static and fixture-only. It shows how to
surface current target, worker status, mailbox activity, breaking news, fleet
state, and submit gates without leaking operational details.

Public fixture dashboard:

```text
https://welttowelt.github.io/storm-ecdsa-harness/
```

Open locally:

```bash
python3 -m http.server 8787 --directory dashboard
```

Then open the local server URL printed by your terminal.

## Redaction Check

Run this before publishing or pushing:

```bash
scripts/redaction-check.sh
```

The check rejects common private material: API-key shapes, remote command
fragments, host/port patterns, private paths, raw nonce assignments, live
mailbox filenames, and forbidden state directories.

Before a public push, also scan committed history:

```bash
scripts/redaction-check.sh --history
```

The GitHub Actions workflow runs both checks on push and pull request.

## Release Rule

Do not publish until:

- `scripts/redaction-check.sh` passes.
- `scripts/redaction-check.sh --history` passes.
- `docs/credits.md` names every borrowed idea or tool.
- All examples use fixture/demo data.
- A human review confirms no private hunt state remains.

See [docs/publish-checklist.md](docs/publish-checklist.md) for the full
publish sequence and [docs/telegram-announcement.md](docs/telegram-announcement.md)
for a short sharing draft.
