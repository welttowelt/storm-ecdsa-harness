# Zellij Control Plane Template

This is a sanitized starter pack for a private STORM-style Zellij board. It is
designed to replace loose manual terminal sessions with one named multiplexer
session, visible policy gates, role tabs, dispatch state, and repeatable worker
launchers.

It is a template, not live state. Keep private controller state, logs, provider
hosts, credentials, payment/account data, raw run output, and candidate material
out of the public repo.

## Install

```bash
cp -R templates/zellij-control-plane ../private-storm-controller
cd ../private-storm-controller
cp state/fleet-policy.env.example state/fleet-policy.env
cp workers.tsv.example workers.tsv
```

Edit `state/fleet-policy.env` and `workers.tsv`, then start the board:

```bash
./bin/start-zellij
```

Resume later:

```bash
zellij attach "STORM BOSS"
```

## Launch Agents

Inside the Zellij session:

```bash
./bin/check-gates --brief
./bin/launch-codex-roles
./bin/launch-claude-roles
./bin/role-loop enqueue --idle
./bin/steer-fleet dispatch
```

The Codex launcher uses:

```bash
codex --cd "$STORM_FLEET_ROOT" --sandbox danger-full-access --ask-for-approval never
```

The Claude launcher uses:

```bash
claude --dangerously-skip-permissions --effort max --model opus
```

Those are private-operation launchers. The policy file and role prompts are the
guardrails: no submit, no secrets, no unbounded compute, no provider action
unless a matching local gate is open.

## Customize

- `layouts/fleet.kdl`: tab and pane layout.
- `state/fleet-policy.env`: local gate state.
- `workers.tsv`: local worker registry.
- `docs/role-goals.md`: reusable `/goal` prompts.
- `bin/role-loop`: recurring LOOP packets for Claude and specialist panes that
  are idle or stale. Set `STORM_ROLE_LOOP_IDLE_MIN_SECONDS` to tune cadence.
- `bin/steer-fleet`: delivery bridge from dispatch rows into live Zellij panes.
- `docs/current-findings.md`: current public-safe operating summary.
- `templates/research-packet.md`: route research packet shape.
- `templates/route-attempt.md`: wallbreaker output shape.

## Public Safety

Before copying anything back to the public harness repo, run the public repo
checks from the public repo root:

```bash
scripts/redaction-check.sh
scripts/check-public-harness.sh
```
