#!/usr/bin/env python3
"""Gate FFG lifetime/cy0 rotation reports before residual or compute.

This parser is public-safe. It reads redacted markdown or stdout packets from
FFG lifetime proof loops and blocks promotion unless the packet has a clean
route compare, enough shots, a positive score edge, useful FFG evidence, and
no-submit discipline.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys
from typing import Iterable


NO_SUBMIT_RE = re.compile(r"\bno_submit_ack\s*=\s*yes\b", re.IGNORECASE)
ROUTE_ID_RE = re.compile(r"\broute_id\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
OWNER_RE = re.compile(r"\b(?:owner|agent|validator)\s*[=:]\s*([A-Za-z0-9_.-]+)\b|\bACK\s+([A-Za-z0-9_.-]+)\b", re.IGNORECASE)
NEXT_RE = re.compile(r"\bnext\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
SOURCE_BASE_RE = re.compile(r"\b(?:source_base|source|base|source commit)\s*[=:]\s*([0-9a-f]{6,40})\b", re.IGNORECASE)
SOURCE_HASH_RE = re.compile(r"\b(?:source_hash|source-hash|source_snippet_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b", re.IGNORECASE)
CANDIDATE_HASH_RE = re.compile(
    r"\b(?:candidate_index_hash|candidate_diff_hash|candidate_hash|diff_hash|index_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b",
    re.IGNORECASE,
)
FRONTIER_SCORE_RE = re.compile(r"\bfrontier(?:_score| score)?\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
EVIDENCE_LABEL_RE = re.compile(r"\bevidence_label\s*[=:]\s*(Prefilter|Partial|Local full run|Promoted)\b", re.IGNORECASE)
PROBE_KIND_RE = re.compile(r"\bProbe kind:\s*`?([A-Za-z0-9_.:-]+)`?|\bprobe_kind\s*[=:]\s*([A-Za-z0-9_.:-]+)\b", re.IGNORECASE)
CALL_RE = re.compile(r"\bCall:\s*`?([0-9]+)`?|\bcall\s*[=:]\s*([0-9]+)\b", re.IGNORECASE)
CAND_ENV_RE = re.compile(r"\b(?:Candidate env|candidate_env)\s*[:=]\s*`?([A-Za-z0-9_,=:+.-]+)`?", re.IGNORECASE)
CARRY_DECISION_RE = re.compile(r"\bsummary\s+decision\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE)
SUMMARY_RE = re.compile(r"^(BASE|CAND|COMPARE)_SUMMARY\s+(.*)$", re.MULTILINE)
KV_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)")
COUNT_RE = re.compile(
    r"\bn_ops\s*[=:]\s*([0-9][0-9_]*)\s+CCX\s*[=:]\s*([0-9][0-9_]*)\s+CCZ\s*[=:]\s*([0-9][0-9_]*)\s+PEAK_QUBITS\s*[=:]\s*([0-9][0-9_]*)\s+bits\s*[=:]\s*([0-9][0-9_]*)\b",
    re.IGNORECASE,
)
FFG_CONTEXT_RE = re.compile(r"\b(?:FFG|TLM_FFG|cy0_park|suffix_width|ffg_lifetime|lifetime proof)\b", re.IGNORECASE)
SPLIT_PASS_RE = re.compile(r"\bFFG_SPLIT_EQUIV:\s*PASS\b", re.IGNORECASE)
CY0_PASS_RE = re.compile(r"\bCY0_PARK_EQUIV:\s*PASS\b", re.IGNORECASE)
COMPUTE_REQUEST_RE = re.compile(
    r"\b(?:launch|start|restart|rearm|scale|dispatch)\b.{0,80}\b(?:pods?|runpod|vast|gpus?|cpus?|scanner|residual|benchmark|eval)\b|"
    r"\b(?:FOR[- ]AKASH|Akash-ready|WINNER|mobile alert|ready[- ]to[- ]submit|submit\s+now)\b",
    re.IGNORECASE,
)


def read_text(paths: Iterable[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths)


def first_match(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    if not match:
        return ""
    return next((group for group in match.groups() if group), "")


def first_float(pattern: re.Pattern[str], text: str) -> float | None:
    value = first_match(pattern, text)
    if not value:
        return None
    try:
        parsed = float(value.replace("_", ""))
    except ValueError:
        return None
    return parsed if math.isfinite(parsed) else None


def first_int(pattern: re.Pattern[str], text: str) -> int | None:
    value = first_match(pattern, text)
    if not value:
        return None
    try:
        return int(value.replace("_", ""), 0)
    except ValueError:
        return None


def parse_keyvals(text: str) -> dict[str, str]:
    return {match.group(1): match.group(2) for match in KV_RE.finditer(text)}


def parse_summaries(text: str) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for match in SUMMARY_RE.finditer(text):
        rows[match.group(1).lower()] = parse_keyvals(match.group(2))
    return rows


def parse_count(text: str) -> dict[str, int]:
    match = COUNT_RE.search(text)
    if not match:
        return {}
    keys = ("n_ops", "ccx", "ccz", "peak_qubits", "bits")
    return {key: int(value.replace("_", "")) for key, value in zip(keys, match.groups())}


def as_int(row: dict[str, str], key: str) -> int | None:
    value = row.get(key)
    if value is None:
        return None
    try:
        return int(value, 0)
    except ValueError:
        return None


def as_float(row: dict[str, str], key: str) -> float | None:
    value = row.get(key)
    if value is None:
        return None
    try:
        parsed = float(value)
    except ValueError:
        return None
    return parsed if math.isfinite(parsed) else None


def dirty_reasons(row: dict[str, str], prefix: str) -> list[str]:
    reasons = []
    for key, label in (
        ("classical", f"{prefix}_classical_dirty"),
        ("phase_batches", f"{prefix}_phase_dirty"),
        ("ancilla_batches", f"{prefix}_ancilla_dirty"),
    ):
        value = as_int(row, key)
        if value is None:
            reasons.append(f"{prefix}_{key}_missing")
        elif value != 0:
            reasons.append(label)
    return reasons


def compare_reasons(row: dict[str, str]) -> list[str]:
    reasons = []
    for key, label in (("output_diff", "compare_output_diff"), ("phase_diff_batches", "compare_phase_diff")):
        value = as_int(row, key)
        if value is None:
            reasons.append(f"compare_{key}_missing")
        elif value != 0:
            reasons.append(label)
    return reasons


def inspect(
    text: str,
    expected_source: str,
    frontier_score_arg: float,
    min_shots: int,
    baseline_ops: int,
    baseline_ccx: int,
    baseline_ccz: int,
) -> dict[str, object]:
    route_id = first_match(ROUTE_ID_RE, text)
    owner = first_match(OWNER_RE, text)
    next_action = first_match(NEXT_RE, text)
    source_base = first_match(SOURCE_BASE_RE, text)
    source_hash = first_match(SOURCE_HASH_RE, text)
    candidate_hash = first_match(CANDIDATE_HASH_RE, text)
    frontier_score = first_float(FRONTIER_SCORE_RE, text) or frontier_score_arg
    evidence_label = first_match(EVIDENCE_LABEL_RE, text)
    probe_kind = first_match(PROBE_KIND_RE, text)
    call = first_int(CALL_RE, text)
    candidate_env = first_match(CAND_ENV_RE, text)
    carry_decision = first_match(CARRY_DECISION_RE, text)
    summaries = parse_summaries(text)
    count = parse_count(text)

    has_no_submit = bool(NO_SUBMIT_RE.search(text))
    has_ffg_context = bool(FFG_CONTEXT_RE.search(text))
    has_split_pass = bool(SPLIT_PASS_RE.search(text))
    has_cy0_pass = bool(CY0_PASS_RE.search(text))
    has_compute_request = bool(COMPUTE_REQUEST_RE.search(text))

    base = summaries.get("base", {})
    cand = summaries.get("cand", {})
    compare = summaries.get("compare", {})
    base_shots = as_int(base, "shots")
    cand_shots = as_int(cand, "shots")
    compare_shots = as_int(compare, "shots")
    qubits = as_float(cand, "qubits")
    avg_tof = as_float(cand, "avg_tof")
    candidate_score = None
    if qubits is not None and avg_tof is not None:
        candidate_score = qubits * math.floor(avg_tof + 0.5)
    score_edge = None if candidate_score is None else frontier_score - candidate_score

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []

    if has_compute_request:
        failures.append("premature_compute_or_submit_language")
    if not has_no_submit:
        failures.append("missing_no_submit_ack")
    if expected_source and source_base and source_base != expected_source:
        failures.append("stale_source_base")
    if evidence_label.lower() in {"local full run", "promoted"}:
        failures.append("ffg_rotation_overclaims_result")
    if carry_decision == "carry-floor-local-support-no-constant-wire":
        failures.append("carry_floor_no_static_carry_cut")

    if base:
        failures.extend(dirty_reasons(base, "baseline"))
    else:
        holds.append("missing_base_summary")
    if cand:
        failures.extend(dirty_reasons(cand, "candidate"))
    else:
        holds.append("missing_candidate_summary")
    if compare:
        failures.extend(compare_reasons(compare))
    else:
        holds.append("missing_compare_summary")

    shot_values = [value for value in (base_shots, cand_shots, compare_shots) if value is not None]
    if len(set(shot_values)) > 1:
        failures.append("shot_mismatch")
    shots = cand_shots or 0
    if cand_shots is not None and cand_shots < min_shots:
        failures.append("route_compare_shots_below_min")
    if candidate_score is not None and candidate_score >= frontier_score:
        failures.append("score_no_edge")
    if baseline_ops and count.get("n_ops") is not None and count["n_ops"] >= baseline_ops:
        failures.append("ops_not_lower_than_baseline")
    if baseline_ccx and count.get("ccx") is not None and count["ccx"] >= baseline_ccx:
        failures.append("ccx_not_lower_than_baseline")
    if baseline_ccz and count.get("ccz") is not None and count["ccz"] > baseline_ccz:
        failures.append("ccz_worse_than_baseline")

    if not route_id:
        holds.append("missing_route_id")
    if not owner:
        holds.append("missing_owner")
    if not next_action:
        holds.append("missing_next_action")
    if not source_base:
        holds.append("missing_source_base")
    if not source_hash:
        holds.append("missing_source_hash")
    if not candidate_hash:
        holds.append("missing_candidate_hash")
    if not evidence_label:
        holds.append("missing_evidence_label")
    elif evidence_label.lower() not in {"prefilter", "partial"}:
        holds.append("evidence_label_not_prefilter_or_partial")
    if not has_ffg_context:
        holds.append("missing_ffg_context")
    if not probe_kind:
        holds.append("missing_probe_kind")
    if call is None:
        holds.append("missing_call")
    if not candidate_env:
        holds.append("missing_candidate_env")
    if not has_split_pass:
        holds.append("missing_split_qcin_toy_pass")
    if not has_cy0_pass:
        holds.append("missing_cy0_park_toy_pass")
    if not carry_decision:
        holds.append("missing_carry_floor_decision")
    if qubits is None:
        holds.append("missing_candidate_qubits")
    if avg_tof is None:
        holds.append("missing_candidate_avg_tof")
    if not count:
        holds.append("missing_count_tail")
    if baseline_ops and count and "n_ops" not in count:
        holds.append("missing_ops_count")
    if baseline_ccx and count and "ccx" not in count:
        holds.append("missing_ccx_count")
    if baseline_ccz and count and "ccz" not in count:
        holds.append("missing_ccz_count")
    if score_edge is None:
        holds.append("missing_score_edge")

    if avg_tof is not None and candidate_score is not None:
        warnings.append("candidate_score_computed_from_rounded_avg_tof")

    if failures:
        gate = "fail"
        decision = "do-not-promote-ffg-lifetime-rotation"
    elif holds:
        gate = "hold"
        decision = "complete-ffg-lifetime-rotation-packet"
    else:
        gate = "pass"
        decision = "ffg-lifetime-rotation-review-no-compute"

    return {
        "gate": gate,
        "decision": decision,
        "route_id": route_id,
        "owner": owner,
        "next_action": next_action,
        "source_base": source_base,
        "expected_source": expected_source,
        "source_hash": source_hash,
        "candidate_hash": candidate_hash,
        "frontier_score": frontier_score,
        "evidence_label": evidence_label,
        "probe_kind": probe_kind,
        "call": call,
        "candidate_env": candidate_env,
        "carry_decision": carry_decision,
        "split_qcin_pass": has_split_pass,
        "cy0_park_pass": has_cy0_pass,
        "ffg_context": has_ffg_context,
        "qubits": qubits,
        "avg_tof": avg_tof,
        "candidate_score": candidate_score,
        "score_edge": score_edge,
        "shots": shots,
        "min_shots": min_shots,
        "count": count,
        "baseline_ops": baseline_ops,
        "baseline_ccx": baseline_ccx,
        "baseline_ccz": baseline_ccz,
        "no_submit_ack": has_no_submit,
        "compute_request": has_compute_request,
        "failures": failures,
        "holds": holds,
        "warnings": warnings,
    }


def join(values: object) -> str:
    if not values:
        return "none"
    if isinstance(values, list):
        return ",".join(str(value) for value in values) if values else "none"
    if isinstance(values, dict):
        return ",".join(f"{key}:{value}" for key, value in sorted(values.items())) if values else "none"
    return str(values)


def text_summary(row: dict[str, object]) -> str:
    return (
        f"ffg_lifetime_rotation_gate={row['gate']} route_id={row['route_id'] or 'missing'} "
        f"owner={row['owner'] or 'missing'} next={row['next_action'] or 'missing'} "
        f"source_base={row['source_base'] or 'missing'} expected_source={row['expected_source'] or 'none'} "
        f"source_hash={row['source_hash'] or 'missing'} candidate_hash={row['candidate_hash'] or 'missing'} "
        f"frontier_score={row['frontier_score']} evidence_label={row['evidence_label'] or 'missing'} "
        f"probe_kind={row['probe_kind'] or 'missing'} call={row['call']} "
        f"candidate_env={row['candidate_env'] or 'missing'} carry_decision={row['carry_decision'] or 'missing'} "
        f"split_qcin_pass={str(row['split_qcin_pass']).lower()} cy0_park_pass={str(row['cy0_park_pass']).lower()} "
        f"ffg_context={str(row['ffg_context']).lower()} qubits={row['qubits']} avg_tof={row['avg_tof']} "
        f"candidate_score={row['candidate_score']} score_edge={row['score_edge']} "
        f"shots={row['shots']} min_shots={row['min_shots']} count={join(row['count'])} "
        f"baseline_ops={row['baseline_ops']} baseline_ccx={row['baseline_ccx']} baseline_ccz={row['baseline_ccz']} "
        f"no_submit_ack={str(row['no_submit_ack']).lower()} compute_request={str(row['compute_request']).lower()} "
        f"decision={row['decision']} failures={join(row['failures'])} holds={join(row['holds'])} "
        f"warnings={join(row['warnings'])}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--expected-source", default="d44cad3")
    parser.add_argument("--frontier-score", type=float, default=1571592960.0)
    parser.add_argument("--min-shots", type=int, default=9024)
    parser.add_argument("--baseline-ops", type=int, default=0)
    parser.add_argument("--baseline-ccx", type=int, default=0)
    parser.add_argument("--baseline-ccz", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    missing = [str(path) for path in args.inputs if not path.is_file()]
    if missing:
        print(f"ffg_lifetime_rotation_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
        return 2
    if args.frontier_score <= 0:
        raise SystemExit("--frontier-score must be positive")
    if args.min_shots < 0:
        raise SystemExit("--min-shots must be >= 0")

    row = inspect(
        read_text(args.inputs),
        args.expected_source,
        args.frontier_score,
        args.min_shots,
        args.baseline_ops,
        args.baseline_ccx,
        args.baseline_ccz,
    )
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
