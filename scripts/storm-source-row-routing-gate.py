#!/usr/bin/env python3
"""Gate q1152 source-scout row routing before proof or closure handoff.

This public-safe parser checks redacted source-row packets. It does not run
miners, build/eval, SSH job control, alerts, or submit.
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
NEXT_ROW_RE = re.compile(r"\b(?:next_source_row|next_ccx_row|next_rank)\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
RANK_RE = re.compile(r"\brank\s*[=:]\s*([0-9]+)\b", re.IGNORECASE)
COUNT_RE = re.compile(r"\bcount\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
SOURCE_BASE_RE = re.compile(r"\b(?:source_base|source|base|source commit)\s*[=:]\s*([0-9a-f]{6,40})\b", re.IGNORECASE)
SOURCE_HASH_RE = re.compile(r"\b(?:source_hash|source-hash|source_snippet_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b", re.IGNORECASE)
CANDIDATE_HASH_RE = re.compile(
    r"\b(?:candidate_index_hash|candidate_diff_hash|candidate_hash|diff_hash|index_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b",
    re.IGNORECASE,
)
SOURCE_LOCATION_RE = re.compile(
    r"\b(?:source_location|site|file)\s*[=:]\s*((?:src/point_add)/[A-Za-z0-9_./+-]+\.rs:[0-9]+)\b",
    re.IGNORECASE,
)
FRONTIER_SCORE_RE = re.compile(r"\bfrontier(?:_score| score)?\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
QUBITS_RE = re.compile(r"\b(?:q|qubits?)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
KIND_RE = re.compile(r"\b(?:kind|op_class)\s*[=:]\s*(CCX|CCZ|CSWAP|TOFFOLI|T)\b", re.IGNORECASE)
FAMILY_RE = re.compile(r"\b(?:family|primitive_family|trace_context_family)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE)
EVIDENCE_LABEL_RE = re.compile(r"\bevidence_label\s*[=:]\s*(Prefilter|Partial|Local full run|Promoted)\b", re.IGNORECASE)
DELTA_RE = re.compile(r"\b(?:expected_avgT_delta|expected_delta|expected_ops_delta|delta)\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
SUPPORT_STATUS_RE = re.compile(r"\bsupport_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE)\b", re.IGNORECASE)
PROOF_STATUS_RE = re.compile(r"\bproof_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN)\b", re.IGNORECASE)
NOVELTY_NEW_RE = re.compile(r"\bnovelty_status\s*[=:]\s*NEW\b|\boutside_closed_ledger\s*[=:]\s*yes\b|\bledger_hit\s*[=:]\s*no\b", re.IGNORECASE)
LEDGER_HIT_RE = re.compile(r"\bledger_hit\s*[=:]\s*yes\b|\bclosed_ledger_hit\s*[=:]\s*yes\b|\bsource[-_ ]counterexample\b", re.IGNORECASE)
PROOF_BACKLOG_RE = re.compile(r"\b(?:proof_backlog|one bounded source proof|bounded_source_proof|source_proof)\b", re.IGNORECASE)
CLOSURE_RE = re.compile(r"\b(?:source_row_closed|closure_reason|close_reason|counterexample_artifact|counterexample_file)\s*[=:]\s*\S+", re.IGNORECASE)
REMOTE_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:studio|runpod|vast|pod|remote)\b|\bstudio\b", re.IGNORECASE)
LOCAL_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:mac|macbook|local|darwin)\b|\b(?:MacBook|mac-local|/Users/[A-Za-z0-9_.-]+)\b", re.IGNORECASE)
COMPUTE_REQUEST_RE = re.compile(
    r"\b(?:launch|start|restart|rearm|scale|dispatch|benchmark|run|route_compare)\b.{0,100}\b(?:pods?|runpod|vast|gpus?|cpus?|scanner|benchmark|eval|residual)\b|"
    r"\b(?:gpu_forever|gpu_island2|fanout_nonce_eval|build_circuit|eval_circuit|count_tof|storm-exact-miner)\b",
    re.IGNORECASE,
)
PREMATURE_RE = re.compile(r"\b(?:FOR[- ]AKASH|WINNER|mobile alert|submit(?:ted)?|ready[- ]to[- ]submit|Akash-ready)\b", re.IGNORECASE)


def read_text(paths: Iterable[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths)


def first_match(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    if not match:
        return ""
    return next((group for group in match.groups() if group), "")


def first_int(pattern: re.Pattern[str], text: str) -> int | None:
    value = first_match(pattern, text)
    if not value:
        return None
    return int(value.replace("_", ""))


def first_float(pattern: re.Pattern[str], text: str) -> float | None:
    value = first_match(pattern, text)
    if not value:
        return None
    return float(value.replace("_", ""))


def inspect(text: str, expected_source: str, expected_qubits: int) -> dict[str, object]:
    route_id = first_match(ROUTE_ID_RE, text)
    owner = first_match(OWNER_RE, text)
    next_action = first_match(NEXT_RE, text)
    next_row = first_match(NEXT_ROW_RE, text)
    rank = first_int(RANK_RE, text)
    count = first_int(COUNT_RE, text)
    source_base = first_match(SOURCE_BASE_RE, text)
    source_hash = first_match(SOURCE_HASH_RE, text)
    candidate_hash = first_match(CANDIDATE_HASH_RE, text)
    source_location = first_match(SOURCE_LOCATION_RE, text)
    frontier_score = first_float(FRONTIER_SCORE_RE, text)
    qubits = first_int(QUBITS_RE, text)
    kind = first_match(KIND_RE, text).upper()
    family = first_match(FAMILY_RE, text)
    evidence_label = first_match(EVIDENCE_LABEL_RE, text)
    delta = first_float(DELTA_RE, text)
    support_status = first_match(SUPPORT_STATUS_RE, text).upper()
    proof_status = first_match(PROOF_STATUS_RE, text).upper()

    closure = bool(
        support_status == "COUNTEREXAMPLE"
        or proof_status == "COUNTEREXAMPLE"
        or LEDGER_HIT_RE.search(text)
        or CLOSURE_RE.search(text)
    )
    packet = bool(NOVELTY_NEW_RE.search(text) and not closure)
    has_no_submit = bool(NO_SUBMIT_RE.search(text))
    has_remote = bool(REMOTE_RE.search(text))
    has_local = bool(LOCAL_RE.search(text))
    has_compute = bool(COMPUTE_REQUEST_RE.search(text))
    has_premature = bool(PREMATURE_RE.search(text))
    has_proof_backlog = bool(PROOF_BACKLOG_RE.search(text))
    has_closure_reason = bool(CLOSURE_RE.search(text))
    negative_delta = delta is not None and delta < 0

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []

    if has_local:
        failures.append("local_heavy_context")
    if has_compute:
        failures.append("premature_compute_request")
    if has_premature:
        failures.append("premature_submit_or_alert_language")
    if not has_no_submit:
        failures.append("missing_no_submit_ack")
    if expected_source and source_base and source_base != expected_source:
        failures.append("stale_source_base")
    if expected_qubits > 0 and qubits is not None and qubits != expected_qubits:
        failures.append("wrong_qubit_tier")
    if evidence_label.lower() in {"local full run", "promoted"}:
        failures.append("source_row_overclaims_result")
    if closure and negative_delta:
        failures.append("counterexample_closure_claims_negative_delta")
    if packet and delta is not None and not negative_delta:
        failures.append("packet_has_nonnegative_expected_delta")

    for label, value in [
        ("missing_route_id", route_id),
        ("missing_owner", owner),
        ("missing_next_action", next_action),
        ("missing_source_base", source_base),
        ("missing_source_hash", source_hash),
        ("missing_source_location", source_location),
        ("missing_op_kind", kind),
    ]:
        if not value:
            holds.append(label)
    if frontier_score is None:
        holds.append("missing_frontier_score")
    if qubits is None:
        holds.append("missing_qubits")
    if rank is None:
        holds.append("missing_rank")
    if count is None:
        holds.append("missing_count")
    if not packet and not closure:
        holds.append("missing_packet_or_closure_decision")

    if packet:
        if not candidate_hash:
            holds.append("missing_candidate_index_or_diff_hash")
        if not family:
            holds.append("missing_primitive_family")
        if evidence_label.lower() != "prefilter":
            holds.append("packet_evidence_label_not_prefilter")
        if not negative_delta:
            holds.append("missing_negative_expected_delta")
        if support_status not in {"UNKNOWN", ""}:
            holds.append("packet_support_status_not_unknown")
        if proof_status not in {"UNPROVEN", "UNKNOWN", ""}:
            holds.append("packet_proof_status_not_unproven")
        if not has_proof_backlog:
            holds.append("missing_bounded_source_proof_next")

    if closure:
        if support_status != "COUNTEREXAMPLE":
            holds.append("closure_missing_support_counterexample")
        if proof_status != "COUNTEREXAMPLE":
            holds.append("closure_missing_proof_counterexample")
        if not has_closure_reason:
            holds.append("missing_closure_reason_or_artifact")
        if not next_row and "next-ccx-source-row" not in (next_action or "").lower():
            holds.append("missing_next_source_row")
        if candidate_hash:
            warnings.append("closure_has_candidate_hash")

    if not has_remote:
        warnings.append("missing_remote_or_studio_context")

    if failures:
        gate = "fail"
        decision = "reject-source-row-routing"
    elif holds:
        gate = "hold"
        decision = "complete-source-row-routing-packet"
    elif closure:
        gate = "pass"
        decision = "source-row-closed-advance-next-no-compute"
    else:
        gate = "pass"
        decision = "source-row-packet-ready-no-compute"

    return {
        "gate": gate,
        "decision": decision,
        "route_id": route_id,
        "owner": owner,
        "next_action": next_action,
        "next_source_row": next_row,
        "rank": rank,
        "count": count,
        "source_base": source_base,
        "expected_source": expected_source,
        "source_hash": bool(source_hash),
        "candidate_hash": bool(candidate_hash),
        "source_location": source_location,
        "frontier_score": frontier_score,
        "qubits": qubits,
        "expected_qubits": expected_qubits,
        "kind": kind,
        "family": family,
        "evidence_label": evidence_label,
        "delta": delta,
        "negative_delta": negative_delta,
        "support_status": support_status or "missing",
        "proof_status": proof_status or "missing",
        "packet": packet,
        "closure": closure,
        "remote_host": has_remote,
        "compute_request": has_compute,
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
        f"source_row_routing_gate={row['gate']} route_id={row['route_id'] or 'missing'} "
        f"owner={row['owner'] or 'missing'} next={row['next_action'] or 'missing'} "
        f"next_source_row={row['next_source_row'] or 'missing'} rank={row['rank']} count={row['count']} "
        f"source_base={row['source_base'] or 'missing'} expected_source={row['expected_source'] or 'none'} "
        f"source_hash={str(row['source_hash']).lower()} candidate_hash={str(row['candidate_hash']).lower()} "
        f"source_location={row['source_location'] or 'missing'} frontier_score={row['frontier_score']} "
        f"qubits={row['qubits']} expected_qubits={row['expected_qubits']} kind={row['kind'] or 'missing'} "
        f"family={row['family'] or 'missing'} evidence_label={row['evidence_label'] or 'missing'} "
        f"delta={row['delta']} negative_delta={str(row['negative_delta']).lower()} "
        f"support_status={row['support_status']} proof_status={row['proof_status']} "
        f"packet={str(row['packet']).lower()} closure={str(row['closure']).lower()} "
        f"remote_host={str(row['remote_host']).lower()} compute_request={str(row['compute_request']).lower()} "
        f"no_submit_ack={str(row['no_submit_ack']).lower()} decision={row['decision']} "
        f"failures={join(row['failures'])} holds={join(row['holds'])} warnings={join(row['warnings'])}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--expected-source", default="d44cad3")
    parser.add_argument("--expected-qubits", type=int, default=1152)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    missing = [str(path) for path in args.inputs if not path.is_file()]
    if missing:
        print(f"source_row_routing_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
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
