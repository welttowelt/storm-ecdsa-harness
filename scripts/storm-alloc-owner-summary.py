#!/usr/bin/env python3
"""Summarize near-peak ALLOC owner rows into caller-level wall ownership."""

from __future__ import annotations

import argparse
import collections
import csv
import re
from pathlib import Path
from typing import Iterable


ALLOC_NEAR_RE = re.compile(r"active=(\d+).*?phase='([^']*)'.*?caller=(\S+)")


CallerKey = tuple[str, str]


class CallerSummary:
    def __init__(self) -> None:
        self.near_peak_allocs = 0
        self.min_active = 10**9
        self.max_active = 0
        self.phases: collections.Counter[str] = collections.Counter()
        self.peak_phases: collections.Counter[str] = collections.Counter()

    def add(self, active: int, phase: str, peak: int) -> None:
        self.near_peak_allocs += 1
        self.min_active = min(self.min_active, active)
        self.max_active = max(self.max_active, active)
        self.phases[phase] += 1
        if active >= peak:
            self.peak_phases[phase] += 1

    @property
    def peak_allocs(self) -> int:
        return sum(self.peak_phases.values())


def read_lines(path: Path) -> Iterable[str]:
    try:
        with path.open() as f:
            yield from f
    except FileNotFoundError as exc:
        raise SystemExit(f"input_not_found path={path}") from exc


def caller_key(raw: str) -> CallerKey:
    file_name, sep, line = raw.rpartition(":")
    if sep and line.isdigit():
        return file_name, line
    return raw, ""


def top_counter_key(counter: collections.Counter[str]) -> str:
    if not counter:
        return ""
    return counter.most_common(1)[0][0]


def parse_alloc_rows(path: Path, peak: int) -> tuple[int, dict[CallerKey, CallerSummary]]:
    rows = 0
    summaries: dict[CallerKey, CallerSummary] = collections.defaultdict(CallerSummary)
    for line in read_lines(path):
        if not line.startswith("ALLOC_NEAR"):
            continue
        match = ALLOC_NEAR_RE.search(line)
        if not match:
            continue
        rows += 1
        active = int(match.group(1))
        phase = match.group(2)
        caller = caller_key(match.group(3))
        summaries[caller].add(active, phase, peak)
    return rows, summaries


def sort_summary(item: tuple[CallerKey, CallerSummary]) -> tuple[int, int, str, int]:
    (file_name, line), summary = item
    try:
        line_int = int(line)
    except ValueError:
        line_int = 0
    return (-summary.near_peak_allocs, -summary.peak_allocs, file_name, line_int)


def write_summary(path: Path, rows: list[tuple[CallerKey, CallerSummary]], limit: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    selected = rows[:limit] if limit else rows
    with path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(
            [
                "caller_file",
                "caller_line",
                "phase_top",
                "near_peak_allocs",
                "min_active",
                "max_active",
                "binds_peak",
                "peak_allocs",
                "peak_phase_top",
            ]
        )
        for (file_name, line), summary in selected:
            writer.writerow(
                [
                    file_name,
                    line,
                    top_counter_key(summary.phases),
                    summary.near_peak_allocs,
                    summary.min_active,
                    summary.max_active,
                    1 if summary.peak_allocs else 0,
                    summary.peak_allocs,
                    top_counter_key(summary.peak_phases),
                ]
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="raw ALLOC_NEAR trace")
    parser.add_argument("--summary-out", type=Path, required=True, help="caller-level TSV summary")
    parser.add_argument("--peak", type=int, default=1152, help="active allocation threshold for binding wall")
    parser.add_argument("--limit", type=int, default=0, help="maximum emitted rows")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    input_rows, summaries = parse_alloc_rows(args.input, args.peak)
    rows = sorted(summaries.items(), key=sort_summary)
    write_summary(args.summary_out, rows, args.limit)
    peak_owner_rows = sum(1 for _, summary in rows if summary.peak_allocs)
    peak_phase_rows = sum(len(summary.peak_phases) for _, summary in rows)
    print(
        "alloc_owner_summary=pass "
        f"input_rows={input_rows} caller_rows={len(rows)} peak_owner_rows={peak_owner_rows} "
        f"peak_phase_rows={peak_phase_rows} summary_out={args.summary_out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
