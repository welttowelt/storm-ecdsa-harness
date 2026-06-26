# Skill: Paper - Dirty Borrowing Entanglement

Use when a lower-Q route borrows an existing working qubit as temporary dirty
workspace, loans a clean-looking lane across a suffix, or reclaims a physical
wire before every dependency on its previous logical owner is proven dead.

## Source

- Bonan Su, Li Zhou, Yuan Feng, and Mingsheng Ying, "Borrowing Dirty Qubits in
  Quantum Programs", arXiv:2508.17190.

## Why We Keep It

The paper's useful gate is stricter than "the borrowed lane is zero when I free
it." A dirty borrow entanglement check is valid only if the borrowed source
stays idle during the borrow window and the whole inserted computation acts as
identity on that source state, including external entanglement with outside
systems.

For the ecdsa.fail lower-Q campaign, this is the exact failure mode behind
cy0/suffix loan experiments: a width cut can land while the evaluator reports
sparse phase/value dirt or dense downstream-pass failure. That is evidence that
the borrow was not identity-safe yet, not evidence for nonce search.

## Apply To

- `loan_zero_qubit` / `reclaim_zero_qubit` changes;
- carry, cout, cy0, suffix, or comparator host borrowing;
- conditionally-clean or dirty-ancilla substitutions;
- any route where a physical qubit is reused before the original logical role
  has an explicit owner handoff;
- q1152-or-lower cuts that pass a count gate but fail raw/no-drop eval.

## Required Invariant

For each borrowed source lane:

```text
candidate=<name>
source_lane=<physical or logical lane>
borrow_window=<start..end>
source_idle_through_window=<yes/no>
restores_original_source_state=<yes/no>
identity_on_external_entanglement=<yes/no>
all_old_owner_consumers_before_borrow=<yes/no>
raw_no_drop_eval=<shots:c/p/a>
```

`restores_original_source_state=yes` means the source returns to the exact
unknown state it held before borrowing, not merely to `|0>`. If the route needs a
known-zero source, it is clean reuse, not dirty borrowing, and must prove the
zero assertion separately.

## Procedure

1. Refresh the frontier and q-tier threshold before route decisions.
2. Identify the old owner and the borrowed owner as separate logical roles even
   if they share a physical id.
3. Build a local ledger for the borrow window: source last use, borrow start,
   all gates touching the source while borrowed, borrow end, source next use.
4. Reject immediately if the source is active, if the route only restores zero
   instead of the original state, or if no identity-on-source proof exists.
5. Run the raw/no-drop 9024-shot gate before stale dead-drop regeneration.
6. Only after raw/no-drop is `0/0/0`, run `paper-dead-gate-elimination` /
   `stable-op-dead-drop` for the current stream.

Helper:

```bash
scripts/dirty-borrow-ledger.sh \
  --frontier 1577850522 \
  --q 1152 \
  --route q1152-cy0-reclaim \
  --candidate cy0-source-window \
  --source-lane cy0 \
  --borrow-window after-prefix..before-reverse-prefix \
  --source-idle unknown \
  --restores-original-state unknown \
  --identity-proof unknown \
  --old-consumers-before-borrow unknown \
  --raw-result 9024:6/8/0
```

## Output

```text
Dirty borrow entanglement gate:
- Route:
- Candidate:
- Frontier/q/max avgT:
- Source lane:
- Borrow window:
- Source idle:
- Restores original source state:
- Identity-on-entanglement proof:
- Raw/no-drop result:
- Decision: prototype-eligible / proof-required / reject-source-active / reject-not-restored / dirty-borrow-invalid / park
```

## Kill Gate

Do not run nonce search, paid compute, or submit gates from a borrowed-lane
route unless the source-idle and identity-on-source obligations are explicit and
the trusted raw/no-drop circuit is clean. Phase dirt is still a failed borrow.
