# Route Attempt

## Decision

Choose one:

- route_attempt
- worker_attempt
- hard_nack

## Context

- Route ID:
- Owner:
- Source/base:
- Current target:
- Evidence label:

## If Route Attempt

- Exact change or proof target:
- Expected edge:
- Required proof:
- Cheap validator:
- Full validator:
- Stop condition:

## If Worker Attempt

- Task:
- Shard/range policy:
- Machine class:
- Budget gate:
- Output artifact:
- Stop condition:

## If Hard NACK

- Closure reason:
- Evidence:
- Ledger row to close:
- Next route family:

## Safety

- Policy gates:
- Secrets excluded:
- no_submit_ack=yes
