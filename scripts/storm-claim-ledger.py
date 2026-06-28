#!/usr/bin/env python3
"""Append, validate, and summarize Storm claim-ledger JSONL entries.

This is the machine-readable partner to the short mailbox ACK/NACK line. It is
public-harness infrastructure only: it does not read mailboxes, contact pods,
send alerts, validate circuits, or submit anything.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any


EVIDENCE_LABELS = {"Prefilter", "Partial", "Local full run", "Promoted"}
CLAIM_KINDS = {"CLAIM", "NACK", "INFO", "REQUEST", "FYI", "PARTIAL"}
PROOF_STATUSES = {"CERTIFIED", "UNKNOWN", "COUNTEREXAMPLE", "UNPROVEN", "N/A"}
LOCAL_FULL_RUN_FIELDS = (
    "frontier_score",
    "candidate_score",
    "qubits",
    "avg_toffoli",
    "classical",
    "phase",
    "ancilla",
)
INTEGER_FIELDS = {"frontier_score", "candidate_score", "qubits", "classical", "phase", "ancilla"}
FLOAT_FIELDS = {"avg_toffoli"}


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def iso(value: dt.datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def parse_time(text: str) -> dt.datetime | None:
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        value = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=dt.timezone.utc)
    return value.astimezone(dt.timezone.utc)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{lineno}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise SystemExit(f"{path}:{lineno}: row must be an object")
        rows.append(row)
    return rows


def is_blank(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def parse_int(value: Any) -> int | None:
    if is_blank(value):
        return None
    try:
        return int(str(value).replace("_", ""))
    except ValueError:
        return None


def parse_float(value: Any) -> float | None:
    if is_blank(value):
        return None
    try:
        return float(str(value).replace("_", ""))
    except ValueError:
        return None


def local_full_submit_ready(row: dict[str, Any]) -> bool:
    if row.get("evidence_label") != "Local full run" or row.get("proof_status") != "CERTIFIED":
        return False
    frontier_score = parse_int(row.get("frontier_score"))
    candidate_score = parse_int(row.get("candidate_score"))
    classical = parse_int(row.get("classical"))
    phase = parse_int(row.get("phase"))
    ancilla = parse_int(row.get("ancilla"))
    if None in (frontier_score, candidate_score, classical, phase, ancilla):
        return False
    return candidate_score < frontier_score and (classical, phase, ancilla) == (0, 0, 0)


def validate_row(row: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    required = {"timestamp", "agent", "kind", "lane", "skill", "file", "next", "no_submit_ack"}
    missing = sorted(required - row.keys())
    if missing:
        errors.append(f"row {index}: missing {','.join(missing)}")
    if row.get("kind") not in CLAIM_KINDS:
        errors.append(f"row {index}: unsupported kind {row.get('kind')!r}")
    if row.get("evidence_label", "Prefilter") not in EVIDENCE_LABELS:
        errors.append(f"row {index}: unsupported evidence_label {row.get('evidence_label')!r}")
    if row.get("proof_status", "N/A") not in PROOF_STATUSES:
        errors.append(f"row {index}: unsupported proof_status {row.get('proof_status')!r}")
    if row.get("no_submit_ack") != "yes":
        errors.append(f"row {index}: no_submit_ack must be yes")
    if row.get("evidence_label") == "Local full run" and not str(row.get("frontier", "")).strip():
        errors.append(f"row {index}: Local full run requires frontier")
    if row.get("proof_status") == "CERTIFIED" and not str(row.get("frontier", "")).strip():
        errors.append(f"row {index}: CERTIFIED proof_status requires frontier")
    for field in INTEGER_FIELDS:
        if not is_blank(row.get(field)) and parse_int(row.get(field)) is None:
            errors.append(f"row {index}: {field} must be an integer")
    for field in FLOAT_FIELDS:
        if not is_blank(row.get(field)) and parse_float(row.get(field)) is None:
            errors.append(f"row {index}: {field} must be numeric")
    if row.get("evidence_label") == "Local full run":
        for field in LOCAL_FULL_RUN_FIELDS:
            if is_blank(row.get(field)):
                errors.append(f"row {index}: Local full run requires {field}")
        counts = (parse_int(row.get("classical")), parse_int(row.get("phase")), parse_int(row.get("ancilla")))
        if all(value is not None for value in counts) and counts != (0, 0, 0):
            errors.append(f"row {index}: Local full run requires classical/phase/ancilla all zero")
        frontier_score = parse_int(row.get("frontier_score"))
        candidate_score = parse_int(row.get("candidate_score"))
        if frontier_score is not None and candidate_score is not None and candidate_score >= frontier_score:
            errors.append(f"row {index}: Local full run requires candidate_score below frontier_score")
    if parse_time(str(row.get("timestamp", ""))) is None:
        errors.append(f"row {index}: timestamp must be RFC3339 UTC")
    expires_at = str(row.get("expires_at", ""))
    if expires_at and parse_time(expires_at) is None:
        errors.append(f"row {index}: expires_at must be RFC3339 UTC when present")
    return errors


def mailbox_line(row: dict[str, Any]) -> str:
    return (
        f"ACK {row['agent']} {row['kind']} {row['lane']} "
        f"skill={row['skill']} file={row['file']} next={row['next']} no_submit_ack=yes"
    )


def cmd_append(args: argparse.Namespace) -> int:
    now = utc_now()
    expires_at = ""
    if args.ttl_minutes:
        expires_at = iso(now + dt.timedelta(minutes=args.ttl_minutes))
    row = {
        "schema": "storm.claim.v1",
        "timestamp": iso(now),
        "agent": args.agent,
        "kind": args.kind,
        "lane": args.lane,
        "skill": args.skill,
        "file": args.file,
        "next": args.next,
        "evidence_label": args.evidence_label,
        "proof_status": args.proof_status,
        "frontier": args.frontier,
        "frontier_score": args.frontier_score,
        "candidate_score": args.candidate_score,
        "qubits": args.qubits,
        "avg_toffoli": args.avg_toffoli,
        "classical": args.classical,
        "phase": args.phase,
        "ancilla": args.ancilla,
        "artifact": args.artifact,
        "expires_at": expires_at,
        "no_submit_ack": "yes",
    }
    errors = validate_row(row, 1)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 2
    args.ledger.parent.mkdir(parents=True, exist_ok=True)
    with args.ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps(row, sort_keys=True))
    print(mailbox_line(row))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    rows = read_jsonl(args.ledger)
    errors: list[str] = []
    for index, row in enumerate(rows, start=1):
        errors.extend(validate_row(row, index))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 2
    print(f"claim_ledger=pass rows={len(rows)}")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    rows = read_jsonl(args.ledger)
    now = utc_now()
    active = 0
    expired = 0
    ready = 0
    for row in rows:
        expires = parse_time(str(row.get("expires_at", "")))
        if expires and expires < now:
            expired += 1
        else:
            active += 1
        if local_full_submit_ready(row):
            ready += 1
    print(f"claim_ledger_summary rows={len(rows)} active={active} expired={expired} local_full_submit_ready={ready}")
    for row in rows[-args.tail :]:
        print(mailbox_line(row))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    append = sub.add_parser("append")
    append.add_argument("--ledger", type=Path, required=True)
    append.add_argument("--agent", required=True)
    append.add_argument("--kind", choices=sorted(CLAIM_KINDS), required=True)
    append.add_argument("--lane", required=True)
    append.add_argument("--skill", required=True)
    append.add_argument("--file", required=True)
    append.add_argument("--next", required=True)
    append.add_argument("--evidence-label", choices=sorted(EVIDENCE_LABELS), default="Prefilter")
    append.add_argument("--proof-status", choices=sorted(PROOF_STATUSES), default="N/A")
    append.add_argument("--frontier", default="")
    append.add_argument("--frontier-score", default="")
    append.add_argument("--candidate-score", default="")
    append.add_argument("--qubits", default="")
    append.add_argument("--avg-toffoli", default="")
    append.add_argument("--classical", default="")
    append.add_argument("--phase", default="")
    append.add_argument("--ancilla", default="")
    append.add_argument("--artifact", default="")
    append.add_argument("--ttl-minutes", type=int, default=0)
    append.set_defaults(func=cmd_append)

    validate = sub.add_parser("validate")
    validate.add_argument("--ledger", type=Path, required=True)
    validate.set_defaults(func=cmd_validate)

    summary = sub.add_parser("summary")
    summary.add_argument("--ledger", type=Path, required=True)
    summary.add_argument("--tail", type=int, default=5)
    summary.set_defaults(func=cmd_summary)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
