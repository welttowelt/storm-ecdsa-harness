# Skill: Dead-Drop Fixed Point

Use when a route wants to remove sampled-dead `CCX`/`CCZ` operations, apply a
dead-drop index file, reuse a residual probe, or promote a deadness scan toward
count, residual, eval, compute, or submit.

## Core Lesson

A dead-op index is not a portable proof. Dynamic deadness on sampled shots can
be a good scout signal, but it is not a source invariant, and it is not stable
after source edits, nonce changes, allocation changes, or op-order changes.

The required promotion shape is:

1. source-bound support proof is `CERTIFIED`;
2. candidate index list is bound to the exact pre-drop stream hash;
3. the candidate stream was rebuilt after the edit;
4. residual/eval reads the rebuilt candidate stream, not an old `ops.bin`;
5. the drop list is replayed to a fixed point on that stream;
6. trusted validation reports `0/0/0` before win language or compute.

## Required Packet

```text
route_id:
stream_hash:
pre_drop_ops_hash:
candidate_indices_sha256:
source_hash:
support_status: CERTIFIED / UNKNOWN / COUNTEREXAMPLE
support_certificate:
dynamic_deadness:
sampled_shots:
rebuilt_after_edit:
residual_probe_rebuilt:
fixed_point:
eval_classical:
eval_phase:
eval_ancilla:
```

## Software Gate

Run:

```bash
python3 scripts/storm-dead-drop-fixedpoint-gate.py \
  --packets <dead-drop-packets.tsv> \
  --summary-out <summary.tsv>
```

Classifications:

- `DYNAMIC_ONLY`: sampled deadness without source-invariant proof.
- `STALE_RESIDUAL`: residual/eval did not rebuild from the candidate stream.
- `UNKNOWN_PROOF`: proof is not source-bound certified.
- `NO_FIXED_POINT`: candidate was not replayed to fixed point.
- `DIRTY_EVAL`: trusted eval is not `0/0/0`.
- `FIXEDPOINT_READY`: ready for validation gates, not a win by itself.

## Kill Gate

Do not run residuals, eval, pods, benchmark, or submit from:

- sampled deadness alone;
- a stale or baseline `ops.bin`;
- bare `support_status=CERTIFIED` without source hash and certificate;
- a drop list whose index hash is not bound to the current stream;
- a non-fixed-point regenerated list;
- any trusted eval with classical, phase, or ancilla failures.

Only `FIXEDPOINT_READY` can advance, and it is still evidence-label `Prefilter`
until trusted validation is clean.
