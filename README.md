# Stormforge ECDSA Harness

Public repo: <https://github.com/welttowelt/stormforge-ecdsa-harness>

Fixture dashboard: <https://welttowelt.github.io/stormforge-ecdsa-harness/>

Stormforge is a sanitized operator layer for coordinating public `ecdsa.fail`
research workflows. It is not the original benchmark harness and it does not
contain private hunt state.

Purpose and limits: `ecdsa.fail` is a public resource-estimation benchmark for
the quantum cost of one `secp256k1` point-add circuit. This repo contains
workflow templates, evidence discipline, dashboard fixtures, and safety checks.
It does not provide runnable attacks, target selection, key recovery, private
compute endpoints, raw scan logs, unreleased nonces, or live candidate diffs.

## Lineage

- Base challenge / benchmark lineage: Gautham Anant and the public
  `ecdsa.fail` challenge. The public framing is described in Sreeram Kannan's
  article: <https://www.linkedin.com/pulse/you-beat-google-sreeram-kannan-rqehc>.
- Early custom agent-harness inspiration: Gajesh Naik / Gajesh2007, including
  custom agent workflows, goal-mode style operation, model/subagent routing, and
  more agent-readable code organization.
- Stormforge contribution: a sanitized coordination/control-plane layer:
  mailbox protocol, ACK/read receipts, route packets, worker roles, dashboard
  views, compute gates, submit gates, and redaction discipline.

See [docs/credits.md](docs/credits.md) and [CREDITS.yaml](CREDITS.yaml) for
explicit attribution. Credits are split into direct tools, public sources, and
group-discussion process inspiration so the repo does not imply copied code or
endorsement where there was only inspiration.

## What This Repo Contains

- A current-target-first operating model.
- Worker role cards and handoff templates.
- Evidence labels and validation gates.
- Route packet and compute request templates.
- A fixture-only dashboard for operator status.
- A redaction checklist and automated redaction scan.
- Public-credit policy for community-derived ideas.

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
https://welttowelt.github.io/stormforge-ecdsa-harness/
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
