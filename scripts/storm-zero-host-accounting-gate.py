#!/usr/bin/env python3
"""Gate borrowed-zero host ideas against allocator active-qubit accounting.

This source-theorem gate targets q1152 "borrow a zero host at the peak" routes.
It checks the current source facts that make free or loaned |0> qubits useless
for headroom relief: free/loaned zeros are removed from the active count, and
alloc/reacquire adds them back before the candidate can hold a new carry.

The optional host-family packet is a small public summary, not a raw trace. It
classifies families as no-relief, alias, no-host, or still needing qid proof.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


TRUTHY = {"1", "true", "yes", "y", "pass", "safe", "ok"}
FALSY = {"0", "false", "no", "n", "fail", "unsafe"}


@dataclass(frozen=True)
class SourceFact:
    name: str
    ok: bool
    reason: str


@dataclass(frozen=True)
class HostFamilyDecision:
    result: str
    reason: str


def norm_key(key: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9]+", "_", key.strip().lower())).strip("_")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError as exc:
        raise SystemExit(f"source_not_found path={path}") from exc


def function_body(text: str, name: str) -> str:
    match = re.search(r"\bfn\s+" + re.escape(name) + r"\b[^{]*\{", text)
    if match is None:
        return ""
    start = match.end() - 1
    depth = 0
    for idx in range(start, len(text)):
        ch = text[idx]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]
    return ""


def has_ordered(text: str, first: str, second: str) -> bool:
    first_idx = text.find(first)
    second_idx = text.find(second)
    return first_idx >= 0 and second_idx >= 0 and first_idx < second_idx


def inspect_sources(point_add_rs: Path, trailmix_mod_rs: Path, gidney_rs: Path) -> list[SourceFact]:
    point_add = read_text(point_add_rs)
    trailmix_mod = read_text(trailmix_mod_rs)
    gidney = read_text(gidney_rs)

    alloc = function_body(point_add, "alloc_qubit")
    free = function_body(point_add, "free")
    reacquire = function_body(point_add, "reacquire")
    loan = function_body(trailmix_mod, "loan_zero_qubit")
    headroom = function_body(trailmix_mod, "target_qubit_headroom")
    cout = function_body(gidney, "controlled_hybrid_add_cout_refs")

    facts = [
        SourceFact(
            "alloc_increments_before_free_pop",
            bool(alloc)
            and "self.active_qubits += 1" in alloc
            and "self.free_qubits.pop()" in alloc
            and has_ordered(alloc, "self.active_qubits += 1", "self.free_qubits.pop()"),
            "alloc_qubit adds active count before it can reuse free_qubits",
        ),
        SourceFact(
            "free_decrements_after_push",
            bool(free)
            and "self.r(q)" in free
            and "self.free_qubits" in free
            and ".push" in free
            and "self.active_qubits -= 1" in free,
            "free resets, pushes the qid to free_qubits, then removes it from active accounting",
        ),
        SourceFact(
            "reacquire_increments_active",
            bool(reacquire)
            and "free_qubits" in reacquire
            and "swap_remove" in reacquire
            and "self.active_qubits += 1" in reacquire,
            "reacquire removes a free qid and adds it back to active accounting",
        ),
        SourceFact(
            "loan_zero_decrements_active",
            bool(loan)
            and "self.free_qubits" in loan
            and ".push" in loan
            and "self.active_qubits -= 1" in loan,
            "loan_zero_qubit marks a measured zero as free and not active",
        ),
        SourceFact(
            "headroom_uses_active_qubits",
            bool(headroom)
            and "TLM_TARGET_Q" in headroom
            and "saturating_sub(circ.active_qubits" in headroom,
            "target_qubit_headroom is target minus active_qubits",
        ),
        SourceFact(
            "cout_clamps_to_headroom",
            bool(cout)
            and "target_qubit_headroom" in cout
            and "fit.selected.min(headroom)" in cout,
            "COUT effective budget is clamped by available active-qubit headroom",
        ),
        SourceFact(
            "cout_allocates_carry_resource",
            "let cy = circ.alloc_qubit()" in gidney and "controlled_clean_add_threaded" in gidney,
            "COUT threaded carries need a qubit resource to hold each extra carry",
        ),
    ]
    return facts


def normalize_row(row: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in row.items():
        out[norm_key(key)] = str(value).strip()
    aliases = {
        "host_type": "host_family",
        "family": "host_family",
        "counted": "counted_active",
        "active_counted": "counted_active",
        "is_zero": "known_zero",
        "owner_idle": "idle",
        "operand_disjoint": "disjoint_from_operands",
        "borrow_delta_active": "delta_active",
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


def read_rows(path: Path | None) -> list[dict[str, str]]:
    if path is None:
        return []
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return []
    if text[0] in "[{":
        loaded = json.loads(text)
        if isinstance(loaded, dict):
            return [normalize_row(loaded)]
        if isinstance(loaded, list):
            return [normalize_row(item) for item in loaded if isinstance(item, dict)]
        raise SystemExit("zero_host_accounting_gate=fail reason=json_must_be_object_or_list")
    if "\t" in text.splitlines()[0] or "," in text.splitlines()[0]:
        dialect = csv.excel_tab if "\t" in text.splitlines()[0] else csv.excel
        return [normalize_row(row) for row in csv.DictReader(text.splitlines(), dialect=dialect)]
    row: dict[str, str] = {}
    for part in re.split(r"\s+", text):
        if "=" in part:
            key, value = part.split("=", 1)
            row[key] = value
    return [normalize_row(row)] if row else []


def classify_host_family(row: dict[str, str]) -> HostFamilyDecision:
    family = row.get("host_family", "").strip().lower()
    counted_active = parse_bool(row, "counted_active")
    known_zero = parse_bool(row, "known_zero")
    idle = parse_bool(row, "idle")
    disjoint = parse_bool(row, "disjoint_from_operands")
    owner_touches = parse_bool(row, "owner_touches_during_borrow")
    delta_active = parse_int(row, "delta_active")

    if family in {"free_pool", "free_zero", "loaned_zero", "loaned"} or counted_active is False:
        return HostFamilyDecision("NO_THROTTLE_RELIEF", "free_or_loaned_zero_is_not_counted_active")
    if family in {"vent_resource", "cout_carry", "carry_resource"}:
        return HostFamilyDecision("NO_THROTTLE_RELIEF", "host_is_the_extra_carry_resource")
    if known_zero is False or family in {"live_data", "data", "operand"}:
        return HostFamilyDecision("NO_HOST", "host_family_not_known_zero")
    if idle is False or owner_touches is True:
        return HostFamilyDecision("HARD_NACK_ALIAS", "owner_touches_during_borrow")
    if disjoint is False:
        return HostFamilyDecision("HARD_NACK_ALIAS", "host_overlaps_operands")
    if counted_active is True and known_zero is True and idle is True and disjoint is True and delta_active == 0:
        return HostFamilyDecision("NEEDS_QID_TRACE", "counted_active_idle_zero_host_requires_qid_proof")
    return HostFamilyDecision("NO_HOST", "missing_counted_idle_zero_disjoint_proof")


def write_summary(path: Path, facts: Iterable[SourceFact], rows: Iterable[dict[str, str]], decisions: Iterable[HostFamilyDecision]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["kind", "name_or_family", "ok_or_result", "reason"])
        for fact in facts:
            writer.writerow(["source_fact", fact.name, int(fact.ok), fact.reason])
        for row, decision in zip(rows, decisions):
            writer.writerow(["host_family", row.get("host_family", ""), decision.result, decision.reason])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--point-add-rs", type=Path, required=True, help="source file containing B::alloc/free/reacquire")
    parser.add_argument("--trailmix-mod-rs", type=Path, required=True, help="source file containing loan_zero_qubit and target_qubit_headroom")
    parser.add_argument("--gidney-rs", type=Path, required=True, help="source file containing COUT headroom clamp")
    parser.add_argument("--host-families", type=Path, help="optional JSON/TSV/CSV/key=value host-family summary")
    parser.add_argument("--summary-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    facts = inspect_sources(args.point_add_rs, args.trailmix_mod_rs, args.gidney_rs)
    rows = read_rows(args.host_families)
    decisions = [classify_host_family(row) for row in rows]

    if args.summary_out:
        write_summary(args.summary_out, facts, rows, decisions)

    source_ok = all(fact.ok for fact in facts)
    no_relief = sum(1 for decision in decisions if decision.result == "NO_THROTTLE_RELIEF")
    alias = sum(1 for decision in decisions if decision.result == "HARD_NACK_ALIAS")
    no_host = sum(1 for decision in decisions if decision.result == "NO_HOST")
    candidates = sum(1 for decision in decisions if decision.result == "NEEDS_QID_TRACE")
    if not source_ok:
        decision = "source-facts-missing"
    elif candidates:
        decision = "needs-qid-trace"
    else:
        decision = "source-accounting-nack"
    print(
        "zero_host_accounting_gate=pass "
        f"source_ok={int(source_ok)} "
        f"facts={len(facts)} "
        f"rows={len(rows)} "
        f"no_relief={no_relief} "
        f"hard_nack_alias={alias} "
        f"no_host={no_host} "
        f"candidate={candidates} "
        f"decision={decision}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
