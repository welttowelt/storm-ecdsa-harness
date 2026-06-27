#!/usr/bin/env python3
"""Join Gidney threaded-add trace rows with near-peak allocation rows."""

from __future__ import annotations

import argparse
import collections
import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


THREAD_RE = re.compile(
    r"TLM_GIDNEY_THREAD call=(\d+) phase=([^ ]+) width=(\d+) "
    r"cin=(\d+) cout=(\d+) vents=(\d+) ops_start=(\d+) ops_end=(\d+)"
)


@dataclass
class ThreadRow:
    call: int
    phase: str
    width: int
    cin: int
    cout: int
    vents: int
    ops_start: int
    ops_end: int


@dataclass
class AllocSummary:
    near_allocs: int = 0
    peak_allocs: int = 0
    min_active: int = 10**9
    max_active: int = 0
    active_counts: collections.Counter[int] = field(default_factory=collections.Counter)

    def add(self, active: int, peak: int) -> None:
        self.near_allocs += 1
        self.min_active = min(self.min_active, active)
        self.max_active = max(self.max_active, active)
        self.active_counts[active] += 1
        if active >= peak:
            self.peak_allocs += 1


def read_lines(path: Path) -> Iterable[str]:
    try:
        with path.open() as f:
            yield from f
    except FileNotFoundError as exc:
        raise SystemExit(f"input_not_found path={path}") from exc


def field_after(line: str, name: str) -> str | None:
    marker = f"{name}="
    start = line.find(marker)
    if start < 0:
        return None
    value_start = start + len(marker)
    if value_start < len(line) and line[value_start] == "'":
        value_end = line.find("'", value_start + 1)
        if value_end < 0:
            return None
        return line[value_start + 1 : value_end]
    value_end = line.find(" ", value_start)
    if value_end < 0:
        value_end = len(line)
    return line[value_start:value_end].rstrip("\r\n")


def parse_thread(line: str) -> ThreadRow | None:
    match = THREAD_RE.search(line)
    if not match:
        return None
    return ThreadRow(
        call=int(match.group(1)),
        phase=match.group(2),
        width=int(match.group(3)),
        cin=int(match.group(4)),
        cout=int(match.group(5)),
        vents=int(match.group(6)),
        ops_start=int(match.group(7)),
        ops_end=int(match.group(8)),
    )


def parse_dead_calls_from_text(text: str) -> set[int]:
    calls: set[int] = set()
    in_array = False
    for line in text.splitlines():
        if "GIDNEY_THREAD_BOUNDARY_DEAD_CALLS" in line:
            in_array = True
        if not in_array:
            continue
        calls.update(int(value) for value in re.findall(r"\b\d+\b", line))
        if "];" in line:
            break
    return calls


def parse_dead_calls(source: Path | None, csv_text: str) -> set[int]:
    calls: set[int] = set()
    if source:
        calls.update(parse_dead_calls_from_text(source.read_text()))
    if csv_text:
        calls.update(int(value) for value in re.findall(r"\d+", csv_text))
    return calls


def parse_trace(path: Path, peak: int) -> tuple[int, int, dict[int, ThreadRow], dict[int, AllocSummary]]:
    thread_rows = 0
    alloc_rows = 0
    threads_by_ops_start: dict[int, ThreadRow] = {}
    alloc_by_ops_start: dict[int, AllocSummary] = collections.defaultdict(AllocSummary)
    for raw_line in read_lines(path):
        line = raw_line.rstrip("\r\n")
        thread = parse_thread(line)
        if thread is not None:
            thread_rows += 1
            threads_by_ops_start[thread.ops_start] = thread
            continue
        if not line.startswith("ALLOC_NEAR") or "gidney.rs:1217" not in line:
            continue
        active = field_after(line, "active")
        ops_idx = field_after(line, "ops_idx")
        if active is None or ops_idx is None:
            continue
        try:
            active_int = int(active)
            ops_idx_int = int(ops_idx)
        except ValueError:
            continue
        alloc_rows += 1
        alloc_by_ops_start[ops_idx_int].add(active_int, peak)
    return thread_rows, alloc_rows, threads_by_ops_start, alloc_by_ops_start


def active_counts_text(counter: collections.Counter[int]) -> str:
    return ",".join(f"{active}:{counter[active]}" for active in sorted(counter, reverse=True))


def write_join(
    path: Path,
    threads_by_ops_start: dict[int, ThreadRow],
    alloc_by_ops_start: dict[int, AllocSummary],
    dead_calls: set[int],
) -> tuple[int, int, int]:
    path.parent.mkdir(parents=True, exist_ok=True)
    joined_rows = 0
    dead_peak_rows = 0
    unmatched_alloc_ops = 0
    with path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(
            [
                "call",
                "phase",
                "width",
                "cin",
                "cout",
                "vents",
                "ops_start",
                "ops_end",
                "near_allocs",
                "peak_allocs",
                "min_active",
                "max_active",
                "boundary_dead",
                "dead_boundary_peak_candidate",
                "active_counts",
            ]
        )
        for ops_start, summary in sorted(alloc_by_ops_start.items()):
            thread = threads_by_ops_start.get(ops_start)
            if thread is None:
                unmatched_alloc_ops += 1
                continue
            boundary_dead = 1 if thread.call in dead_calls else 0
            candidate = 1 if boundary_dead and thread.cout and summary.peak_allocs else 0
            dead_peak_rows += candidate
            joined_rows += 1
            writer.writerow(
                [
                    thread.call,
                    thread.phase,
                    thread.width,
                    thread.cin,
                    thread.cout,
                    thread.vents,
                    thread.ops_start,
                    thread.ops_end,
                    summary.near_allocs,
                    summary.peak_allocs,
                    summary.min_active,
                    summary.max_active,
                    boundary_dead,
                    candidate,
                    active_counts_text(summary.active_counts),
                ]
            )
    return joined_rows, dead_peak_rows, unmatched_alloc_ops


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="trace containing ALLOC_NEAR and TLM_GIDNEY_THREAD rows")
    parser.add_argument("--out", type=Path, required=True, help="joined TSV output")
    parser.add_argument("--peak", type=int, default=1152, help="active allocation threshold")
    parser.add_argument("--gidney-source", type=Path, help="source file containing GIDNEY_THREAD_BOUNDARY_DEAD_CALLS")
    parser.add_argument("--dead-calls", default="", help="extra comma/space separated dead-boundary call indexes")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    dead_calls = parse_dead_calls(args.gidney_source, args.dead_calls)
    thread_rows, alloc_rows, threads_by_ops_start, alloc_by_ops_start = parse_trace(args.input, args.peak)
    joined_rows, dead_peak_rows, unmatched_alloc_ops = write_join(
        args.out, threads_by_ops_start, alloc_by_ops_start, dead_calls
    )
    print(
        "gidney_thread_join=pass "
        f"thread_rows={thread_rows} alloc_rows={alloc_rows} alloc_ops={len(alloc_by_ops_start)} "
        f"joined_rows={joined_rows} unmatched_alloc_ops={unmatched_alloc_ops} "
        f"dead_calls={len(dead_calls)} dead_boundary_peak_candidates={dead_peak_rows} out={args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
