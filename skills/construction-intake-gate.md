# Construction Intake Gate

Use this before converting a paper-mining scout into a source-bound construction
handoff, skill card, route packet, residual, or compute request.

## Command

    python3 scripts/storm-construction-intake-gate.py \
      <redacted-construction-packet.txt> \
      --require-pass

Defaults assume source `d44cad3`. Override only after a fresh frontier lock
changes the public source.

## Pass Requirements

- route id, owner, next action, paper reference, source base, source location,
  source hash, candidate hash, and current source replacement are present;
- q/T economics include current q, target q, current average Toffoli, predicted
  candidate or extra average Toffoli, frontier score, candidate score, and
  positive score edge;
- restore, phase, and ancilla proof obligations are named;
- a bounded toy falsifier is named;
- evidence label is Prefilter, Partial, Paper score, or Historical clue;
- `no_submit_ack=yes` is present and there is no pod, GPU, CPU, scanner,
  residual, benchmark, alert, or submit request.

## Decisions

- `pass`: source-bound construction intake review, no-compute.
- `hold`: missing source, candidate, economics, proof-obligation, or bounded-toy
  fields.
- `fail`: paper-only/scout-only packet, counterexample, stale source,
  nonpositive score edge, compute request, submit/alert language, overclaimed
  evidence label, or missing no-submit ACK.
