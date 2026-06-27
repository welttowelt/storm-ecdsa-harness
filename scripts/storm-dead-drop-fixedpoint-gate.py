#!/usr/bin/env python3
"""Gate dead-drop packets before residuals, eval, compute, or submit.

This classifier separates sampled dynamic deadness from source-invariant,
fixed-point dead-drop evidence. It is intentionally an admission gate: it does
not rebuild circuits, run residuals, edit source, dispatch compute, or submit.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


TRUTHY = {"1", "true", "yes", "y", "pass", "clean", "certified"}
FALSY = {"0", "false", "no", "n", "fail", "dirty", "unknown"}


@dataclass(frozen=True)
class Decision:
    result: str
    reason: str


def norm_key(key: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9]+", "_", key.strip().lower())).strip("_")


def normalize_row(row: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in row.items():
        out[norm_key(key)] = str(value).strip()
    aliases = {
        "idx_sha256": "candidate_indices_sha256",
        "index_sha256": "candidate_indices_sha256",
        "indices_sha256": "candidate_indices_sha256",
        "proof": "support_status",
        "proof_status": "support_status",
        "support": "support_status",
        "rebuilt": "rebuilt_after_edit",
        "ops_rebuilt": "rebuilt_after_edit",
        "residual_rebuilt": "residual_probe_rebuilt",
        "fixed_point_replay": "fixed_point",
        "same_stream_replay": "fixed_point",
        "classical": "eval_classical",
        "phase": "eval_phase",
        "ancilla": "eval_ancilla",
    }
    for old, new in aliases.items():
        if old in out and new not in out:
            out[new] = out[old]
    return out


def parse_bool(row: dict[str, str], key: str) -> bool | None:
    value = row.get(key, "").strip().lower()
    if value in TRUTHY:
        return True
    if value in FALSY:
        return False
    return None


def parse_int(row: dict[str, str], key: str) -> int | None:
    value = row.get(key, "").strip()
    if value == "":
        return None
    try:
        return int(value, 0)
    except ValueError:
        return None


def status(row: dict[str, str], key: str) -> str:
    return row.get(key, "").strip().upper()


def read_rows(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return []
    if text[0] in "[{":
        loaded = json.loads(text)
        if isinstance(loaded, dict):
            return [normalize_row(loaded)]
        if isinstance(loaded, list):
            return [normalize_row(item) for item in loaded if isinstance(item, dict)]
        raise SystemExit("dead_drop_fixedpoint_gate=fail reason=json_must_be_object_or_list")
    if "\t" in text.splitlines()[0] or "," in text.splitlines()[0]:
        dialect = csv.excel_tab if "\t" in text.splitlines()[0] else csv.excel
        return [normalize_row(row) for row in csv.DictReader(text.splitlines(), dialect=dialect)]
    row: dict[str, str] = {}
    for part in re.split(r"\s+", text):
        if "=" in part:
            key, value = part.split("=", 1)
            row[key] = value
    return [normalize_row(row)] if row else []


def classify(row: dict[str, str]) -> Decision:
    dynamic = parse_bool(row, "dynamic_deadness")
    sampled_shots = parse_int(row, "sampled_shots")
    support = status(row, "support_status")
    fixed_point = parse_bool(row, "fixed_point")
    rebuilt = parse_bool(row, "rebuilt_after_edit")
    residual_rebuilt = parse_bool(row, "residual_probe_rebuilt")

    if dynamic is True or (sampled_shots is not None and sampled_shots > 0 and support != "CERTIFIED"):
        return Decision("DYNAMIC_ONLY", "sampled_deadness_without_source_invariant")
    if support != "CERTIFIED":
        return Decision("UNKNOWN_PROOF", "support_status_not_certified")
    if not row.get("source_hash", "") or not row.get("support_certificate", ""):
        return Decision("UNKNOWN_PROOF", "missing_source_bound_certificate")
    if not row.get("stream_hash", "") or not row.get("pre_drop_ops_hash", "") or not row.get("candidate_indices_sha256", ""):
        return Decision("UNKNOWN_PROOF", "missing_stream_or_index_hash")
    if rebuilt is not True:
        return Decision("STALE_RESIDUAL", "ops_not_rebuilt_after_edit")
    if residual_rebuilt is not True:
        return Decision("STALE_RESIDUAL", "residual_probe_not_rebuilt_from_candidate_stream")
    if fixed_point is not True:
        return Decision("NO_FIXED_POINT", "dead_drop_list_not_replayed_to_fixed_point")

    cls = parse_int(row, "eval_classical")
    pha = parse_int(row, "eval_phase")
    anc = parse_int(row, "eval_ancilla")
    if cls is not None and pha is not None and anc is not None and (cls != 0 or pha != 0 or anc != 0):
        return Decision("DIRTY_EVAL", "trusted_eval_not_clean")

    return Decision("FIXEDPOINT_READY", "source_bound_rebuilt_fixed_point_packet")


def write_summary(path: Path, rows: Iterable[dict[str, str]], decisions: Iterable[Decision]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["route_id", "result", "reason"])
        for row, decision in zip(rows, decisions):
            writer.writerow([row.get("route_id", row.get("candidate_id", "")), decision.result, decision.reason])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packets", type=Path, required=True, help="dead-drop packet TSV/CSV/JSON/key=value file")
    parser.add_argument("--summary-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = read_rows(args.packets)
    if not rows:
        raise SystemExit("dead_drop_fixedpoint_gate=fail reason=no_rows")
    decisions = [classify(row) for row in rows]
    if args.summary_out:
        write_summary(args.summary_out, rows, decisions)

    counts = {key: 0 for key in ["FIXEDPOINT_READY", "DYNAMIC_ONLY", "STALE_RESIDUAL", "UNKNOWN_PROOF", "NO_FIXED_POINT", "DIRTY_EVAL"]}
    for decision in decisions:
        counts[decision.result] = counts.get(decision.result, 0) + 1
    if counts["FIXEDPOINT_READY"]:
        overall = "ready-for-validation"
    elif counts["DYNAMIC_ONLY"] or counts["STALE_RESIDUAL"] or counts["NO_FIXED_POINT"]:
        overall = "fixedpoint-required"
    else:
        overall = "proof-required"

    print(
        "dead_drop_fixedpoint_gate=pass "
        f"rows={len(rows)} "
        f"ready={counts['FIXEDPOINT_READY']} "
        f"dynamic_only={counts['DYNAMIC_ONLY']} "
        f"stale_residual={counts['STALE_RESIDUAL']} "
        f"unknown_proof={counts['UNKNOWN_PROOF']} "
        f"no_fixedpoint={counts['NO_FIXED_POINT']} "
        f"dirty_eval={counts['DIRTY_EVAL']} "
        f"decision={overall}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
