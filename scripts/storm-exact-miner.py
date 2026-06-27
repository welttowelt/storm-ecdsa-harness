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


SITE_CLASSIFIERS: dict[tuple[str, int], dict[str, str]] = {
    ("gcd.rs", 1460): {
        "primitive_family": "apply_cswap_live",
        "support_domain": "GCD apply symbol with swp=1 and unequal coordinate registers",
        "falsifier_template": "choose a reachable apply symbol with swp=1 and x_reg[j] != y_reg[j]",
        "witness": "step0 apply model: swp=1, forward xr=1 yr=0, reverse xr=0 yr=1",
    },
    ("gcd.rs", 1508): {
        "primitive_family": "apply_cswap_live",
        "support_domain": "GCD inverse-apply symbol with swp=1 and unequal coordinate registers",
        "falsifier_template": "choose a reachable apply symbol with swp=1 and x_reg[j] != y_reg[j]",
        "witness": "step0 apply model: swp=1, forward xr=1 yr=0, reverse xr=0 yr=1",
    },
    ("arith.rs", 834): {
        "primitive_family": "adder_carry_live",
        "support_domain": "plain Gidney carry creation",
        "falsifier_template": "set both carry controls to 1 and compare the next sum bit",
        "witness": "n=2, a=01, b=01; skipping the carry changes 1+1 from 10 to 00",
    },
    ("square.rs", 151): {
        "primitive_family": "square_cross_live",
        "support_domain": "symmetric square off-diagonal cross product",
        "falsifier_template": "set the two source square bits to 1",
        "witness": "n=2, x=11; skipping the cross term changes x^2 from 1001 to 0101",
    },
    ("square.rs", 180): {
        "primitive_family": "square_cross_live",
        "support_domain": "reverse symmetric square off-diagonal cross product",
        "falsifier_template": "start from a valid product row whose cross term is 1",
        "witness": "n=2, x=11; reverse row must rebuild the cross term to drain prod",
    },
    ("codec.rs", 272): {
        "primitive_family": "codec_table_live",
        "support_domain": "compressed-dialog pair/triple codec support",
        "falsifier_template": "enumerate valid compressed symbols and find a true-control row",
        "witness": "valid codec triples over {001,100,101,110,111} make every logical CCX live",
    },
    ("arith.rs", 1196): {
        "primitive_family": "const_comparator_carry_live",
        "support_domain": "+f HMR phase-recovery comparator carry",
        "falsifier_template": "choose constant bit0, cin=0, and a0=1",
        "witness": "F_SECP256K1 bit0=1 gives ci=1 and next carry=1",
        "phase_obligation": "missing carry changes the CCZ/CZ phase discharge",
    },
    ("arith.rs", 1240): {
        "primitive_family": "phase_recovery_live",
        "support_domain": "HMR phase-recovery CCZ",
        "falsifier_template": "set ctrl, a_top, and cy_top to 1 under the HMR condition",
        "witness": "ctrl=1, a_top=1, cy_top=1 stamps a required phase",
        "phase_obligation": "omission is phase dirt even if the value path is unchanged",
    },
    ("arith.rs", 1312): {
        "primitive_family": "ffg_prefix_carry0_live",
        "support_domain": "+f prefix carry0, f bit0 is one",
        "falsifier_template": "set ctrl=1 and a0=1",
        "witness": "cy0 = ctrl & a0 is 1 for f bit0",
    },
    ("arith.rs", 1854): {
        "primitive_family": "vented_carry_live",
        "support_domain": "support-bounded carry after dead(i) guard is false",
        "falsifier_template": "set a[i]=1 and b[i]=1 on a reached live bit",
        "witness": "line is emitted only when dead(i)=false; a=b=1 produces carry",
    },
    ("arith.rs", 1859): {
        "primitive_family": "carry_live",
        "support_domain": "non-vented carry creation after dead(i) guard is false",
        "falsifier_template": "set a[i]=1 and b[i]=1 on a reached live bit",
        "witness": "a=b=1 toggles b[i+1]",
    },
    ("arith.rs", 1874): {
        "primitive_family": "carry_uncompute_live",
        "support_domain": "non-vented carry uncompute after dead(i) guard is false",
        "falsifier_template": "start from a valid live carry with a[i]=b[i]=1",
        "witness": "reverse CCX is needed to restore the carry lane",
        "restoration_obligation": "skipping leaves the carry lane dirty",
    },
    ("arith.rs", 504): {
        "primitive_family": "cuccaro_sum_live",
        "support_domain": "controlled Cuccaro gated sum",
        "falsifier_template": "set ctrl=1, xi=1, yi=0",
        "witness": "baseline toggles yi; omission leaves yi unchanged",
    },
    ("comparator.rs", 702): {
        "primitive_family": "comparator_carry_live",
        "support_domain": "bottom comparator carry",
        "falsifier_template": "one-bit comparator witness with a=0,b=1,split=1",
        "witness": "skipping flips the comparison predicate",
    },
    ("comparator.rs", 740): {
        "primitive_family": "comparator_carry_uncompute_live",
        "support_domain": "reverse bottom comparator carry cleanup",
        "falsifier_template": "start from the forward comparator witness state",
        "witness": "reverse omission leaves a,b,c dirty",
        "restoration_obligation": "skipping leaves comparator scratch dirty",
    },
    ("comparator.rs", 821): {
        "primitive_family": "comparator_predicate_live",
        "support_domain": "controlled comparator predicate deposit",
        "falsifier_template": "set ctrl=1 and carry=0 in the X-sandwich body",
        "witness": "ctrl=1, carry=0 toggles target after carry is inverted",
    },
    ("gcd.rs", 748): {
        "primitive_family": "controlled_double_cswap_live",
        "support_domain": "controlled modular double left-shift",
        "falsifier_template": "set ctrl=1 and adjacent shifted bits unequal",
        "witness": "controlled shift changes the value when neighboring bits differ",
    },
    ("gcd.rs", 776): {
        "primitive_family": "controlled_double_cswap_live",
        "support_domain": "controlled modular double reverse shift",
        "falsifier_template": "set ctrl=1 and adjacent shifted bits unequal",
        "witness": "reverse controlled shift is needed to restore the value",
    },
    ("mcx.rs", 54): {
        "primitive_family": "mcx_prefix_live",
        "support_domain": "two-control prefix target toggle",
        "falsifier_template": "set both controls to 1 and target to 0",
        "witness": "a=b=1 toggles target",
    },
    ("mcx.rs", 77): {
        "primitive_family": "mcx_prefix_live",
        "support_domain": "scheduled prefix-control CCX",
        "falsifier_template": "set both controls to 1 and target to 0",
        "witness": "a=b=1 toggles target",
    },
    ("fused.rs", 991): {
        "primitive_family": "fold_control_live",
        "support_domain": "fold derived control e&d",
        "falsifier_template": "set fold controls e=1 and d=1",
        "witness": "e=d=1 sets cc=1",
    },
    ("fused.rs", 1096): {
        "primitive_family": "fold_control_live",
        "support_domain": "rebuilt fold derived control e&d",
        "falsifier_template": "set fold controls e=1 and d=1",
        "witness": "reverse fold needs cc rebuilt for cleanup/phase",
        "restoration_obligation": "skipping breaks fold control cleanup",
    },
    ("fused.rs", 1170): {
        "primitive_family": "fold_control_live",
        "support_domain": "chunked fold derived control e&d",
        "falsifier_template": "set fold controls e=1 and d=1",
        "witness": "e=d=1 sets cc=1",
    },
    ("fused.rs", 1562): {
        "primitive_family": "fold_carry_live",
        "support_domain": "fused fold conditional carry helper",
        "falsifier_template": "set the two carry controls to 1",
        "witness": "c1=c2=1 toggles the fold carry target",
    },
    ("fused.rs", 1990): {
        "primitive_family": "fold_s2_y1_live",
        "support_domain": "inverse cdouble fold d=s2&y1",
        "falsifier_template": "set s2=1 and y1=1",
        "witness": "s2=y1=1 sets d=1",
    },
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
    trace.add_argument("--frontier", default="", help="default frontier label when input omits frontier")
    trace.add_argument("--source-base", default="", help="default source base when input omits source_base")
    trace.add_argument("--stream-hash", default="", help="default stream hash when input omits stream_hash")

    mine = sub.add_parser("mine", help="find omission candidates from normalized facts")
    mine.add_argument("--facts", required=True, help="normalized facts JSONL")
    mine.add_argument("--out", required=True, help="candidate JSONL output path")
    mine.add_argument(
        "--include-unknown-sites",
        action="store_true",
        help="also emit UNKNOWN manual-proof packets for source-site facts with no built-in proof trigger",
    )
    mine.add_argument(
        "--max-unknown-sites",
        type=int,
        default=0,
        help="maximum UNKNOWN site packets to emit; 0 means no limit",
    )
    mine.add_argument(
        "--min-site-weight",
        type=float,
        default=1.0,
        help="minimum executed weight for --include-unknown-sites packets",
    )

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


def source_site_key(source_location: str) -> tuple[str, int] | None:
    match = re.search(r"([^/:]+\.rs):(\d+)$", source_location)
    if not match:
        return None
    return (match.group(1), int(match.group(2)))


def classify_source_site(source_location: str) -> dict[str, str]:
    key = source_site_key(source_location)
    if key is None:
        return {}
    return SITE_CLASSIFIERS.get(key, {})


def text_field(record: dict[str, Any], name: str, default: str = "") -> str:
    value = record.get(name, default)
    if value is None:
        return default
    return str(value)


def normalize_fact(record: dict[str, Any], index: int, defaults: dict[str, str] | None = None) -> dict[str, Any]:
    defaults = defaults or {}
    frontier = str(record.get("frontier") or defaults.get("frontier") or "unknown")
    source_base = str(record.get("source_base") or record.get("source") or defaults.get("source_base") or "unknown")
    source_file = str(record.get("source_file", record.get("file", "")))
    source_line = str(record.get("source_line", record.get("line", "")))
    if record.get("source_location"):
        source_location = str(record["source_location"])
    elif source_file and source_line:
        source_location = f"{source_file}:{source_line}"
    else:
        source_location = "unknown"
    context = str(record.get("branch_context", record.get("context", "")))
    rank = str(record.get("rank", ""))
    first_idx = str(record.get("first_idx", ""))
    last_idx = str(record.get("last_idx", ""))
    stream_hash = str(record.get("stream_hash") or record.get("ops_hash") or defaults.get("stream_hash") or "")
    if not stream_hash:
        stream_hash = stable_id("site-stream", source_base, source_location, context, rank, first_idx, last_idx)
    op_class = str(record.get("op_class", record.get("kind", "unknown"))).lower()
    if record.get("op_id"):
        op_id = str(record["op_id"])
    elif rank or first_idx or last_idx or context:
        op_id = f"rank={rank or index};context={context or 'none'};span={first_idx or '?'}-{last_idx or '?'}"
    else:
        op_id = str(record.get("index", index))
    classifier = classify_source_site(source_location)

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
        "emitted_weight": as_number(record.get("emitted_weight", record.get("count")), default=1.0),
        "executed_weight": as_number(record.get("executed_weight", record.get("count")), default=1.0),
        "support_certificate": str(record.get("support_certificate", "")),
        "branch_context": context,
        "site_rank": rank,
        "trace_span": {
            "first_idx": first_idx,
            "last_idx": last_idx,
        },
        "primitive_family": text_field(record, "primitive_family", classifier.get("primitive_family", "")),
        "support_domain": text_field(record, "support_domain", classifier.get("support_domain", "")),
        "falsifier_template": text_field(
            record,
            "falsifier_template",
            classifier.get("falsifier_template", ""),
        ),
        "witness": text_field(record, "witness", classifier.get("witness", "")),
        "phase_obligation": text_field(record, "phase_obligation", classifier.get("phase_obligation", "")),
        "restoration_obligation": text_field(
            record,
            "restoration_obligation",
            classifier.get("restoration_obligation", ""),
        ),
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
        "branch_context": fact.get("branch_context", ""),
        "site_rank": fact.get("site_rank", ""),
        "trace_span": fact.get("trace_span", {}),
        "primitive_family": fact.get("primitive_family", ""),
        "support_domain": fact.get("support_domain", ""),
        "falsifier_template": fact.get("falsifier_template", ""),
        "witness": fact.get("witness", ""),
        "phase_obligation": fact.get("phase_obligation", ""),
        "restoration_obligation": fact.get("restoration_obligation", ""),
        "fastest_falsifier": "derive the source invariant, then run a toy/support enumeration or trace witness before any circuit edit",
    }


