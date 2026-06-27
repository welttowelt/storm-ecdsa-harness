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
3. Mine candidates:
   `python3 scripts/storm-exact-miner.py mine --facts <facts.jsonl> --out <candidates.jsonl>`.
4. Build proof packets:
   `python3 scripts/storm-exact-miner.py prove --candidates <candidates.jsonl> --out <proofs.jsonl>`.
5. Rank packets:
   `python3 scripts/storm-exact-miner.py rank --proofs <proofs.jsonl> --out <ranked.jsonl>`.
6. Apply Redsky review before any patch: strongest objection, fastest falsifier,
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
- Top packet:
- Fastest falsifier:
- Next gate:
```

## Completion Gate

A mined packet is `Prefilter` evidence. It becomes actionable only after proof
status is `CERTIFIED`, allocator order is unchanged, and a trusted validation
plan is named. No compute, submit, mobile alert, or win language follows from
the miner alone.
