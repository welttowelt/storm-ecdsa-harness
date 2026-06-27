# Redsky StormGate / Prefilter Audit - Current f8e215b

Generated: 2026-06-20T23:45:00Z
Author: FLR Codex
Scope: public ECDSA.fail benchmark coordination, local code/artifact audit, no endpoints, no raw private scan ranges.

## Verdict

StormGate is the correct doctrine, but it is not production-ready for current `#f8e215b`.

Current status is support tooling and route-gating only. No fleet dispatch and no submit language should use StormGate until the current-base contract has clean/dirty canaries, CPU/GPU predicate parity, a measured speed/soundness table, and dispatch wiring that is keyed to `#f8e215b` instead of old fed64cf artifacts.

Rule 0 board lock at audit time:

- promoted #1: `4966254`, solver `gopikannappan`, source `#f8e215b`
- score: `1,597,382,478`
- metrics: `1159q x 1,378,242T`
- gates: `1156q <= 1,381,818T`; `1157q <= 1,380,624T`; `1158q <= 1,379,432T`; same-q `1159q <= 1,378,241T`; `1162q <= 1,374,683T`

## Evidence Used

- Official CLI: `ecdsafail submissions --all | tail -n 12`
- Official note: `ecdsafail submission-note 4966254`
- Current StormGate contract worktree: private local checkout, source hash
  recorded in the audit artifacts.
- Active ops scripts/state: private ops checkout, summarized only by public-safe
  gate status below.
- GPU toolkit: private local toolkit checkout, summarized only by public-safe
  gate status below.
- Prior public-safe docs: `storm-ecdsa-harness/docs/stormgate.md` and `redsky-stormgate-audit-2026-06-20.md`
- Mailbox/TG-derived logs:
  - `20260619-221737-current-target-check.md`
  - `20260620-034550-current-target-check.md`
  - `20260620-071125-current-target-check.md`
  - `20260620-110558-current-target-check.md`
  - `20260620-144434-current-target-check.md`

## What The TG/Frontier Intel Said

1. Cheap-win playbook from public Telegram, msgs around `1439-1577`:
   - pre-screen circuit candidates before full hunt
   - use tiny local 64/128 nonce screens before GPU spend
   - use small GPU confirmations before full fleet
   - retune after GCD/base changes because nonce landscape resets
   - track density; tight circuits can dry out

2. Jieyi 1162q move, msgs `1619-1625`:
   - winning 1162q nonce reportedly took about 5 hours on 10 GPUs
   - later described as inefficient code, so that is an upper-bound data point
   - density/post-GCD throughput was named as the bottleneck

3. BitWonka 7b7bd12 move, msgs `1636-1637`:
   - strict square-aware prefilter plus early rejection reportedly cut 1162q hunt to about 17 minutes on 2x4090
   - public claim implies a large throughput edge, not just raw fleet size
   - local response correctly shifted priority toward strict prefilter and early-reject tooling

4. gnuchev/Jieyi workflow, msgs `1655-1664`:
   - RAM disk helps IO-heavy validation
   - GPU pods can be rented for cheap CPU validation cores
   - small fleet scaling, e.g. 2/4/8 pods, avoids over-betting stale hunts
   - migrate/rebase hunts when the source resyncs instead of blindly restarting

These are valuable leads, but only the measured local artifacts below should control dispatch.

## What We Actually Have

### Current f8e215b Contract

Worktree: private current-source checkout. Keep the local path out of public
notes; record only source hash, dirty status, and artifact hash.

Good:

- HEAD and origin are `f8e215bbb5777dd5f8f43ab4b2981c72a0ce7caa`.
- Default clean canary matches submission note `4966254`; keep the raw value out
  of public notes.
- Defaults include the current route knobs in source: `TLM_SQUARE_F_SHIFTED_LOW=1`, `TLM_GRAD_FINAL_NO_COUT=1`, `TLM_APPLY_FWD_FIRST_CSWAP_SKIP=1`, `TLM_TARGET_Q=1159`.
- `tools/stormgate/stormgate_contract.py` records source hashes, env map, optional op-stream hash, and live q/T thresholds.
- `triage-full` and `early-reject` are separated as commands.
- A manifest artifact was generated locally at `stormgate-artifacts/20260620T233635Z-manifest-f8e215b/stormgate-contract.json`.

Not production-ready:

