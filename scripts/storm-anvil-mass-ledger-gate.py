#!/usr/bin/env python3
"""Gate Anvil conditional Toffoli mass/economics ledgers.

This public-safe parser checks TSV/CSV-style ledger summaries. It does not run
miners, build/eval, SSH job control, pods, alerts, or submit.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
import re
import sys
from typing import Iterable


REQUIRED_COLUMNS = {
    "route_id",
    "source_base",
    "source_location",
    "source_hash",
    "candidate_class",
    "current_q",
    "target_q",
    "current_avg_tof",
    "predicted_avg_tof",
    "candidate_score",
    "score_edge",
    "required_support",
    "known_counterexample",
    "next_gate",
}

GATE_ALLOWLIST = {
    "source-packet-novelty",
    "source_packet_novelty",
    "construction-intake",
    "construction_intake",
    "pebbling-theorem",
    "pebbling_theorem",
    "transcript-overlap",
    "transcript_overlap",
    "ffg-pair-proof",
    "ffg_pair_proof",
    "nack",
    "close",
    "hold",
}

NO_SUBMIT_RE = re.compile(r"\bno_submit_ack\s*[=:]\s*yes\b", re.IGNORECASE)
SOURCE_LOCATION_RE = re.compile(r"^src/point_add/[A-Za-z0-9_./+-]+\.rs(?::[0-9]+)?$")
HASH_RE = re.compile(r"^[0-9a-fA-F]{8,64}$")
COMPUTE_REQUEST_RE = re.compile(
    r"\b(?:launch|start|restart|rearm|scale|dispatch|residual|benchmark|run|route_compare)\b.{0,100}\b(?:pods?|runpod|vast|gpus?|cpus?|scanner|residual|9024|benchmark|eval)\b|"
    r"\b(?:gpu_forever|gpu_island2|fanout_nonce_eval|build_circuit|eval_circuit|count_tof|drop_effect_probe|storm-exact-miner)\b",
    re.IGNORECASE,
)
PREMATURE_RE = re.compile(r"\b(?:FOR[- ]AKASH|WINNER|mobile alert|submit(?:ted)?|ready[- ]to[- ]submit|Akash-ready)\b", re.IGNORECASE)
LOCAL_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:mac|macbook|local|darwin)\b|\b(?:MacBook|mac-local|/Users/[A-Za-z0-9_.-]+)\b", re.IGNORECASE)
NEGATED_GUARDRAIL_RE = re.compile(
    r"\b(?:no|never)\s+(?:compute|pods?|residual|route[-_ ]?compare|benchmark|alert|winner|akash|submit|submission)\b|"
    r"\b(?:do not|must not|cannot|can not)\s+(?:launch|start|restart|rearm|scale|dispatch|run|trigger|alert|write|submit)\b|"
    r"\b(?:does not|do not)\s+(?:authorize|license)\b|"
    r"\bnot\s+(?:authorized|licensed|allowed|a submit|a submission|ready[- ]to[- ]submit)\b",
    re.IGNORECASE,
)


def read_text(paths: Iterable[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths)


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


def normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_")


def meaningful(value: str) -> bool:
    return value.strip().lower() not in {"", "unknown", "none", "missing", "tbd", "todo", "n/a", "na", "null"}


def parse_float(value: str) -> float | None:
    value = value.strip().replace("_", "")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_int(value: str) -> int | None:
    value = value.strip().replace("_", "")
    if not value:
        return None
    try:
        return int(value, 0)
    except ValueError:
        return None


def is_truthy(value: str) -> bool:
    return value.strip().lower() in {"yes", "true", "1", "counterexample", "closed", "nack"}


def next_gate_class(value: str) -> str:
    return normalize_key(value).replace("_gate", "")


def parse_rows(text: str) -> tuple[list[dict[str, str]], list[str], str]:
    lines = [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if not lines:
        return [], [], "tsv"
    sample = "\n".join(lines[:3])
    delimiter = "\t"
    if "," in sample and "\t" not in sample:
        delimiter = ","
    reader = csv.DictReader(io.StringIO("\n".join(lines)), delimiter=delimiter)
    if not reader.fieldnames:
        return [], [], "csv" if delimiter == "," else "tsv"
    fieldnames = [normalize_key(name) for name in reader.fieldnames]
    rows: list[dict[str, str]] = []
    for raw in reader:
        row = {normalize_key(key or ""): (value or "").strip() for key, value in raw.items()}
        rows.append(row)
    return rows, fieldnames, "csv" if delimiter == "," else "tsv"


def inspect(text: str, expected_source: str) -> dict[str, object]:
    risk_text = risk_scan_text(text)
    rows, fieldnames, dialect = parse_rows(text)
    columns = set(fieldnames)
    missing_columns = sorted(REQUIRED_COLUMNS - columns)

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []
    row_failures: list[str] = []
    row_holds: list[str] = []

    if not rows:
        failures.append("empty_ledger")
    if missing_columns:
        holds.append("missing_required_columns")
    if not NO_SUBMIT_RE.search(text) and "no_submit_ack" not in columns:
        failures.append("missing_no_submit_ack")
    if COMPUTE_REQUEST_RE.search(risk_text):
        failures.append("premature_compute_or_residual_request")
    if PREMATURE_RE.search(risk_text):
        failures.append("premature_submit_or_alert_language")
    if LOCAL_RE.search(text):
        failures.append("local_heavy_context")

    positive_rows = 0
    closure_rows = 0
    source_bases: set[str] = set()
    next_gates: set[str] = set()
    min_score_edge: float | None = None
    max_score_edge: float | None = None

    for index, row in enumerate(rows, 1):
        prefix = f"row{index}"
        source_base = row.get("source_base", "")
        source_bases.add(source_base or "missing")
        if expected_source and source_base and source_base != expected_source:
            row_failures.append(f"{prefix}:stale_source_base")
        if row.get("no_submit_ack", "").lower() not in {"", "yes", "true", "1"}:
            row_failures.append(f"{prefix}:no_submit_ack_not_yes")
        for column in REQUIRED_COLUMNS:
            if column in columns and not meaningful(row.get(column, "")):
                row_holds.append(f"{prefix}:missing_{column}")
        source_location = row.get("source_location", "")
        source_hash = row.get("source_hash", "")
        if source_location and not SOURCE_LOCATION_RE.match(source_location):
            row_failures.append(f"{prefix}:bad_source_location")
        if source_hash and not HASH_RE.match(source_hash):
            row_failures.append(f"{prefix}:bad_source_hash")

        current_q = parse_int(row.get("current_q", ""))
        target_q = parse_int(row.get("target_q", ""))
        current_avg = parse_float(row.get("current_avg_tof", ""))
        predicted_avg = parse_float(row.get("predicted_avg_tof", ""))
        candidate_score = parse_float(row.get("candidate_score", ""))
        score_edge = parse_float(row.get("score_edge", ""))
        frontier_score = parse_float(row.get("frontier_score", ""))
        for label, value in [
            ("current_q", current_q),
            ("target_q", target_q),
            ("current_avg_tof", current_avg),
            ("predicted_avg_tof", predicted_avg),
            ("candidate_score", candidate_score),
            ("score_edge", score_edge),
        ]:
            if label in columns and value is None:
                row_holds.append(f"{prefix}:bad_numeric_{label}")
        if target_q is not None and predicted_avg is not None and candidate_score is not None:
            computed_score = target_q * predicted_avg
            if abs(candidate_score - computed_score) > 1.0:
                row_failures.append(f"{prefix}:candidate_score_mismatch")
        if frontier_score is not None and candidate_score is not None and score_edge is not None:
            computed_edge = frontier_score - candidate_score
            if abs(score_edge - computed_edge) > 1.0:
                row_failures.append(f"{prefix}:score_edge_mismatch")
        elif "frontier_score" not in columns:
            warnings.append("missing_frontier_score_column")

        if score_edge is not None:
            min_score_edge = score_edge if min_score_edge is None else min(min_score_edge, score_edge)
            max_score_edge = score_edge if max_score_edge is None else max(max_score_edge, score_edge)
        gate = next_gate_class(row.get("next_gate", ""))
        next_gates.add(gate or "missing")
        if gate and gate not in GATE_ALLOWLIST:
            row_holds.append(f"{prefix}:unknown_next_gate")
        known_counterexample = is_truthy(row.get("known_counterexample", ""))
        if known_counterexample:
            closure_rows += 1
            if gate not in {"nack", "close", "hold"}:
                row_failures.append(f"{prefix}:counterexample_routed_to_positive_gate")
        elif score_edge is not None and score_edge <= 0 and gate not in {"nack", "close", "hold"}:
            row_failures.append(f"{prefix}:nonpositive_score_edge_without_nack")
        elif score_edge is not None and score_edge > 0 and gate not in {"nack", "close", "hold"}:
            positive_rows += 1

    if rows and positive_rows == 0 and closure_rows == 0:
        holds.append("no_positive_or_closure_rows")
    if row_failures:
        failures.extend(sorted(set(value.split(":", 1)[1] for value in row_failures)))
    if row_holds:
        holds.extend(sorted(set(value.split(":", 1)[1] for value in row_holds)))

    if failures:
        gate = "fail"
        decision = "ledger-nack"
    elif holds:
        gate = "hold"
        decision = "complete-mass-ledger"
    else:
        gate = "pass"
        decision = "mass-ledger-ready-no-compute"

    return {
        "gate": gate,
        "decision": decision,
        "dialect": dialect,
        "row_count": len(rows),
        "columns": sorted(columns),
        "missing_columns": missing_columns,
        "positive_rows": positive_rows,
        "closure_rows": closure_rows,
        "source_bases": sorted(source_bases),
        "next_gates": sorted(next_gates),
        "min_score_edge": min_score_edge,
        "max_score_edge": max_score_edge,
        "no_submit_ack": bool(NO_SUBMIT_RE.search(text) or "no_submit_ack" in columns),
        "failures": failures,
        "holds": holds,
        "warnings": sorted(set(warnings)),
        "row_failures": row_failures,
        "row_holds": row_holds,
    }


def join(values: object) -> str:
    if not values:
        return "none"
    if isinstance(values, list):
        return ",".join(str(value) for value in values) if values else "none"
    return str(values)


def text_summary(row: dict[str, object]) -> str:
    return (
        f"anvil_mass_ledger_gate={row['gate']} decision={row['decision']} "
        f"dialect={row['dialect']} row_count={row['row_count']} "
        f"positive_rows={row['positive_rows']} closure_rows={row['closure_rows']} "
        f"missing_columns={join(row['missing_columns'])} source_bases={join(row['source_bases'])} "
        f"next_gates={join(row['next_gates'])} min_score_edge={row['min_score_edge']} "
        f"max_score_edge={row['max_score_edge']} no_submit_ack={str(row['no_submit_ack']).lower()} "
        f"failures={join(row['failures'])} holds={join(row['holds'])} warnings={join(row['warnings'])} "
        f"row_failures={join(row['row_failures'])} row_holds={join(row['row_holds'])}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path, nargs="+")
    parser.add_argument("--expected-source", default="d44cad3")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    missing = [str(path) for path in args.ledger if not path.is_file()]
    if missing:
        print(f"anvil_mass_ledger_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
        return 2
    row = inspect(read_text(args.ledger), args.expected_source)
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
