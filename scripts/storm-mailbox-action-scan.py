#!/usr/bin/env python3
"""Surface directed worker asks before an operator posts a new steering note.

This is a public-safe text scanner. It reads a redacted mailbox tail or any
similar coordination transcript from a file or stdin and prints lines that look
like direct asks to the operator since the latest operator steering post. It
does not contact hosts, read private paths, dispatch compute, or submit.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_TARGETS = (
    "Storm-Codex",
    "codex-storm",
    "Boss Storm",
    "Storm Codex",
)

ASK_CUES = (
    "confirm whether",
    "please ack",
    "please ACK",
    "awaiting",
    "want me to",
    "should i",
    "should I",
    "decision requested",
    "operator decision",
    "needs storm",
    "storm-codex:",
)

HEADER_FROM_RE = re.compile(r"^##\s+.+?\s+from:\s*([^-#\n]+?)(?:\s+-|$)", re.IGNORECASE)
BRACKET_ROUTE_RE = re.compile(r"^\[[^\]]+\]\s+([^-\n]+?)\s*->\s*([^\s:]+)")


@dataclass
class ReviewLine:
    lineno: int
    speaker: str
    target: str
    cue: str
    text: str


def read_text(path: Path | None) -> str:
    if path is None or str(path) == "-":
        return sys.stdin.read()
    return path.read_text(encoding="utf-8")


def line_speaker(line: str, current: str) -> str:
    match = HEADER_FROM_RE.search(line)
    if match:
        return match.group(1).strip()
    match = BRACKET_ROUTE_RE.search(line)
    if match:
        return match.group(1).strip()
    return current


def header_speaker(line: str) -> str:
    match = HEADER_FROM_RE.search(line)
    if match:
        return match.group(1).strip()
    return ""


def line_is_operator_ack(line: str, targets: list[str]) -> bool:
    stripped = line.strip().lower()
    for target in targets:
        target_lower = target.lower()
        if stripped.startswith(f"ack {target_lower} "):
            return True
        if stripped.startswith(f"nack {target_lower} "):
            return True
    return False


def target_hit(line: str, targets: list[str]) -> str:
    lower = line.lower()
    for target in targets:
        if target.lower() in lower:
            return target
    return ""


def speaker_is_target(speaker: str, targets: list[str]) -> bool:
    speaker = speaker.lower()
    return any(target.lower() in speaker for target in targets)


def ask_cue(line: str) -> str:
    if "?" in line:
        return "question-mark"
    lower = line.lower()
    for cue in ASK_CUES:
        if cue.lower() in lower:
            return cue.lower()
    return ""


def compact(text: str, width: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= width:
        return text
    return text[: max(0, width - 3)] + "..."


def scan(text: str, targets: list[str], context_lines: int) -> list[ReviewLine]:
    lines = text.splitlines()
    reviews: list[ReviewLine] = []
    current_speaker = "unknown"
    recent_target = ""
    recent_target_ttl = 0
    start_index = 0

    for index, line in enumerate(lines):
        speaker = header_speaker(line)
        if (speaker and speaker_is_target(speaker, targets)) or line_is_operator_ack(line, targets):
            start_index = index

    for index, line in enumerate(lines[start_index:], start=start_index + 1):
        current_speaker = line_speaker(line, current_speaker)
        if line_is_operator_ack(line, targets):
            current_speaker = target_hit(line, targets) or current_speaker
        hit = target_hit(line, targets)
        if hit:
            recent_target = hit
            recent_target_ttl = context_lines
        elif recent_target_ttl > 0:
            recent_target_ttl -= 1
        else:
            recent_target = ""

        cue = ask_cue(line)
        target = hit or recent_target
        if cue and target and not speaker_is_target(current_speaker, targets):
            reviews.append(
                ReviewLine(
                    lineno=index,
                    speaker=current_speaker or "unknown",
                    target=target,
                    cue=cue,
                    text=compact(line, 220),
                )
            )
    return reviews


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("-"), help="file to scan, or '-' for stdin")
    parser.add_argument(
        "--target",
        action="append",
        default=[],
        help="target alias to treat as the operator; may be repeated",
    )
    parser.add_argument(
        "--context-lines",
        type=int,
        default=2,
        help="also flag ask-cue lines this many lines after a target mention",
    )
    parser.add_argument("--fail-on-review", action="store_true", help="exit 1 when review lines are found")
    parser.add_argument("--max-text", type=int, default=220, help="reserved for output compatibility")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    targets = args.target or list(DEFAULT_TARGETS)
    reviews = scan(read_text(args.input), targets, max(0, args.context_lines))
    status = "review" if reviews else "pass"
    print(f"mailbox_action_scan={status} count={len(reviews)}")
    for review in reviews:
        print(
            "review "
            f"line={review.lineno} "
            f"speaker={review.speaker!r} "
            f"target={review.target!r} "
            f"cue={review.cue!r} "
            f"text={review.text!r}"
        )
    if reviews and args.fail_on_review:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