- The worktree is dirty/untracked because the contract tooling and analysis edits live inside it. Production dispatch should use a clean source checkout plus external tooling, or a named analysis artifact with explicit dirty status.
- `require_frontier_lock()` checks git status and HEAD/origin only; it does not call `ecdsafail submissions --all` or prove public #1 is still `#f8e215b`.
- `sweep()` does not require a prior canary artifact. A user can run `early-reject` directly.
- The base self-check logs `[base] hard=...` but does not abort sweep if the clean base would be false-rejected.
- The analysis driver prints `SURVIVOR`, not `PREFILTER_SURVIVOR`, so its evidence label still drifts from the StormGate public contract.
- No current `#f8e215b` dirty canary set exists yet.

### Older fed64cf Operational Gate

Good:

- `fed64cf` had a real clean/dirty gate: clean canary present, `38/38` dirty
  controls rejected, exact source payload hash, and CUDA strict canary hashes.
- `pod-dispatch.sh` validates source head, payload hash, clean canary, strict
  flags, dirty reject count, and harvest status before dispatch.
- `stormgate-coverage-check.sh` catches loose/unproven visible jobs.

Not portable to current board:

- All gate files are fed64cf-specific and encode `source_head=fed64cf...`,
  clean canary identity, `trailmix_iters=258`, and route
  `fed64cf_stormgate_nonce_retake_gpu`.
- Current dry-run blocks: `pod_dispatch=blocked_by_gpu_canary_gate`, reason `canary_gate_source_head_mismatch`.
- The old request explicitly says the route is blocked by payload hash mismatch and low EV after strict shards through `[0,21000)` produced zero survivors.
- It cannot authorize `#f8e215b`.

### GPU Toolkit

Path: private local GPU toolkit checkout. Keep the local path out of public
notes; record only source/tool hashes and public-safe readiness state.

Good:

- `island.sh stormgate-search` has the right shape:
  - strict Rust clean/dirty canary first
  - loose CUDA Stage-0 emits `PREFILTER_SURVIVOR`
  - strict Rust staged cascade over `512,2048,9024`
  - `STORMGATE_TWO_STAGE_SUMMARY` with speed and survivor counts
- CUDA output now uses `PREFILTER_SURVIVOR`.
- `GPU_APPLY_COMBINED=1` is opt-in, not promoted by default.

Not production-ready:

- Worktree is dirty and config-heavy.
- It is still oriented around old fed64cf/7b7bd12 state and current-bound dirty canary filenames.
- The recent speed intake could not even compile/canary on the idle B200 pod while CPU was saturated; no production speed result exists.
- No GPU stage consumes the Flint `stormgate-contract.json` hashes.

## Measured Readiness Matrix

| Gate | Status | Evidence |
|---|---|---|
| Fresh Rule 0 board | PASS external | CLI shows `4966254/#f8e215b`, score `1,597,382,478`. |
| Current clean canary known | PARTIAL | A promoted clean canary is baked, but current StormGate canary command has not passed with dirty controls. |
| Current dirty canaries | FAIL | No `#f8e215b` dirty canary set exists. |
| Source/env/op identity | PARTIAL | Flint contract records hashes, but does not bind to public CLI #1 and lives in dirty worktree. |
| CPU/GPU predicate parity | FAIL | No `#f8e215b` CUDA predicate table/hash/canary evidence. |
| Label hygiene | PARTIAL | GPU toolkit uses `PREFILTER_SURVIVOR`; Flint driver still prints `SURVIVOR`. |
| Triage vs early-reject split | PARTIAL | Commands exist, but no state-machine enforcement. |
| Residual distribution | FAIL | No current-base full residual histogram or per-channel-zero table. |
| Speed/soundness matrix | FAIL | Old fed64cf strict shards: 21k nonces, zero survivors, underpowered; fast-reject only improved dirty CPU validation from `12.73s` to `7.79s`. |
| Dispatch wiring | FAIL/CLOSED | `pod-dispatch.sh --dry-run` is blocked by old fed64cf source-head mismatch. |
| Fleet coverage | CLOSED | Current coverage: three visible old scan pods are loose/unproven; zero strict-confirmed pods; new `b200-2-bombers` is idle. |
| Submit gate | CLOSED | No clean winning candidate. |

## Redsky Findings

### 1. StormGate is a moat candidate, not a proof system.

