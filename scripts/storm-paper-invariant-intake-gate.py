#!/usr/bin/env python3
"""Gate paper-mining model-pass packets before skill or route promotion.

This public-safe parser checks redacted paper/model-pass summaries. It does not
fetch papers, run miners, build/eval, SSH job control, alerts, or submit.
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
SKILL_NAME_RE = re.compile(r"\b(?:skill_name|skill-card|skill_card)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE)
PAPER_RE = re.compile(r"\b(?:paper_url|paper|arxiv|doi)\s*[=:]\s*([A-Za-z0-9_.:/?&=#%+-]+)\b", re.IGNORECASE)
SOURCE_BASE_RE = re.compile(r"\b(?:source_base|source|base|source commit)\s*[=:]\s*([0-9a-f]{6,40})\b", re.IGNORECASE)
SOURCE_HASH_RE = re.compile(r"\b(?:source_hash|source-hash|source_snippet_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b", re.IGNORECASE)
CANDIDATE_HASH_RE = re.compile(
    r"\b(?:candidate_index_hash|candidate_diff_hash|candidate_hash|diff_hash|index_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b",
    re.IGNORECASE,
)
SOURCE_LOCATION_RE = re.compile(
    r"\b(?:source_location|source_file|site|file)\s*[=:]\s*((?:src/point_add)/[A-Za-z0-9_./+-]+\.rs(?::[0-9]+)?)\b",
    re.IGNORECASE,
)
QUBITS_RE = re.compile(r"\b(?:q|qubits?)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
FRONTIER_SCORE_RE = re.compile(r"\bfrontier(?:_score| score)?\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
SCORE_EDGE_RE = re.compile(r"\bscore_edge\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
DELTA_RE = re.compile(r"\b(?:expected_avgT_delta|expected_delta|avgT_delta|delta)\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
EVIDENCE_LABEL_RE = re.compile(r"\bevidence_label\s*[=:]\s*(Prefilter|Partial|Paper score|Historical clue|Local full run|Promoted)\b", re.IGNORECASE)
LOCAL_INVARIANT_RE = re.compile(
    r"\b(?:local_invariant|exact_local_invariant|source_invariant)\s*[=:]\s*([A-Za-z0-9_.:/@,+-]+)\b",
    re.IGNORECASE,
)
SCORED_IR_EFFECT_RE = re.compile(
    r"\b(?:scored_IR_effect|scored_ir_effect|ir_effect)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b",
    re.IGNORECASE,
)
CONDITION_SOURCE_RE = re.compile(r"\bcondition_source\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE)
SUPPORT_STATUS_RE = re.compile(r"\bsupport_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN)\b", re.IGNORECASE)
PROOF_STATUS_RE = re.compile(r"\bproof_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN)\b", re.IGNORECASE)
SOURCE_BOUND_RE = re.compile(r"\b(?:source-hash-bound|source_bound\s*[=:]\s*yes|source_hash\s*[=:]|source-bound)\b", re.IGNORECASE)
SOURCE_BACKED_RE = re.compile(r"\b(?:source_backed|source-backed)\s*[=:]\s*(yes|true|1)\b", re.IGNORECASE)
PAPER_ONLY_RE = re.compile(r"\b(?:paper_only|paper-only|scout_only|scout-only)\s*[=:]\s*(yes|true|1)\b", re.IGNORECASE)

COMPUTE_REQUEST_RE = re.compile(
    r"\b(?:launch|start|restart|rearm|scale|dispatch|residual|benchmark|run)\b.{0,100}\b(?:pods?|runpod|vast|gpus?|cpus?|scanner|residual|9024|benchmark|eval)\b|"
    r"\b(?:gpu_forever|gpu_island2|fanout_nonce_eval|build_circuit|eval_circuit|count_tof|drop_effect_probe|storm-exact-miner)\b",
    re.IGNORECASE,
)
PREMATURE_RE = re.compile(r"\b(?:FOR[- ]AKASH|WINNER|mobile alert|submit(?:ted)?|ready[- ]to[- ]submit|Akash-ready)\b", re.IGNORECASE)
LOCAL_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:mac|macbook|local|darwin)\b|\b(?:MacBook|mac-local|/Users/[A-Za-z0-9_.-]+)\b", re.IGNORECASE)
REMOTE_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:studio|runpod|vast|pod|remote)\b|\b(?:studio|runpod:|vast:|owned pod|owned-pod)\b", re.IGNORECASE)

SCORE_VISIBLE_EFFECTS = {
    "delete_ccx_ccz",
    "classically_discount_ccx_ccz",
    "trusted_eval_avgt_cut",
}
NO_SCORE_EFFECTS = {
    "no_score_effect",
    "t_depth_only",
    "relative_phase_only",
    "paper_only",
    "none",
}
VALID_CONDITION_SOURCES = {"measured_bit", "condition_stack", "trusted_eval", "none"}


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
        return float(value.replace("_", ""))
    except ValueError:
        return None


def first_int(pattern: re.Pattern[str], text: str) -> int | None:
    value = first_match(pattern, text)
    if not value:
        return None
    try:
        return int(value.replace("_", ""), 0)
    except ValueError:
        return None


def normalize(value: str) -> str:
    return value.strip().lower().replace("-", "_")


def inspect(text: str, expected_source: str, expected_qubits: int) -> dict[str, object]:
    route_id = first_match(ROUTE_ID_RE, text)
    owner = first_match(OWNER_RE, text)
    next_action = first_match(NEXT_RE, text)
    skill_name = first_match(SKILL_NAME_RE, text)
    paper = first_match(PAPER_RE, text)
    source_base = first_match(SOURCE_BASE_RE, text)
    source_hash = first_match(SOURCE_HASH_RE, text)
    candidate_hash = first_match(CANDIDATE_HASH_RE, text)
    source_location = first_match(SOURCE_LOCATION_RE, text)
    qubits = first_int(QUBITS_RE, text)
    frontier_score = first_float(FRONTIER_SCORE_RE, text)
    score_edge = first_float(SCORE_EDGE_RE, text)
    delta = first_float(DELTA_RE, text)
    evidence_label = first_match(EVIDENCE_LABEL_RE, text)
    local_invariant = first_match(LOCAL_INVARIANT_RE, text)
    scored_ir_effect = normalize(first_match(SCORED_IR_EFFECT_RE, text))
    condition_source = normalize(first_match(CONDITION_SOURCE_RE, text))
    support_status = first_match(SUPPORT_STATUS_RE, text).upper()
    proof_status = first_match(PROOF_STATUS_RE, text).upper()

    has_no_submit = bool(NO_SUBMIT_RE.search(text))
    has_source_bound = bool(source_hash and SOURCE_BOUND_RE.search(text))
    has_source_backed = bool(SOURCE_BACKED_RE.search(text) or (source_location and local_invariant and has_source_bound))
    has_paper_only = bool(PAPER_ONLY_RE.search(text))
    has_compute_request = bool(COMPUTE_REQUEST_RE.search(text))
    has_premature = bool(PREMATURE_RE.search(text))
    has_local = bool(LOCAL_RE.search(text))
    has_remote = bool(REMOTE_RE.search(text))
    score_visible = scored_ir_effect in SCORE_VISIBLE_EFFECTS
    no_score_effect = scored_ir_effect in NO_SCORE_EFFECTS
    certified = support_status == "CERTIFIED" and proof_status == "CERTIFIED"
    counterexample = support_status == "COUNTEREXAMPLE" or proof_status == "COUNTEREXAMPLE"
    unknown_proof = support_status in {"UNKNOWN", "UNPROVEN"} or proof_status in {"UNKNOWN", "UNPROVEN"}
    negative_edge = (score_edge is not None and score_edge > 0) or (delta is not None and delta < 0)

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []

    if has_local:
        failures.append("local_heavy_context")
    if has_paper_only:
        failures.append("paper_only_scout")
    if no_score_effect:
        failures.append("no_score_visible_ir_effect")
    if counterexample:
        failures.append("support_or_proof_counterexample")
    if score_edge is not None and score_edge <= 0:
        failures.append("score_no_edge")
    if delta is not None and delta >= 0:
        failures.append("nonnegative_expected_delta")
    if expected_source and source_base and source_base != expected_source:
        failures.append("stale_source_base")
    if expected_qubits > 0 and qubits is not None and qubits != expected_qubits:
        failures.append("wrong_qubit_tier")
    if evidence_label.lower() in {"local full run", "promoted"}:
        failures.append("paper_packet_overclaims_result")
    if has_compute_request:
        failures.append("premature_compute_or_residual_request")
    if has_premature:
        failures.append("premature_submit_or_akash_language")
    if not has_no_submit:
        failures.append("missing_no_submit_ack")

    if not route_id:
        holds.append("missing_route_id")
    if not owner:
        holds.append("missing_owner")
    if not next_action:
        holds.append("missing_next_action")
    if not skill_name:
        holds.append("missing_skill_name")
    if not paper:
        holds.append("missing_paper_reference")
    if not source_base:
        holds.append("missing_source_base")
    if frontier_score is None:
        holds.append("missing_frontier_score")
    if qubits is None:
        holds.append("missing_qubits")
    if not source_hash:
        holds.append("missing_source_hash")
    if not candidate_hash:
        holds.append("missing_candidate_hash")
    if not has_source_bound:
        holds.append("missing_source_hash_bound_context")
    if not source_location:
        holds.append("missing_source_location")
    if not local_invariant:
        holds.append("missing_local_invariant")
    if not has_source_backed:
        holds.append("missing_source_backed_flag")
    if not scored_ir_effect:
        holds.append("missing_scored_ir_effect")
    elif not score_visible and not no_score_effect:
        holds.append("unknown_scored_ir_effect")
    if scored_ir_effect == "classically_discount_ccx_ccz":
        if not condition_source:
            holds.append("missing_condition_source")
        elif condition_source not in VALID_CONDITION_SOURCES - {"none"}:
            holds.append("unsupported_condition_source")
    elif condition_source and condition_source not in VALID_CONDITION_SOURCES:
        holds.append("unsupported_condition_source")
    if not support_status:
        holds.append("missing_support_status")
    if not proof_status:
        holds.append("missing_proof_status")
    if unknown_proof:
        holds.append("support_or_proof_unknown")
    if not negative_edge:
        holds.append("missing_negative_score_edge")
    if not evidence_label:
        holds.append("missing_evidence_label")
    elif evidence_label.lower() not in {"prefilter", "partial", "paper score", "historical clue"}:
        holds.append("evidence_label_not_prefilter_partial_or_paper")
    if not has_remote:
        warnings.append("missing_remote_or_studio_route")

    if failures:
        gate = "fail"
        decision = "do-not-promote-paper-hit"
    elif holds:
        gate = "hold"
        decision = "complete-source-backed-paper-invariant"
    else:
        gate = "pass"
        decision = "source-backed-skill-review-no-compute"

    return {
        "gate": gate,
        "decision": decision,
        "route_id": route_id,
        "owner": owner,
        "next_action": next_action,
        "skill_name": skill_name,
        "paper_reference": paper,
        "source_base": source_base,
        "expected_source": expected_source,
        "source_hash_bound": has_source_bound,
        "candidate_hash_bound": bool(candidate_hash),
        "source_location": source_location,
        "source_backed": has_source_backed,
        "frontier_score": frontier_score,
        "qubits": qubits,
        "expected_qubits": expected_qubits,
        "score_edge": score_edge,
        "delta": delta,
        "negative_edge": negative_edge,
        "evidence_label": evidence_label,
        "local_invariant": bool(local_invariant),
        "scored_ir_effect": scored_ir_effect,
        "score_visible_effect": score_visible,
        "condition_source": condition_source,
        "support_status": support_status,
        "proof_status": proof_status,
        "certified": certified,
        "paper_only": has_paper_only,
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
        f"paper_invariant_intake_gate={row['gate']} route_id={row['route_id'] or 'missing'} "
        f"owner={row['owner'] or 'missing'} next={row['next_action'] or 'missing'} "
        f"skill_name={row['skill_name'] or 'missing'} paper_reference={row['paper_reference'] or 'missing'} "
        f"source_base={row['source_base'] or 'missing'} expected_source={row['expected_source'] or 'none'} "
        f"source_hash_bound={str(row['source_hash_bound']).lower()} "
        f"candidate_hash_bound={str(row['candidate_hash_bound']).lower()} "
        f"source_location={row['source_location'] or 'missing'} source_backed={str(row['source_backed']).lower()} "
        f"frontier_score={row['frontier_score']} qubits={row['qubits']} expected_qubits={row['expected_qubits']} "
        f"score_edge={row['score_edge']} delta={row['delta']} negative_edge={str(row['negative_edge']).lower()} "
        f"evidence_label={row['evidence_label'] or 'missing'} local_invariant={str(row['local_invariant']).lower()} "
        f"scored_ir_effect={row['scored_ir_effect'] or 'missing'} "
        f"score_visible_effect={str(row['score_visible_effect']).lower()} "
        f"condition_source={row['condition_source'] or 'missing'} "
        f"support_status={row['support_status'] or 'missing'} proof_status={row['proof_status'] or 'missing'} "
        f"certified={str(row['certified']).lower()} paper_only={str(row['paper_only']).lower()} "
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
        print(f"paper_invariant_intake_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
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
