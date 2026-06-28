#!/usr/bin/env python3
"""Screen Gidney erase-CCZ residual packets before any validation spend.

This is a public-safe parser. It reads source files and optional redacted route
packets. It does not build, evaluate, run SSH, start pods, alert, or submit.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys
from typing import Iterable


DEFAULT_TOTAL_TOFFOLI = 12_310_809_446
DEFAULT_SHOTS = 9_024
DEFAULT_FRONTIER_TOFFOLI = 1_364_230
DELTA_TOLERANCE = 1e-9

NO_SUBMIT_RE = re.compile(r"\bno_submit_ack\s*=\s*yes\b", re.IGNORECASE)
ROUTE_ID_RE = re.compile(r"\broute_id\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
OWNER_RE = re.compile(r"\b(?:owner|agent|validator)\s*[=:]\s*([A-Za-z0-9_.-]+)\b|\bACK\s+([A-Za-z0-9_.-]+)\b", re.IGNORECASE)
NEXT_RE = re.compile(r"\bnext\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
SOURCE_BASE_RE = re.compile(r"\b(?:source_base|source|base|source commit)\s*[=:]\s*([0-9a-f]{6,40})\b", re.IGNORECASE)
QUBITS_RE = re.compile(r"\b(?:q|qubits?)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
KIND_RE = re.compile(r"\b(?:kind|op_class|op_kind)\s*[=:]\s*(CCX|CCZ|TOFFOLI|T)\b", re.IGNORECASE)
TABLE_RE = re.compile(r"\b(?:table_family|table|family|primitive_family)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE)
CALL_RE = re.compile(r"\b(?:call_index|call)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
MASS_RE = re.compile(r"\b(?:expected_shot_mass|shot_mass|expected_mass|mass)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
DELTA_RE = re.compile(r"\b(?:expected_avgT_delta|expected_delta|delta)\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
SUPPORT_RE = re.compile(r"\bsupport_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE)\b", re.IGNORECASE)
PROOF_RE = re.compile(r"\bproof_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN)\b", re.IGNORECASE)
RESTORE_RE = re.compile(r"\brestore_proof\s*[=:]\s*([01]|true|false|yes|no)\b", re.IGNORECASE)
PHASE_RE = re.compile(r"\bphase_proof\s*[=:]\s*([01]|true|false|yes|no)\b", re.IGNORECASE)
CANDIDATE_HASH_RE = re.compile(r"\b(?:candidate_index_hash|candidate_diff_hash|candidate_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b", re.IGNORECASE)
SOURCE_LOCATION_RE = re.compile(r"\b(?:source_location|site|file)\s*[=:]\s*((?:src/point_add)/[A-Za-z0-9_./+-]+\.rs:[0-9]+)\b", re.IGNORECASE)
COMPUTE_RE = re.compile(
    r"\b(?:launch|start|restart|scale|dispatch|fire\s+up|spin\s+up)\b.{0,100}\b(?:pods?|runpod|vast|gpus?|cpus?|scanner|nonce)\b|"
    r"\b(?:benchmark|route_compare|build_circuit|eval_circuit|ecdsafail\s+run)\b",
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


def first_bool(pattern: re.Pattern[str], text: str) -> bool | None:
    value = first_match(pattern, text).lower()
    if not value:
        return None
    return value in {"1", "true", "yes"}


def const_numbers(source: str, name: str) -> list[int]:
    match = re.search(r"const\s+" + re.escape(name) + r"[^=]*=\s*&\[(.*?)\];", source, re.S)
    if not match:
        return []
    return [int(value.replace("_", ""), 0) for value in re.findall(r"0x[0-9a-fA-F_]+|\b\d[\d_]*\b", match.group(1))]


def default_envs(mod_rs: str) -> set[str]:
    return set(re.findall(r'set_default_env\("([^"]+)"', mod_rs))


def win_total(frontier_toffoli: int, shots: int) -> int:
    # Rust f64::round rounds x.5 away from zero, so to round strictly below the
    # current integer metric the average must be below frontier - 0.5.
    return math.ceil((frontier_toffoli - 0.5) * shots) - 1


def inspect_source(gidney_rs: str, mod_rs: str, total_toffoli: int, shots: int, frontier_toffoli: int) -> dict[str, object]:
    defaults = default_envs(mod_rs)
    erase_residual = const_numbers(gidney_rs, "GIDNEY_ERASE_CCZ_RESIDUAL_CALLS")
    capped_residual = const_numbers(gidney_rs, "GIDNEY_ERASE_CAPPED_CCZ_RESIDUAL_CALLS")
    erase_remainder = const_numbers(gidney_rs, "GIDNEY_ERASE_CCZ_REMAINDER_CALLS")
    capped_remainder = const_numbers(gidney_rs, "GIDNEY_ERASE_CAPPED_CCZ_REMAINDER_CALLS")
    winning_total = win_total(frontier_toffoli, shots)
    return {
        "default_exact_erase_all_ccz": "TLM_GIDNEY_SKIP_EXACT_ERASE_ALL_CCZ" in defaults,
        "default_small_residual": "TLM_GIDNEY_SKIP_SMALL_RESIDUAL_DEAD" in defaults,
        "erase_residual_count": len(erase_residual),
        "capped_residual_count": len(capped_residual),
        "erase_remainder_count": len(erase_remainder),
        "capped_remainder_count": len(capped_remainder),
        "erase_residual_calls": erase_residual,
        "capped_residual_calls": capped_residual,
        "erase_remainder_calls": erase_remainder,
        "capped_remainder_calls": capped_remainder,
        "current_total_toffoli": total_toffoli,
        "shots": shots,
        "frontier_toffoli": frontier_toffoli,
        "winning_total_max": winning_total,
        "required_drop": max(0, total_toffoli - winning_total),
    }


def inspect_packet(text: str, source: dict[str, object], expected_source: str, expected_qubits: int) -> dict[str, object]:
    route_id = first_match(ROUTE_ID_RE, text)
    owner = first_match(OWNER_RE, text)
    next_action = first_match(NEXT_RE, text)
    source_base = first_match(SOURCE_BASE_RE, text)
    qubits = first_int(QUBITS_RE, text)
    kind = first_match(KIND_RE, text).upper()
    table_family = first_match(TABLE_RE, text)
    call_index = first_int(CALL_RE, text)
    mass = first_int(MASS_RE, text)
    delta = first_float(DELTA_RE, text)
    support_status = first_match(SUPPORT_RE, text).upper()
    proof_status = first_match(PROOF_RE, text).upper()
    restore_proof = first_bool(RESTORE_RE, text)
    phase_proof = first_bool(PHASE_RE, text)
    candidate_hash = first_match(CANDIDATE_HASH_RE, text)
    source_location = first_match(SOURCE_LOCATION_RE, text)

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []

    if COMPUTE_RE.search(text):
        failures.append("premature_compute_request")
    if PREMATURE_RE.search(text):
        failures.append("premature_submit_or_alert_language")
    if not NO_SUBMIT_RE.search(text):
        failures.append("missing_no_submit_ack")
    if expected_source and source_base and source_base != expected_source:
        failures.append("stale_source_base")
    if expected_qubits and qubits is not None and qubits != expected_qubits:
        failures.append("wrong_qubit_tier")
    if kind and kind != "CCZ":
        failures.append("not_ccz")
    if delta is not None and delta >= 0:
        failures.append("nonnegative_expected_delta")
    implied_delta = -mass / int(source["shots"]) if mass is not None and int(source["shots"]) else None
    if delta is not None and implied_delta is not None and delta < implied_delta - DELTA_TOLERANCE:
        failures.append("delta_overclaims_shot_mass")

    for label, value in [
        ("missing_route_id", route_id),
        ("missing_owner", owner),
        ("missing_next_action", next_action),
        ("missing_source_base", source_base),
        ("missing_qubits", qubits),
        ("missing_kind", kind),
        ("missing_table_family", table_family),
        ("missing_call_index", call_index),
        ("missing_expected_shot_mass", mass),
        ("missing_candidate_hash", candidate_hash),
        ("missing_source_location", source_location),
    ]:
        if value in {"", None}:
            holds.append(label)

    table = table_family.lower()
    residual_calls: list[int] = []
    existing_calls: list[int] = []
    if table in {"gidney_erase_ccz_residual", "erase_ccz_residual"}:
        residual_calls = list(source["erase_residual_calls"])  # type: ignore[arg-type]
        existing_calls = residual_calls + list(source["erase_remainder_calls"])  # type: ignore[arg-type]
    elif table in {"gidney_erase_capped_ccz_residual", "erase_capped_ccz_residual", "capped_ccz_residual"}:
        residual_calls = list(source["capped_residual_calls"])  # type: ignore[arg-type]
        existing_calls = residual_calls + list(source["capped_remainder_calls"])  # type: ignore[arg-type]
    elif table in {"gidney_erase_ccz_new_call", "erase_ccz_new_call"}:
        existing_calls = list(source["erase_residual_calls"]) + list(source["erase_remainder_calls"])  # type: ignore[arg-type]
    elif table in {"gidney_erase_capped_ccz_new_call", "erase_capped_ccz_new_call", "capped_ccz_new_call"}:
        existing_calls = list(source["capped_residual_calls"]) + list(source["capped_remainder_calls"])  # type: ignore[arg-type]
    elif "remainder" in table:
        failures.append("default_on_remainder_not_new_edge")
    elif table_family:
        holds.append("unknown_table_family")

    if call_index is not None and residual_calls and call_index not in residual_calls:
        failures.append("call_not_in_residual_table")
    if call_index is not None and residual_calls and source["default_small_residual"] and call_index in residual_calls:
        failures.append("default_on_residual_not_new_edge")
    if call_index is not None and "new_call" in table and call_index in existing_calls:
        failures.append("new_call_already_default_on")
    required_drop = int(source["required_drop"])
    if mass is not None and mass < required_drop:
        failures.append("shot_mass_below_rounding_bar")

    certified = support_status == "CERTIFIED" and proof_status == "CERTIFIED" and restore_proof is True and phase_proof is True
    if not certified:
        if support_status != "CERTIFIED":
            holds.append("support_not_certified")
        if proof_status != "CERTIFIED":
            holds.append("proof_not_certified")
        if restore_proof is not True:
            holds.append("restore_proof_missing")
        if phase_proof is not True:
            holds.append("phase_proof_missing")

    if source["default_exact_erase_all_ccz"]:
        warnings.append("exact_erase_all_ccz_already_default_on")
    if not source["default_small_residual"]:
        warnings.append("small_residual_not_default_on")

    if failures:
        gate = "fail"
        decision = "reject-gidney-ccz-residual-packet"
    elif holds:
        gate = "hold"
        decision = "needs-certified-source-proof-no-compute"
    else:
        gate = "pass"
        decision = "eligible-for-storm-compute-unlock-review-no-auto-compute"

    return {
        "gate": gate,
        "decision": decision,
        "route_id": route_id,
        "owner": owner,
        "next_action": next_action,
        "source_base": source_base,
        "expected_source": expected_source,
        "qubits": qubits,
        "expected_qubits": expected_qubits,
        "kind": kind,
        "table_family": table_family,
        "call_index": call_index,
        "expected_shot_mass": mass,
        "implied_avgT_delta": implied_delta,
        "required_drop": required_drop,
        "delta": delta,
        "support_status": support_status or "missing",
        "proof_status": proof_status or "missing",
        "restore_proof": restore_proof,
        "phase_proof": phase_proof,
        "candidate_hash": bool(candidate_hash),
        "source_location": source_location,
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
        f"gidney_ccz_residual_gate={row['gate']} decision={row['decision']} "
        f"route_id={row.get('route_id', '') or 'source-screen'} owner={row.get('owner', '') or 'missing'} "
        f"source_base={row.get('source_base', '') or row.get('expected_source', 'none')} "
        f"q={row.get('qubits', 'n/a')} table_family={row.get('table_family', 'source-screen') or 'source-screen'} "
        f"call_index={row.get('call_index', 'n/a')} expected_shot_mass={row.get('expected_shot_mass', 'n/a')} "
        f"implied_avgT_delta={row.get('implied_avgT_delta', 'n/a')} "
        f"required_drop={row['required_drop']} default_exact_erase_all_ccz={str(row['default_exact_erase_all_ccz']).lower()} "
        f"default_small_residual={str(row['default_small_residual']).lower()} "
        f"erase_residual_count={row['erase_residual_count']} capped_residual_count={row['capped_residual_count']} "
        f"erase_remainder_count={row['erase_remainder_count']} capped_remainder_count={row['capped_remainder_count']} "
        f"support_status={row.get('support_status', 'n/a')} proof_status={row.get('proof_status', 'n/a')} "
        f"restore_proof={row.get('restore_proof', 'n/a')} phase_proof={row.get('phase_proof', 'n/a')} "
        f"no_submit_ack={str(row.get('no_submit_ack', False)).lower()} "
        f"failures={join(row.get('failures', []))} holds={join(row.get('holds', []))} warnings={join(row.get('warnings', []))}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gidney-rs", type=Path, required=True)
    parser.add_argument("--point-add-mod-rs", type=Path, required=True)
    parser.add_argument("--packet", type=Path, action="append", default=[])
    parser.add_argument("--expected-source", default="d44cad3")
    parser.add_argument("--expected-qubits", type=int, default=1152)
    parser.add_argument("--current-total-toffoli", type=int, default=DEFAULT_TOTAL_TOFFOLI)
    parser.add_argument("--shots", type=int, default=DEFAULT_SHOTS)
    parser.add_argument("--frontier-toffoli", type=int, default=DEFAULT_FRONTIER_TOFFOLI)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    missing = [str(path) for path in [args.gidney_rs, args.point_add_mod_rs, *args.packet] if not path.is_file()]
    if missing:
        print(f"gidney_ccz_residual_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
        return 2

    source = inspect_source(
        args.gidney_rs.read_text(encoding="utf-8", errors="replace"),
        args.point_add_mod_rs.read_text(encoding="utf-8", errors="replace"),
        args.current_total_toffoli,
        args.shots,
        args.frontier_toffoli,
    )
    if args.packet:
        row = {**source, **inspect_packet(read_text(args.packet), source, args.expected_source, args.expected_qubits)}
    else:
        row = {
            **source,
            "gate": "pass",
            "decision": "source-screen-only-no-compute",
            "expected_source": args.expected_source,
            "failures": [],
            "holds": [],
            "warnings": [
                "exact_erase_all_ccz_already_default_on" if source["default_exact_erase_all_ccz"] else "exact_erase_all_ccz_not_default_on",
                "small_residual_not_default_on" if not source["default_small_residual"] else "small_residual_default_on",
            ],
        }

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