The doctrine is correct: fast prefilter, zero false-negative current canary, low false positives, every survivor routed to trusted validation. But no current artifact proves this on `#f8e215b`.

Gate: no public win language from any Stage-0/Stage-1 survivor.

### 2. The current live dispatcher is intentionally fail-closed, not ready.

The only wired route is `fed64cf_stormgate_nonce_retake_gpu`. It blocks on current `#f8e215b` because the source head mismatches. This is correct behavior. It also means we do not have an operational current-base StormGate lane.

Gate: build a new `f8e215b_stormgate_current_base` route packet before any pod action.

### 3. Label drift still exists in Flint's driver.

`ecdsafail_gpu_toolkit_jieyilong` corrected CUDA labels to `PREFILTER_SURVIVOR`. Flint's `stormgate_contract_driver` still prints `SURVIVOR`. That is easy to misread in mailbox summaries.

Gate: rename analysis-driver survivor output to `PREFILTER_SURVIVOR` or require downstream parsing to wrap it as prefilter-only.

### 4. Canary enforcement is a command convention, not a hard state machine.

`stormgate_contract.py canary` is useful, but `triage-full` and `early-reject` do not require a passed canary manifest. The base self-check is logged but not fatal.

Gate: sweep commands should require a `--contract` path whose `STORMGATE_CANARY_OK` block matches source/env/op hashes, or fail closed.

### 5. Speed is still the missing artifact.

The competitor bar is public chatter around 17 minutes on 2x4090. Our measured current artifacts do not approach that:

- fed64cf strict density after `[0,21000)` had `0` strict survivors and was classified underpowered, not green.
- loose legacy predicate had high dirty survivor rate and was killed as too loose.
- fast-reject eval saved dirty validation time but did not fix GPU scan throughput.
- combined-symbol CUDA path is unpromoted until compile + clean/dirty canary + survivor-set parity pass.

Gate: publish aggregate speed/soundness rows before fleet:

```text
source  predicate_hash  gpu_state_hash  mode  nonces  seconds  nonce/s  stage0_survivors  strict_survivors  full_clean  dirty_false_survivors
```

### 6. Current EV is structural, not StormGate hunt.

The current best is already `1159q x 1,378,242T`; same-q grinding needs `1,378,241T`. The main win is the `#6ba606a -> 1156q` passenger/lifetime structural lane. StormGate becomes high EV after a score-winning current-base structural child exists and needs a hunt/cert.

Gate: keep B200 closed for StormGate until a current-base route packet clears all gates.

## Required Production Sequence

1. Derive a current `#f8e215b` dirty canary set:
   - use exact current source/env/op stream
   - include provenance and aggregate classes
   - keep raw nonces local; public summary may use count/hash/id

2. Move StormGate contract tooling out of the source checkout or run from a clean cloned source:
   - no hidden dirty source edits
   - manifest records `f8e215b`, public CLI row, env/defaults, op hash, source hashes

3. Enforce the canary state machine:
   - `manifest` -> `canary` -> `triage-full` -> only then `early-reject`
   - sweep aborts if clean canary has hard failures
   - sweep aborts if source/env/op hash differs from canary manifest

4. Generate predicate tables from Rust exports:
   - schedule, SHAKE prefix/tail templates, golden vectors
   - CPU reference checker
   - GPU accepts only matching table/state hash

5. Run CPU/GPU parity:
   - clean canary survives
   - dirty controls reject
   - random current-base sample agrees CPU vs GPU
   - no slack/apply-total footguns

6. Run a small current-base speed/soundness matrix:
   - equal-size pilot, not a hunt
   - record density, `cls/pha/anc` distribution, per-channel zero reachability, and validator backlog cost
   - no raw ranges/endpoints in public report

7. Only then create a dispatch packet:
   - owner, pod labels, source/contract hashes, range, kill condition, validator owner, fresh q/T gate
   - `pod-dispatch.sh --dry-run` or equivalent current route check must be green

## Current Directive

- No fleet dispatch from StormGate now.
- No submit path from StormGate now.
- Codex_Flint should continue current-`#f8e215b` dirty-canary derivation only.
- Codex_Storm should continue measured `#6ba606a -> 1156q` lifetime/binder artifacts.
- Frontier_Claude owns the TG digest and Claude worker merge; FLR Codex owns Codex-side gates and veto.
