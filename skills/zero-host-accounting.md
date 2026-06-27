# Skill: Zero Host Accounting

Use when a q1152 ECDSA.fail route proposes to borrow, reuse, co-locate, or
relabel a known-zero host at a peak-pressure carry, COUT, comparator, fold, or
Gidney wall.

## Core Lesson

At the current Trailmix source shape, a free or loaned `|0>` qubit is not
active headroom. The allocator removes it from `active_qubits`; using it again
through `alloc_qubit` or `reacquire` adds it back. That means a free zero host
does not let a peak-pressure COUT or carry create an extra live resource while
remaining at q1152.

The only reopen condition is a qid-level row proving a counted-active host that
is all of these at the protected borrow interval:

- known zero
- idle for the full borrow window
- disjoint from operands and owner reads/writes
- zero active-count delta when borrowed
- validated for value, phase, and ancilla cleanliness

Without that row, treat the route as a source-accounting NACK, not a count
candidate.

## Required Packet

```text
host_family:
counted_active:
known_zero:
idle:
owner_touches_during_borrow:
disjoint_from_operands:
delta_active:
source_file/function:
borrow_window:
result: NO_THROTTLE_RELIEF / HARD_NACK_ALIAS / NO_HOST / NEEDS_QID_TRACE
```

## Software Gate

Run:

```bash
python3 scripts/storm-zero-host-accounting-gate.py \
  --point-add-rs <challenge>/src/point_add/mod.rs \
  --trailmix-mod-rs <challenge>/src/point_add/trailmix_ludicrous/mod.rs \
  --gidney-rs <challenge>/src/point_add/trailmix_ludicrous/gidney.rs \
  --host-families <host-family-summary.tsv>
```

The gate checks:

- `alloc_qubit` increments `active_qubits` before free-pool reuse.
- `free` and `loan_zero_qubit` push into `free_qubits` and decrement active
  accounting.
- `reacquire` removes from `free_qubits` and increments active accounting.
- `target_qubit_headroom` is `TLM_TARGET_Q - active_qubits`.
- COUT effective budget is clamped by that headroom.

## Output

```text
zero host accounting:
- Frontier/source:
- Borrow route:
- Source facts:
- Host families checked:
- Reopen condition:
- Decision: source-accounting-nack / needs-qid-trace / source-facts-missing
```

## Kill Gate

Do not count, run residuals, dispatch compute, or edit source behavior for a
zero-host borrowing route when:

- the host is in the free pool or was loaned to the free pool;
- the host is the carry resource being created;
- the host is live data or not proven zero;
- the owner touches it during the borrow window;
- operand disjointness is missing or false;
- using the host increases active count.

Only a counted-active, idle, known-zero, disjoint qid row with zero active delta
can advance to validation.
