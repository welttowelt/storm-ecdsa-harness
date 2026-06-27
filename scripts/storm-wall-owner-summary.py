#!/usr/bin/env python3
"""Summarize wall-owner op-site contexts for exact-miner scout intake."""

from __future__ import annotations

import argparse
import collections
import csv
from pathlib import Path
from typing import Iterable


SourceKey = tuple[str, str, str, str, str]
FamilyKey = tuple[str, str]


def as_int(text: str) -> int:
    try:
        return int(str(text).strip())
    except ValueError:
        return 0


def read_contexts(path: Path) -> Iterable[dict[str, str]]:
    try:
        with path.open(newline="") as f:
            yield from csv.DictReader(f, delimiter="\t")
    except FileNotFoundError as exc:
        raise SystemExit(f"input_not_found path={path}") from exc


def row_source_hash(row: dict[str, str], default: str) -> str:
    return (
        row.get("source_hash")
        or row.get("source_snippet_hash")
        or row.get("source_code_hash")
        or default
        or ""
    ).strip()


def sort_source(item: tuple[SourceKey, int]) -> tuple[int, str, int, str, str, str]:
    (file_name, line, family, kind, source_hash), count = item
    return (-count, file_name, as_int(line), family, kind, source_hash)


def sort_family(item: tuple[FamilyKey, int]) -> tuple[int, str, str]:
    (family, kind), count = item
    return (-count, family, kind)


def write_source_summary(path: Path, rows: list[tuple[SourceKey, int]], limit: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    selected = rows[:limit] if limit else rows
    with path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(["file", "line", "family", "kind", "count", "source_hash"])
        for (file_name, line, family, kind, source_hash), count in selected:
            writer.writerow([file_name, line, family, kind, count, source_hash])


def write_family_summary(path: Path, rows: list[tuple[FamilyKey, int]], limit: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    selected = rows[:limit] if limit else rows
    with path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(["family", "kind", "count"])
        for (family, kind), count in selected:
            writer.writerow([family, kind, count])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contexts", type=Path, required=True, help="wall-owner-contexts TSV")
    parser.add_argument("--source-line-out", type=Path, required=True, help="source-line-family-summary TSV")
    parser.add_argument("--family-kind-out", type=Path, required=True, help="family-kind-summary TSV")
    parser.add_argument("--source-hash", default="", help="default public source hash or source label")
    parser.add_argument("--limit", type=int, default=0, help="maximum rows per output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source_counts: collections.Counter[SourceKey] = collections.Counter()
    family_counts: collections.Counter[FamilyKey] = collections.Counter()
    input_rows = 0
    for row in read_contexts(args.contexts):
        file_name = row.get("file", "")
        line = row.get("line", "")
        family = row.get("family", "")
        kind = row.get("kind", "").upper()
        count = as_int(row.get("count", "0"))
        source_hash = row_source_hash(row, args.source_hash)
        if not file_name or not line or not family or not kind or count <= 0:
            continue
        input_rows += 1
        source_counts[(file_name, line, family, kind, source_hash)] += count
        family_counts[(family, kind)] += count

    source_rows = sorted(source_counts.items(), key=sort_source)
    family_rows = sorted(family_counts.items(), key=sort_family)
    write_source_summary(args.source_line_out, source_rows, args.limit)
    write_family_summary(args.family_kind_out, family_rows, args.limit)
    print(
        "wall_owner_summary=pass "
        f"input_rows={input_rows} source_rows={len(source_rows)} family_rows={len(family_rows)} "
        f"source_line_out={args.source_line_out} family_kind_out={args.family_kind_out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
