# Bluesky/Redsky Five-Loop Gate - 2026-06-28

Context: Storm coordination already had Bluesky and Redsky audit cards, but the
loop output was still easy to compress into prose. This patch makes the audit
cycle checkable before it steers workers, compute, or public claims.

## Loop 1 - Prose-Only Audit Packets

Bluesky proposal: preserve the useful optimism of Bluesky while making each
field parseable.

Redsky attack: a route can sound complete while omitting the missing
measurement, stop condition, or fastest falsifier.

Implementation:

- added `scripts/storm-bluesky-redsky-loop-gate.py`;
- added a public-safe five-loop JSON fixture;
- required the canonical Bluesky and Redsky fields for every loop.

Evidence:

```text
bluesky_redsky_loop_gate=pass ... loops=5
```

## Loop 2 - Evidence-Label Drift

Bluesky proposal: include evidence labels in each loop so readers can quickly
triage the strength of a claim.

Redsky attack: the top-level loop can say `Partial` while the Redsky section
implies something stronger.

Implementation:

- added allowed evidence labels;
- required Redsky evidence to match the loop evidence;
- printed evidence counts in the summary line.

Evidence:

```text
evidence=Partial:5
```

## Loop 3 - Finding Without Verification

Bluesky proposal: each audit finding should produce a small public artifact or
a deliberate park decision.

Redsky attack: a finding without an implementation and verification command can
hide broken tooling.

Implementation:

- added `implemented`, `artifact`, `implementation`, and `verification` checks;
- added `--require-implemented` for implementation-focused runs.

Evidence:

```text
implemented=5 verified=5
```

## Loop 4 - Loop Count Drift

Bluesky proposal: keep the exact number of requested loops visible.

Redsky attack: five requested loops can become three real loops plus a summary.

Implementation:

- default gate behavior requires exactly five loops;
- loop numbers must be sequential;
- `--exact-loops 0` remains available for exploratory audits.

Evidence:

```text
loops=5
```

## Loop 5 - Public Boundary

Bluesky proposal: store public-safe learnings in the repo without copying raw
coordination state.

Redsky attack: process packets can accidentally quote private paths, alert
topics, token prefixes, or private-key blocks.

Implementation:

- scanned every string in the packet for forbidden private-state patterns;
- kept the stronger repo-wide redaction check as a separate verification step.

Evidence:

```text
redaction-check=pass
```

## Decision

Proceed with this as a process-control gate only. A pass does not unlock pods,
Akash handoff, alerts, or submit language. It only proves that this five-loop
audit produced implemented, verified, public-safe process improvements.
