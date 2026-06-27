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

For public `site_audit` TSVs that contain only source locations and weights,
normalize the TSV and opt into source-site backlog packets:

```bash
python3 scripts/storm-exact-miner.py trace-facts \
  --input examples/site-audit.example.tsv \
  --frontier 1571592960/d44cad3 \
  --source-base d44cad3 \
  --stream-hash d44-site-audit-example \
  --out /tmp/storm-site-facts.jsonl

python3 scripts/storm-exact-miner.py mine \
  --facts /tmp/storm-site-facts.jsonl \
  --include-unknown-sites \
  --max-unknown-sites 200 \
  --out /tmp/storm-site-candidates.jsonl
```

These packets are rankable proof targets only. They do not certify an omission.
Known generic-live source families are tagged with `primitive_family`,
`support_domain`, `falsifier_template`, and `witness`, then proven as
`COUNTEREXAMPLE` so they cannot be confused with candidate work. Unclassified
source sites remain `UNKNOWN` and must receive a real source invariant before
any circuit edit, residual, compute, alert, or submit step.

When a fact stream preserves `TRACE_OP_SITES` context values, the miner decodes
Gidney-family contexts into `trace_context_family`, `trace_context_call`, and
`trace_context_bit`. This keeps q1152 binder rows from the threaded/hybrid
adder and HMR erase paths separate in the NACK ledger, and lets the support
checker close generic-live carry/sum/phase rows without hardcoding every
callsite.

The same context decoding covers generic-live GCD shift/cswap rows, comparator
carry rows, constant-chunk carries, and fused-fold carries. Those rows are
closed as source counterexamples unless a later packet supplies a route-specific
public support certificate; decoded context is identity/provenance, not a clean
skip proof.

For proof-routing runs, insert the support checker and ledger:

```bash
python3 scripts/storm-exact-miner.py support-check \
  --facts /tmp/storm-site-facts.jsonl \
  --out /tmp/storm-site-supported.jsonl

python3 scripts/storm-exact-miner.py mine \
  --facts /tmp/storm-site-supported.jsonl \
  --include-unknown-sites \
  --out /tmp/storm-site-candidates.jsonl

python3 scripts/storm-exact-miner.py prove \
  --candidates /tmp/storm-site-candidates.jsonl \
  --out /tmp/storm-site-proofs.jsonl

python3 scripts/storm-exact-miner.py falsify \
  --packets /tmp/storm-site-proofs.jsonl \
  --ledger examples/nack-ledger.example.jsonl \
  --out /tmp/storm-site-falsified.jsonl

python3 scripts/storm-exact-miner.py ledger \
  --packets /tmp/storm-site-falsified.jsonl \
  --out /tmp/storm-nack-ledger.jsonl
```

`falsify --ledger` reads an existing NACK ledger and applies those entries to
the packet stream. To write a new ledger, run the separate `ledger` command.

`support-check` is intentionally conservative. It can mark known source
counterexamples, exact-remainder checks, and externally certified support facts;
dirty-host rows remain `UNKNOWN` unless `restore_proof=1`, `phase_proof=1`, and
a source-hash-bound public support certificate are all present. Restoration or
phase obligation text alone is not a proof.

## Packet Fields

Each packet records:

- route id, frontier, source base, stream hash, and source location;
- optional public source hash for source-snippet or proof-input identity;
- op class and executed weight;
- primitive family, support domain, falsifier template, and witness when known;
- proof method, support status, support note, support hash, and witness hash;
- decoded trace context family, call, and bit when available;
- allocator unchanged flag;
- proof kind and proof status;
- expected average-Toffoli delta;
- Redsky evidence label;
- validation target and kill gate.

The output schema is represented by
`templates/exact-skip-candidate.json`.

## Proof Discipline

The v1 miner can certify or reject only simple public-safe obligations:

- a source-hash-bound external public certificate was supplied with the trace
  fact;
- a built-in exact-remainder range check proves `value_max < modulus`.
- a source-site classifier supplies a generic-live counterexample witness.
- a dirty-host route supplies `restore_proof=1`, `phase_proof=1`, and a
  source-hash-bound public certificate.

Bare input statuses are not proof. `CERTIFIED` requires a public
`support_certificate` bound to `source_hash`, or a built-in proof such as an
exact-remainder range check; `COUNTEREXAMPLE` requires both a falsifier
template and witness. An external counterexample witness does not need a named
`primitive_family`; the ledger key will use the source location, optional
source hash, trace context, and trace span when the family is blank.
For `primitive_family=dirty_host`, a bound certificate still remains
`UNKNOWN` until the row also carries truthy `restore_proof` and `phase_proof`
fields.

Everything else is emitted as `UNKNOWN`. `UNKNOWN` packets are useful backlog,
but they do not authorize compute, circuit edits, win language, alerting, or
submit work.

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
