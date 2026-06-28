#!/usr/bin/env python3
"""Detect duplicate GPU/eval wrappers in public-safe pod snapshots.

Fleet workers often paste redacted process snapshots or mailbox state before
deciding whether a paid pod should keep running. This gate fails closed when
multiple active GPU wrappers cover the same route or multiple eval wrappers
cover the same nonce. It also holds eval snapshots that lack queued-marker,
lock, or isolation evidence, because those results are only triage-grade.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys
from typing import Iterable


POD_RE = re.compile(
    r"\b(?:pod(?:_id)?|runpod|instance|machine)\s*[=:]\s*([A-Za-z0-9_.-]+)|\brunpod:([A-Za-z0-9_.-]+)",
    re.IGNORECASE,
)
ROUTE_RE = re.compile(
    r"(\[\s*[0-9_]+\s*,\s*[0-9_]+\s*\)|"
    r"\b(?:range|route|shard)\s*[=:]?\s*\[?\s*[0-9_]+\s*,\s*[0-9_]+\s*\)?|"
    r"\bFANOUT_(?:START|FROM)\s*=\s*[0-9_]+\b.*\bFANOUT_(?:END|TO|STOP)\s*=\s*[0-9_]+\b)",
    re.IGNORECASE,
)
NONCE_RE = re.compile(
    r"\b(?:nonce|DIALOG_TAIL_NONCE)\s*[=: ]\s*([0-9_]+)\b|\beval-([0-9_]+)\.queued\b",
    re.IGNORECASE,
)
GPU_WRAPPER_RE = re.compile(r"\b(?:gpu_forever(?:\.sh)?|gpu_island2)\b", re.IGNORECASE)
GPU_CONTROLLER_RE = re.compile(r"\bgpu_forever(?:\.sh)?\b", re.IGNORECASE)
GPU_ISLAND_RE = re.compile(r"\bgpu_island2\b", re.IGNORECASE)
EVAL_WRAPPER_RE = re.compile(r"\b(?:ev\.sh|eval_circuit|build_circuit)\b", re.IGNORECASE)
LOCK_RE = re.compile(r"\b(?:flock|lockfile|storm-official-eval\.lock|official-eval\.lock)\b", re.IGNORECASE)
QUEUE_RE = re.compile(r"\beval-[0-9_]+\.queued\b|\bqueued\b", re.IGNORECASE)
ISOLATED_RE = re.compile(r"\b(?:mktemp\s+-d|mktemp\s+-t|workdir|workspace|git\s+worktree|rsync)\b", re.IGNORECASE)
IGNORE_RE = re.compile(r"\b(?:grep|rg|awk|sed)\b.*\b(?:gpu_forever|ev\.sh|eval_circuit|build_circuit)\b", re.IGNORECASE)


def read_text(paths: Iterable[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths)


def normalize_route(raw: str | None) -> str:
    if not raw:
        return "unknown-route"
    digits = re.findall(r"[0-9_]+", raw)
    if len(digits) >= 2:
        return f"{digits[0].replace('_', '')}-{digits[1].replace('_', '')}"
    return re.sub(r"\s+", "", raw.lower())


def route_from_command(line: str) -> str:
    route_match = ROUTE_RE.search(line)
    if route_match:
        return normalize_route(route_match.group(0))
    forever = re.search(r"\bgpu_forever(?:\.sh)?\s+([0-9_]+)\s+([0-9_]+)\s+[0-9_]+\b", line, re.IGNORECASE)
    if forever:
        start = int(forever.group(1).replace("_", ""))
        total = int(forever.group(2).replace("_", ""))
        return f"{start}-{start + total}"
    island = re.search(r"\bgpu_island2\s+([0-9_]+)\s+([0-9_]+)\b", line, re.IGNORECASE)
    if island:
        start = int(island.group(1).replace("_", ""))
        count = int(island.group(2).replace("_", ""))
        return f"{start}-{start + count}"
    return "unknown-route"


def first_group(match: re.Match[str] | None, fallback: str) -> str:
    if not match:
        return fallback
    for value in match.groups():
        if value:
            return value
    return fallback


def active_lines(text: str) -> list[str]:
    rows: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or IGNORE_RE.search(stripped):
            continue
        if re.match(r"^(?:ACK|NACK|ACK/NACK)\b", stripped):
            continue
        if GPU_WRAPPER_RE.search(stripped) or EVAL_WRAPPER_RE.search(stripped):
            rows.append(stripped)
    return rows


def pid_ppid(line: str) -> tuple[str, str] | None:
    match = re.match(r"^\s*([0-9]+)\s+([0-9]+)\s+", line)
    if not match:
        return None
    return match.group(1), match.group(2)


def inspect(text: str) -> dict[str, object]:
    gpu_controllers_by_key: dict[tuple[str, str], set[str]] = defaultdict(set)
    gpu_workers_by_key: dict[tuple[str, str], set[str]] = defaultdict(set)
    eval_by_key: dict[tuple[str, str], set[str]] = defaultdict(set)
    route_unknown = 0
    nonce_unknown = 0
    lines = active_lines(text)
    controller_pids = {
        parsed[0]
        for line in lines
        if GPU_CONTROLLER_RE.search(line)
        for parsed in [pid_ppid(line)]
        if parsed is not None
    }
    child_controller_pids = {
        parsed[0]
        for line in lines
        if GPU_CONTROLLER_RE.search(line)
        for parsed in [pid_ppid(line)]
        if parsed is not None and parsed[1] in controller_pids
    }

    for line in lines:
        pod = first_group(POD_RE.search(line), "unknown-pod")
        if GPU_WRAPPER_RE.search(line):
            route = route_from_command(line)
            if route == "unknown-route":
                route_unknown += 1
            if GPU_CONTROLLER_RE.search(line):
                parsed = pid_ppid(line)
                if parsed is not None and parsed[0] in child_controller_pids:
                    continue
                gpu_controllers_by_key[(pod, route)].add(line)
            elif GPU_ISLAND_RE.search(line):
                gpu_workers_by_key[(pod, route)].add(line)
        if EVAL_WRAPPER_RE.search(line):
            nonce = first_group(NONCE_RE.search(line), "unknown-nonce").replace("_", "")
            if nonce == "unknown-nonce":
                nonce_unknown += 1
            eval_by_key[(pod, nonce)].add(line)

    duplicate_gpu = {
        f"controller:{pod}:{route}": len(lines)
        for (pod, route), lines in gpu_controllers_by_key.items()
        if len(lines) > 1
    }
    duplicate_gpu.update(
        {
            f"worker:{pod}:{route}": len(lines)
            for (pod, route), lines in gpu_workers_by_key.items()
            if len(lines) > 1
        }
    )
    duplicate_eval = {f"{pod}:{nonce}": len(lines) for (pod, nonce), lines in eval_by_key.items() if len(lines) > 1}
    queued_marker = bool(QUEUE_RE.search(text))
    lock = bool(LOCK_RE.search(text))
    isolated = bool(ISOLATED_RE.search(text))

    failures: list[str] = []
    warnings: list[str] = []
    if duplicate_gpu:
        failures.append("duplicate_gpu_route_wrapper")
    if duplicate_eval and not (queued_marker and (lock or isolated)):
        failures.append("duplicate_eval_nonce_wrapper")
    if route_unknown:
        warnings.append("gpu_wrapper_missing_route")
    if nonce_unknown:
        warnings.append("eval_wrapper_missing_nonce")
    if eval_by_key and not (queued_marker or lock or isolated):
        warnings.append("eval_without_queue_lock_or_isolation")

    if failures:
        gate = "fail"
        decision = "collapse-duplicates-before-guard"
    elif warnings:
        gate = "hold"
        decision = "needs-clearer-wrapper-evidence"
    else:
        gate = "pass"
        decision = "single-wrapper-or-queued"

    return {
        "gate": gate,
        "decision": decision,
        "gpu_wrapper_keys": len(gpu_controllers_by_key) + len(gpu_workers_by_key),
        "eval_wrapper_keys": len(eval_by_key),
        "duplicate_gpu": duplicate_gpu,
        "duplicate_eval": duplicate_eval,
        "queued_marker": queued_marker,
        "lock": lock,
        "isolated": isolated,
        "failures": failures,
        "warnings": warnings,
    }


def text_summary(row: dict[str, object]) -> str:
    failures = ",".join(row["failures"]) if row["failures"] else "none"
    warnings = ",".join(row["warnings"]) if row["warnings"] else "none"
    duplicate_gpu = ",".join(f"{key}:{count}" for key, count in row["duplicate_gpu"].items()) or "none"
    duplicate_eval = ",".join(f"{key}:{count}" for key, count in row["duplicate_eval"].items()) or "none"
    return (
        f"pod_wrapper_dup_gate={row['gate']} "
        f"gpu_wrapper_keys={row['gpu_wrapper_keys']} eval_wrapper_keys={row['eval_wrapper_keys']} "
        f"queued_marker={str(row['queued_marker']).lower()} lock={str(row['lock']).lower()} "
        f"isolated={str(row['isolated']).lower()} decision={row['decision']} "
        f"duplicate_gpu={duplicate_gpu} duplicate_eval={duplicate_eval} "
        f"failures={failures} warnings={warnings}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    missing = [str(path) for path in args.inputs if not path.is_file()]
    if missing:
        print(f"pod_wrapper_dup_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
        return 2

    row = inspect(read_text(args.inputs))
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
