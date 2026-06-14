# Storm ECDSA Harness

Public repo: <https://github.com/welttowelt/storm-ecdsa-harness>

Fixture dashboard: <https://welttowelt.github.io/storm-ecdsa-harness/>

Storm is a sanitized operator control plane for coordinating public
`ecdsa.fail` research workflows. It is the layer around the solver: deciding
what deserves attention, forcing evidence labels, routing workers, gating
compute, recording ACKs, and keeping public notes safe to share. The edge is
multi-model collaboration: different workers can contribute through mailbox or
API handoffs, but every claim still has to pass the same evidence, critique, and
validation gates. It is not the original benchmark harness and it does not
contain private hunt state.

Purpose and limits: `ecdsa.fail` is a public resource-estimation benchmark for
the quantum cost of one `secp256k1` point-add circuit. This repo contains
workflow templates, evidence discipline, dashboard fixtures, and safety checks.
It does not provide runnable attacks, target selection, key recovery, private
compute endpoints, raw scan logs, unreleased nonces, or live candidate diffs.

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
- Storm contribution: a sanitized coordination/control-plane layer:
  mailbox protocol, ACK/read receipts, route packets, worker roles, dashboard
  views, compute gates, submit gates, and redaction discipline.

See [docs/credits.md](docs/credits.md) and [CREDITS.yaml](CREDITS.yaml) for
explicit attribution. Credits are split into direct tools, public sources, and
group-discussion process inspiration so the repo does not imply copied code or
endorsement where there was only inspiration.

## What This Repo Contains

- A current-target-first operating model.
- Worker role cards and handoff templates.
- Critique-before-compute audit loop.
- Evidence labels and validation gates.
- Route packet and compute request templates.
- External pressure-test worker prompt pattern.
- Safe filled examples for the templates.
- A fixture-only dashboard for operator status.
- A redaction checklist and automated redaction scan.
- Public-credit policy for community-derived ideas.

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
