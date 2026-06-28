#!/usr/bin/env python3
"""Validate a five-loop Bluesky/Redsky audit packet.

The gate turns iterative audit work into a machine-readable artifact. It does
not authorize compute or submit; those still require their dedicated gates.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path
from typing import Any


ALLOWED_EVIDENCE = {
    "Prefilter",
    "Partial",
    "Local full run",
    "Promoted",
    "Paper score",
    "Historical clue",
    "N/A",
}

ALLOWED_CLAIM_SCOPES = {
    "process-control",
    "source-proof",
    "route-triage",
    "compute-gate",
    "submit-gate",
    "paper-score",
}

ALLOWED_DECISIONS = {
    "proceed",
    "measure",
    "park",
    "kill",
    "hold",
    "nack",
    "request-human-review",
}

BLUESKY_REQUIRED = [
    "route_or_idea",
    "best_case",
    "missing_measurement",
    "smallest_useful_experiment",
    "bounded_alternative",
    "hidden_assumption",
    "stop_condition",
    "decision",
]

REDSKY_REQUIRED = [
    "route_or_claim",
    "current_public_truth_checked",
    "evidence_label",
    "strongest_objection",
    "fastest_falsifier",
    "failure_class",
    "missing_gate",
    "decision",
    "required_verification",
]

LOOP_REQUIRED = [
    "loop",
    "finding",
    "artifact",
    "implemented",
    "implementation",
    "verification",
    "evidence_label",
    "claim_scope",
    "compute_dispatch_allowed",
    "submit_language_allowed",
    "bluesky",
    "redsky",
]

FORBIDDEN_TEXT = [
    ("api_key", re.compile(r"\b(rpa_|sk-[A-Za-z0-9_-]{12,}|xox[baprs]-|ghp_|github_pat_|AKIA)[A-Za-z0-9_-]*")),
    ("private_mailbox", re.compile(r"\.ecdsafail/coord\.md")),
    ("private_home_path", re.compile(r"/Users/(odin|olifreuler)/(\.ecdsafail|\.ssh|\.codex|Library)/")),
    ("private_alert_topic", re.compile(r"ntfy\.sh/ecdsa", re.I)),
    ("private_key_block", re.compile(r"BEGIN (OPENSSH|RSA|EC|DSA) PRIVATE KEY")),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gate a machine-readable Bluesky/Redsky audit loop packet."
    )
    parser.add_argument("packet", type=Path, help="JSON packet to validate")
    parser.add_argument(
        "--exact-loops",
        type=int,
        default=5,
        help="required loop count; use 0 to disable the exact-count check",
    )
    parser.add_argument(
        "--require-implemented",
        action="store_true",
        help="require every loop to be implemented and verified",
    )
    return parser.parse_args()


def load_packet(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"json_decode=fail path={path} error={exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("packet_must_be_json_object")
    return data


def flattened_strings(value: Any, prefix: str = "$") -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(value, str):
        rows.append((prefix, value))
    elif isinstance(value, dict):
        for key, item in value.items():
            rows.extend(flattened_strings(item, f"{prefix}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.extend(flattened_strings(item, f"{prefix}[{index}]"))
    return rows


def is_blank(value: Any) -> bool:
    return not isinstance(value, str) or not value.strip()


def require_fields(obj: dict[str, Any], fields: list[str], scope: str, errors: list[str]) -> None:
    for field in fields:
        if field not in obj:
            errors.append(f"{scope} missing {field}")


def require_nonblank(obj: dict[str, Any], fields: list[str], scope: str, errors: list[str]) -> None:
    for field in fields:
        if field not in obj:
            continue
        if is_blank(obj[field]):
            errors.append(f"{scope} blank {field}")


def validate_decision(value: Any, scope: str, errors: list[str]) -> None:
    if value not in ALLOWED_DECISIONS:
        errors.append(f"{scope} invalid decision={value!r}")


def validate_loop(loop: dict[str, Any], index: int, require_implemented: bool, errors: list[str]) -> None:
    scope = f"loop[{index}]"
    require_fields(loop, LOOP_REQUIRED, scope, errors)
    require_nonblank(loop, ["finding", "artifact", "implementation", "verification"], scope, errors)

    expected_loop = index + 1
    if loop.get("loop") != expected_loop:
        errors.append(f"{scope} nonsequential loop={loop.get('loop')!r} expected={expected_loop}")

    evidence = loop.get("evidence_label")
    if evidence not in ALLOWED_EVIDENCE:
        errors.append(f"{scope} invalid evidence_label={evidence!r}")

    claim_scope = loop.get("claim_scope")
    if claim_scope not in ALLOWED_CLAIM_SCOPES:
        errors.append(f"{scope} invalid claim_scope={claim_scope!r}")

    if not isinstance(loop.get("compute_dispatch_allowed"), bool):
        errors.append(f"{scope} compute_dispatch_allowed must be boolean")
    if not isinstance(loop.get("submit_language_allowed"), bool):
        errors.append(f"{scope} submit_language_allowed must be boolean")

    if require_implemented and loop.get("implemented") is not True:
        errors.append(f"{scope} finding not implemented")
    if require_implemented and is_blank(loop.get("verification")):
        errors.append(f"{scope} implemented finding has no verification")

    bluesky = loop.get("bluesky")
    if not isinstance(bluesky, dict):
        errors.append(f"{scope} bluesky must be object")
    else:
        require_fields(bluesky, BLUESKY_REQUIRED, f"{scope}.bluesky", errors)
        require_nonblank(bluesky, BLUESKY_REQUIRED[:-1], f"{scope}.bluesky", errors)
        validate_decision(bluesky.get("decision"), f"{scope}.bluesky", errors)

    redsky = loop.get("redsky")
    if not isinstance(redsky, dict):
        errors.append(f"{scope} redsky must be object")
        return

    require_fields(redsky, REDSKY_REQUIRED, f"{scope}.redsky", errors)
    require_nonblank(redsky, REDSKY_REQUIRED[:-1], f"{scope}.redsky", errors)
    validate_decision(redsky.get("decision"), f"{scope}.redsky", errors)

    if redsky.get("evidence_label") != evidence:
        errors.append(
            f"{scope} evidence_label mismatch loop={evidence!r} redsky={redsky.get('evidence_label')!r}"
        )

    public_truth = str(redsky.get("current_public_truth_checked", "")).strip().lower()
    if public_truth in {"memory", "memory only", "not checked", "unknown", "n/a"}:
        errors.append(f"{scope}.redsky current_public_truth_checked is not fresh enough")

    if loop.get("compute_dispatch_allowed") is True:
        for field in ["owner", "validator", "budget", "kill_gate", "frontier", "source_base", "q_tier"]:
            if is_blank(loop.get(field)):
                errors.append(f"{scope} compute dispatch missing {field}")

    if loop.get("submit_language_allowed") is True:
        if evidence != "Local full run":
            errors.append(f"{scope} submit language requires Local full run evidence")
        for field in ["local_full_run_clean", "score_below_frontier", "fresh_frontier_recheck"]:
            if loop.get(field) is not True:
                errors.append(f"{scope} submit language missing true {field}")


def validate_forbidden_text(packet: dict[str, Any], errors: list[str]) -> None:
    for path, text in flattened_strings(packet):
        for label, pattern in FORBIDDEN_TEXT:
            if pattern.search(text):
                errors.append(f"{path} forbidden_text={label}")


def main() -> int:
    args = parse_args()
    packet = load_packet(args.packet)
    errors: list[str] = []

    require_fields(packet, ["schema_version", "route_id", "frontier", "generated_at", "loops"], "$", errors)
    require_nonblank(packet, ["route_id", "frontier", "generated_at"], "$", errors)
    validate_forbidden_text(packet, errors)

    loops = packet.get("loops")
    if not isinstance(loops, list):
        errors.append("$.loops must be list")
        loops = []
    if args.exact_loops and len(loops) != args.exact_loops:
        errors.append(f"loop_count={len(loops)} expected={args.exact_loops}")

    for index, loop in enumerate(loops):
        if not isinstance(loop, dict):
            errors.append(f"loop[{index}] must be object")
            continue
        validate_loop(loop, index, args.require_implemented, errors)

    decision_counts = collections.Counter()
    evidence_counts = collections.Counter()
    implemented = 0
    verified = 0
    compute_allowed = 0
    submit_allowed = 0
    for loop in loops:
        if not isinstance(loop, dict):
            continue
        redsky = loop.get("redsky") if isinstance(loop.get("redsky"), dict) else {}
        decision_counts[str(redsky.get("decision", ""))] += 1
        evidence_counts[str(loop.get("evidence_label", ""))] += 1
        implemented += int(loop.get("implemented") is True)
        verified += int(not is_blank(loop.get("verification")))
        compute_allowed += int(loop.get("compute_dispatch_allowed") is True)
        submit_allowed += int(loop.get("submit_language_allowed") is True)

    status = "pass" if not errors else "fail"
    print(
        f"bluesky_redsky_loop_gate={status} "
        f"route_id={packet.get('route_id', '')} "
        f"loops={len(loops)} "
        f"implemented={implemented} "
        f"verified={verified} "
        f"compute_dispatch_allowed={compute_allowed} "
        f"submit_language_allowed={submit_allowed} "
        f"evidence={','.join(f'{k}:{v}' for k, v in sorted(evidence_counts.items()) if k)} "
        f"decisions={','.join(f'{k}:{v}' for k, v in sorted(decision_counts.items()) if k)}"
    )
    for error in errors:
        print(f"error={error}", file=sys.stderr)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
