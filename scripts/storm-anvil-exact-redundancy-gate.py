#!/usr/bin/env python3
"""Gate single high-mass Anvil op exact-redundancy packets before review.

This public-safe parser checks redacted packet text only. It does not run
miners, build/eval, SSH job control, pods, alerts, or submit.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys
from typing import Iterable


DEFAULT_SHOTS = 9_024
DEFAULT_QUBITS = 1_152
DEFAULT_FRONTIER_TOFFOLI = 1_364_230
DEFAULT_FRONTIER_SCORE = 1_571_592_960
DEFAULT_TOTAL_TOFFOLI = 12_310_809_446
DELTA_TOLERANCE = 1e-9

NO_SUBMIT_RE = re.compile(r"\bno_submit_ack\s*[=:]\s*yes\b", re.IGNORECASE)
ROUTE_ID_RE = re.compile(r"\broute_id\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
OWNER_RE = re.compile(r"\b(?:owner|agent|validator)\s*[=:]\s*([A-Za-z0-9_.-]+)\b|\bACK\s+([A-Za-z0-9_.-]+)\b", re.IGNORECASE)
NEXT_RE = re.compile(r"\bnext\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
SOURCE_BASE_RE = re.compile(r"\b(?:source_base|source|base|source commit)\s*[=:]\s*([0-9a-f]{6,40})\b", re.IGNORECASE)
SOURCE_LOCATION_RE = re.compile(r"\b(?:source_location|site|file)\s*[=:]\s*((?:src/point_add)/[A-Za-z0-9_./+-]+\.rs:[0-9]+)\b", re.IGNORECASE)
SOURCE_HASH_RE = re.compile(r"\b(?:source_hash|source-hash|source_snippet_hash)\s*[=:]\s*([0-9a-fA-F]{8,64})\b", re.IGNORECASE)
CANDIDATE_HASH_RE = re.compile(
    r"\b(?:candidate_index_hash|candidate_diff_hash|candidate_hash|proof_hash|packet_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b",
    re.IGNORECASE,
)
LEDGER_HASH_RE = re.compile(r"\b(?:ledger_hash|mass_ledger_hash|raw_ledger_hash)\s*[=:]\s*([0-9a-fA-F]{8,64})\b", re.IGNORECASE)
CANDIDATE_CLASS_RE = re.compile(r"\b(?:candidate_class|route_class|class)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE)
CURRENT_Q_RE = re.compile(r"\b(?:current_q|q|qubits?)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
TARGET_Q_RE = re.compile(r"\btarget_q\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
FRONTIER_SCORE_RE = re.compile(r"\bfrontier(?:_score| score)?\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
CURRENT_TOTAL_RE = re.compile(r"\b(?:current_total_tof|current_total_toffoli|total_toffoli)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
OP_INDEX_RE = re.compile(r"\bop_index\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
KIND_RE = re.compile(r"\bkind\s*[=:]\s*(CCX|CCZ|TOFFOLI|T)\b", re.IGNORECASE)
Q_TARGET_RE = re.compile(r"\bq_target\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
Q_C1_RE = re.compile(r"\bq_c1\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
Q_C2_RE = re.compile(r"\bq_c2\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
C_CONDITION_RE = re.compile(r"\bc_condition\s*[=:]\s*(0x[0-9a-fA-F_]+|[0-9][0-9_]*)\b", re.IGNORECASE)
MASS_RE = re.compile(r"\b(?:expected_shot_mass|shot_mass|mass|expected_mass)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
DELTA_RE = re.compile(r"\b(?:expected_avgT_delta|expected_delta|avgT_delta|delta)\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
CANDIDATE_SCORE_RE = re.compile(r"\bcandidate_score\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
SCORE_EDGE_RE = re.compile(r"\bscore_edge\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
SUPPORT_STATUS_RE = re.compile(r"\bsupport_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN)\b", re.IGNORECASE)
PROOF_STATUS_RE = re.compile(r"\bproof_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN)\b", re.IGNORECASE)
EXACT_SUPPORT_RE = re.compile(r"\b(?:exact_support|value_proof|value_exact_status|redundancy_status)\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN)\b", re.IGNORECASE)
RESTORE_RE = re.compile(r"\brestore_proof\s*[=:]\s*(CERTIFIED|[01]|true|false|yes|no|unknown)\b", re.IGNORECASE)
PHASE_RE = re.compile(r"\bphase_proof\s*[=:]\s*(CERTIFIED|[01]|true|false|yes|no|unknown)\b", re.IGNORECASE)
ANCILLA_RE = re.compile(r"\bancilla_proof\s*[=:]\s*(CERTIFIED|[01]|true|false|yes|no|unknown)\b", re.IGNORECASE)
ALLOCATOR_RE = re.compile(r"\b(?:allocator_unchanged|allocator_order|allocator_order_hash|alloc_order)\s*[=:]\s*\S+", re.IGNORECASE)
EVIDENCE_LABEL_RE = re.compile(r"\bevidence_label\s*[=:]\s*(Prefilter|Counterexample|Partial|Local full run|Promoted)\b", re.IGNORECASE)
CLOSURE_RE = re.compile(r"\b(?:closure_reason|close_reason|counterexample_artifact|counterexample_file|falsifier|witness)\s*[=:]\s*\S+", re.IGNORECASE)
WITNESS_LIVE_RE = re.compile(r"\b(?:live_witness|witness_status|support_witness)\s*[=:]\s*(live|differs|different|counterexample)\b", re.IGNORECASE)
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


def first_status(pattern: re.Pattern[str], text: str) -> str:
    return first_match(pattern, text).upper()


def first_boolish(pattern: re.Pattern[str], text: str) -> bool | None:
    value = first_match(pattern, text).lower()
    if not value:
        return None
    if value in {"1", "true", "yes", "certified"}:
        return True
    if value in {"0", "false", "no", "unknown"}:
        return False
    return None


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


def win_total(frontier_toffoli: int, shots: int) -> int:
    return math.ceil((frontier_toffoli - 0.5) * shots) - 1


def rounded_score(total_toffoli: int, mass: int, qubits: int, shots: int) -> tuple[float, int, int]:
    candidate_avg = (total_toffoli - mass) / shots
    rounded_avg = math.floor(candidate_avg + 0.5)
    return candidate_avg, rounded_avg, rounded_avg * qubits


def almost_equal(left: float, right: float, tolerance: float = 1e-6) -> bool:
    return abs(left - right) <= tolerance


def inspect(
    text: str,
    expected_source: str,
    expected_qubits: int,
    shots: int,
    frontier_toffoli: int,
    default_frontier_score: float,
    default_total_toffoli: int,
) -> dict[str, object]:
    risk_text = risk_scan_text(text)
    route_id = first_match(ROUTE_ID_RE, text)
    owner = first_match(OWNER_RE, text)
    next_action = first_match(NEXT_RE, text)
    source_base = first_match(SOURCE_BASE_RE, text)
    source_location = first_match(SOURCE_LOCATION_RE, text)
    source_hash = first_match(SOURCE_HASH_RE, text)
    candidate_hash = first_match(CANDIDATE_HASH_RE, text)
    ledger_hash = first_match(LEDGER_HASH_RE, text)
    candidate_class = first_match(CANDIDATE_CLASS_RE, text).lower()
    qubits = first_int(CURRENT_Q_RE, text)
    target_q = first_int(TARGET_Q_RE, text)
    frontier_score = first_float(FRONTIER_SCORE_RE, text)
    if frontier_score is None:
        frontier_score = default_frontier_score
    total_toffoli = first_int(CURRENT_TOTAL_RE, text)
    if total_toffoli is None:
        total_toffoli = default_total_toffoli
    op_index = first_int(OP_INDEX_RE, text)
    kind = first_match(KIND_RE, text).upper()
    q_target = first_int(Q_TARGET_RE, text)
    q_c1 = first_int(Q_C1_RE, text)
    q_c2 = first_int(Q_C2_RE, text)
    c_condition = first_int(C_CONDITION_RE, text)
    mass = first_int(MASS_RE, text)
    delta = first_float(DELTA_RE, text)
    candidate_score = first_float(CANDIDATE_SCORE_RE, text)
    score_edge = first_float(SCORE_EDGE_RE, text)
    support_status = first_status(SUPPORT_STATUS_RE, text)
    proof_status = first_status(PROOF_STATUS_RE, text)
    exact_support = first_status(EXACT_SUPPORT_RE, text)
    restore_proof = first_boolish(RESTORE_RE, text)
    phase_proof = first_boolish(PHASE_RE, text)
    ancilla_proof = first_boolish(ANCILLA_RE, text)
    evidence_label = first_match(EVIDENCE_LABEL_RE, text)
    has_allocator = bool(ALLOCATOR_RE.search(text))
    required_drop = max(0, total_toffoli - win_total(frontier_toffoli, shots))
    implied_delta = -mass / shots if mass is not None and shots else None
    computed_avg = None
    computed_rounded_avg = None
    computed_score = None
    computed_edge = None
    if mass is not None and qubits is not None:
        computed_avg, computed_rounded_avg, computed_score = rounded_score(total_toffoli, mass, qubits, shots)
        computed_edge = frontier_score - computed_score

    certified = (
        support_status == "CERTIFIED"
        and proof_status == "CERTIFIED"
        and exact_support == "CERTIFIED"
        and restore_proof is True
        and phase_proof is True
        and ancilla_proof is True
    )
    closure = (
        support_status == "COUNTEREXAMPLE"
        or proof_status == "COUNTEREXAMPLE"
        or exact_support == "COUNTEREXAMPLE"
        or bool(CLOSURE_RE.search(text))
    )
    unknown = (
        support_status in {"UNKNOWN", "UNPROVEN"}
        or proof_status in {"UNKNOWN", "UNPROVEN"}
        or exact_support in {"UNKNOWN", "UNPROVEN"}
    )

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
    if target_q is not None and qubits is not None and target_q != qubits:
        failures.append("q_cut_claim_not_single_op_redundancy")
    if kind and kind not in {"CCX", "CCZ", "TOFFOLI"}:
        failures.append("unscored_or_unexpected_kind")
    if mass is not None and (mass < 0 or mass > shots):
        failures.append("mass_out_of_range")
    if not closure and mass is not None and mass < required_drop:
        failures.append("shot_mass_below_rounding_bar")
    if delta is not None and delta >= 0:
        failures.append("nonnegative_expected_delta")
    if delta is not None and implied_delta is not None and delta < implied_delta - DELTA_TOLERANCE:
        failures.append("delta_overclaims_shot_mass")
    if candidate_score is not None and computed_score is not None and not almost_equal(candidate_score, float(computed_score)):
        failures.append("candidate_score_mismatch")
    if score_edge is not None and computed_edge is not None and not almost_equal(score_edge, computed_edge):
        failures.append("score_edge_mismatch")
    if certified and computed_edge is not None and computed_edge <= 0:
        failures.append("certified_packet_has_no_score_edge")
    if evidence_label.lower() in {"local full run", "promoted"}:
        failures.append("packet_overclaims_result")
    if certified and WITNESS_LIVE_RE.search(text):
        failures.append("certified_packet_contains_live_counterexample_witness")
    if closure and certified:
        failures.append("packet_claims_both_certified_and_counterexample")

    for label, value in [
        ("missing_route_id", route_id),
        ("missing_owner", owner),
        ("missing_next_action", next_action),
        ("missing_source_base", source_base),
        ("missing_source_location", source_location),
        ("missing_source_hash", source_hash),
        ("missing_candidate_hash", candidate_hash),
        ("missing_candidate_class", candidate_class),
        ("missing_qubits", qubits),
        ("missing_op_index", op_index),
        ("missing_kind", kind),
        ("missing_q_target", q_target),
        ("missing_q_c1", q_c1),
        ("missing_q_c2", q_c2),
        ("missing_c_condition", c_condition),
        ("missing_expected_shot_mass", mass),
        ("missing_expected_avgT_delta", delta),
        ("missing_candidate_score", candidate_score),
        ("missing_score_edge", score_edge),
    ]:
        if value in {"", None}:
            holds.append(label)
    if "redundan" not in candidate_class and "exact_support" not in candidate_class and "exact-support" not in candidate_class:
        holds.append("candidate_class_not_exact_redundancy")
    if not ledger_hash:
        warnings.append("missing_mass_ledger_hash")
    if not support_status:
        holds.append("missing_support_status")
    if not proof_status:
        holds.append("missing_proof_status")
    if not exact_support:
        holds.append("missing_exact_support_status")
    if unknown:
        holds.append("proof_or_support_unknown")
    if restore_proof is not True and not closure:
        holds.append("restore_proof_missing")
    if phase_proof is not True and not closure:
        holds.append("phase_proof_missing")
    if ancilla_proof is not True and not closure:
        holds.append("ancilla_proof_missing")
    if not evidence_label:
        holds.append("missing_evidence_label")
    elif evidence_label.lower() not in {"prefilter", "partial", "counterexample"}:
        holds.append("evidence_label_not_prefilter_partial_or_counterexample")
    if not has_allocator and not closure:
        holds.append("missing_allocator_order")
    if closure and not CLOSURE_RE.search(text):
        holds.append("missing_closure_reason_or_counterexample_artifact")
    if not certified and not closure:
        holds.append("missing_certified_or_counterexample_decision")
    if not REMOTE_RE.search(text):
        warnings.append("missing_remote_or_studio_context")

    if failures:
        gate = "fail"
        decision = "reject-anvil-exact-redundancy-packet"
    elif holds:
        gate = "hold"
        decision = "complete-anvil-exact-redundancy-proof-no-compute"
    elif closure:
        gate = "pass"
        decision = "anvil-exact-redundancy-counterexample-closed-no-compute"
    else:
        gate = "pass"
        decision = "anvil-exact-redundancy-review-no-compute"

    return {
        "gate": gate,
        "decision": decision,
        "route_id": route_id,
        "owner": owner,
        "next_action": next_action,
        "source_base": source_base,
        "expected_source": expected_source,
        "source_location": source_location,
        "source_hash": bool(source_hash),
        "candidate_hash": bool(candidate_hash),
        "ledger_hash": bool(ledger_hash),
        "candidate_class": candidate_class or "missing",
        "qubits": qubits,
        "target_q": target_q,
        "expected_qubits": expected_qubits,
        "op_index": op_index,
        "kind": kind or "missing",
        "q_target": q_target,
        "q_c1": q_c1,
        "q_c2": q_c2,
        "c_condition": c_condition,
        "expected_shot_mass": mass,
        "required_drop": required_drop,
        "expected_avgT_delta": delta,
        "implied_avgT_delta": implied_delta,
        "candidate_avg": computed_avg,
        "candidate_avg_rounded": computed_rounded_avg,
        "candidate_score": candidate_score,
        "computed_candidate_score": computed_score,
        "score_edge": score_edge,
        "computed_score_edge": computed_edge,
        "frontier_score": frontier_score,
        "current_total_toffoli": total_toffoli,
        "support_status": support_status or "missing",
        "proof_status": proof_status or "missing",
        "exact_support": exact_support or "missing",
        "restore_proof": restore_proof,
        "phase_proof": phase_proof,
        "ancilla_proof": ancilla_proof,
        "evidence_label": evidence_label or "missing",
        "allocator_order": has_allocator,
        "closure": closure,
        "certified": certified,
        "no_submit_ack": bool(NO_SUBMIT_RE.search(text)),
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
        f"anvil_exact_redundancy_gate={row['gate']} "
        f"route_id={row['route_id'] or 'missing'} owner={row['owner'] or 'missing'} "
        f"next={row['next_action'] or 'missing'} source_base={row['source_base'] or 'missing'} "
        f"expected_source={row['expected_source'] or 'none'} source_location={row['source_location'] or 'missing'} "
        f"source_hash={str(row['source_hash']).lower()} candidate_hash={str(row['candidate_hash']).lower()} "
        f"ledger_hash={str(row['ledger_hash']).lower()} candidate_class={row['candidate_class']} "
        f"qubits={row['qubits']} target_q={row['target_q']} expected_qubits={row['expected_qubits']} "
        f"op_index={row['op_index']} kind={row['kind']} q_target={row['q_target']} q_c1={row['q_c1']} "
        f"q_c2={row['q_c2']} expected_shot_mass={row['expected_shot_mass']} required_drop={row['required_drop']} "
        f"expected_avgT_delta={row['expected_avgT_delta']} implied_avgT_delta={row['implied_avgT_delta']} "
        f"candidate_avg_rounded={row['candidate_avg_rounded']} candidate_score={row['candidate_score']} "
        f"computed_candidate_score={row['computed_candidate_score']} score_edge={row['score_edge']} "
        f"computed_score_edge={row['computed_score_edge']} support_status={row['support_status']} "
        f"proof_status={row['proof_status']} exact_support={row['exact_support']} "
        f"restore_proof={row['restore_proof']} phase_proof={row['phase_proof']} "
        f"ancilla_proof={row['ancilla_proof']} evidence_label={row['evidence_label']} "
        f"allocator_order={str(row['allocator_order']).lower()} certified={str(row['certified']).lower()} "
        f"closure={str(row['closure']).lower()} no_submit_ack={str(row['no_submit_ack']).lower()} "
        f"decision={row['decision']} failures={join(row['failures'])} holds={join(row['holds'])} "
        f"warnings={join(row['warnings'])}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--expected-source", default="d44cad3")
    parser.add_argument("--expected-qubits", type=int, default=DEFAULT_QUBITS)
    parser.add_argument("--shots", type=int, default=DEFAULT_SHOTS)
    parser.add_argument("--frontier-toffoli", type=int, default=DEFAULT_FRONTIER_TOFFOLI)
    parser.add_argument("--frontier-score", type=float, default=DEFAULT_FRONTIER_SCORE)
    parser.add_argument("--current-total-toffoli", type=int, default=DEFAULT_TOTAL_TOFFOLI)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    missing = [str(path) for path in args.inputs if not path.is_file()]
    if missing:
        print(f"anvil_exact_redundancy_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
        return 2

    row = inspect(
        read_text(args.inputs),
        args.expected_source,
        args.expected_qubits,
        args.shots,
        args.frontier_toffoli,
        args.frontier_score,
        args.current_total_toffoli,
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
