#!/usr/bin/env python3
"""Gate scanner restarts while compute is closed.

This parser is public-safe: it reads redacted owner packets, route summaries,
or pod snapshots and decides whether a GPU/CPU scanner restart should be
blocked before paid compute continues.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Iterable


SCANNER_RE = re.compile(
    r"\b(?:gpu_island2|gpu_forever(?:\.sh)?|search_driver\.sh|fanout_nonce_eval|"
    r"island_search_driver|scanner(?:_deep)?|nonce\s+search|brute\s+force)\b",
    re.IGNORECASE,
)
OFFICIAL_EVAL_RE = re.compile(r"\b(?:eval_circuit|build_circuit|official eval|full validation)\b", re.IGNORECASE)
CLOSED_RE = re.compile(
    r"\b(?:compute_gate|gate|fleet_gate)\s*[=:]\s*(?:closed|none)\b|"
    r"\bcompute\s+(?:gate\s+)?(?:is\s+)?closed\b|"
    r"\bqueue\s*[=:]\s*(?:pod_dispatch=)?(?:empty_or_no_eligible_job|empty|none)\b|"
    r"\bno\s+eligible\s+(?:pod\s+)?job\b",
    re.IGNORECASE,
)
OPEN_RE = re.compile(
    r"\b(?:compute_gate|gate|fleet_gate)\s*[=:]\s*(?:open|approved|route_ack)\b|"
    r"\bStorm[- ]route[- ]ACK\b|"
    r"\broute_ack\s*[=:]\s*yes\b",
    re.IGNORECASE,
)
CERTIFIED_RE = re.compile(
    r"\b(?:support_status|proof_status)\s*[=:]\s*CERTIFIED\b|"
    r"\bsource[- ]hash[- ]bound\b.{0,120}\bCERTIFIED\b",
    re.IGNORECASE | re.DOTALL,
)
FULL_CLEAN_RE = re.compile(
    r"\b(?:0\s*/\s*0\s*/\s*0|classical\s*[=:]\s*0\b.{0,40}\bphase\s*[=:]\s*0\b.{0,40}\bancilla\s*[=:]\s*0)\b",
    re.IGNORECASE | re.DOTALL,
)
NO_SUBMIT_RE = re.compile(r"\bno_submit_ack\s*=\s*yes\b", re.IGNORECASE)
SOURCE_BASE_RE = re.compile(r"\b(?:source_base|source|base|source commit)\s*[=:]\s*([0-9a-f]{6,40})\b", re.IGNORECASE)
FRONTIER_SCORE_RE = re.compile(r"\bfrontier(?:_score| score)?\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
QUBITS_RE = re.compile(r"\b(?:q|qubits?)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
DELTA_RE = re.compile(r"\b(?:expected_avgT_delta|expected_delta|expected_ops_delta|delta)\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
VALIDATION_OWNER_RE = re.compile(r"\b(?:validation_owner|validator)\s*[=:]\s*([A-Za-z0-9_.-]+)\b", re.IGNORECASE)
BUDGET_RE = re.compile(r"\b(?:budget|max_budget|compute_budget|max_nonce|max_range|max_minutes|max_dollars|max_shots)\s*[=:]\s*\S+", re.IGNORECASE)
STOP_RE = re.compile(r"\b(?:stop_condition|kill_condition|kill_gate|stop_after|abort_if)\s*[=:]\s*\S+", re.IGNORECASE)
OWNER_RE = re.compile(r"\b(?:owner|agent|from)\s*[=:]\s*([A-Za-z0-9_.-]+)\b|\bACK\s+([A-Za-z0-9_.-]+)\b", re.IGNORECASE)
NEXT_RE = re.compile(r"\bnext\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
POD_RE = re.compile(r"\b(?:pod|runpod|instance|machine)\s*[=:]\s*([A-Za-z0-9_.:-]+)|\brunpod:([A-Za-z0-9_.-]+)", re.IGNORECASE)
ROUTE_RE = re.compile(r"\b(?:route|range|shard|candidate|lane)\s*[=:]\s*([A-Za-z0-9_.:/@+,\[\)-]+)", re.IGNORECASE)
EVIDENCE_RE = re.compile(r"\bevidence_label\s*[=:]\s*(Prefilter|Partial|Local full run|Promoted)\b", re.IGNORECASE)
STALE_RE = re.compile(r"\b(?:stale|manual_gpu_island2_missing|route_reopened|fed64cf_stormgate_nonce_retake_gpu)\b", re.IGNORECASE)
START_RE = re.compile(r"\b(?:start|restart|rearm|launch|scale|fire\s+up|spin\s+up)\b", re.IGNORECASE)
ALERT_RE = re.compile(
    r"(?<![A-Za-z0-9_-])(?:WINNER|Akash-ready|FOR[- ]AKASH|mobile alert|ready[- ]to[- ]submit|submit(?:ted)?)(?![A-Za-z0-9_-])",
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
    return float(value.replace("_", ""))


def first_int(pattern: re.Pattern[str], text: str) -> int | None:
    value = first_match(pattern, text)
    if not value:
        return None
    return int(value.replace("_", ""))


def inspect(text: str, expected_source: str, expected_qubits: int) -> dict[str, object]:
    scanner = bool(SCANNER_RE.search(text))
    official_eval = bool(OFFICIAL_EVAL_RE.search(text))
    closed = bool(CLOSED_RE.search(text))
    open_gate = bool(OPEN_RE.search(text))
    certified = bool(CERTIFIED_RE.search(text))
    full_clean = bool(FULL_CLEAN_RE.search(text))
    no_submit = bool(NO_SUBMIT_RE.search(text))
    stale = bool(STALE_RE.search(text))
    restart = bool(START_RE.search(text))
    alert_language = bool(ALERT_RE.search(text))
    owner = first_match(OWNER_RE, text)
    pod = first_match(POD_RE, text)
    route = first_match(ROUTE_RE, text)
    next_action = first_match(NEXT_RE, text)
    evidence_label = first_match(EVIDENCE_RE, text)
    source_base = first_match(SOURCE_BASE_RE, text)
    frontier_score = first_float(FRONTIER_SCORE_RE, text)
    qubits = first_int(QUBITS_RE, text)
    delta = first_float(DELTA_RE, text)
    validation_owner = first_match(VALIDATION_OWNER_RE, text)
    budget = bool(BUDGET_RE.search(text))
    stop_condition = bool(STOP_RE.search(text))
    negative_edge = delta is not None and delta < 0

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []

    if alert_language:
        failures.append("premature_alert_or_submit_language")
    if scanner and closed:
        failures.append("scanner_restart_under_closed_compute_gate")
    if scanner and stale:
        failures.append("stale_or_manual_scanner_route")
    if scanner and not (open_gate and (certified or full_clean)):
        failures.append("scanner_without_route_ack_and_certified_evidence")
    if evidence_label.lower() in {"local full run", "promoted"} and not full_clean:
        failures.append("scanner_overclaims_validation_label")
    if not no_submit:
        failures.append("missing_no_submit_ack")

    if scanner and not owner:
        holds.append("missing_owner")
    if scanner and not source_base:
        holds.append("missing_source_base")
    if scanner and expected_source and source_base and source_base != expected_source:
        failures.append("stale_source_base")
    if scanner and frontier_score is None:
        holds.append("missing_frontier_score")
    if scanner and qubits is None:
        holds.append("missing_qubits")
    if scanner and expected_qubits > 0 and qubits is not None and qubits != expected_qubits:
        failures.append("wrong_qubit_tier")
    if scanner and not negative_edge:
        holds.append("missing_negative_expected_edge")
    if scanner and not validation_owner:
        holds.append("missing_validation_owner")
    if scanner and not budget:
        holds.append("missing_budget")
    if scanner and not stop_condition:
        holds.append("missing_stop_condition")
    if scanner and not pod:
        holds.append("missing_pod_identity")
    if scanner and not route:
        holds.append("missing_route_or_range")
    if scanner and not next_action:
        holds.append("missing_next_action")
    if official_eval and not scanner:
        warnings.append("official_eval_packet_not_scanner_restart")
    if scanner and not evidence_label:
        warnings.append("missing_evidence_label")

    if failures:
        gate = "fail"
        decision = "stop-or-do-not-start-scanner"
    elif holds:
        gate = "hold"
        decision = "complete-route-owner-and-gate-evidence"
    else:
        gate = "pass"
        decision = "scanner-restart-gate-cleared" if scanner else "no-scanner-restart"

    return {
        "gate": gate,
        "decision": decision,
        "scanner": scanner,
        "official_eval": official_eval,
        "closed_compute_gate": closed,
        "open_gate": open_gate,
        "certified_evidence": certified,
        "full_clean_evidence": full_clean,
        "stale_or_manual": stale,
        "restart_language": restart,
        "owner": owner,
        "pod_identity": pod,
        "route_or_range": route,
        "next_action": next_action,
        "evidence_label": evidence_label,
        "source_base": source_base,
        "expected_source": expected_source,
        "frontier_score": frontier_score,
        "qubits": qubits,
        "expected_qubits": expected_qubits,
        "delta": delta,
        "negative_edge": negative_edge,
        "validation_owner": validation_owner,
        "budget": budget,
        "stop_condition": stop_condition,
        "no_submit_ack": no_submit,
        "failures": failures,
        "holds": holds,
        "warnings": warnings,
    }


def join(values: object) -> str:
    if not values:
        return "none"
    if isinstance(values, list):
        return ",".join(values) if values else "none"
    return str(values)


def text_summary(row: dict[str, object]) -> str:
    return (
        f"compute_restart_gate={row['gate']} "
        f"scanner={str(row['scanner']).lower()} official_eval={str(row['official_eval']).lower()} "
        f"closed_compute_gate={str(row['closed_compute_gate']).lower()} "
        f"open_gate={str(row['open_gate']).lower()} certified_evidence={str(row['certified_evidence']).lower()} "
        f"full_clean_evidence={str(row['full_clean_evidence']).lower()} "
        f"stale_or_manual={str(row['stale_or_manual']).lower()} "
        f"owner={row['owner'] or 'missing'} pod_identity={row['pod_identity'] or 'missing'} "
        f"route_or_range={row['route_or_range'] or 'missing'} next_action={row['next_action'] or 'missing'} "
        f"source_base={row['source_base'] or 'missing'} expected_source={row['expected_source'] or 'none'} "
        f"frontier_score={row['frontier_score']} qubits={row['qubits']} expected_qubits={row['expected_qubits']} "
        f"delta={row['delta']} negative_edge={str(row['negative_edge']).lower()} "
        f"validation_owner={row['validation_owner'] or 'missing'} budget={str(row['budget']).lower()} "
        f"stop_condition={str(row['stop_condition']).lower()} "
        f"evidence_label={row['evidence_label'] or 'missing'} "
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
        print(f"compute_restart_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
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
