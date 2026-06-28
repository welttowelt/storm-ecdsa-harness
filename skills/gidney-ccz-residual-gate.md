# Gidney CCZ Residual Gate

Use this before spending validation work on `TLM_GIDNEY_SKIP_SMALL_RESIDUAL_DEAD`
or related Gidney erase-CCZ claims.

## Command

    python3 scripts/storm-gidney-ccz-residual-gate.py \
      --gidney-rs <ecdsafail source>/src/point_add/trailmix_ludicrous/gidney.rs \
      --point-add-mod-rs <ecdsafail source>/src/point_add/mod.rs \
      --packet <redacted-ccz-residual-packet.txt> \
      --require-pass

Without `--packet`, the command emits a source screen only. It never unlocks
compute by itself.

## Pass Requirements

- `source_base=d44cad3`, `q=1152`, `kind=CCZ`, and `no_submit_ack=yes`.
- The packet names a new erase-CCZ call/key outside the current default-on
  residual and remainder lists, or it explicitly proves that the current source
  does not default-enable that residual list.
- `expected_shot_mass` is at least the rounded-score drop required to beat the
  current q1152 frontier.
- If `expected_avgT_delta` is supplied, it must not claim more average-Toffoli
  drop than the packet's `expected_shot_mass / shots` supports.
- `support_status=CERTIFIED`, `proof_status=CERTIFIED`, `restore_proof=1`, and
  `phase_proof=1`.
- No pod, GPU, CPU, scanner, residual, benchmark, alert, or submit request.

## Decisions

- `pass`: eligible for Storm compute-unlock review, with no automatic compute.
- `hold`: source proof, restore proof, phase proof, or packet fields are missing.
- `fail`: default-on residual/remainder row, stale source, wrong q-tier,
  non-CCZ packet, below-bar mass, compute request, submit/alert language, or
  missing no-submit ACK.
