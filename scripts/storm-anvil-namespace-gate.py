#!/usr/bin/env python3
"""Gate Anvil high-mass op namespace/source-binding packets.

This public-safe parser checks redacted packet text only. It does not run
miners, build/eval, SSH job control, pods, alerts, or submit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Iterable


DEFAULT_SOURCE = "d44cad3"
DEFAULT_QUBITS = 1_152
DEFAULT_FRONTIER_SCORE = 1_571_592_960
DEFAULT_REQUIRED_MASS = 2_439

NO_SUBMIT_RE = re.compile(r"\bno_submit_ack\s*[=:]\s*yes\b", re.IGNORECASE)
ROUTE_ID_RE = re.compile(r"\broute_id\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
OWNER_RE = re.compile(r"\b(?:owner|agent|validator)\s*[=:]\s*([A-Za-z0-9_.-]+)\b|\bACK\s+([A-Za-z0-9_.-]+)\b", re.IGNORECASE)
NEXT_RE = re.compile(r"\bnext\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
NEXT_ROW_RE = re.compile(r"\b(?:next_source_row|next_op_index|advance_to_op_index)\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
SOURCE_BASE_RE = re.compile(r"\b(?:source_base|source|base|source commit)\s*[=:]\s*([0-9a-f]{6,40})\b", re.IGNORECASE)
SOURCE_LOCATION_RE = re.compile(r"\b(?:source_location|site|file)\s*[=:]\s*((?:src/point_add)/[A-Za-z0-9_./+-]+\.rs:[0-9]+)\b", re.IGNORECASE)
SOURCE_HASH_RE = re.compile(r"\b(?:source_hash|source-hash|source_snippet_hash)\s*[=:]\s*([0-9a-fA-F]{8,64})\b", re.IGNORECASE)
CANDIDATE_HASH_RE = re.compile(
    r"\b(?:candidate_index_hash|candidate_diff_hash|candidate_hash|index_hash|proof_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b",
    re.IGNORECASE,
)
TRACE_HASH_RE = re.compile(r"\b(?:trace_context_hash|trace_hash|binding_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b", re.IGNORECASE)
FRONTIER_SCORE_RE = re.compile(r"\bfrontier(?:_score| score)?\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
QUBITS_RE = re.compile(r"\b(?:current_q|q|qubits?)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
OP_INDEX_RE = re.compile(r"\b(?:op_index|anvil_op_index)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
SUPPORT_INDEX_RE = re.compile(r"\b(?:support_lookup_index|support_index|post_idx|pre_idx)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
SUPPORT_OP_ID_RE = re.compile(r"\b(?:support_op_id|op_id)\s*[=:]\s*([A-Za-z0-9_.:;=+-]+)\b", re.IGNORECASE)
KIND_RE = re.compile(r"\bkind\s*[=:]\s*(CCX|CCZ|TOFFOLI|T)\b", re.IGNORECASE)
Q_TARGET_RE = re.compile(r"\bq_target\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
Q_C1_RE = re.compile(r"\bq_c1\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
Q_C2_RE = re.compile(r"\bq_c2\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
MASS_RE = re.compile(r"\b(?:expected_shot_mass|shot_mass|mass|expected_mass)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
DELTA_RE = re.compile(r"\b(?:expected_avgT_delta|expected_delta|avgT_delta|delta)\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
NAMESPACE_RE = re.compile(r"\b(?:index_namespace|support_namespace|namespace)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE)
NAMESPACE_STATUS_RE = re.compile(r"\bnamespace_status\s*[=:]\s*(MATCHED|BOUND|MISSING|MISMATCH|AMBIGUOUS|UNKNOWN)\b", re.IGNORECASE)
SOURCE_BINDING_RE = re.compile(r"\b(?:source_binding_status|row_binding_status|binding_status)\s*[=:]\s*(BOUND|UNBOUND|MISSING|MISMATCH|AMBIGUOUS|UNKNOWN)\b", re.IGNORECASE)
SUPPORT_STATUS_RE = re.compile(r"\bsupport_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN|MISSING)\b", re.IGNORECASE)
PROOF_STATUS_RE = re.compile(r"\bproof_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN|MISSING)\b", re.IGNORECASE)
EVIDENCE_LABEL_RE = re.compile(r"\bevidence_label\s*[=:]\s*(Prefilter|Counterexample|Partial|Local full run|Promoted)\b", re.IGNORECASE)
FAMILY_RE = re.compile(r"\b(?:family|primitive_family|trace_context_family)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE)
TRACE_CALL_RE = re.compile(r"\btrace_context_call\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
TRACE_BIT_RE = re.compile(r"\btrace_context_bit\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
CLOSURE_RE = re.compile(r"\b(?:closure_reason|close_reason|counterexample_artifact|counterexample_file|falsifier|witness)\s*[=:]\s*\S+", re.IGNORECASE)
SOURCE_BOUND_RE = re.compile(r"\b(?:source[-_ ]?bound|source_hash_bound|source_hash\s*[=:])\b", re.IGNORECASE)

REMOTE_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:studio|runpod|vast|pod|remote)\b|\bstudio\b", re.IGNORECASE)
LOCAL_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:mac|macbook|local|darwin)\b|\b(?:MacBook|mac-local|/Users/[A-Za-z0-9_.-]+)\b", re.IGNORECASE)
COMPUTE_REQUEST_RE = re.compile(
    r"\b(?:launch|start|restart|rearm|scale|dispatch|residual|benchmark|run|route_compare)\b.{0,100}\b(?:pods?|runpod|vast|gpus?|cpus?|scanner|residual|9024|benchmark|eval)\b|"
    r"\b(?:gpu_forever|gpu_island2|fanout_nonce_eval|build_circuit|eval_circuit|count_tof|drop_effect_probe|storm-exact-miner)\b",
    re.IGNORECASE,
)
PREMATURE_RE = re.compile(r"\b(?:FOR[- ]AKASH|WINNER|mobile alert|submit(?:ted)?|ready[- ]to[- ]submit|Akash-ready)\b", re.IGNORECASE)
NEGATED_GUARDRAIL_RE = re.compile(
    r"\b(?:no|never)\s+(?:compute|pods?|residual|route[-_ ]?compare|benchmark|alert|winner|akash|submit|submission)\b|"
    r"\b(?:do not|must not|cannot|can not)\s+(?:launch|start|restart|rearm|scale|dispatch|run|trigger|alert|write|submit)\b|"
    r"\b(?:does not|do not)\s+(?:authorize|license)\b|"
    r"\bnot\s+(?:authorized|licensed|allowed|a submit|a submission|ready[- ]to[- ]submit)\b",
    re.IGNORECASE,
)


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
    return int(value.replace("_", ""), 0)


def first_float(pattern: re.Pattern[str], text: str) -> float | None:
    value = first_match(pattern, text)
    if not value:
        return None
    return float(value.replace("_", ""))


def risk_scan_text(text: str) -> str:
    kept: list[str] = []
    skip_continuation = False
    for line in text.splitlines():
        stripped = line.strip()
        if skip_continuation:
            if not stripped or re.search(r"[.!?]\s*$", stripped):
                skip_continuation = False
            continue
        if NEGATED_GUARDRAIL_RE.search(line):
            if stripped and not re.search(r"[.!?]\s*$", stripped):
                skip_continuation = True
            continue
        kept.append(line)
    return "\n".join(kept)


def inspect(text: str, expected_source: str, expected_qubits: int, required_mass: int) -> dict[str, object]:
    risk_text = risk_scan_text(text)
    route_id = first_match(ROUTE_ID_RE, text)
    owner = first_match(OWNER_RE, text)
    next_action = first_match(NEXT_RE, text)
    next_row = first_match(NEXT_ROW_RE, text)
    source_base = first_match(SOURCE_BASE_RE, text)
    source_location = first_match(SOURCE_LOCATION_RE, text)
    source_hash = first_match(SOURCE_HASH_RE, text)
    candidate_hash = first_match(CANDIDATE_HASH_RE, text)
    trace_hash = first_match(TRACE_HASH_RE, text)
    frontier_score = first_float(FRONTIER_SCORE_RE, text)
    qubits = first_int(QUBITS_RE, text)
    op_index = first_int(OP_INDEX_RE, text)
    support_index = first_int(SUPPORT_INDEX_RE, text)
    support_op_id = first_match(SUPPORT_OP_ID_RE, text)
    kind = first_match(KIND_RE, text).upper()
    q_target = first_int(Q_TARGET_RE, text)
    q_c1 = first_int(Q_C1_RE, text)
    q_c2 = first_int(Q_C2_RE, text)
    mass = first_int(MASS_RE, text)
    delta = first_float(DELTA_RE, text)
    namespace = first_match(NAMESPACE_RE, text)
    namespace_status = first_match(NAMESPACE_STATUS_RE, text).upper()
    binding_status = first_match(SOURCE_BINDING_RE, text).upper()
    support_status = first_match(SUPPORT_STATUS_RE, text).upper()
    proof_status = first_match(PROOF_STATUS_RE, text).upper()
    evidence_label = first_match(EVIDENCE_LABEL_RE, text)
    family = first_match(FAMILY_RE, text)
    trace_call = first_int(TRACE_CALL_RE, text)
    trace_bit = first_int(TRACE_BIT_RE, text)

    namespace_bound = namespace_status in {"MATCHED", "BOUND"} and binding_status in {"BOUND", ""}
    closure = support_status == "COUNTEREXAMPLE" or proof_status == "COUNTEREXAMPLE" or bool(CLOSURE_RE.search(text))
    packet = namespace_bound and not closure

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []

    if LOCAL_RE.search(text):
        failures.append("local_heavy_context")
    if COMPUTE_REQUEST_RE.search(risk_text):
        failures.append("premature_compute_or_residual_request")
    if PREMATURE_RE.search(risk_text):
        failures.append("premature_submit_or_alert_language")
    if not NO_SUBMIT_RE.search(text):
        failures.append("missing_no_submit_ack")
    if expected_source and source_base and source_base != expected_source:
        failures.append("stale_source_base")
    if expected_qubits > 0 and qubits is not None and qubits != expected_qubits:
        failures.append("wrong_qubit_tier")
    if evidence_label.lower() in {"local full run", "promoted"}:
        failures.append("namespace_packet_overclaims_result")
    if kind and kind not in {"CCX", "CCZ", "TOFFOLI"}:
        failures.append("unscored_or_unexpected_kind")
    if mass is not None and (mass < 0 or mass > 9024):
        failures.append("mass_out_of_range")
    if not closure and mass is not None and mass < required_mass:
        failures.append("shot_mass_below_rounding_bar")
    if closure and delta is not None and delta < 0:
        failures.append("counterexample_closure_claims_negative_delta")

    for label, value in [
        ("missing_route_id", route_id),
        ("missing_owner", owner),
        ("missing_next_action", next_action),
        ("missing_source_base", source_base),
        ("missing_namespace", namespace),
        ("missing_namespace_status", namespace_status),
        ("missing_evidence_label", evidence_label),
    ]:
        if not value:
            holds.append(label)
    if frontier_score is None:
        holds.append("missing_frontier_score")
    if qubits is None:
        holds.append("missing_qubits")
    for label, value in [
        ("missing_op_index", op_index),
        ("missing_kind", kind),
        ("missing_q_target", q_target),
        ("missing_q_c1", q_c1),
        ("missing_q_c2", q_c2),
        ("missing_expected_shot_mass", mass),
    ]:
        if value is None or value == "":
            holds.append(label)

    if namespace_status in {"MISSING", "MISMATCH", "AMBIGUOUS", "UNKNOWN"}:
        holds.append(f"namespace_{namespace_status.lower()}")
    if binding_status in {"UNBOUND", "MISSING", "MISMATCH", "AMBIGUOUS", "UNKNOWN"}:
        holds.append(f"source_binding_{binding_status.lower()}")
    if not support_index and not support_op_id and not trace_hash:
        holds.append("missing_support_index_or_trace_hash")
    if support_status in {"MISSING", "UNKNOWN", "UNPROVEN", ""} and closure:
        holds.append("closure_missing_counterexample_status")

    if packet:
        for label, value in [
            ("missing_source_location", source_location),
            ("missing_source_hash", source_hash),
            ("missing_candidate_index_hash", candidate_hash),
            ("missing_trace_context_family", family),
        ]:
            if not value:
                holds.append(label)
        if not SOURCE_BOUND_RE.search(text):
            holds.append("missing_source_bound_context")
        if evidence_label.lower() != "prefilter":
            holds.append("packet_evidence_label_not_prefilter")
        if delta is not None and delta >= 0:
            failures.append("packet_has_nonnegative_expected_delta")
        if support_status not in {"UNKNOWN", "UNPROVEN", "CERTIFIED", ""}:
            holds.append("packet_support_status_not_open_or_certified")
        if proof_status not in {"UNKNOWN", "UNPROVEN", "CERTIFIED", ""}:
            holds.append("packet_proof_status_not_open_or_certified")
        if trace_call is None and trace_bit is None:
            warnings.append("missing_trace_call_or_bit")

    if closure:
        for label, value in [
            ("missing_source_location", source_location),
            ("missing_source_hash", source_hash),
            ("missing_trace_context_family", family),
        ]:
            if not value:
                holds.append(label)
        if support_status != "COUNTEREXAMPLE":
            holds.append("closure_missing_support_counterexample")
        if proof_status != "COUNTEREXAMPLE":
            holds.append("closure_missing_proof_counterexample")
        if not CLOSURE_RE.search(text):
            holds.append("missing_closure_reason_or_witness")
        if not next_row and "next" not in (next_action or "").lower() and "advance" not in (next_action or "").lower():
            holds.append("missing_next_op_index")
        if candidate_hash:
            warnings.append("closure_has_candidate_hash")

    if not REMOTE_RE.search(text):
        warnings.append("missing_remote_or_studio_context")

    if failures:
        gate = "fail"
        decision = "reject-anvil-namespace-packet"
    elif holds:
        gate = "hold"
        decision = "complete-anvil-namespace-binding"
    elif closure:
        gate = "pass"
        decision = "anvil-row-closed-advance-next-no-compute"
    else:
        gate = "pass"
        decision = "anvil-row-source-bound-ready-no-compute"

    return {
        "gate": gate,
        "decision": decision,
        "route_id": route_id,
        "owner": owner,
        "next_action": next_action,
        "next_op_index": next_row,
        "source_base": source_base,
        "expected_source": expected_source,
        "frontier_score": frontier_score,
        "qubits": qubits,
        "op_index": op_index,
        "support_lookup_index": support_index,
        "support_op_id": bool(support_op_id),
        "namespace": namespace,
        "namespace_status": namespace_status,
        "source_binding_status": binding_status,
        "source_location": source_location,
        "source_hash": bool(source_hash),
        "candidate_hash": bool(candidate_hash),
        "trace_context_hash": bool(trace_hash),
        "trace_context_family": family,
        "trace_context_call": trace_call,
        "trace_context_bit": trace_bit,
        "kind": kind,
        "q_target": q_target,
        "q_c1": q_c1,
        "q_c2": q_c2,
        "expected_shot_mass": mass,
        "required_mass": required_mass,
        "expected_avgT_delta": delta,
        "support_status": support_status,
        "proof_status": proof_status,
        "evidence_label": evidence_label,
        "packet": packet and not closure,
        "closure": closure,
        "failures": sorted(set(failures)),
        "holds": sorted(set(holds)),
        "warnings": sorted(set(warnings)),
    }


def print_summary(result: dict[str, object]) -> None:
    fields = [
        ("anvil_namespace_gate", result["gate"]),
        ("decision", result["decision"]),
        ("route_id", result["route_id"] or "-"),
        ("op_index", result["op_index"] if result["op_index"] is not None else "-"),
        ("namespace", result["namespace"] or "-"),
        ("namespace_status", result["namespace_status"] or "-"),
        ("source_binding_status", result["source_binding_status"] or "-"),
        ("source_location", result["source_location"] or "-"),
        ("expected_shot_mass", result["expected_shot_mass"] if result["expected_shot_mass"] is not None else "-"),
        ("packet", str(result["packet"]).lower()),
        ("closure", str(result["closure"]).lower()),
        ("failures", ",".join(result["failures"]) if result["failures"] else "-"),
        ("holds", ",".join(result["holds"]) if result["holds"] else "-"),
        ("warnings", ",".join(result["warnings"]) if result["warnings"] else "-"),
    ]
    print(" ".join(f"{key}={value}" for key, value in fields))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packets", nargs="+", type=Path)
    parser.add_argument("--expected-source", default=DEFAULT_SOURCE)
    parser.add_argument("--expected-qubits", type=int, default=DEFAULT_QUBITS)
    parser.add_argument("--required-mass", type=int, default=DEFAULT_REQUIRED_MASS)
    parser.add_argument("--require-pass", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    text = read_text(args.packets)
    result = inspect(text, args.expected_source, args.expected_qubits, args.required_mass)
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print_summary(result)
    if result["gate"] == "fail":
        return 2
    if args.require_pass and result["gate"] != "pass":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
