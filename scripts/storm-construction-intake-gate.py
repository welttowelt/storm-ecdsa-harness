#!/usr/bin/env python3
"""Gate paper-mined construction intake packets before route promotion.

This public-safe parser checks redacted construction packets. It does not fetch
papers, run miners, build/eval, SSH job control, pods, alerts, or submit.
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
PAPER_RE = re.compile(r"\b(?:paper_url|paper|arxiv|doi)\s*[=:]\s*([A-Za-z0-9_.:/?&=#%+-]+)\b", re.IGNORECASE)
SOURCE_BASE_RE = re.compile(r"\b(?:source_base|source|base|source commit)\s*[=:]\s*([0-9a-f]{6,40})\b", re.IGNORECASE)
SOURCE_HASH_RE = re.compile(r"\b(?:source_hash|source-hash|source_snippet_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b", re.IGNORECASE)
CANDIDATE_HASH_RE = re.compile(
    r"\b(?:candidate_index_hash|candidate_diff_hash|candidate_hash|diff_hash|index_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b",
    re.IGNORECASE,
)
SOURCE_LOCATION_RE = re.compile(r"\b(?:source_location|source_file|site|file)\s*[=:]\s*((?:src/point_add)/[A-Za-z0-9_./+-]+\.rs(?::[0-9]+)?)\b", re.IGNORECASE)
REPLACEMENT_RE = re.compile(r"\b(?:source_replacement|replacement_primitive|construction|construction_replacement)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE)
CURRENT_Q_RE = re.compile(r"\b(?:current_q|current_qubits)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
TARGET_Q_RE = re.compile(r"\b(?:target_q|target_qubits|q)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
CURRENT_AVG_RE = re.compile(r"\b(?:current_avg_tof|current_avgT|baseline_avg_tof)\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
EXTRA_AVG_RE = re.compile(r"\b(?:extra_avg_tof|predicted_extra_avgT|extra_avgT)\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
CANDIDATE_AVG_RE = re.compile(r"\b(?:candidate_avg_tof|predicted_avg_tof|candidate_avgT)\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
CANDIDATE_SCORE_RE = re.compile(r"\b(?:candidate_score|predicted_score)\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
FRONTIER_SCORE_RE = re.compile(r"\bfrontier(?:_score| score)?\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
SCORE_EDGE_RE = re.compile(r"\bscore_edge\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
RESTORE_OBLIGATION_RE = re.compile(r"\b(?:restore_obligation|restoration_obligation)\s*[=:]\s*([A-Za-z0-9_.:/@,+-]+)\b", re.IGNORECASE)
PHASE_OBLIGATION_RE = re.compile(r"\bphase_obligation\s*[=:]\s*([A-Za-z0-9_.:/@,+-]+)\b", re.IGNORECASE)
ANCILLA_OBLIGATION_RE = re.compile(r"\bancilla_obligation\s*[=:]\s*([A-Za-z0-9_.:/@,+-]+)\b", re.IGNORECASE)
TOY_RE = re.compile(r"\b(?:toy_falsifier|bounded_toy_falsifier|falsifier)\s*[=:]\s*([A-Za-z0-9_.:/@,+-]+)\b", re.IGNORECASE)
BOUNDED_RE = re.compile(r"\b(?:bounded_toy|toy_bounded|bounded_falsifier)\s*[=:]\s*(yes|true|1)\b|\bbounded[-_ ]toy\b", re.IGNORECASE)
SUPPORT_STATUS_RE = re.compile(r"\bsupport_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN)\b", re.IGNORECASE)
PROOF_STATUS_RE = re.compile(r"\bproof_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN)\b", re.IGNORECASE)
EVIDENCE_LABEL_RE = re.compile(r"\bevidence_label\s*[=:]\s*(Prefilter|Partial|Paper score|Historical clue|Local full run|Promoted)\b", re.IGNORECASE)
SOURCE_BOUND_RE = re.compile(r"\b(?:source_bound|source-backed|source_backed|source-hash-bound)\s*[=:]\s*(yes|true|1)\b|\bsource_hash\s*[=:]", re.IGNORECASE)
PAPER_ONLY_RE = re.compile(r"\b(?:paper_only|paper-only|scout_only|scout-only)\s*[=:]\s*(yes|true|1)\b", re.IGNORECASE)
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


def inspect(text: str, expected_source: str) -> dict[str, object]:
    risk_text = risk_scan_text(text)
    route_id = first_match(ROUTE_ID_RE, text)
    owner = first_match(OWNER_RE, text)
    next_action = first_match(NEXT_RE, text)
    paper = first_match(PAPER_RE, text)
    source_base = first_match(SOURCE_BASE_RE, text)
    source_hash = first_match(SOURCE_HASH_RE, text)
    candidate_hash = first_match(CANDIDATE_HASH_RE, text)
    source_location = first_match(SOURCE_LOCATION_RE, text)
    replacement = first_match(REPLACEMENT_RE, text)
    current_q = first_int(CURRENT_Q_RE, text)
    target_q = first_int(TARGET_Q_RE, text)
    current_avg = first_float(CURRENT_AVG_RE, text)
    extra_avg = first_float(EXTRA_AVG_RE, text)
    candidate_avg = first_float(CANDIDATE_AVG_RE, text)
    frontier_score = first_float(FRONTIER_SCORE_RE, text)
    candidate_score = first_float(CANDIDATE_SCORE_RE, text)
    score_edge = first_float(SCORE_EDGE_RE, text)
    restore_obligation = first_match(RESTORE_OBLIGATION_RE, text)
    phase_obligation = first_match(PHASE_OBLIGATION_RE, text)
    ancilla_obligation = first_match(ANCILLA_OBLIGATION_RE, text)
    toy_falsifier = first_match(TOY_RE, text)
    support_status = first_match(SUPPORT_STATUS_RE, text).upper()
    proof_status = first_match(PROOF_STATUS_RE, text).upper()
    evidence_label = first_match(EVIDENCE_LABEL_RE, text)

    if candidate_avg is None and current_avg is not None and extra_avg is not None:
        candidate_avg = current_avg + extra_avg
    if candidate_score is None and candidate_avg is not None and target_q is not None:
        candidate_score = candidate_avg * target_q
    if score_edge is None and frontier_score is not None and candidate_score is not None:
        score_edge = frontier_score - candidate_score
    count_edge = score_edge is not None and score_edge > 0
    has_source_bound = bool(source_hash and SOURCE_BOUND_RE.search(text))
    bounded_toy = bool(BOUNDED_RE.search(text) or "bounded" in toy_falsifier.lower())
    counterexample = support_status == "COUNTEREXAMPLE" or proof_status == "COUNTEREXAMPLE"
    unknown = support_status in {"UNKNOWN", "UNPROVEN", ""} or proof_status in {"UNKNOWN", "UNPROVEN", ""}

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []

    if LOCAL_RE.search(text):
        failures.append("local_heavy_context")
    if PAPER_ONLY_RE.search(text):
        failures.append("paper_only_or_scout_only")
    if COMPUTE_REQUEST_RE.search(risk_text):
        failures.append("premature_compute_or_residual_request")
    if PREMATURE_RE.search(risk_text):
        failures.append("premature_submit_or_alert_language")
    if not NO_SUBMIT_RE.search(text):
        failures.append("missing_no_submit_ack")
    if expected_source and source_base and source_base != expected_source:
        failures.append("stale_source_base")
    if counterexample:
        failures.append("construction_counterexample")
    if score_edge is not None and score_edge <= 0:
        failures.append("nonpositive_score_edge")
    if evidence_label.lower() in {"local full run", "promoted"}:
        failures.append("construction_packet_overclaims_result")

    for label, value in [
        ("missing_route_id", route_id),
        ("missing_owner", owner),
        ("missing_next_action", next_action),
        ("missing_paper_reference", paper),
        ("missing_source_base", source_base),
        ("missing_source_hash", source_hash),
        ("missing_candidate_hash", candidate_hash),
        ("missing_source_location", source_location),
        ("missing_source_replacement", replacement),
        ("missing_restore_obligation", restore_obligation),
        ("missing_phase_obligation", phase_obligation),
        ("missing_ancilla_obligation", ancilla_obligation),
        ("missing_toy_falsifier", toy_falsifier),
    ]:
        if not value:
            holds.append(label)
    if current_q is None:
        holds.append("missing_current_q")
    if target_q is None:
        holds.append("missing_target_q")
    if current_avg is None:
        holds.append("missing_current_avg_tof")
    if candidate_avg is None and extra_avg is None:
        holds.append("missing_candidate_or_extra_avg_tof")
    if frontier_score is None:
        holds.append("missing_frontier_score")
    if candidate_score is None:
        holds.append("missing_candidate_score")
    if score_edge is None:
        holds.append("missing_score_edge")
    if not has_source_bound:
        holds.append("missing_source_bound_context")
    if not bounded_toy:
        holds.append("missing_bounded_toy_falsifier")
    if not support_status:
        holds.append("missing_support_status")
    if not proof_status:
        holds.append("missing_proof_status")
    if not evidence_label:
        holds.append("missing_evidence_label")
    elif evidence_label.lower() not in {"prefilter", "partial", "paper score", "historical clue"}:
        holds.append("evidence_label_not_intake_grade")
    if target_q is not None and current_q is not None and target_q >= current_q:
        warnings.append("target_q_not_lower_than_current_q")
    if unknown:
        warnings.append("proof_unknown_expected_for_intake")
    if not REMOTE_RE.search(text):
        warnings.append("missing_remote_or_studio_context")

    if failures:
        gate = "fail"
        decision = "no-source-bound-construction"
    elif holds:
        gate = "hold"
        decision = "complete-construction-intake-packet"
    else:
        gate = "pass"
        decision = "construction-intake-review-no-compute"

    return {
        "gate": gate,
        "decision": decision,
        "route_id": route_id,
        "owner": owner,
        "source_base": source_base,
        "paper_reference": paper,
        "source_location": source_location,
        "source_hash_bound": has_source_bound,
        "candidate_hash": bool(candidate_hash),
        "replacement": replacement,
        "current_q": current_q,
        "target_q": target_q,
        "current_avg_tof": current_avg,
        "extra_avg_tof": extra_avg,
        "candidate_avg_tof": candidate_avg,
        "frontier_score": frontier_score,
        "candidate_score": candidate_score,
        "score_edge": score_edge,
        "count_edge": count_edge,
        "restore_obligation": bool(restore_obligation),
        "phase_obligation": bool(phase_obligation),
        "ancilla_obligation": bool(ancilla_obligation),
        "toy_falsifier": bool(toy_falsifier),
        "bounded_toy": bounded_toy,
        "support_status": support_status or "missing",
        "proof_status": proof_status or "missing",
        "evidence_label": evidence_label,
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
        f"construction_intake_gate={row['gate']} decision={row['decision']} "
        f"route_id={row['route_id'] or 'missing'} owner={row['owner'] or 'missing'} "
        f"source_base={row['source_base'] or 'missing'} paper_reference={row['paper_reference'] or 'missing'} "
        f"source_location={row['source_location'] or 'missing'} source_hash_bound={str(row['source_hash_bound']).lower()} "
        f"candidate_hash={str(row['candidate_hash']).lower()} replacement={row['replacement'] or 'missing'} "
        f"current_q={row['current_q']} target_q={row['target_q']} current_avg_tof={row['current_avg_tof']} "
        f"extra_avg_tof={row['extra_avg_tof']} candidate_avg_tof={row['candidate_avg_tof']} "
        f"frontier_score={row['frontier_score']} candidate_score={row['candidate_score']} "
        f"score_edge={row['score_edge']} count_edge={str(row['count_edge']).lower()} "
        f"restore_obligation={str(row['restore_obligation']).lower()} phase_obligation={str(row['phase_obligation']).lower()} "
        f"ancilla_obligation={str(row['ancilla_obligation']).lower()} bounded_toy={str(row['bounded_toy']).lower()} "
        f"support_status={row['support_status']} proof_status={row['proof_status']} "
        f"evidence_label={row['evidence_label'] or 'missing'} no_submit_ack={str(row['no_submit_ack']).lower()} "
        f"failures={join(row['failures'])} holds={join(row['holds'])} warnings={join(row['warnings'])}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path, nargs="+")
    parser.add_argument("--expected-source", default="d44cad3")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    missing = [str(path) for path in args.packet if not path.is_file()]
    if missing:
        print(f"construction_intake_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
        return 2
    row = inspect(read_text(args.packet), args.expected_source)
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
