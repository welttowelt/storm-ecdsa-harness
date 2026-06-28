# Candidate Validation Packet Gate

Use this before FOR-AKASH, candidate, win, or submit-gate language appears in
mailbox or handoff text.

## Gate

Run a redacted validation packet through:

    python3 scripts/storm-candidate-validation-packet-gate.py validation-packet.txt --require-pass

The packet must include:

- remote host or owned pod evidence,
- validator or owner identity,
- official validation path,
- no_submit_ack=yes,
- fresh frontier score and source/base,
- emitted or loaded ops matching the expected op stream,
- qubits at or below the route limit,
- score below the frontier,
- classical, phase, and ancilla counts all zero,
- preserved artifact evidence.

## Discipline

- This gate never runs validation and never submits.
- A pass means handoff to Storm for fresh frontier and submit decision. It is
  not an automatic submit authorization.
- Missing host, score, q, c/p/a, frontier, ops, or artifact evidence is a hold.
- Local Mac validation packets, dirty c/p/a, q overflow, op-stream mismatch, or
  no score edge fail the gate.

## Output

    candidate_validation_packet_gate=<pass|hold|fail> official_path=... remote_host=... ops=... qubits=... score=... counts=... decision=...
