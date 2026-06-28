#!/usr/bin/env python3
"""Gate source packets against already closed counterexample ledgers.

This is a public-safe parser for redacted packet and ledger summaries. It does
not run miners, build/eval, SSH job control, alerts, or submit.
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
KIND_RE = re.compile(
    r"\b(?:kind|op_class)\s*[=:]\s*(CCX|CCZ|CX|CZ|X|SWAP|CSWAP|TOFFOLI|T)\b",
    re.IGNORECASE,
)
FAMILY_RE = re.compile(r"\b(?:family|primitive_family|trace_context_family)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE)
EVIDENCE_LABEL_RE = re.compile(r"\bevidence_label\s*[=:]\s*(Prefilter|Partial|Local full run|Promoted)\b", re.IGNORECASE)
DELTA_RE = re.compile(r"\b(?:expected_avgT_delta|expected_delta|expected_ops_delta|delta)\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
SUPPORT_STATUS_RE = re.compile(r"\bsupport_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE)\b", re.IGNORECASE)
PROOF_STATUS_RE = re.compile(r"\bproof_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN)\b", re.IGNORECASE)
SOURCE_BOUND_RE = re.compile(r"\b(?:source-hash-bound|source_hash\s*[=:]|source-bound)\b", re.IGNORECASE)
SOURCE_PROOF_RE = re.compile(
    r"\b(?:source[-_ ]proof|bounded[-_ ]source[-_ ]proof|one bounded source proof|proof_backlog|exact[-_ ]miner|certificate|counterexample)\b",
    re.IGNORECASE,
)

NOVELTY_NEW_RE = re.compile(
    r"\bnovelty_status\s*[=:]\s*NEW\b|"
    r"\boutside_closed_ledger\s*[=:]\s*yes\b|"
    r"\bledger_hit\s*[=:]\s*no\b|"
    r"\bclosed_ledger_hit\s*[=:]\s*no\b",
    re.IGNORECASE,
)
NOVELTY_UNKNOWN_RE = re.compile(
    r"\bnovelty_status\s*[=:]\s*UNKNOWN\b|"
    r"\bledger_hit\s*[=:]\s*unknown\b|"
    r"\bclosed_ledger_hit\s*[=:]\s*unknown\b|"
    r"\boutside_closed_ledger\s*[=:]\s*unknown\b",
    re.IGNORECASE,
)
LEDGER_HIT_RE = re.compile(
    r"\bledger_hit\s*[=:]\s*yes\b|"
    r"\bclosed_ledger_hit\s*[=:]\s*yes\b|"
    r"\bauto_nack\s*[=:]\s*true\b|"
    r"\bnack_note\s*[=:]\s*\S+|"
    r"\bsource[-_ ]counterexample\b",
    re.IGNORECASE,
)
NEXT_UNCLOSED_EMPTY_RE = re.compile(r"\bNEXT_UNCLOSED\s*(?:[=:]\s*)?(?:empty|none|0)\b", re.IGNORECASE)
CURRENT_UNKNOWN_RE = re.compile(r"\bcurrent_unknown_scored\s*[=:]\s*([0-9]+)\b", re.IGNORECASE)
CLOSED_BY_JSONL_RE = re.compile(r"\bclosed_by_existing_jsonl\s*[=:]\s*([0-9]+)\b", re.IGNORECASE)
SUMMARY_TOTAL_RE = re.compile(r"\b(?:summary_ccx_ccz_total|source_family_total|family_summary_total|summary_total)\s*[=:]\s*([0-9]+)\b", re.IGNORECASE)
CLOSED_TOTAL_RE = re.compile(r"\b(?:closed_by_counterexample_jsonl|closed_total|closed_after_all_jsonl|closed_by_all_jsonl)\s*[=:]\s*([0-9]+)\b", re.IGNORECASE)
OPEN_AFTER_RE = re.compile(r"\b(?:open_after_all_jsonl_plus_fresh[0-9]+|open_after_all_jsonl|open_after_join|open_after)\s*[=:]\s*([0-9]+)\b", re.IGNORECASE)
OPEN_DIGEST_RE = re.compile(r"\bopen_digest\s*[=:]\s*([0-9a-fA-F]{64})\b", re.IGNORECASE)
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

PREMATURE_RE = re.compile(r"\b(?:FOR[- ]AKASH|WINNER|mobile alert|submit(?:ted)?|ready[- ]to[- ]submit|Akash-ready)\b", re.IGNORECASE)
COMPUTE_REQUEST_RE = re.compile(
    r"\b(?:launch|start|scale|fire\s+up|spin\s+up|rent)\b.{0,80}\b(?:pods?|runpod|vast|akash|gpus?|cpus?|scanners?|nonce)\b|"
    r"\b(?:gpus?|cpus?|nonce|island)\s+search\b|"
    r"\bbrute\s+force\b",
    re.IGNORECASE,
)
LOCAL_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:mac|macbook|local|darwin)\b|\b(?:MacBook|mac-local|/Users/[A-Za-z0-9_.-]+)\b", re.IGNORECASE)
REMOTE_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:studio|runpod|vast|pod|remote)\b|\b(?:studio|runpod:|vast:|owned pod|owned-pod)\b", re.IGNORECASE)


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
    current_unknown = first_int(CURRENT_UNKNOWN_RE, text)
    closed_by_jsonl = first_int(CLOSED_BY_JSONL_RE, text)
    summary_total = first_int(SUMMARY_TOTAL_RE, text)
    closed_total = first_int(CLOSED_TOTAL_RE, text)
    open_after = first_int(OPEN_AFTER_RE, text)
    open_digest = first_match(OPEN_DIGEST_RE, text).lower()

    has_no_submit = bool(NO_SUBMIT_RE.search(text))
    has_source_bound = bool(source_hash and SOURCE_BOUND_RE.search(text))
    has_source_proof_intent = bool(SOURCE_PROOF_RE.search(text))
    has_novelty_new = bool(NOVELTY_NEW_RE.search(text))
    has_novelty_unknown = bool(NOVELTY_UNKNOWN_RE.search(text))
    has_ledger_hit = bool(LEDGER_HIT_RE.search(text))
    has_next_unclosed_empty = bool(NEXT_UNCLOSED_EMPTY_RE.search(text))
    has_counterexample = support_status == "COUNTEREXAMPLE" or proof_status == "COUNTEREXAMPLE" or has_ledger_hit
    has_all_current_closed = (
        current_unknown is not None
        and closed_by_jsonl is not None
        and current_unknown > 0
        and current_unknown == closed_by_jsonl
        and not has_novelty_new
    )
    has_source_family_exhausted = (
        (
            summary_total is not None
            and summary_total > 0
            and open_after == 0
        )
        or (
            summary_total is not None
            and summary_total > 0
            and open_digest == EMPTY_SHA256
        )
    ) and not has_novelty_new
    has_premature_language = bool(PREMATURE_RE.search(text))
    has_compute_request = bool(COMPUTE_REQUEST_RE.search(text))
    has_local_host = bool(LOCAL_RE.search(text))
    has_remote_host = bool(REMOTE_RE.search(text))
    has_negative_delta = delta is not None and delta < 0
    is_scored_kind = kind in {"CCX", "CCZ"}

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []

    if has_counterexample:
        failures.append("source_counterexample_or_ledger_hit")
    if has_all_current_closed:
        failures.append("all_current_unknowns_closed")
    if has_source_family_exhausted:
        failures.append("source_family_exhausted")
    if has_next_unclosed_empty and not has_novelty_new:
        failures.append("next_unclosed_empty_without_new_packet")
    if has_premature_language:
        failures.append("premature_submit_or_akash_language")
    if has_compute_request:
        failures.append("premature_compute_request")
    if has_local_host:
        failures.append("local_heavy_context")
    if not has_no_submit:
        failures.append("missing_no_submit_ack")
    if expected_source and source_base and source_base != expected_source:
        failures.append("stale_source_base")
    if expected_qubits > 0 and qubits is not None and qubits != expected_qubits:
        failures.append("wrong_qubit_tier")
    if evidence_label.lower() in {"local full run", "promoted"}:
        failures.append("source_packet_overclaims_result")
    if delta is not None and not has_negative_delta:
        failures.append("nonnegative_expected_delta")
    if kind and not is_scored_kind:
        failures.append("non_scored_op_kind")

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
    if not source_hash:
        holds.append("missing_source_hash")
    if not candidate_hash:
        holds.append("missing_candidate_index_or_diff_hash")
    if not has_source_bound:
        holds.append("missing_source_hash_bound_context")
    if not source_location:
        holds.append("missing_source_location")
    if not kind:
        holds.append("missing_op_kind")
    if not family:
        warnings.append("missing_primitive_or_trace_family")
    if not evidence_label:
        holds.append("missing_evidence_label")
    elif evidence_label.lower() not in {"prefilter", "partial"}:
        holds.append("evidence_label_not_prefilter_or_partial")
    if delta is None:
        holds.append("missing_expected_delta")
    if not has_novelty_new:
        holds.append("missing_novelty_status_new_or_outside_closed_ledger")
    if has_novelty_unknown:
        holds.append("novelty_unknown")
    if not has_source_proof_intent:
        holds.append("missing_bounded_source_proof_next")
    if support_status in {"", "UNKNOWN"} and proof_status in {"", "UNKNOWN", "UNPROVEN"}:
        warnings.append("support_unproven_expected_for_novelty_gate")
    if not has_remote_host:
        warnings.append("missing_remote_or_studio_route")

    if failures:
        gate = "fail"
        decision = "do-not-open-source-packet"
    elif holds:
        gate = "hold"
        decision = "complete-source-novelty-evidence"
    else:
        gate = "pass"
        decision = "admit-one-bounded-source-proof-no-compute"

    return {
        "gate": gate,
        "decision": decision,
        "route_id": route_id,
        "owner": owner,
        "next_action": next_action,
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
        "support_status": support_status or "missing",
        "proof_status": proof_status or "missing",
        "current_unknown_scored": current_unknown,
        "closed_by_existing_jsonl": closed_by_jsonl,
        "summary_total": summary_total,
        "closed_total": closed_total,
        "open_after": open_after,
        "open_digest": open_digest or "missing",
        "source_family_exhausted": has_source_family_exhausted,
        "next_unclosed_empty": has_next_unclosed_empty,
        "outside_closed_ledger": has_novelty_new,
        "novelty_unknown": has_novelty_unknown,
        "source_bound": has_source_bound,
        "source_proof_intent": has_source_proof_intent,
        "ledger_hit": has_ledger_hit,
        "counterexample": has_counterexample,
        "remote_host": has_remote_host,
        "local_host": has_local_host,
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
        f"source_packet_novelty_gate={row['gate']} "
        f"route_id={row['route_id'] or 'missing'} owner={row['owner'] or 'missing'} "
        f"next={row['next_action'] or 'missing'} source_base={row['source_base'] or 'missing'} "
        f"expected_source={row['expected_source'] or 'none'} source_hash={str(row['source_hash']).lower()} "
        f"candidate_hash={str(row['candidate_hash']).lower()} "
        f"source_bound={str(row['source_bound']).lower()} source_location={row['source_location'] or 'missing'} "
        f"frontier_score={row['frontier_score']} qubits={row['qubits']} expected_qubits={row['expected_qubits']} "
        f"kind={row['kind'] or 'missing'} family={row['family'] or 'missing'} "
        f"evidence_label={row['evidence_label'] or 'missing'} delta={row['delta']} "
        f"support_status={row['support_status']} proof_status={row['proof_status']} "
        f"current_unknown_scored={row['current_unknown_scored']} closed_by_existing_jsonl={row['closed_by_existing_jsonl']} "
        f"summary_total={row['summary_total']} closed_total={row['closed_total']} open_after={row['open_after']} "
        f"open_digest={row['open_digest']} source_family_exhausted={str(row['source_family_exhausted']).lower()} "
        f"next_unclosed_empty={str(row['next_unclosed_empty']).lower()} outside_closed_ledger={str(row['outside_closed_ledger']).lower()} "
        f"ledger_hit={str(row['ledger_hit']).lower()} counterexample={str(row['counterexample']).lower()} "
        f"source_proof_intent={str(row['source_proof_intent']).lower()} remote_host={str(row['remote_host']).lower()} "
        f"compute_request={str(row['compute_request']).lower()} no_submit_ack={str(row['no_submit_ack']).lower()} "
        f"decision={row['decision']} failures={join(row['failures'])} holds={join(row['holds'])} warnings={join(row['warnings'])}"
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
        print(f"source_packet_novelty_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
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
