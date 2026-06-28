#!/usr/bin/env python3
"""Gate combined real-emit support packets before compute review.

This public-safe parser checks redacted same-invariant emit-bundle packets or
counterexample closures. It does not run miners, build/eval, SSH job control,
pods, alerts, or submit.
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
DEFAULT_FRONTIER_TOFFOLI = 1_364_230
DEFAULT_TOTAL_TOFFOLI = 12_310_809_446
DELTA_TOLERANCE = 1e-9

NO_SUBMIT_RE = re.compile(r"\bno_submit_ack\s*=\s*yes\b", re.IGNORECASE)
ROUTE_ID_RE = re.compile(r"\broute_id\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
OWNER_RE = re.compile(r"\b(?:owner|agent|validator)\s*[=:]\s*([A-Za-z0-9_.-]+)\b|\bACK\s+([A-Za-z0-9_.-]+)\b", re.IGNORECASE)
NEXT_RE = re.compile(r"\bnext\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
SOURCE_BASE_RE = re.compile(r"\b(?:source_base|source|base|source commit)\s*[=:]\s*([0-9a-f]{6,40})\b", re.IGNORECASE)
QUBITS_RE = re.compile(r"\b(?:q|qubits?)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
FRONTIER_SCORE_RE = re.compile(r"\bfrontier(?:_score| score)?\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
ROW_COUNT_RE = re.compile(r"\b(?:row_count|rows|bundle_rows)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
TOTAL_MASS_RE = re.compile(r"\b(?:expected_shot_mass|shot_mass|bundle_shot_mass|total_shot_mass|sum_count)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
MAX_SINGLE_RE = re.compile(r"\b(?:max_single_shot_mass|max_single_count|max_row_count)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
DELTA_RE = re.compile(r"\b(?:expected_avgT_delta|expected_delta|avgT_delta|delta)\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
CANDIDATE_HASH_RE = re.compile(
    r"\b(?:candidate_index_hash|candidate_diff_hash|candidate_hash|diff_hash|index_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b",
    re.IGNORECASE,
)
SOURCE_LOCATION_ANY_RE = re.compile(r"src/point_add/[A-Za-z0-9_./+-]+\.rs:[0-9]+")
HASH_TOKEN_RE = re.compile(r"\b[0-9a-fA-F]{8,64}\b")
SOURCE_HASH_KEY_RE = re.compile(r"\b(?:source_hash|source_hashes|source-hash|source_snippet_hash|source_snippet_hashes)\s*[=:]\s*([0-9a-fA-F,._:-]+)", re.IGNORECASE)
SHARED_INVARIANT_RE = re.compile(r"\b(?:shared_invariant|same_invariant|bundle_invariant|literal_shared_invariant)\s*[=:]\s*(yes|true|1|no|false|0|unknown)\b", re.IGNORECASE)
WITNESS_RE = re.compile(r"\b(?:witness_status|witnesses|support_witness)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE)
SUPPORT_STATUS_RE = re.compile(r"\bsupport_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN)\b", re.IGNORECASE)
PROOF_STATUS_RE = re.compile(r"\bproof_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN)\b", re.IGNORECASE)
RESTORE_RE = re.compile(r"\brestore_proof\s*[=:]\s*([01]|true|false|yes|no)\b", re.IGNORECASE)
PHASE_RE = re.compile(r"\bphase_proof\s*[=:]\s*([01]|true|false|yes|no)\b", re.IGNORECASE)
EVIDENCE_LABEL_RE = re.compile(r"\bevidence_label\s*[=:]\s*(Prefilter|Counterexample|Partial|Local full run|Promoted)\b", re.IGNORECASE)
CLOSURE_RE = re.compile(r"\b(?:closure_reason|close_reason|counterexample_artifact|counterexample_file)\s*[=:]\s*\S+", re.IGNORECASE)
CLOSED_OR_DEFAULT_RE = re.compile(
    r"\b(?:closed_ledger_hit|ledger_hit|default_on_table|default_on_table_status|table_origin|default_on|already_harvested)\s*[=:]\s*(yes|true|1|default_on|table_origin|closed|hit)\b",
    re.IGNORECASE,
)
LIVE_WITNESS_RE = re.compile(r"\b(?:any_row_live|live_witness|row_live|witnesses_differ)\s*[=:]\s*(yes|true|1|live|differs|different)\b", re.IGNORECASE)
COMPUTE_REQUEST_RE = re.compile(
    r"\b(?:launch|start|restart|rearm|scale|dispatch|residual|benchmark|run|route_compare)\b.{0,100}\b(?:pods?|runpod|vast|gpus?|cpus?|scanner|residual|9024|benchmark|eval)\b|"
    r"\b(?:gpu_forever|gpu_island2|fanout_nonce_eval|build_circuit|eval_circuit|count_tof|drop_effect_probe|storm-exact-miner)\b",
    re.IGNORECASE,
)
PREMATURE_RE = re.compile(r"\b(?:FOR[- ]AKASH|WINNER|mobile alert|submit(?:ted)?|ready[- ]to[- ]submit|Akash-ready)\b", re.IGNORECASE)
LOCAL_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:mac|macbook|local|darwin)\b|\b(?:MacBook|mac-local|/Users/[A-Za-z0-9_.-]+)\b", re.IGNORECASE)
REMOTE_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:studio|runpod|vast|pod|remote)\b|\bstudio\b", re.IGNORECASE)
NEGATED_GUARDRAIL_RE = re.compile(
    r"\b(?:no|never)\s+(?:compute|pods?|residual|route[-_ ]?compare|benchmark|alert|winner|akash|submit|submission)\b|"
    r"\b(?:do not|must not|cannot|can not)\s+(?:launch|start|restart|rearm|scale|dispatch|run|trigger|alert|write|submit)\b|"
    r"\b(?:does not|do not)\s+(?:authorize|license)\b|"
    r"\bnot\s+(?:authorized|licensed|allowed|a submit|a submission|ready[- ]to[- ]submit)\b|"
    r"\bwithout\s+storm[-_ ]?(?:compute[-_ ]?)?unlock\b",
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


def first_bool(pattern: re.Pattern[str], text: str) -> bool | None:
    value = first_match(pattern, text).lower()
    if not value:
        return None
    if value in {"1", "true", "yes"}:
        return True
    if value in {"0", "false", "no"}:
        return False
    return None


def source_hashes(text: str) -> list[str]:
    values: list[str] = []
    for match in SOURCE_HASH_KEY_RE.finditer(text):
        values.extend(HASH_TOKEN_RE.findall(match.group(1)))
    return values


def risk_scan_text(text: str) -> str:
    """Drop explicit negative guardrails before scanning for risky requests."""
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


def inspect(text: str, expected_source: str, expected_qubits: int, shots: int, frontier_toffoli: int, current_total: int) -> dict[str, object]:
    risk_text = risk_scan_text(text)
    route_id = first_match(ROUTE_ID_RE, text)
    owner = first_match(OWNER_RE, text)
    next_action = first_match(NEXT_RE, text)
    source_base = first_match(SOURCE_BASE_RE, text)
    qubits = first_int(QUBITS_RE, text)
    frontier_score = first_float(FRONTIER_SCORE_RE, text)
    row_count = first_int(ROW_COUNT_RE, text)
    total_mass = first_int(TOTAL_MASS_RE, text)
    max_single = first_int(MAX_SINGLE_RE, text)
    delta = first_float(DELTA_RE, text)
    candidate_hash = first_match(CANDIDATE_HASH_RE, text)
    locations = sorted(set(SOURCE_LOCATION_ANY_RE.findall(text)))
    hashes = sorted(set(source_hashes(text)))
    shared_invariant = first_bool(SHARED_INVARIANT_RE, text)
    witness_status = first_match(WITNESS_RE, text).lower()
    support_status = first_match(SUPPORT_STATUS_RE, text).upper()
    proof_status = first_match(PROOF_STATUS_RE, text).upper()
    restore_proof = first_bool(RESTORE_RE, text)
    phase_proof = first_bool(PHASE_RE, text)
    evidence_label = first_match(EVIDENCE_LABEL_RE, text)
    required_drop = max(0, current_total - win_total(frontier_toffoli, shots))
    implied_delta = -total_mass / shots if total_mass is not None and shots else None
    certified = support_status == "CERTIFIED" and proof_status == "CERTIFIED"
    closure = support_status == "COUNTEREXAMPLE" or proof_status == "COUNTEREXAMPLE" or bool(CLOSURE_RE.search(text))
    unknown = support_status in {"UNKNOWN", "UNPROVEN"} or proof_status in {"UNKNOWN", "UNPROVEN"}

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
    if unknown:
        failures.append("proof_unknown_close_as_nack")
    if not closure and total_mass is not None and total_mass < required_drop:
        failures.append("bundle_mass_below_rounding_bar")
    if not closure and row_count is not None and row_count < 2:
        failures.append("single_row_not_bundle")
    if certified and max_single is not None and max_single >= required_drop:
        failures.append("single_row_clears_bar_use_single_packet_gate")
    if not closure and shared_invariant is False:
        failures.append("bundle_not_shared_invariant")
    if certified and (CLOSED_OR_DEFAULT_RE.search(text) or "closed" in witness_status or "default" in witness_status):
        failures.append("closed_or_default_on_row_in_bundle")
    if not closure and (LIVE_WITNESS_RE.search(text) or "live" in witness_status or "differ" in witness_status):
        failures.append("live_or_different_witness_in_bundle")
    if certified and delta is not None and delta >= 0:
        failures.append("nonnegative_certified_delta")
    if certified and delta is not None and implied_delta is not None and delta < implied_delta - DELTA_TOLERANCE:
        failures.append("delta_overclaims_bundle_mass")
    if evidence_label.lower() in {"local full run", "promoted"}:
        failures.append("packet_overclaims_result")

    for label, value in [
        ("missing_route_id", route_id),
        ("missing_owner", owner),
        ("missing_next_action", next_action),
        ("missing_source_base", source_base),
        ("missing_candidate_hash", candidate_hash),
    ]:
        if not value:
            holds.append(label)
    if frontier_score is None:
        holds.append("missing_frontier_score")
    if qubits is None:
        holds.append("missing_qubits")
    if row_count is None:
        holds.append("missing_row_count")
    if total_mass is None:
        holds.append("missing_expected_shot_mass")
    if max_single is None:
        holds.append("missing_max_single_shot_mass")
    if len(locations) < 2 and not closure:
        holds.append("missing_multiple_source_locations")
    if not hashes:
        holds.append("missing_source_hashes")
    if shared_invariant is None and not closure:
        holds.append("missing_shared_invariant")
    if not witness_status and not closure:
        holds.append("missing_witness_status")
    if not support_status:
        holds.append("missing_support_status")
    if not proof_status:
        holds.append("missing_proof_status")
    if restore_proof is not True:
        holds.append("restore_proof_missing")
    if phase_proof is not True:
        holds.append("phase_proof_missing")
    if certified and delta is None:
        holds.append("missing_counted_negative_delta")
    if closure and not CLOSURE_RE.search(text):
        holds.append("missing_closure_reason_or_artifact")
    if not certified and not closure and not unknown:
        holds.append("missing_certified_or_counterexample_decision")
    if evidence_label and evidence_label.lower() not in {"prefilter", "counterexample", "partial"}:
        holds.append("evidence_label_not_prefilter_counterexample_or_partial")
    if not REMOTE_RE.search(text):
        warnings.append("missing_remote_or_studio_context")

    if failures:
        gate = "fail"
        decision = "close-emit-bundle-nack"
    elif holds:
        gate = "hold"
        decision = "complete-emit-bundle-support-packet"
    elif closure:
        gate = "pass"
        decision = "emit-bundle-counterexample-closed-no-compute"
    else:
        gate = "pass"
        decision = "emit-bundle-certified-no-compute-review"

    return {
        "gate": gate,
        "decision": decision,
        "route_id": route_id,
        "owner": owner,
        "source_base": source_base,
        "q": qubits,
        "row_count": row_count,
        "source_locations": len(locations),
        "source_hashes": len(hashes),
        "candidate_hash": bool(candidate_hash),
        "expected_shot_mass": total_mass,
        "max_single_shot_mass": max_single,
        "required_drop": required_drop,
        "implied_avgT_delta": implied_delta,
        "delta": delta,
        "shared_invariant": shared_invariant,
        "witness_status": witness_status or "missing",
        "support_status": support_status or "missing",
        "proof_status": proof_status or "missing",
        "restore_proof": restore_proof,
        "phase_proof": phase_proof,
        "closure": closure,
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
        f"emit_bundle_support_gate={row['gate']} decision={row['decision']} "
        f"route_id={row['route_id'] or 'missing'} owner={row['owner'] or 'missing'} "
        f"source_base={row['source_base'] or 'missing'} q={row['q']} row_count={row['row_count']} "
        f"source_locations={row['source_locations']} source_hashes={row['source_hashes']} "
        f"candidate_hash={str(row['candidate_hash']).lower()} expected_shot_mass={row['expected_shot_mass']} "
        f"max_single_shot_mass={row['max_single_shot_mass']} required_drop={row['required_drop']} "
        f"implied_avgT_delta={row['implied_avgT_delta']} delta={row['delta']} "
        f"shared_invariant={row['shared_invariant']} witness_status={row['witness_status']} "
        f"support_status={row['support_status']} proof_status={row['proof_status']} "
        f"restore_proof={row['restore_proof']} phase_proof={row['phase_proof']} closure={row['closure']} "
        f"no_submit_ack={str(row['no_submit_ack']).lower()} failures={join(row['failures'])} "
        f"holds={join(row['holds'])} warnings={join(row['warnings'])}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path, nargs="+")
    parser.add_argument("--expected-source", default="d44cad3")
    parser.add_argument("--expected-qubits", type=int, default=1152)
    parser.add_argument("--shots", type=int, default=DEFAULT_SHOTS)
    parser.add_argument("--frontier-toffoli", type=int, default=DEFAULT_FRONTIER_TOFFOLI)
    parser.add_argument("--current-total-toffoli", type=int, default=DEFAULT_TOTAL_TOFFOLI)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    missing = [str(path) for path in args.packet if not path.is_file()]
    if missing:
        print(f"emit_bundle_support_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
        return 2
    row = inspect(read_text(args.packet), args.expected_source, args.expected_qubits, args.shots, args.frontier_toffoli, args.current_total_toffoli)
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
