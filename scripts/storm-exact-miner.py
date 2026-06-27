#!/usr/bin/env python3
"""Build public, proof-ready exact-skip packets from op-trace facts.

This tool is intentionally a coordinator/miner, not a solver. It normalizes
public trace facts, finds value-exact omission candidates, emits proof
obligations, and ranks packets for fleet workers. It never submits, hunts
nonces, touches private fleet state, or declares a route clean.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


PRIVATE_KEY_RE = "|".join(
    [
        "id_" + "ed25519",
        "BEGIN OPEN" + "SSH PRIVATE KEY",
        "BEGIN RSA" + " PRIVATE KEY",
    ]
)

FORBIDDEN_PATTERNS = {
    "private_home_path": re.compile(r"/Users/[A-Za-z0-9._-]+"),
    "remote_command": re.compile(r"ssh\s+\S+@"),
    "root_remote": re.compile("root" + "@"),
    "host_port": re.compile(r"([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{2,5})?"),
    "runpod_endpoint": re.compile(r"runpod\.io|proxy\.runpod\.net"),
    "private_key_name": re.compile(PRIVATE_KEY_RE),
    "url_token": re.compile("to" + "ken="),
    "live_mailbox_name": re.compile("ECDSA_FAIL_" + "AGENT_HANDOFF"),
    "raw_nonce_assignment": re.compile(
        r"(^|[^A-Za-z])(nonce|TAIL_NONCE|DIALOG_TAIL_NONCE)[_A-Za-z0-9-]*[=:]\s*[0-9]{4,}",
        re.IGNORECASE,
    ),
}

EVIDENCE_LABELS = {
    "Paper score",
    "Prefilter",
    "Partial run",
    "Local full run",
    "Promoted",
}

PROOF_STATUS_ORDER = {
    "CERTIFIED": 0,
    "UNKNOWN": 1,
    "COUNTEREXAMPLE": 2,
}


class ExactMinerError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Mine public value-exact skip packets from normalized op-trace facts."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    trace = sub.add_parser("trace-facts", help="normalize JSONL or TSV op-trace facts")
    trace.add_argument("--input", required=True, help="public JSONL/TSV trace facts")
    trace.add_argument("--out", required=True, help="normalized JSONL output path")

    mine = sub.add_parser("mine", help="find omission candidates from normalized facts")
    mine.add_argument("--facts", required=True, help="normalized facts JSONL")
    mine.add_argument("--out", required=True, help="candidate JSONL output path")

    prove = sub.add_parser("prove", help="create proof packets from candidates")
    prove.add_argument("--candidates", required=True, help="candidate JSONL")
    prove.add_argument("--out", required=True, help="proof packet JSONL output path")

    rank = sub.add_parser("rank", help="rank proof packets for fleet intake")
    rank.add_argument("--proofs", required=True, help="proof packet JSONL")
    rank.add_argument("--out", required=True, help="ranked JSONL output path")

    return parser.parse_args()


def fail(message: str) -> None:
    raise ExactMinerError(message)


def load_records(path: str) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.is_file():
        fail(f"input_not_found path={path}")
    raw = p.read_text()
    check_public_safe(raw, f"file:{p.name}")
    first = next((line for line in raw.splitlines() if line.strip()), "")
    if not first:
        return []
    if first.lstrip().startswith("{"):
        records = [json.loads(line) for line in raw.splitlines() if line.strip()]
    else:
        records = list(csv.DictReader(raw.splitlines(), delimiter="\t"))
    for record in records:
        check_public_safe(record, "record")
    return records


def write_jsonl(path: str, records: Iterable[dict[str, Any]]) -> None:
    p = Path(path)
    with p.open("w") as f:
        for record in records:
            check_public_safe(record, "output")
            f.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")


def check_public_safe(value: Any, where: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            check_public_safe(str(key), where)
            check_public_safe(item, where)
        return
    if isinstance(value, list):
        for item in value:
            check_public_safe(item, where)
        return
    if not isinstance(value, str):
        return
    for name, pattern in FORBIDDEN_PATTERNS.items():
        if pattern.search(value):
            fail(f"redaction_risk where={where} pattern={name}")


def as_bool(value: Any, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def as_number(value: Any, default: float = 1.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(v) for v in value if str(v) != ""]
    text = str(value).strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            decoded = json.loads(text)
            if isinstance(decoded, list):
                return [str(v) for v in decoded if str(v) != ""]
        except json.JSONDecodeError:
            pass
    return [part.strip() for part in re.split(r"[,\s]+", text) if part.strip()]


def as_int_maybe(value: Any) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip()
    try:
        return int(text, 0)
    except ValueError:
        return None


def stable_id(prefix: str, *parts: Any) -> str:
    h = hashlib.sha256()
    for part in parts:
        h.update(str(part).encode())
        h.update(b"\0")
    return f"{prefix}-{h.hexdigest()[:16]}"


def normalize_fact(record: dict[str, Any], index: int) -> dict[str, Any]:
    frontier = str(record.get("frontier", "unknown"))
    source_base = str(record.get("source_base", record.get("source", "unknown")))
    stream_hash = str(record.get("stream_hash", record.get("ops_hash", "unknown")))
    source_location = str(record.get("source_location", record.get("source_file", "unknown")))
    op_class = str(record.get("op_class", record.get("kind", "unknown"))).lower()
    op_id = str(record.get("op_id", record.get("index", index)))

    fact = {
        "fact_id": stable_id("fact", frontier, stream_hash, op_id, source_location, op_class),
        "frontier": frontier,
        "source_base": source_base,
        "stream_hash": stream_hash,
        "op_id": op_id,
        "source_location": source_location,
        "op_class": op_class,
        "controls": as_list(record.get("controls")),
        "targets": as_list(record.get("targets", record.get("target"))),
        "known_zero_controls": as_list(record.get("known_zero_controls")),
        "known_one_controls": as_list(record.get("known_one_controls")),
        "dead_targets": as_list(record.get("dead_targets")),
        "target_live": as_bool(record.get("target_live"), default=True),
        "exact_remainder": as_bool(record.get("exact_remainder"), default=False),
        "allocator_unchanged": as_bool(record.get("allocator_unchanged"), default=True),
        "emitted_weight": as_number(record.get("emitted_weight"), default=1.0),
        "executed_weight": as_number(record.get("executed_weight"), default=1.0),
        "support_certificate": str(record.get("support_certificate", "")),
        "branch_context": str(record.get("branch_context", "")),
        "value_max": record.get("value_max", ""),
        "modulus": record.get("modulus", ""),
    }
    return fact


def build_candidate(fact: dict[str, Any], reason: str, proof_kind: str, proof_inputs: dict[str, Any]) -> dict[str, Any]:
    delta = -abs(as_number(fact.get("executed_weight"), default=1.0))
    route_id = stable_id("exact-skip", fact["fact_id"], reason, proof_kind)
    return {
        "route_id": route_id,
        "frontier": fact["frontier"],
        "source_base": fact["source_base"],
        "stream_hash": fact["stream_hash"],
        "fact_id": fact["fact_id"],
        "source_location": fact["source_location"],
        "op_class": fact["op_class"],
        "executed_weight": fact["executed_weight"],
        "allocator_unchanged": fact["allocator_unchanged"],
        "proof_kind": proof_kind,
        "proof_status": "UNPROVEN",
        "proof_inputs": proof_inputs,
        "expected_avgT_delta": delta,
        "evidence_label": "Prefilter",
        "validation_target": "trusted full 0/0/0 after source proof",
        "kill_gate": "block compute if allocator changes, proof is UNKNOWN, or any cls/pha/anc dirt appears",
        "reason": reason,
    }


def mine_candidates(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for fact in facts:
        controls = set(fact["controls"])
        known_zero = controls.intersection(fact["known_zero_controls"])
        if known_zero:
            candidates.append(
                build_candidate(
                    fact,
                    "known-zero-control",
                    "qcp",
                    {"controls": sorted(known_zero), "support_certificate": fact["support_certificate"]},
                )
            )
        dead_targets = set(fact["targets"]).intersection(fact["dead_targets"])
        if dead_targets or not fact["target_live"]:
            candidates.append(
                build_candidate(
                    fact,
                    "dead-output",
                    "dge",
                    {
                        "dead_targets": sorted(dead_targets),
                        "target_live": fact["target_live"],
                        "support_certificate": fact["support_certificate"],
                    },
                )
            )
        if fact["exact_remainder"]:
            candidates.append(
                build_candidate(
                    fact,
                    "exact-remainder",
                    "bitvec_unsat",
                    {
                        "value_max": fact["value_max"],
                        "modulus": fact["modulus"],
                        "support_certificate": fact["support_certificate"],
                    },
                )
            )
        if fact["op_class"] in {"cswap", "shift"} and known_zero:
            candidates.append(
                build_candidate(
                    fact,
                    "reachable-control-excludes-fire",
                    "aqcel",
                    {"controls": sorted(known_zero), "support_certificate": fact["support_certificate"]},
                )
            )
    deduped: list[dict[str, Any]] = []
    for candidate in candidates:
        if candidate["route_id"] in seen:
            continue
        seen.add(candidate["route_id"])
        deduped.append(candidate)
    return deduped


def validate_candidate_schema(candidate: dict[str, Any]) -> None:
    required = {
        "route_id",
        "frontier",
        "source_base",
        "stream_hash",
        "source_location",
        "op_class",
        "executed_weight",
        "allocator_unchanged",
        "proof_kind",
        "proof_status",
        "expected_avgT_delta",
        "evidence_label",
        "validation_target",
        "kill_gate",
    }
    missing = sorted(required.difference(candidate))
    if missing:
        fail(f"candidate_missing_fields route_id={candidate.get('route_id', 'unknown')} fields={','.join(missing)}")
    if candidate["evidence_label"] not in EVIDENCE_LABELS:
        fail(f"unsupported_evidence_label route_id={candidate['route_id']} label={candidate['evidence_label']}")


def prove_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    validate_candidate_schema(candidate)
    packet = dict(candidate)
    inputs = packet.get("proof_inputs", {})
    certificate = str(inputs.get("support_certificate", "")).strip()
    status = "UNKNOWN"
    note = "manual proof required before compute"

    if not packet.get("allocator_unchanged", False):
        status = "COUNTEREXAMPLE"
        note = "allocator order changed; this route is outside fixed-allocation exact-skip scope"
    elif packet["proof_kind"] == "bitvec_unsat":
        value_max = as_int_maybe(inputs.get("value_max"))
        modulus = as_int_maybe(inputs.get("modulus"))
        if value_max is not None and modulus is not None and value_max < modulus:
            status = "CERTIFIED"
            note = "built-in range check proves value_max < modulus"
        elif certificate:
            status = "CERTIFIED"
            note = "external public certificate supplied"
    elif certificate:
        status = "CERTIFIED"
        note = "external public certificate supplied"

    packet["proof_status"] = status
    packet["proof_note"] = note
    packet["proof_hash"] = stable_id("proof", packet["route_id"], packet["proof_kind"], status, inputs)
    return packet


def rank_key(packet: dict[str, Any]) -> tuple[Any, ...]:
    status_rank = PROOF_STATUS_ORDER.get(packet.get("proof_status", "UNKNOWN"), 9)
    allocator_rank = 0 if packet.get("allocator_unchanged", False) else 1
    proof_locality = 0 if packet.get("proof_kind") in {"qcp", "bitvec_unsat", "dge", "aqcel"} else 1
    delta = as_number(packet.get("expected_avgT_delta"), default=0.0)
    return (status_rank, allocator_rank, proof_locality, delta)


def main() -> int:
    args = parse_args()
    try:
        if args.command == "trace-facts":
            records = load_records(args.input)
            facts = [normalize_fact(record, idx) for idx, record in enumerate(records)]
            write_jsonl(args.out, facts)
            print(f"storm_exact_miner=pass command=trace-facts facts={len(facts)}")
        elif args.command == "mine":
            facts = load_records(args.facts)
            candidates = mine_candidates(facts)
            write_jsonl(args.out, candidates)
            print(f"storm_exact_miner=pass command=mine candidates={len(candidates)}")
        elif args.command == "prove":
            candidates = load_records(args.candidates)
            proof_packets = [prove_candidate(candidate) for candidate in candidates]
            write_jsonl(args.out, proof_packets)
            print(f"storm_exact_miner=pass command=prove packets={len(proof_packets)}")
        elif args.command == "rank":
            proof_packets = load_records(args.proofs)
            for packet in proof_packets:
                validate_candidate_schema(packet)
            ranked = sorted(proof_packets, key=rank_key)
            write_jsonl(args.out, ranked)
            print(f"storm_exact_miner=pass command=rank packets={len(ranked)}")
        return 0
    except (ExactMinerError, json.JSONDecodeError, OSError, KeyError, ValueError) as exc:
        print(f"storm_exact_miner=fail error={exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
