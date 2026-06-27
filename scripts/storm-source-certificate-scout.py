#!/usr/bin/env python3
"""Build exact-miner source-certificate scout TSVs from wall-owner summaries."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable


OUTPUT_FIELDS = [
    "rank",
    "count",
    "kind",
    "file",
    "line",
    "context",
    "trace_context_family",
    "trace_context_call",
    "trace_context_bit",
    "source_hash",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="") as f:
            return list(csv.DictReader(f, delimiter="\t"))
    except FileNotFoundError as exc:
        raise SystemExit(f"input_not_found path={path}") from exc


def closed_keys(paths: Iterable[Path]) -> set[tuple[str, str, str]]:
    keys: set[tuple[str, str, str]] = set()
    for path in paths:
        for row in read_tsv(path):
            file_name = row.get("file", row.get("source_file", ""))
            line = row.get("line", row.get("source_line", ""))
            kind = row.get("kind", row.get("op_class", "")).upper()
            if file_name and line and kind:
                keys.add((file_name, line, kind))
    return keys


def as_int(text: str) -> int:
    try:
        return int(str(text).strip())
    except ValueError:
        return 0


def build_rows(args: argparse.Namespace) -> list[dict[str, str]]:
    closed = closed_keys(args.closed)
    rows: list[dict[str, str]] = []
    for row in read_tsv(args.summary):
        file_name = row.get("file", "")
        line = row.get("line", "")
        family = row.get("family", "")
        kind = row.get("kind", "").upper()
        count = row.get("count", "0")
        if not file_name or not line or not kind:
            continue
        if not args.include_unclassified and family == "unclassified":
            continue
        if (file_name, line, kind) in closed:
            continue
        rows.append(
            {
                "rank": "",
                "count": str(as_int(count)),
                "kind": kind,
                "file": file_name,
                "line": line,
                "context": row.get("context", "none") or "none",
                "trace_context_family": family,
                "trace_context_call": row.get("trace_context_call", ""),
                "trace_context_bit": row.get("trace_context_bit", ""),
                "source_hash": row.get("source_hash", args.source_hash),
            }
        )
    rows.sort(key=lambda item: (-as_int(item["count"]), item["file"], as_int(item["line"]), item["kind"]))
    if args.limit:
        rows = rows[: args.limit]
    for index, row in enumerate(rows, start=1):
        row["rank"] = str(index)
    return rows


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, delimiter="\t", fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, required=True, help="source-line-family-summary TSV")
    parser.add_argument("--closed", type=Path, action="append", default=[], help="closed/site-audit TSV to exclude")
    parser.add_argument("--out", type=Path, required=True, help="exact-miner-ready scout TSV")
    parser.add_argument("--source-hash", required=True, help="public source hash or source label for emitted rows")
    parser.add_argument("--limit", type=int, default=0, help="maximum emitted rows")
    parser.add_argument("--include-unclassified", action="store_true", help="include unclassified rows")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    rows = build_rows(args)
    write_rows(args.out, rows)
    print(f"source_certificate_scout=pass rows={len(rows)} out={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
