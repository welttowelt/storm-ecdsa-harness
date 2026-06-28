#!/usr/bin/env python3
"""Gate Mac-local heavy ECDSA.fail compute from redacted process snapshots.

This is a public-safe parser for HOT STOP packets and process tails. It does
not inspect live processes or kill anything. It only classifies text evidence so
workers can block local heavy compute and route it to studio or owned pods.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Iterable


HEAVY_RE = re.compile(
    r"\b(?:build_circuit|eval_circuit|fanout_nonce_eval|ccx_site_histogram|gpu_island2|"
    r"route_compare|search_driver|storm-exact-miner(?:\.py)?|lower-q|source-line|"
    r"ffg(?:[-_ ]?lifetime|[-_ ]?proof)?|proof[-_ ]?loop|scanner|"
    r"kiln-validate-nonce\.sh|vast-fanout|gpu_forever(?:\.sh)?)\b|"
    r"\btarget/release/[A-Za-z0-9_.-]+\b|"
    r"\bcargo\s+(?:build|run)\s+--release\b|"
    r"\becdsafail\s+(?:benchmark|run|submit)\b",
    re.IGNORECASE,
)
LOCAL_RE = re.compile(
    r"\b(?:host|machine|scope)\s*[=:]\s*(?:mac|macbook|local|darwin)\b|"
    r"\b(?:MacBook|Oli\s+MacBook|mac-local|local-process|local wrapper|/Users/[A-Za-z0-9_.-]+)\b",
    re.IGNORECASE,
)
LOCAL_HEADER_RE = re.compile(r"^\s*(?:host|machine|scope)\s*[=:]\s*(?:mac|macbook|local|darwin)\b", re.IGNORECASE | re.MULTILINE)
REMOTE_RE = re.compile(
    r"\b(?:host|machine|scope)\s*[=:]\s*(?:studio|runpod|vast|pod|remote)\b|"
    r"\b(?:runpod:|vast:|studio|owned pod|owned-pod|ssh\s+)\b",
    re.IGNORECASE,
)
REMOTE_HEADER_RE = re.compile(r"^\s*(?:host|machine|scope)\s*[=:]\s*(?:studio|runpod|vast|pod|remote)\b", re.IGNORECASE | re.MULTILINE)
ALLOW_RE = re.compile(r"\b(?:lightweight harness|check-public-harness|redaction-check|py_compile|git diff --check)\b", re.IGNORECASE)
RECURRING_WRAPPER_RE = re.compile(
    r"\b(?:while\s+(?:true|pgrep)|watch\s+-n|tail\s+-f|"
    r"sleep\s+[0-9]+.*(?:ssh|runpod|vast|fleet)|"
    r"(?:watch|scan|fleet|validation)[-_ ]loop)\b",
    re.IGNORECASE,
)


def read_text(paths: Iterable[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths)


def inspect(text: str, assume_local: bool = False) -> dict[str, object]:
    heavy_lines: list[str] = []
    local_heavy = 0
    remote_heavy = 0
    unknown_heavy = 0
    recurring_lines = 0
    local_recurring = 0
    remote_recurring = 0
    unknown_recurring = 0
    allowed_lightweight = bool(ALLOW_RE.search(text))
    global_local = bool(LOCAL_HEADER_RE.search(text))
    global_remote = bool(REMOTE_HEADER_RE.search(text)) and not global_local
    terms: set[str] = set()

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        line_local = bool(LOCAL_RE.search(stripped))
        line_remote = bool(REMOTE_RE.search(stripped))
        is_local = bool(line_local or global_local or assume_local)
        is_remote = bool(line_remote or global_remote)
        recurring = bool(RECURRING_WRAPPER_RE.search(stripped))
        if recurring:
            recurring_lines += 1
            terms.add("recurring-wrapper")
            if is_local:
                local_recurring += 1
            elif is_remote:
                remote_recurring += 1
            else:
                unknown_recurring += 1
        matches = [match.group(0) for match in HEAVY_RE.finditer(stripped)]
        if not matches:
            continue
        heavy_lines.append(stripped)
        terms.update(match.lower() for match in matches)
        if line_local or (is_local and not is_remote):
            local_heavy += 1
        elif is_remote:
            remote_heavy += 1
        else:
            unknown_heavy += 1

    if local_heavy or local_recurring:
        gate = "fail"
        decision = "stop-mac-local-heavy-compute"
    elif unknown_heavy or unknown_recurring:
        gate = "hold"
        decision = "require-host-and-owner-evidence"
    else:
        gate = "pass"
        decision = "no-local-heavy-compute"

    return {
        "gate": gate,
        "decision": decision,
        "heavy_lines": len(heavy_lines),
        "local_heavy": local_heavy,
        "remote_heavy": remote_heavy,
        "unknown_heavy": unknown_heavy,
        "recurring_lines": recurring_lines,
        "local_recurring": local_recurring,
        "remote_recurring": remote_recurring,
        "unknown_recurring": unknown_recurring,
        "allowed_lightweight": allowed_lightweight,
        "terms": sorted(terms),
    }


def text_summary(row: dict[str, object]) -> str:
    terms = ",".join(row["terms"]) if row["terms"] else "none"
    return (
        f"local_heavy_compute_gate={row['gate']} "
        f"heavy_lines={row['heavy_lines']} local_heavy={row['local_heavy']} "
        f"remote_heavy={row['remote_heavy']} unknown_heavy={row['unknown_heavy']} "
        f"recurring_lines={row['recurring_lines']} local_recurring={row['local_recurring']} "
        f"remote_recurring={row['remote_recurring']} unknown_recurring={row['unknown_recurring']} "
        f"allowed_lightweight={str(row['allowed_lightweight']).lower()} "
        f"decision={row['decision']} terms={terms}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--assume-local", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    missing = [str(path) for path in args.inputs if not path.is_file()]
    if missing:
        print(f"local_heavy_compute_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
        return 2

    row = inspect(read_text(args.inputs), assume_local=args.assume_local)
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
