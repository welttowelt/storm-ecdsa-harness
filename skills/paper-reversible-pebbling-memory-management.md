# Skill: Paper - Reversible Pebbling Memory Management

Use when a lower-Q ecdsa.fail route lowers peak qubits by recomputing,
delaying, or cleaning intermediate values instead of simply deleting gates.

## Source

- Luca Meuli, Mathias Soeken, and Giovanni De Micheli, "Reversible Pebbling Game
  for Quantum Memory Management", arXiv:1904.02121.
- Related but less direct: Ding et al., "SQUARE: Strategic Quantum Ancilla Reuse
  for Modular Quantum Programs via Cost-Effective Uncomputation",
  arXiv:2004.08539. Use it for modular uncompute/reuse policy, not as a lower
  bound proof.

## Why We Keep It

The paper maps quantum memory cleanup to a reversible pebbling problem on a DAG:
each intermediate value is a node, and a valid strategy chooses when to compute,
keep, uncompute, or recompute nodes under a fixed qubit budget. This is exactly
the shape of the q1152 wall: one-qubit savings are possible only when the
cleanup/recompute strategy is value, phase, and ancilla safe.

The useful lesson is the trade: lower peak qubits usually costs extra
operations. That is acceptable only if the new operation count still beats the
frontier threshold and the cleanup dependencies are regenerated for the edited
stream. A paper-inspired qubit cut is not real until the recompute/uncompute DAG
is explicit and the trusted evaluator accepts the edited stream.

## Apply To

- inverse-fold and register-add peaks where a stored carry can be recomputed;
- FFG/fold schedule changes that move a live value across the peak;
- dead-drop regeneration after op-stream edits;
- transcript or codec changes that trade resident bits for decode/replay work;
- any q1152-or-lower route that is clean no-drop but needs peak relief.

## Do Not Use For

- broad adder-family swaps after the peak ledger shows the peak is a width-1
  carry floor;
- declaring q1153 a theoretical floor from one local profile;
- using sampled dead-op indexes as a stable proof after an op-stream edit;
- continuing a route whose recompute cost cannot clear the q-tier score gate.

## Required Invariant

For every intermediate value removed from the peak, name the producer DAG node,
all consumers, and the recompute/uncompute path that restores every qubit on
both active and inactive branches.

Required shape:

```text
node=<value> producer=<callsite/op-range> consumers=<callsite/op-ranges>
live_across_peak=<yes/no> branch_condition=<condition or unconditional>
move=<delay|uncompute-before-peak|recompute-after-peak|keep-and-park>
restore=<exact inverse path> stale_drop_state=<none|historical|regenerated|fixed-point>
```

## Procedure

1. Lock the frontier and compute the target max average Toffoli for the proposed
   q tier.
2. Build a peak ledger from profile/timeline output: phase label, local peak,
   live hosts, producer callsite, consumers, and cleanup point.
3. Convert one pressure point into a small DAG: inputs, intermediate nodes,
   outputs, and reversible cleanup edges.
4. Choose one pebbling move:
   - recompute a value after the peak;
   - uncompute earlier and replay later;
   - delay allocation until the consumer window;
   - keep the value and reject the cut if recompute is too expensive.
5. Rebuild without stale dead-drop files. If the op stream changed, regenerate
   drop candidates for the current stream before judging correctness.
6. Run the gate sequence: count, partial residual, full residual, then official
   benchmark only after 0/0/0.

Use `scripts/pebble-memory-ledger.sh` to normalize evidence from build/eval
logs before posting to the mailbox. When attacking transcript storage, pass a
`TLM_TAPE`/`TLM_FFG` trace with `--trace-log`, `--trace-target-q`, and, when the
peak occurs inside a child adder, `--trace-active-floor` for neighboring tape
rows. The helper then records the plateau tape length, pending-window pressure,
codec family, and coincident FFG calls. The helper intentionally records dirty
results too; dirty evidence is how stale-drop and missing-consumer routes get
closed.

## Current Applied Gate

2026-06-26 production gate, q1152 Gidney suffix route:

- raw/no-drop Gidney stream at `4cd1b2f` is q1152 but dirty:
  `12 classical / 12 phase / 0 ancilla`;
- exact current-stream `DEAD_SCAN_REAL_SEED=1` found 59,972 raw-index candidate
  dead CCX/CCZ ops with an estimated 56,199.5705 raw-stream avg-Toffoli cut;
- applying that regenerated raw-index `DROP_DEAD_FILE` changed the stream and
  worsened trusted eval to `2696 classical / 141 phase / 0 ancilla`.

Conclusion: raw-index dead drops are not stable operation identities for this
route. Continue only with stable identities or edited-seed fixed point; otherwise
work path B (+f-PAD/carry approximation) or the floor audit.

2026-06-26 Fig-2/adder-family closure:

- the peak instance is a width-1 `s=2` chunk: one internal carry stacked on a
  1152 resident floor;
- streaming/non-ripple adders that help wide chunks do not help this peak and
  can increase peak width.

Conclusion: use this skill to audit resident-base and transcript/fold
dependencies, not to keep swapping adder implementations at the closed peak.

2026-06-26 q1147 transcript/FFG plateau gate:

- local 3-symbol dialog codec is entropy-tight (`ceil(log2(5^3)) = 7`), so a
  useful cut needs schedule/pebble timing rather than another local 3-symbol
  mapping;
- apply this card by tracing `TLM_TAPE` rows next to `TLM_FFG` rows, then model
  one segment as a producer/consumer DAG before trying to uncompute or replay
  it;
- the acceptance question is not "can we save a tape bit somewhere?" but "can we
  save a resident bit at every q-target plateau row without adding more Toffoli
  than the q-tier score headroom permits?"

## Output

```text
Reversible pebbling memory gate:
- Frontier:
- q target / max avgT:
- Peak node:
- Removed or delayed value:
- Producer / consumers:
- Pebbling move:
- Trace ledger:
- Extra ops estimate:
- Dead-drop state: none / historical / regenerated / fixed point
- Residual evidence:
- Decision: continue / regenerate / park
```

## Kill Gate

Park the route if the DAG node has an unlisted consumer, the recompute path
touches a control/host that is live for the same condition, the extra Toffoli
cannot beat the q-tier threshold, or the only clean evidence uses stale drop
indices.

## Loop Rule

Repeat this loop while the lower-Q goal is active:

1. refresh frontier and q-tier score thresholds;
2. pick exactly one peak node from the latest ledger;
3. build the producer/consumer DAG;
4. run one pebbling move or prove why it cannot reduce peak;
5. post the normalized ledger;
6. if closed, choose a different peak node or pivot to nonce/Toffoli axis.
