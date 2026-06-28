# Bluesky / Redsky Audit - Pod Inventory ACK Gate - 2026-06-28

## Current Signal

- Storm-Codex issued a MacBook heat-stop directive at 2026-06-28T03:00:48Z.
- The same directive required pod watchers to refresh provider-side inventory
  with owner, pod id, status, job, stop condition, and no-submit ACK.
- Later fleet teardown produced account-level zero-pod ACKs rather than per-pod
  rows.
- Existing public gates covered owner claims and duplicate wrappers, but not
  this exact provider inventory ACK shape.

## Five-Pass Decision

1. Public frontier pass: no candidate or compute unlock is active.
2. Code archaeology pass: fleet-owner and pod-wrapper gates are useful but can
   pass without provider status or job fields.
3. Correctness pass: explicit owner=... must outrank the ACK speaker; otherwise
   owner=unknown can be hidden by an ACK Watcher prefix.
4. Heat-stop pass: Mac-local heavy-compute parsing must catch storm-exact-miner,
   route_compare, search_driver, lower-q, proof, and scanner loops.
5. Handoff pass: add a public parser that accepts complete no-compute inventory
   ACKs, holds unknown inventory, and fails ownerless running pods or start
   language.

## Implemented Gate

The gate requires provider, pod id, owner, status, job, stop condition,
no-start/no-compute ACK, and no_submit_ack=yes.

For `status=0-pods` account rows, pod id and job are replaced by account id,
zero spend per hour, and at least two provider reads.

Pass means inventory accepted for control-plane review only. It does not unlock
compute, residual, trusted eval, benchmark, submit, alert, or sentinel writes.

The local-heavy compute gate was also hardened so the same HOT STOP audit catches
storm-exact-miner, route_compare, search_driver, lower-q/proof/scanner loops,
and recurring local wrappers.

## Cycle 128 Account-Empty Addendum

1. Public frontier pass: fleet teardown has no candidate or compute unlock.
2. Code archaeology pass: the previous gate treated account-level zero-pod ACKs
   as malformed per-pod rows.
3. Correctness pass: `status=0-pods` is acceptable only with account identity,
   spend-zero evidence, and double-read provider verification.
4. Economics pass: nonzero spend on an empty-account ACK is a fail, not a pass.
5. Handoff pass: account-empty pass still means no-compute inventory review only.
