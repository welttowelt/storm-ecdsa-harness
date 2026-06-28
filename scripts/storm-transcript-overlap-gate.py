#!/usr/bin/env python3
"""Gate transcript peak-overlap drop packets before implementation or compute.

This public-safe parser checks redacted transcript/drop summaries. It does not
run miners, build/eval, SSH job control, alerts, or submit.
"""

from __future__ import annotations

import argparse
import json
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
SOURCE_BOUND_RE = re.compile(r"\b(?:source-hash-bound|source_bound\s*[=:]\s*yes|source_hash\s*[=:])\b", re.IGNORECASE)
FRONTIER_SCORE_RE = re.compile(r"\bfrontier(?:_score| score)?\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
QUBITS_RE = re.compile(r"\b(?:q|qubits?)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
TARGET_Q_RE = re.compile(r"\btarget_q\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
AVG_T_RE = re.compile(r"\b(?:candidate_avgT|candidate_avg_tof|avgT|avg_tof|avg_toffoli)\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
CANDIDATE_SCORE_RE = re.compile(r"\b(?:candidate_score|score)\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
SCORE_EDGE_RE = re.compile(r"\bscore_edge\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
DELTA_RE = re.compile(r"\b(?:expected_avgT_delta|expected_delta|delta)\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
EVIDENCE_LABEL_RE = re.compile(r"\bevidence_label\s*[=:]\s*(Prefilter|Partial|Local full run|Promoted)\b", re.IGNORECASE)
PEAK_ROWS_RE = re.compile(r"\b(?:peak_rows|peak_calls|peak_binders)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
OVERLAP_ROWS_RE = re.compile(r"\b(?:overlap_rows|transcript_overlap_rows|peak_overlap_rows)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
REQUIRED_CALLS_RE = re.compile(r"\brequired_calls\s*[=:]\s*([0-9_,+-]+)\b", re.IGNORECASE)
COVERED_CALLS_RE = re.compile(r"\bcovered_calls\s*[=:]\s*([0-9_,+-]+)\b", re.IGNORECASE)
STALE_WARNINGS_RE = re.compile(r"\b(?:stale_index_warnings|stale_indices|stale-index warnings)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
ORIGIN_ACTIVE_ONLY_RE = re.compile(r"\b(?:origin_map|origin|source_map)\s*[=:]\s*(?:active-only|active_only|activeonly)\b|\bactive-only origin\b", re.IGNORECASE)
TRANSCRIPT_RE = re.compile(r"\b(?:transcript[-_ ]peak[-_ ]overlap|peak[-_ ]overlap[-_ ]inventory|transcript_inventory|TRACE_TLM|TLM_OVERLAP)\b", re.IGNORECASE)
EXACT_SUPPORT_RE = re.compile(
    r"\b(?:exact_support|support_status|proof_status)\s*[=:]\s*CERTIFIED\b|"
    r"\bsource[-_ ]hash[-_ ]bound\b.{0,120}\b(?:exact support|CERTIFIED)\b",
    re.IGNORECASE | re.DOTALL,
)
SUPPORT_COUNTER_RE = re.compile(r"\b(?:support_status|proof_status|exact_support)\s*[=:]\s*COUNTEREXAMPLE\b", re.IGNORECASE)
SUPPORT_UNKNOWN_RE = re.compile(r"\b(?:support_status|proof_status|exact_support)\s*[=:]\s*(UNKNOWN|UNPROVEN)\b", re.IGNORECASE)
DIRTY_RE = re.compile(
    r"\b(?:dirty|rc\s*[=:]\s*1)\b|"
    r"\bdirty_(?:classical|phase(?:_shots)?|any_fail)\s*[=:]\s*[1-9][0-9]*\b|"
    r"\bc\s*[=:]\s*[1-9][0-9]*\b|\bp\s*[=:]\s*[1-9][0-9]*\b|\ba\s*[=:]\s*[1-9][0-9]*\b",
    re.IGNORECASE,
)
COMPUTE_REQUEST_RE = re.compile(
    r"\b(?:launch|start|restart|rearm|scale|dispatch|residual|benchmark|run)\b.{0,100}\b(?:pods?|runpod|vast|gpus?|cpus?|scanner|residual|9024|benchmark|eval)\b|"
    r"\b(?:gpu_forever|gpu_island2|fanout_nonce_eval|build_circuit|eval_circuit|count_tof|drop_effect_probe)\b",
    re.IGNORECASE,
)
PREMATURE_RE = re.compile(r"\b(?:FOR[- ]AKASH|WINNER|mobile alert|submit(?:ted)?|ready[- ]to[- ]submit|Akash-ready)\b", re.IGNORECASE)
LOCAL_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:mac|macbook|local|darwin)\b|\b(?:MacBook|mac-local|/Users/[A-Za-z0-9_.-]+)\b", re.IGNORECASE)
REMOTE_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:studio|runpod|vast|pod|remote)\b|\b(?:studio|runpod:|vast:|owned pod|owned-pod)\b", re.IGNORECASE)


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
    return float(value.replace("_", ""))


def first_int(pattern: re.Pattern[str], text: str) -> int | None:
    value = first_match(pattern, text)
    if not value:
        return None
    return int(value.replace("_", ""))


def parse_call_set(text: str) -> set[str]:
    return {part.strip() for part in text.replace("_", "").split(",") if part.strip()}


def inspect(text: str, expected_source: str, expected_qubits: int) -> dict[str, object]:
    route_id = first_match(ROUTE_ID_RE, text)
    owner = first_match(OWNER_RE, text)
    next_action = first_match(NEXT_RE, text)
    source_base = first_match(SOURCE_BASE_RE, text)
    frontier_score = first_float(FRONTIER_SCORE_RE, text)
    qubits = first_int(QUBITS_RE, text)
    target_q = first_int(TARGET_Q_RE, text)
    avg_t = first_float(AVG_T_RE, text)
    candidate_score = first_float(CANDIDATE_SCORE_RE, text)
    score_edge = first_float(SCORE_EDGE_RE, text)
    delta = first_float(DELTA_RE, text)
    evidence_label = first_match(EVIDENCE_LABEL_RE, text)
    peak_rows = first_int(PEAK_ROWS_RE, text)
    overlap_rows = first_int(OVERLAP_ROWS_RE, text)
    stale_warnings = first_int(STALE_WARNINGS_RE, text) or 0
    required_calls = parse_call_set(first_match(REQUIRED_CALLS_RE, text))
    covered_calls = parse_call_set(first_match(COVERED_CALLS_RE, text))

    effective_q = target_q or qubits
    computed_score = None
    if candidate_score is None and avg_t is not None and effective_q is not None:
        computed_score = avg_t * effective_q
        candidate_score = computed_score
    if score_edge is None and frontier_score is not None and candidate_score is not None:
        score_edge = frontier_score - candidate_score

    has_source_hash = bool(SOURCE_HASH_RE.search(text))
    has_source_bound = bool(has_source_hash and SOURCE_BOUND_RE.search(text))
    has_transcript = bool(TRANSCRIPT_RE.search(text))
    has_exact_support = bool(EXACT_SUPPORT_RE.search(text))
    has_support_unknown = bool(SUPPORT_UNKNOWN_RE.search(text))
    has_support_counter = bool(SUPPORT_COUNTER_RE.search(text))
    has_active_only_origin = bool(ORIGIN_ACTIVE_ONLY_RE.search(text))
    has_dirty = bool(DIRTY_RE.search(text))
    has_compute_request = bool(COMPUTE_REQUEST_RE.search(text))
    has_premature = bool(PREMATURE_RE.search(text))
    has_local = bool(LOCAL_RE.search(text))
    has_remote = bool(REMOTE_RE.search(text))
    has_no_submit = bool(NO_SUBMIT_RE.search(text))
    has_score_edge = score_edge is not None and score_edge > 0
    has_negative_delta = delta is not None and delta < 0
    missing_calls = sorted(required_calls - covered_calls)

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []

    if has_local:
        failures.append("local_heavy_context")
    if has_dirty:
        failures.append("dirty_bounded_probe")
    if stale_warnings > 0:
        failures.append("stale_index_warnings")
    if has_active_only_origin:
        failures.append("active_only_origin_map")
    if has_support_counter:
        failures.append("support_counterexample")
    if score_edge is not None and score_edge <= 0:
        failures.append("score_no_edge")
    if delta is not None and not has_negative_delta:
        failures.append("nonnegative_expected_delta")
    if missing_calls:
        failures.append("missing_required_peak_calls")
    if has_compute_request:
        failures.append("premature_compute_or_residual_request")
    if has_premature:
        failures.append("premature_submit_or_akash_language")
    if not has_no_submit:
        failures.append("missing_no_submit_ack")
    if expected_source and source_base and source_base != expected_source:
        failures.append("stale_source_base")
    if expected_qubits > 0 and qubits is not None and qubits != expected_qubits:
        failures.append("wrong_qubit_tier")
    if evidence_label.lower() in {"local full run", "promoted"}:
        failures.append("transcript_packet_overclaims_result")

    if not route_id:
        holds.append("missing_route_id")
    if not owner:
        holds.append("missing_owner")
    if not next_action:
        holds.append("missing_next_action")
    if not source_base:
        holds.append("missing_source_base")
    if frontier_score is None:
        holds.append("missing_frontier_score")
    if qubits is None:
        holds.append("missing_qubits")
    if not has_source_hash:
        holds.append("missing_source_hash")
    if not has_source_bound:
        holds.append("missing_source_hash_bound_context")
    if not has_transcript:
        holds.append("missing_transcript_peak_overlap_inventory")
    if peak_rows is None:
        holds.append("missing_peak_rows")
    elif peak_rows <= 0:
        failures.append("no_peak_rows")
    if overlap_rows is None:
        holds.append("missing_overlap_rows")
    elif overlap_rows <= 0:
        failures.append("no_overlap_rows")
    if not has_exact_support:
        holds.append("missing_exact_support_certified")
    if has_support_unknown:
        holds.append("support_unknown")
    if score_edge is None:
        holds.append("missing_score_edge")
    if not evidence_label:
        holds.append("missing_evidence_label")
    elif evidence_label.lower() not in {"prefilter", "partial"}:
        holds.append("evidence_label_not_prefilter_or_partial")
    if not has_remote:
        warnings.append("missing_remote_or_studio_route")
    if avg_t is not None and computed_score is not None:
        warnings.append("candidate_score_computed_from_avgT")

    if failures:
        gate = "fail"
        decision = "do-not-implement-drop"
    elif holds:
        gate = "hold"
        decision = "complete-transcript-overlap-inventory"
    else:
        gate = "pass"
        decision = "source-theorem-review-no-compute"

    return {
        "gate": gate,
        "decision": decision,
        "route_id": route_id,
        "owner": owner,
        "next_action": next_action,
        "source_base": source_base,
        "expected_source": expected_source,
        "frontier_score": frontier_score,
        "qubits": qubits,
        "expected_qubits": expected_qubits,
        "target_q": target_q,
        "avg_t": avg_t,
        "candidate_score": candidate_score,
        "computed_score": computed_score,
        "score_edge": score_edge,
        "delta": delta,
        "evidence_label": evidence_label,
        "peak_rows": peak_rows,
        "overlap_rows": overlap_rows,
        "stale_index_warnings": stale_warnings,
        "required_calls": sorted(required_calls),
        "covered_calls": sorted(covered_calls),
        "missing_calls": missing_calls,
        "source_hash_bound": has_source_bound,
        "transcript_inventory": has_transcript,
        "exact_support": has_exact_support,
        "support_unknown": has_support_unknown,
        "active_only_origin": has_active_only_origin,
        "dirty_evidence": has_dirty,
        "score_edge_ok": has_score_edge,
        "remote_host": has_remote,
        "compute_request": has_compute_request,
        "no_submit_ack": has_no_submit,
        "failures": failures,
        "holds": holds,
        "warnings": warnings,
    }


def join(values: object) -> str:
    if not values:
        return "none"
    if isinstance(values, list):
        return ",".join(str(value) for value in values) if values else "none"
    return str(values)


def text_summary(row: dict[str, object]) -> str:
    return (
        f"transcript_overlap_gate={row['gate']} route_id={row['route_id'] or 'missing'} "
        f"owner={row['owner'] or 'missing'} next={row['next_action'] or 'missing'} "
        f"source_base={row['source_base'] or 'missing'} expected_source={row['expected_source'] or 'none'} "
        f"frontier_score={row['frontier_score']} qubits={row['qubits']} expected_qubits={row['expected_qubits']} "
        f"target_q={row['target_q']} avgT={row['avg_t']} candidate_score={row['candidate_score']} "
        f"score_edge={row['score_edge']} delta={row['delta']} evidence_label={row['evidence_label'] or 'missing'} "
        f"peak_rows={row['peak_rows']} overlap_rows={row['overlap_rows']} "
        f"stale_index_warnings={row['stale_index_warnings']} required_calls={join(row['required_calls'])} "
        f"covered_calls={join(row['covered_calls'])} missing_calls={join(row['missing_calls'])} "
        f"source_hash_bound={str(row['source_hash_bound']).lower()} transcript_inventory={str(row['transcript_inventory']).lower()} "
        f"exact_support={str(row['exact_support']).lower()} active_only_origin={str(row['active_only_origin']).lower()} "
        f"dirty_evidence={str(row['dirty_evidence']).lower()} score_edge_ok={str(row['score_edge_ok']).lower()} "
        f"remote_host={str(row['remote_host']).lower()} compute_request={str(row['compute_request']).lower()} "
        f"no_submit_ack={str(row['no_submit_ack']).lower()} decision={row['decision']} "
        f"failures={join(row['failures'])} holds={join(row['holds'])} warnings={join(row['warnings'])}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--expected-source", default="d44cad3")
    parser.add_argument("--expected-qubits", type=int, default=1147)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    missing = [str(path) for path in args.inputs if not path.is_file()]
    if missing:
        print(f"transcript_overlap_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
        return 2

    row = inspect(read_text(args.inputs), args.expected_source, args.expected_qubits)
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
