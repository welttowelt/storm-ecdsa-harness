#!/usr/bin/env python3
"""Gate q1152 fanout GPU survivors against official phase-aware eval evidence.

The fanout CUDA predicate is a high-volume prefilter. It can produce survivor
nonces that later fail trusted replay through classical mismatch, phase
garbage, or ancilla garbage. This script turns mixed GPU and eval logs into a
single admission decision so fleet workers do not promote prefilter survivors
as clean candidates.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import sys
from typing import Iterable


NONCE_RE = re.compile(r"\bnonce\s*[=:]\s*(?:nonce\s*[=:]\s*)?(\d+)\b", re.IGNORECASE)
GPU_SURVIVOR_RE = re.compile(
    r"\bSTORM_RUNPOD_GPU_CLEAN_PREFILTER\b|"
    r"\b(?:gpu|prefilter|stage-1|cuda)[A-Za-z0-9_-]*.*\b(?:clean|survivor)\b|"
    r"^\s*CLEAN\s+nonce\s*=",
    re.IGNORECASE,
)
OFFICIAL_HINT_RE = re.compile(
    r"\b(?:official|trusted|eval|validation|build_circuit|eval_circuit|classical|phase|ancilla|BEST)\b",
    re.IGNORECASE,
)
COUNT_PATTERNS = (
    (
        re.compile(
            r"\bclassical(?:_mismatches)?\s*[=:]\s*(\d+)\b.*"
            r"\bphase(?:_garbage_batches)?\s*[=:]\s*(\d+)\b.*"
            r"\bancilla(?:_garbage_batches)?\s*[=:]\s*(\d+)\b",
            re.IGNORECASE,
        ),
        ("classical", "phase", "ancilla"),
    ),
    (
        re.compile(
            r"\bc\s*[=:]\s*(\d+)\b.*\bp\s*[=:]\s*(\d+)\b.*\ba\s*[=:]\s*(\d+)\b",
            re.IGNORECASE,
        ),
        ("classical", "phase", "ancilla"),
    ),
)
EVAL_BLOCK_RE = re.compile(
    r"\bclassical\s+mismatches\s*:\s*(\d+)\b.*?"
    r"\bphase-garbage\s+batches\s*:\s*(\d+)\b.*?"
    r"\bancilla-garbage\s+batches\s*:\s*(\d+)\b",
    re.IGNORECASE | re.DOTALL,
)


@dataclass
class NonceRecord:
    nonce: str
    gpu_survivor: bool = False
    official_seen: bool = False
    classical: int | None = None
    phase: int | None = None
    ancilla: int | None = None
    lines: list[str] = field(default_factory=list)

    @property
    def has_counts(self) -> bool:
        return self.classical is not None and self.phase is not None and self.ancilla is not None

    @property
    def clean(self) -> bool:
        return self.has_counts and self.classical == 0 and self.phase == 0 and self.ancilla == 0

    @property
    def dirty(self) -> bool:
        return self.has_counts and not self.clean

    @property
    def missing_official(self) -> bool:
        return self.gpu_survivor and not self.has_counts

    @property
    def dirty_class(self) -> str:
        classes: list[str] = []
        if (self.classical or 0) > 0:
            classes.append("classical")
        if (self.phase or 0) > 0:
            classes.append("phase")
        if (self.ancilla or 0) > 0:
            classes.append("ancilla")
        return "+".join(classes) if classes else "none"


def parse_counts(line: str) -> tuple[int, int, int] | None:
    for pattern, _names in COUNT_PATTERNS:
        match = pattern.search(line)
        if match:
            return tuple(int(match.group(i)) for i in range(1, 4))  # type: ignore[return-value]
    return None


def iter_lines(paths: Iterable[Path]) -> Iterable[tuple[str, str]]:
    for path in paths:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            for lineno, line in enumerate(fh, 1):
                yield f"{path}:{lineno}", line.rstrip("\n")


def update_official_counts(record: NonceRecord, counts: tuple[int, int, int]) -> None:
    record.official_seen = True
    record.classical, record.phase, record.ancilla = counts


def parse(
    paths: Iterable[Path],
    default_nonce: str | None = None,
    mark_default_survivor: bool = False,
) -> dict[str, NonceRecord]:
    records: dict[str, NonceRecord] = {}
    path_list = list(paths)
    if default_nonce and mark_default_survivor:
        records.setdefault(default_nonce, NonceRecord(nonce=default_nonce)).gpu_survivor = True
    for source, line in iter_lines(path_list):
        nonce_match = NONCE_RE.search(line)
        if not nonce_match:
            continue
        nonce = nonce_match.group(1)
        record = records.setdefault(nonce, NonceRecord(nonce=nonce))
        record.lines.append(source)
        if GPU_SURVIVOR_RE.search(line):
            record.gpu_survivor = True
        counts = parse_counts(line)
        if counts and OFFICIAL_HINT_RE.search(line):
            update_official_counts(record, counts)
    if default_nonce:
        record = records.setdefault(default_nonce, NonceRecord(nonce=default_nonce))
        for path in path_list:
            text = path.read_text(encoding="utf-8", errors="replace")
            match = EVAL_BLOCK_RE.search(text)
            if match:
                record.lines.append(str(path))
                counts = tuple(int(match.group(i)) for i in range(1, 4))
                update_official_counts(record, counts)  # type: ignore[arg-type]
    return records


def summarize(records: dict[str, NonceRecord]) -> dict[str, object]:
    rows = list(records.values())
    gpu = [row for row in rows if row.gpu_survivor]
    official = [row for row in rows if row.has_counts]
    clean = [row for row in official if row.clean]
    dirty = [row for row in official if row.dirty]
    missing = [row for row in gpu if row.missing_official]
    phase_dirty = [row for row in dirty if (row.phase or 0) > 0]
    classical_dirty = [row for row in dirty if (row.classical or 0) > 0]
    ancilla_dirty = [row for row in dirty if (row.ancilla or 0) > 0]

    if clean:
        decision = "ready_for_fresh_frontier_recheck"
        gate = "ready"
    elif missing:
        decision = "hold_for_official_eval"
        gate = "hold"
    elif dirty:
        decision = "nack_prefilter_survivors"
        gate = "nack"
    else:
        decision = "no_survivor_evidence"
        gate = "fail"

    return {
        "gate": gate,
        "decision": decision,
        "nonces_seen": len(rows),
        "gpu_survivors": len(gpu),
        "official_evals": len(official),
        "official_clean": len(clean),
        "official_dirty": len(dirty),
        "missing_official": len(missing),
        "phase_dirty": len(phase_dirty),
        "classical_dirty": len(classical_dirty),
        "ancilla_dirty": len(ancilla_dirty),
        "phase_gap": bool(phase_dirty),
        "records": [
            {
                "nonce": row.nonce,
                "gpu_survivor": row.gpu_survivor,
                "official_seen": row.official_seen,
                "classical": row.classical,
                "phase": row.phase,
                "ancilla": row.ancilla,
                "dirty_class": row.dirty_class,
                "line_count": len(row.lines),
            }
            for row in sorted(rows, key=lambda item: int(item.nonce))
        ],
    }


def text_summary(summary: dict[str, object]) -> str:
    keys = [
        "gpu_survivors",
        "official_evals",
        "official_clean",
        "official_dirty",
        "missing_official",
        "phase_dirty",
        "classical_dirty",
        "ancilla_dirty",
    ]
    fields = " ".join(f"{key}={summary[key]}" for key in keys)
    return (
        f"fanout_survivor_phase_gate={summary['gate']} {fields} "
        f"phase_gap={str(summary['phase_gap']).lower()} decision={summary['decision']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path, help="GPU and official eval logs to parse")
    parser.add_argument(
        "--nonce",
        help="attach raw eval_circuit logs without nonce text to this nonce",
    )
    parser.add_argument(
        "--mark-survivor",
        action="store_true",
        help="with --nonce, mark that nonce as a GPU/stage-1 survivor",
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="exit non-zero unless an official 0/0/0 record is present",
    )
    args = parser.parse_args()

    missing_paths = [str(path) for path in args.logs if not path.is_file()]
    if missing_paths:
        print(f"fanout_survivor_phase_gate=fail missing_logs={','.join(missing_paths)}", file=sys.stderr)
        return 2

    if args.mark_survivor and not args.nonce:
        print("fanout_survivor_phase_gate=fail mark_survivor_requires_nonce", file=sys.stderr)
        return 2

    summary = summarize(parse(args.logs, default_nonce=args.nonce, mark_default_survivor=args.mark_survivor))
    if args.json:
        print(json.dumps(summary, sort_keys=True))
    else:
        print(text_summary(summary))

    if summary["gate"] == "fail":
        return 2
    if args.require_ready and summary["gate"] != "ready":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
