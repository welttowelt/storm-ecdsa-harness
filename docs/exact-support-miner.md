# Exact Support Miner

The exact support miner is a public-safe fleet tool for turning op-trace facts
into ranked value-exact skip packets. It is a research-harness artifact, not a
solver, submitter, mailbox reader, fleet dispatcher, or nonce hunter.

## Purpose

The miner targets fixed-allocation average-Toffoli reductions. It looks for
omissions that preserve the circuit function and allocator order, then emits a
packet another worker can prove, patch, and validate through the normal Redsky
gate. This is the durable route behind exact-dead and exact-remainder work:
find small omissions repeatedly, keep the proof local, and block compute until
the proof packet is strong.

## Public Boundary

Inputs must be fixture or public trace facts only. Do not include private
mailbox exports, live candidate diffs, remote endpoints, private paths, raw
logs, account details, keys, tokens, or unreleased nonce values.

The miner rejects common private shapes before writing output. Public packet
fields should use source-like locations such as `src/point_add/demo.rs:42`,
public commit labels, fixture stream hashes, and evidence labels.

## Workflow

```bash
python3 scripts/storm-exact-miner.py trace-facts \
  --input examples/op-trace-facts.example.jsonl \
  --out /tmp/storm-facts.jsonl

python3 scripts/storm-exact-miner.py mine \
  --facts /tmp/storm-facts.jsonl \
  --out /tmp/storm-candidates.jsonl

python3 scripts/storm-exact-miner.py prove \
  --candidates /tmp/storm-candidates.jsonl \
  --out /tmp/storm-proof-packets.jsonl

python3 scripts/storm-exact-miner.py rank \
  --proofs /tmp/storm-proof-packets.jsonl \
  --out /tmp/storm-ranked.jsonl
```

## Packet Fields

Each packet records:

- route id, frontier, source base, stream hash, and source location;
- op class and executed weight;
- allocator unchanged flag;
- proof kind and proof status;
- expected average-Toffoli delta;
- Redsky evidence label;
- validation target and kill gate.

The output schema is represented by
`templates/exact-skip-candidate.json`.

## Proof Discipline

The v1 miner can certify only simple public-safe obligations:

- an external public certificate was supplied with the trace fact;
- a built-in exact-remainder range check proves `value_max < modulus`.

Everything else is emitted as `UNKNOWN`. `UNKNOWN` packets are useful backlog,
but they do not authorize compute, circuit edits, win language, or submit work.

## Redsky And PIP Gates

Before acting on a packet, the worker must state:

- strongest objection;
- fastest falsifier;
- proof method;
- expected score movement;
- dirty classes to track;
- completion evidence.

The completion gate is a trusted validation path with `cls/pha/anc = 0/0/0`,
fresh frontier lock, legal narrow diff, and explicit submit decision. A packet
alone is `Prefilter` evidence.

## Kill Gates

Park the packet immediately if:

- allocator order changes;
- proof status is `UNKNOWN` or `COUNTEREXAMPLE`;
- stale dead-gate indexes are involved;
- the claim needs private data to understand;
- validation shows classical, phase, or ancilla dirt;
- the route starts asking for compute before proof.
