#!/usr/bin/env python3
"""Summarize FANOUT_NONCE_LIST burst triage without promoting prefilter hits.

The fanout helper can evaluate many survivor nonces from one op-stream build.
This gate parses public-safe burst logs and produces a route-control decision:
either no candidate in the burst, hold for clearer evidence, or send a possible
0/0/0 row to full local official validation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Iterable


NONCE_LIST_RE = re.compile(r"\bFANOUT_NONCE_LIST\b[^\n:=]*(?:[:=])?\s*([0-9_ ,]+)", re.IGNORECASE)
CLEAN_RE = re.compile(r"\bclean\s*[=:]\s*(\d+)\b", re.IGNORECASE)
ROW_RE = re.compile(
    r"\bnonce\s*[=: ]\s*([0-9_]+)\b.*\bc\s*[=:]\s*(\d+)\b.*\bp\s*[=:]\s*(\d+)\b.*\ba\s*[=:]\s*(\d+)\b",
    re.IGNORECASE,
)
BEST_RE = re.compile(r"\bBEST\b|best dirty", re.IGNORECASE)


def read_text(paths: Iterable[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths)


def parse_nonce_list(text: str) -> set[str]:
    nonces: set[str] = set()
    for match in NONCE_LIST_RE.finditer(text):
        for token in re.findall(r"[0-9_]+", match.group(1)):
            nonces.add(token.replace("_", ""))
    return nonces


def parse_rows(text: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in text.splitlines():
        match = ROW_RE.search(line)
        if not match:
            continue
        nonce, classical, phase, ancilla = match.groups()
        cpa = (int(classical), int(phase), int(ancilla))
        rows.append(
            {
                "nonce": nonce.replace("_", ""),
                "classical": cpa[0],
                "phase": cpa[1],
                "ancilla": cpa[2],
                "zero": cpa == (0, 0, 0),
                "best": bool(BEST_RE.search(line)),
            }
        )
    return rows


def inspect(text: str) -> dict[str, object]:
    burst_nonces = parse_nonce_list(text)
    rows = parse_rows(text)
    row_nonces = {str(row["nonce"]) for row in rows}
    clean_values = [int(match.group(1)) for match in CLEAN_RE.finditer(text)]
    clean_summary = clean_values[-1] if clean_values else None
    zero_rows = [row for row in rows if row["zero"]]
    best_rows = [row for row in rows if row["best"]]
    best_dirty = [row for row in best_rows if not row["zero"]]

    if (clean_summary or 0) > 0 or zero_rows:
        gate = "candidate"
        decision = "full-local-validation-required"
    elif clean_summary == 0 and rows:
        gate = "nack"
        decision = "no-0-0-0-in-burst"
    elif burst_nonces or rows:
        gate = "hold"
        decision = "missing-clean-summary-or-count-rows"
    else:
        gate = "fail"
        decision = "no-burst-triage-evidence"

    return {
        "gate": gate,
        "decision": decision,
        "burst_nonces": len(burst_nonces) or len(row_nonces),
        "triage_rows": len(rows),
        "clean_summary": clean_summary,
        "zero_rows": len(zero_rows),
        "best_rows": len(best_rows),
        "best_dirty": len(best_dirty),
        "candidate_nonces": [row["nonce"] for row in zero_rows],
    }


def text_summary(row: dict[str, object]) -> str:
    clean_summary = "missing" if row["clean_summary"] is None else row["clean_summary"]
    candidates = ",".join(str(item) for item in row["candidate_nonces"]) or "none"
    return (
        f"fanout_burst_triage_gate={row['gate']} "
        f"burst_nonces={row['burst_nonces']} triage_rows={row['triage_rows']} "
        f"clean_summary={clean_summary} zero_rows={row['zero_rows']} "
        f"best_rows={row['best_rows']} best_dirty={row['best_dirty']} "
        f"decision={row['decision']} candidate_nonces={candidates}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-no-candidate", action="store_true")
    args = parser.parse_args()

    missing = [str(path) for path in args.logs if not path.is_file()]
    if missing:
        print(f"fanout_burst_triage_gate=fail missing_logs={','.join(missing)}", file=sys.stderr)
        return 2

    row = inspect(read_text(args.logs))
    if args.json:
        print(json.dumps(row, sort_keys=True))
    else:
        print(text_summary(row))

    if row["gate"] == "fail":
        return 2
    if args.require_no_candidate and row["gate"] != "nack":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
