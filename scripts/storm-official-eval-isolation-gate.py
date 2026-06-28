#!/usr/bin/env python3
"""Gate official eval helpers against shared ops.bin/score.json races.

Remote workers often validate many survivor nonces on the same checkout. If two
helpers rebuild ops.bin or score.json concurrently, later eval output can be
from the wrong op stream. This script inspects public-safe helper snippets or
logs and fails closed unless the eval path is serialized with a lock or uses an
isolated per-run workspace.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Iterable


BUILD_RE = re.compile(r"\bbuild_circuit\b")
EVAL_RE = re.compile(r"\beval_circuit\b")
EVAL_HELPER_RE = re.compile(r"\b(?:ev\.sh|safe-eval|storm_eval_|DIALOG_TAIL_NONCE)\b")
SHARED_ARTIFACT_RE = re.compile(r"\b(?:ops\.bin|score\.json|results\.tsv)\b")
LOCK_RE = re.compile(r"\b(?:flock|lockfile|storm-official-eval\.lock|official-eval\.lock)\b")
ISOLATED_RE = re.compile(
    r"\b(?:mktemp\s+-d|mktemp\s+-t|TMPDIR|workdir|workspace|rsync|cp\s+-a|git\s+worktree|trap\s+.*rm\s+-rf)\b",
    re.IGNORECASE,
)
UNSAFE_BG_RE = re.compile(r"(?:build_circuit|eval_circuit).*(?:&\s*$|nohup|parallel|xargs\s+-P)", re.MULTILINE)
HELPER_BG_RE = re.compile(r"(?:ev\.sh|safe-eval|DIALOG_TAIL_NONCE).*(?:&\s*$|nohup|parallel|xargs\s+-P)", re.MULTILINE)
DONE_RE = re.compile(r"\b(?:STORM_RUNPOD_EVAL_DONE|correctness FAILED|correctness OK|=== experiment OK ===)\b")


def read_text(paths: Iterable[Path]) -> str:
    chunks: list[str] = []
    for path in paths:
        chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(chunks)


def inspect(text: str) -> dict[str, object]:
    has_build = bool(BUILD_RE.search(text))
    has_eval = bool(EVAL_RE.search(text))
    has_eval_helper = bool(EVAL_HELPER_RE.search(text))
    shared_artifact = bool(SHARED_ARTIFACT_RE.search(text))
    lock = bool(LOCK_RE.search(text))
    isolated = bool(ISOLATED_RE.search(text))
    unsafe_background = bool(UNSAFE_BG_RE.search(text))
    helper_background = bool(HELPER_BG_RE.search(text))
    done_marker = bool(DONE_RE.search(text))

    failures: list[str] = []
    warnings: list[str] = []

    if not (has_eval or has_eval_helper):
        failures.append("missing_eval_circuit")
    if not has_build:
        warnings.append("missing_build_circuit")
    if unsafe_background:
        failures.append("background_or_parallel_eval")
    if helper_background and not (lock or isolated):
        failures.append("background_or_parallel_eval_helper")
    if has_build and has_eval and shared_artifact and not (lock or isolated):
        failures.append("shared_artifact_without_lock_or_isolation")
    if has_eval_helper and not has_eval and not (lock or isolated):
        warnings.append("helper_without_visible_lock_or_isolation")
    if (has_eval or has_eval_helper) and not done_marker:
        warnings.append("missing_done_marker")

    if failures:
        gate = "fail"
        decision = "triage-only"
    elif lock or isolated:
        gate = "pass"
        decision = "serialized-or-isolated"
    else:
        gate = "hold"
        decision = "insufficient-isolation-evidence"

    return {
        "gate": gate,
        "decision": decision,
        "has_build": has_build,
        "has_eval": has_eval,
        "has_eval_helper": has_eval_helper,
        "shared_artifact": shared_artifact,
        "lock": lock,
        "isolated": isolated,
        "unsafe_background": unsafe_background,
        "helper_background": helper_background,
        "done_marker": done_marker,
        "failures": failures,
        "warnings": warnings,
    }


def text_summary(row: dict[str, object]) -> str:
    fields = [
        "has_build",
        "has_eval",
        "has_eval_helper",
        "shared_artifact",
        "lock",
        "isolated",
        "unsafe_background",
        "helper_background",
        "done_marker",
    ]
    flags = " ".join(f"{key}={str(row[key]).lower()}" for key in fields)
    failures = ",".join(row["failures"]) if row["failures"] else "none"
    warnings = ",".join(row["warnings"]) if row["warnings"] else "none"
    return (
        f"official_eval_isolation_gate={row['gate']} {flags} "
        f"decision={row['decision']} failures={failures} warnings={warnings}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    missing = [str(path) for path in args.inputs if not path.is_file()]
    if missing:
        print(f"official_eval_isolation_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
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
