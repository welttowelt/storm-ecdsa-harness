# STORM harness in production

This repo documents the operating model used by the live STORM controller. The
private controller runs the active work. The public repo publishes the reusable
protocol, templates, checks, and fixture dashboard without exposing live state.

## Production Behavior

| Area | STORM harness in production | Public repo surface |
| --- | --- | --- |
| Primary role | Local active `ecdsa.fail` controller for route selection, validation, fleet dispatch, and publication gates. | Public operating model, templates, examples, and release checks. |
| Current target | Refreshes public leaderboard/source state before acting and closes stale routes. | Fixture examples plus the current-target-first rule. |
| Main artifacts | Route packets, compute requests, mailbox entries, model handoffs, validation records, benchmark notes, gate artifacts, and public-note drafts. | Markdown templates and filled public-safe examples. |
| Benchmarks | Runs official local validation, score checks, and submission-note preparation in the private workspace. | Documents the validator contract; does not ship live benchmark outputs. |
| Models | Coordinates Codex-, Claude-, DeepSeek-, Kimi-, and OpenRouter-style workers through explicit roles. | Operator cards and handoff formats. |
| Mailbox | Reads the shared mailbox tail, posts ACKs, records strategic-goal packets, and routes worker objections back into state. | Mailbox template and examples only. |
| Zellij board | Runs the live boss lane, policy/dispatch surface, auditor, PUA/PIP lane, research lane, local benchmark lane, wallbreakers, provider manager, long-context workers, and generic worker panes in one named multiplexer session. | `docs/zellij-control-plane.md` plus the sanitized starter pack under `templates/zellij-control-plane/`. |
| External chat | Human or connector input is converted into source-labeled evidence before it affects routing. | Announcement draft and credit policy. |
| Fleet | Dispatches CPU/GPU work only when a route has a validator, budget, owner, non-overlap rule, and kill gate. | Compute-request template and fixture fleet states. |
| Stormgate | Uses fast prefiltering and first-error validation to reduce wasted full evaluations. GPU output stays `Prefilter` until trusted validation. | Public Stormgate contract, labels, and redaction boundary. |
| Dashboard | Private board reads live state files and queue status. | Static fixture dashboard that shows the same concepts without live data. |
| Redaction | Release checks block private paths, endpoints, keys, logs, mailbox exports, raw ranges, and unreleased nonces. | `scripts/redaction-check.sh`, checklist, and CI workflow. |

## Controller Loop

1. Refresh public frontier state.
2. Refresh the Zellij board status surface and policy pane.
3. Read mailbox tail and ACK directed handoffs.
4. Pick one active route or explicitly park it.
5. Require a route packet with evidence label, validator, owner, budget, and
   falsifier.
6. Run cheap source checks, canaries, and prefilters before paid compute.
7. Dispatch fleet work only after the gate artifacts exist.
8. Treat every scanner row as `Prefilter` until trusted validation returns
   `0/0/0`.
9. Open the submit gate only after a fresh frontier check, score win, legal
   diff, public note, and explicit submit flag.

## Public Boundary

The public release is not a toy architecture. It is the same operating model
with private inputs removed.

Keep these out of public commits:

- live mailbox exports,
- private fleet config,
- pod endpoints or account IDs,
- keys, tokens, or local credential names,
- raw scan logs and run logs,
- raw nonce ranges or unreleased candidate diffs,
- absolute local paths from an operator machine.

The OSS value is the discipline: current-target lock, evidence labels,
canary-gated compute, mailbox ACKs, route packets, first-error validation, and
release redaction.
