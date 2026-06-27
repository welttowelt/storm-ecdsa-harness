# Skill: Exact Support Miner

Use when a worker needs reusable, public-safe value-exact skip packets for
`ecdsa.fail` frontier work. This skill routes the worker through
`scripts/storm-exact-miner.py` and blocks compute until proof evidence exists.

## Trigger

Use this card when:

- extending `TLM_*` exact-dead or exact-remainder skips;
- converting trace facts into route packets;
- ranking fixed-allocation average-Toffoli omissions;
- deciding whether a candidate is ready for proof, patch, or validation.

## Public Boundary

Do not feed the miner private mailbox exports, raw logs, endpoints, keys,
account data, live candidate diffs, private paths, or unreleased nonce values.
Use fixture or public trace facts only.

## Protocol

1. Refresh the public frontier and name the source base.
2. Normalize trace facts:
   `python3 scripts/storm-exact-miner.py trace-facts --input <public.jsonl> --out <facts.jsonl>`.
   If the input is a raw source-site TSV, provide `--frontier`,
   `--source-base`, and `--stream-hash` defaults.
3. Run support checking when facts include source-site rows:
   `python3 scripts/storm-exact-miner.py support-check --facts <facts.jsonl> --out <supported.jsonl>`.
   This marks known generic-live rows as counterexamples and keeps dirty-host
   rows unknown unless restoration, phase, and public certificate fields exist.
4. Mine candidates:
   `python3 scripts/storm-exact-miner.py mine --facts <supported-or-facts.jsonl> --out <candidates.jsonl>`.
   For source-site TSVs without proof annotations, add
   `--include-unknown-sites --max-unknown-sites <n>` to emit rankable UNKNOWN
   proof backlog packets. The miner tags known generic-live source rows with
   `primitive_family`, `falsifier_template`, and `witness`, then marks them
   `COUNTEREXAMPLE` during `prove`; only unclassified rows remain UNKNOWN.
5. Build proof packets:
   `python3 scripts/storm-exact-miner.py prove --candidates <candidates.jsonl> --out <proofs.jsonl>`.
6. Apply falsifiers and optional NACK ledger:
   `python3 scripts/storm-exact-miner.py falsify --packets <proofs.jsonl> --out <falsified.jsonl>`.
7. Emit reusable public NACK entries:
   `python3 scripts/storm-exact-miner.py ledger --packets <falsified.jsonl> --out <ledger.jsonl>`.
8. Rank packets:
   `python3 scripts/storm-exact-miner.py rank --proofs <falsified-or-proofs.jsonl> --out <ranked.jsonl>`.
9. Apply Redsky review before any patch: strongest objection, fastest falsifier,
   dirty classes, expected score movement, validation target, and kill gate.

## Output

Report:

```text
Exact support miner:
- Frontier/source:
- Facts:
- Candidates:
- Certified:
- Unknown:
- Counterexample:
- Top packet:
- Fastest falsifier:
- Next gate:
```

## Completion Gate

A mined packet is `Prefilter` evidence. It becomes actionable only after proof
status is `CERTIFIED`, allocator order is unchanged, and a trusted validation
plan is named. No compute, submit, mobile alert, or win language follows from
the miner alone.

## Source-Site Classifier

Raw source-site weights are not proof. Before promoting a source-site packet,
require one of:

- a public support certificate proving a control is fixed or a target is dead;
- an exact-remainder certificate;
- a source counterexample witness that closes the row as generic-live.

If the miner emits `COUNTEREXAMPLE`, record the NACK and move on. If it emits
`UNKNOWN`, the next worker must supply a bounded invariant or falsifier before
the row reaches residual validation.
