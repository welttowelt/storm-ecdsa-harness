#!/usr/bin/env python3
"""Gate official candidate validation packets before FOR-AKASH language.

This parser is public-safe. It reads redacted validation summaries only; it
does not run build_circuit, eval_circuit, benchmark, alerts, or submit.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys
from typing import Iterable


BUILD_RE = re.compile(r"\bbuild_circuit\b", re.IGNORECASE)
EVAL_RE = re.compile(r"\beval_circuit\b", re.IGNORECASE)
OFFICIAL_RE = re.compile(r"\b(?:official|trusted|local full run|ecdsafail run)\b", re.IGNORECASE)
NO_SUBMIT_RE = re.compile(r"\bno_submit_ack\s*=\s*yes\b", re.IGNORECASE)
REMOTE_HOST_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:studio|runpod|vast|pod|remote)\b|\b(?:runpod:|vast:|studio|owned pod|owned-pod)\b", re.IGNORECASE)
LOCAL_HOST_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:mac|macbook|local|darwin)\b|\b(?:MacBook|mac-local|/Users/[A-Za-z0-9_.-]+)\b", re.IGNORECASE)
OWNER_RE = re.compile(r"\b(?:owner|validator|agent)\s*[=:]\s*[A-Za-z0-9_.-]+|\bACK\s+[A-Za-z0-9_.-]+\b", re.IGNORECASE)
ARTIFACT_RE = re.compile(r"\b(?:artifact|artifacts|preserve|preserved|score\.json|ops\.bin|results\.tsv|report\.md)\b", re.IGNORECASE)
FRONTIER_RE = re.compile(r"\bfrontier(?:_score| score)?\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
SOURCE_RE = re.compile(r"\b(?:source|source_base|source commit|base)\s*[=:]\s*([0-9a-f]{6,40})\b", re.IGNORECASE)
OPS_RE = re.compile(r"\b(?:emitted|loaded)[_-]?\s*ops\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
Q_RE = re.compile(r"\b(?:q|qubits?)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
SCORE_RE = re.compile(r"\b(?:candidate_)?score\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
AVG_RE = re.compile(r"\b(?:avg(?:_executed)?(?:_tof|_toffoli)?|average toffoli|avgT)\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
CLEAN_LINE_RE = re.compile(
    r"\bc\s*[=:]\s*([0-9]+)\b.*\bp\s*[=:]\s*([0-9]+)\b.*\ba\s*[=:]\s*([0-9]+)\b",
    re.IGNORECASE,
)
EVAL_BLOCK_RE = re.compile(
    r"\bclassical\s+mismatches\s*:\s*([0-9]+)\b.*?"
    r"\bphase-garbage\s+batches\s*:\s*([0-9]+)\b.*?"
    r"\bancilla-garbage\s+batches\s*:\s*([0-9]+)\b",
    re.IGNORECASE | re.DOTALL,
)
PREMATURE_RE = re.compile(
    r"\b(?:FOR[- ]AKASH|WINNER|mobile alert|ready[- ]to[- ]submit|Akash-ready)\b|"
    r"\bsubmit\s+(?:now|candidate|ready|decision|this)\b",
    re.IGNORECASE,
)


def read_text(paths: Iterable[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths)


def parse_number(pattern: re.Pattern[str], text: str) -> float | None:
    match = pattern.search(text)
    if not match:
        return None
    return float(match.group(1).replace("_", ""))


def parse_int(pattern: re.Pattern[str], text: str) -> int | None:
    value = parse_number(pattern, text)
    if value is None:
        return None
    return int(value)


def parse_counts(text: str) -> tuple[int, int, int] | None:
    match = CLEAN_LINE_RE.search(text)
    if match:
        return tuple(int(match.group(i)) for i in range(1, 4))  # type: ignore[return-value]
    match = EVAL_BLOCK_RE.search(text)
    if match:
        return tuple(int(match.group(i)) for i in range(1, 4))  # type: ignore[return-value]
    return None


def inspect(text: str, frontier_score: float, max_qubits: int, expected_ops: int, expected_source: str) -> dict[str, object]:
    frontier_in_packet = parse_number(FRONTIER_RE, text)
    effective_frontier = frontier_in_packet if frontier_in_packet is not None else frontier_score
    source_match = SOURCE_RE.search(text)
    source_base = source_match.group(1) if source_match else ""
    ops = parse_int(OPS_RE, text)
    qubits = parse_int(Q_RE, text)
    score = parse_number(SCORE_RE, text)
    avg = parse_number(AVG_RE, text)
    counts = parse_counts(text)
    computed_score = None
    if score is None and avg is not None and qubits is not None:
        computed_score = float(math.floor(avg + 0.5) * qubits)
        score = computed_score

    has_official_path = bool((BUILD_RE.search(text) and EVAL_RE.search(text)) or OFFICIAL_RE.search(text))
    has_remote_host = bool(REMOTE_HOST_RE.search(text))
    has_local_host = bool(LOCAL_HOST_RE.search(text))
    has_owner = bool(OWNER_RE.search(text))
    has_artifact = bool(ARTIFACT_RE.search(text))
    has_no_submit = bool(NO_SUBMIT_RE.search(text))
    has_source = bool(source_base)
    has_premature_language = bool(PREMATURE_RE.search(text))

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []

    if has_local_host:
        failures.append("local_validation_packet")
    if has_premature_language:
        failures.append("premature_alert_or_submit_language")
    if not has_remote_host:
        holds.append("missing_remote_host")
    if not has_owner:
        holds.append("missing_owner_or_validator")
    if not has_official_path:
        holds.append("missing_official_validation_path")
    if not has_no_submit:
        failures.append("missing_no_submit_ack")
    if frontier_in_packet is None:
        holds.append("missing_frontier_score")
    if not has_source:
        holds.append("missing_source_base")
    if expected_source and source_base and source_base != expected_source:
        failures.append("stale_source_base")
    if expected_ops > 0 and ops is None:
        holds.append("missing_ops")
    elif expected_ops > 0 and ops != expected_ops:
        failures.append("ops_mismatch")
    if counts is None:
        holds.append("missing_cpa_counts")
    elif counts != (0, 0, 0):
        failures.append("dirty_cpa_counts")
    if qubits is None:
        holds.append("missing_qubits")
    elif qubits > max_qubits:
        failures.append("qubits_exceed_max")
    if score is None:
        holds.append("missing_score")
    elif score >= effective_frontier:
        failures.append("score_no_edge")
    if not has_artifact:
        holds.append("missing_artifact_evidence")

    if failures:
        gate = "fail"
        decision = "not-candidate"
    elif holds:
        gate = "hold"
        decision = "complete-validation-packet"
    else:
        gate = "pass"
        decision = "candidate-for-akash-handoff-no-submit"

    return {
        "gate": gate,
        "decision": decision,
        "frontier_score": effective_frontier,
        "source_base": source_base,
        "expected_source": expected_source,
        "ops": ops,
        "expected_ops": expected_ops,
        "qubits": qubits,
        "max_qubits": max_qubits,
        "score": score,
        "computed_score": computed_score,
        "counts": counts,
        "official_path": has_official_path,
        "remote_host": has_remote_host,
        "local_host": has_local_host,
        "owner": has_owner,
        "artifact": has_artifact,
        "no_submit_ack": has_no_submit,
        "failures": failures,
        "holds": holds,
        "warnings": warnings,
    }


def text_summary(row: dict[str, object]) -> str:
    failures = ",".join(row["failures"]) if row["failures"] else "none"
    holds = ",".join(row["holds"]) if row["holds"] else "none"
    warnings = ",".join(row["warnings"]) if row["warnings"] else "none"
    counts = row["counts"] if row["counts"] is not None else "missing"
    return (
        f"candidate_validation_packet_gate={row['gate']} "
        f"official_path={str(row['official_path']).lower()} remote_host={str(row['remote_host']).lower()} "
        f"local_host={str(row['local_host']).lower()} owner={str(row['owner']).lower()} "
        f"artifact={str(row['artifact']).lower()} no_submit_ack={str(row['no_submit_ack']).lower()} "
        f"source_base={row['source_base'] or 'missing'} expected_source={row['expected_source'] or 'none'} "
        f"ops={row['ops']} expected_ops={row['expected_ops']} qubits={row['qubits']} "
        f"max_qubits={row['max_qubits']} score={row['score']} frontier_score={row['frontier_score']} "
        f"counts={counts} decision={row['decision']} failures={failures} holds={holds} warnings={warnings}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--frontier-score", type=float, default=1571592960.0)
    parser.add_argument("--max-qubits", type=int, default=1152)
    parser.add_argument("--expected-ops", type=int, default=10221059)
    parser.add_argument("--expected-source", default="d44cad3")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    missing = [str(path) for path in args.inputs if not path.is_file()]
    if missing:
        print(f"candidate_validation_packet_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
        return 2

    row = inspect(read_text(args.inputs), args.frontier_score, args.max_qubits, args.expected_ops, args.expected_source)
    if args.json:
        print(json.dumps(row, sort_keys=True))
    else:
        print(text_summary(row))

    if row["gate"] == "fail":
        return 1
    if args.require_pass and row["gate"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
