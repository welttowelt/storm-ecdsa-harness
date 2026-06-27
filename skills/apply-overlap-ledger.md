# Skill: Apply Overlap Ledger

Use when a lower-Q ECDSA.fail route claims a width cut by delaying, streaming,
or loaning pending dialog symbols or the last tape window across
`tlm_apply_inverse_mod_sub_fold`.

## Purpose

This skill turns the current apply/codec/fold overlap idea into a reusable
public proof gate. It does not prove a solver route by itself. It records the
minimum evidence needed before fleet compute:

- a `TLM_TAPE` row at the target fold iteration;
- a candidate-specific `TLM_OVERLAP_CHECK` row;
- zero reads during the fold;
- read/restore evidence;
- phase-channel evidence;
- a route-specific public certificate before compute.

## Procedure

Run the ledger on a public trace:

```bash
scripts/apply-overlap-ledger.sh \
  --trace examples/apply-overlap-trace.example.txt \
  --frontier 1571592960 \
  --q 1147 \
  --target-q 1146 \
  --route <tree-or-branch> \
  --candidate pending_symbols
```

The default target is the current high-pressure fold:
`target_phase=tlm_apply_inverse_mod_sub_fold`, `target_i=255`.

## Decisions

- `missing-tape-overlap-trace`: capture `TLM_TAPE` rows before editing code.
- `measure-read-restore-phase`: add a candidate-specific overlap row.
- `overlap-nacked-read-during-fold`: the fold still reads the candidate wires.
- `overlap-restore-proof-missing`: read/write restoration is not proved.
- `overlap-phase-proof-missing`: phase cleanliness is not proved.
- `certificate-ready`: attach the public certificate before compute.
- `support-certified-binder-fact`: promote to a bounded local solver patch.

## Kill Gate

Do not submit or dispatch compute from this ledger alone. A certified ledger row
only says the overlap fact is ready for a local patch. The patch still needs toy
tests, exact read/restore tests, phase tests, trusted local `0/0/0`, and an
official score below the refreshed frontier.