def has_source_counterexample(fact: dict[str, Any]) -> bool:
    family = str(fact.get("primitive_family", ""))
    return bool(family and fact.get("falsifier_template") and fact.get("witness"))


def source_site_backlog_candidate(fact: dict[str, Any]) -> dict[str, Any]:
    proof_kind = "source_counterexample" if has_source_counterexample(fact) else "manual_source_invariant"
    reason = "source-site-counterexample" if proof_kind == "source_counterexample" else "source-site-proof-backlog"
    return build_candidate(
        fact,
        reason,
        proof_kind,
        {
            "source_location": fact["source_location"],
            "op_class": fact["op_class"],
            "branch_context": fact.get("branch_context", ""),
            "site_rank": fact.get("site_rank", ""),
            "trace_span": fact.get("trace_span", {}),
            "support_certificate": fact["support_certificate"],
            "primitive_family": fact.get("primitive_family", ""),
            "support_domain": fact.get("support_domain", ""),
            "falsifier_template": fact.get("falsifier_template", ""),
            "witness": fact.get("witness", ""),
            "phase_obligation": fact.get("phase_obligation", ""),
            "restoration_obligation": fact.get("restoration_obligation", ""),
        },
    )


def mine_candidates(
    facts: list[dict[str, Any]],
    include_unknown_sites: bool = False,
    max_unknown_sites: int = 0,
    min_site_weight: float = 1.0,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    unknown_sites = 0
    for fact in facts:
        before = len(candidates)
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
        if (
            include_unknown_sites
            and len(candidates) == before
            and fact["source_location"] != "unknown"
            and fact["op_class"] in {"ccx", "ccz", "cswap", "shift", "remainder"}
            and as_number(fact.get("executed_weight"), default=0.0) >= min_site_weight
            and (max_unknown_sites <= 0 or unknown_sites < max_unknown_sites)
        ):
            candidates.append(source_site_backlog_candidate(fact))
            unknown_sites += 1
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
    elif packet["proof_kind"] == "source_counterexample":
        template = str(inputs.get("falsifier_template", "")).strip()
        witness = str(inputs.get("witness", "")).strip()
        if template and witness:
            status = "COUNTEREXAMPLE"
            note = "source witness falsifies this omission"
        else:
            status = "UNKNOWN"
            note = "source counterexample packet is missing falsifier_template or witness"
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
            defaults = {
                "frontier": args.frontier,
                "source_base": args.source_base,
                "stream_hash": args.stream_hash,
            }
            facts = [normalize_fact(record, idx, defaults) for idx, record in enumerate(records)]
            write_jsonl(args.out, facts)
            print(f"storm_exact_miner=pass command=trace-facts facts={len(facts)}")
        elif args.command == "mine":
            facts = load_records(args.facts)
            candidates = mine_candidates(
                facts,
                include_unknown_sites=args.include_unknown_sites,
                max_unknown_sites=args.max_unknown_sites,
                min_site_weight=args.min_site_weight,
            )
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
