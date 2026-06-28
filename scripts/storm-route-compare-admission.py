#!/usr/bin/env python3
"""Gate route-compare outputs before residual, compute, or submit.

This is an admission filter, not a simulator. It parses public
BASE/CAND/COMPARE summary lines and blocks promotion unless the baseline and
candidate are channel-clean, the comparison agrees, and the candidate has a
score edge against the supplied frontier score.
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import Any


SUMMARY_RE = re.compile(r"^(BASE|CAND|COMPARE)_SUMMARY\s+(.*)$")
KV_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)")


def parse_keyvals(text: str) -> dict[str, str]:
    return {match.group(1): match.group(2) for match in KV_RE.finditer(text)}


def load_summaries(path: Path) -> dict[str, dict[str, str]]:
    summaries: dict[str, dict[str, str]] = {}
    try:
        lines = path.read_text().splitlines()
    except FileNotFoundError as exc:
        raise SystemExit(f"input_not_found path={path}") from exc
    for line in lines:
        match = SUMMARY_RE.match(line.strip())
        if not match:
            continue
        summaries[match.group(1).lower()] = parse_keyvals(match.group(2))
    return summaries


def as_float(row: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except ValueError:
        return default


def as_int(row: dict[str, str], key: str, default: int = 0) -> int:
    try:
        return int(str(row.get(key, default)), 0)
    except ValueError:
        return default


def required_float(row: dict[str, str], key: str, prefix: str, reasons: list[str]) -> float | None:
    value = row.get(key)
    if value is None:
        reasons.append(f"{prefix}_{key}_missing")
        return None
    try:
        parsed = float(value)
    except ValueError:
        reasons.append(f"{prefix}_{key}_malformed")
        return None
    if not math.isfinite(parsed):
        reasons.append(f"{prefix}_{key}_malformed")
        return None
    return parsed


def required_int(row: dict[str, str], key: str, prefix: str, reasons: list[str]) -> int | None:
    value = row.get(key)
    if value is None:
        reasons.append(f"{prefix}_{key}_missing")
        return None
    try:
        return int(value, 0)
    except ValueError:
        reasons.append(f"{prefix}_{key}_malformed")
        return None


def summary_dirty_reasons(row: dict[str, str], prefix: str) -> list[str]:
    reasons = []
    for key, label in (
        ("classical", f"{prefix}_classical"),
        ("phase_batches", f"{prefix}_phase"),
        ("ancilla_batches", f"{prefix}_ancilla"),
    ):
        if as_int(row, key) != 0:
            reasons.append(label)
    return reasons


def compare_dirty_reasons(compare: dict[str, str]) -> list[str]:
    reasons = []
    if as_int(compare, "output_diff") != 0:
        reasons.append("compare_output_diff")
    if as_int(compare, "phase_diff_batches") != 0:
        reasons.append("compare_phase_diff")
    return reasons


def decide(summaries: dict[str, dict[str, str]], frontier_score: float, min_shots: int) -> dict[str, Any]:
    missing = [name for name in ("base", "cand", "compare") if name not in summaries]
    if missing:
        return {
            "gate": "hold",
            "admitted": 0,
            "baseline_clean": 0,
            "candidate_clean": 0,
            "compare_clean": 0,
            "score_edge": 0,
            "score": "nan",
            "raw_score": "nan",
            "avg_tof_rounded": 0,
            "decision": "missing-summary",
            "reasons": ",".join(f"missing_{name}" for name in missing),
            "shots": 0,
            "min_shots": min_shots,
        }

    base = summaries["base"]
    cand = summaries["cand"]
    compare = summaries["compare"]

    field_reasons: list[str] = []
    base_shots = required_int(base, "shots", "baseline", field_reasons)
    cand_shots = required_int(cand, "shots", "candidate", field_reasons)
    compare_shots = required_int(compare, "shots", "compare", field_reasons)
    q = required_float(cand, "qubits", "candidate", field_reasons)
    avg_tof = required_float(cand, "avg_tof", "candidate", field_reasons)
    for row, prefix in ((base, "baseline"), (cand, "candidate")):
        for key in ("classical", "phase_batches", "ancilla_batches"):
            required_int(row, key, prefix, field_reasons)
    for key in ("output_diff", "phase_diff_batches"):
        required_int(compare, key, "compare", field_reasons)

    base_reasons = summary_dirty_reasons(base, "baseline")
    cand_reasons = summary_dirty_reasons(cand, "candidate")
    compare_reasons = compare_dirty_reasons(compare)
    base_field_reasons = [reason for reason in field_reasons if reason.startswith("baseline_")]
    cand_field_reasons = [reason for reason in field_reasons if reason.startswith("candidate_")]
    compare_field_reasons = [reason for reason in field_reasons if reason.startswith("compare_")]
    score = 0.0
    raw_score = 0.0
    avg_tof_rounded = 0
    if q is not None and avg_tof is not None:
        avg_tof_rounded = math.floor(avg_tof + 0.5)
        score = q * avg_tof_rounded
        raw_score = q * avg_tof
    score_edge = bool(score and score < frontier_score)
    shot_values = [value for value in (base_shots, cand_shots, compare_shots) if value is not None]
    shot_mismatch = len(set(shot_values)) > 1
    shots = cand_shots or 0

    if field_reasons:
        gate = "hold"
        decision = "incomplete-summary-no-admission"
    elif q is not None and q <= 0:
        gate = "hold"
        decision = "invalid-score-input-no-admission"
        field_reasons.append("candidate_qubits_nonpositive")
    elif avg_tof is not None and avg_tof <= 0:
        gate = "hold"
        decision = "invalid-score-input-no-admission"
        field_reasons.append("candidate_avg_tof_nonpositive")
    elif shot_mismatch:
        gate = "fail"
        decision = "shot-mismatch-no-admission"
    elif base_reasons:
        gate = "fail"
        decision = "dirty-baseline-no-admission"
    elif cand_reasons:
        gate = "fail"
        decision = "dirty-candidate-no-admission"
    elif compare_reasons:
        gate = "fail"
        decision = "route-diff-no-admission"
    elif not score_edge:
        gate = "fail"
        decision = "score-no-edge"
    elif min_shots > 0 and shots < min_shots:
        gate = "hold"
        decision = "insufficient-shots-no-admission"
    else:
        gate = "pass"
        decision = "route-clean-score-edge"

    return {
        "gate": gate,
        "admitted": int(gate == "pass"),
        "baseline_clean": int(not base_reasons and not base_field_reasons),
        "candidate_clean": int(not cand_reasons and not cand_field_reasons),
        "compare_clean": int(not compare_reasons and not compare_field_reasons),
        "score_edge": int(score_edge),
        "score": score,
        "raw_score": raw_score,
        "avg_tof_rounded": avg_tof_rounded,
        "decision": decision,
        "reasons": ",".join(field_reasons + base_reasons + cand_reasons + compare_reasons) or "none",
        "qubits": q or 0,
        "avg_tof": avg_tof or 0,
        "shots": shots,
        "min_shots": min_shots,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--route-compare", type=Path, required=True, help="route_compare.out-style summary log")
    parser.add_argument("--frontier-score", type=float, required=True, help="public score to beat")
    parser.add_argument("--min-shots", type=int, default=9024, help="minimum matching BASE/CAND/COMPARE shots for admission")
    parser.add_argument("--require-admission", action="store_true", help="exit nonzero unless the gate admits the route")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summaries = load_summaries(args.route_compare)
    if args.frontier_score <= 0:
        raise SystemExit("--frontier-score must be positive")
    if args.min_shots < 0:
        raise SystemExit("--min-shots must be >= 0")
    result = decide(summaries, args.frontier_score, args.min_shots)
    score = result["score"]
    score_text = f"{score:.6f}" if isinstance(score, (int, float)) else str(score)
    raw_score = result["raw_score"]
    raw_score_text = f"{raw_score:.6f}" if isinstance(raw_score, (int, float)) else str(raw_score)
    print(
        f"route_compare_admission={result['gate']} "
        f"admitted={result['admitted']} "
        f"baseline_clean={result['baseline_clean']} "
        f"candidate_clean={result['candidate_clean']} "
        f"compare_clean={result['compare_clean']} "
        f"score_edge={result['score_edge']} "
        f"score={score_text} "
        f"raw_score={raw_score_text} "
        f"frontier_score={args.frontier_score:.6f} "
        f"qubits={result.get('qubits', 0):.0f} "
        f"avg_tof={result.get('avg_tof', 0):.6f} "
        f"avg_tof_rounded={result['avg_tof_rounded']} "
        f"shots={result['shots']} "
        f"min_shots={result['min_shots']} "
        f"decision={result['decision']} "
        f"reasons={result['reasons']}"
    )
    if args.require_admission and not result["admitted"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
