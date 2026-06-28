# Paper Invariant Intake Gate

Use this before turning a paper-mining hit or model-pass packet into a Storm
skill card, route packet, compute request, or handoff.

## Command

    python3 scripts/storm-paper-invariant-intake-gate.py \
      <redacted-paper-model-pass.txt> \
      --require-pass

Defaults assume source d44cad3 and q1152. Override only when a fresh frontier
lock changes the public source or target tier.

## Pass Requirements

- route id, owner, next action, skill name, and paper reference are present;
- source base, source hash, candidate index/diff hash, and source location are
  present;
- the packet is source-hash-bound and source-backed;
- local_invariant names the exact local source invariant;
- scored_IR_effect is one of delete_CCX_CCZ, classically_discount_CCX_CCZ, or
  trusted_eval_avgT_cut;
- classically discounted CCX/CCZ routes name a measured condition source;
- support_status=CERTIFIED and proof_status=CERTIFIED;
- expected_avgT_delta is negative or score_edge is positive;
- evidence_label is Prefilter, Partial, Paper score, or Historical clue;
- no local-heavy context, compute/residual request, submit, alert, or Akash
  language appears;
- no_submit_ack=yes is present.

## Decisions

- pass: source-backed-skill-review-no-compute.
- hold: complete missing source, candidate, proof, or score-edge fields.
- fail: do not promote the paper hit; no skill card, route, compute, pod,
  submit, or alert.

Paper-only T-count, T-depth, relative-phase, or asymptotic improvements are
not score routes unless the packet binds the idea to a current local source
invariant and a score-visible IR effect.
