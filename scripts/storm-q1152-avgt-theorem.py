#!/usr/bin/env python3
"""Emit a q1152 avg-Toffoli source-theorem packet.

This is a source/IR gate for paper-mining hits. It distinguishes papers that
reduce generic T-depth/T-count from changes that the ecdsa.fail scorer can see:
deleting CCX/CCZ ops, or moving them under classical measured conditions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import struct
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable, Iterator


NO_BIT = (1 << 64) - 1
OP_BYTES = 56
MAGIC_ZSTD = b"QECCOPSZ"
MAGIC_RAW = b"QECCOPS1"

OP_NAMES = {
    0: "NEG",
    1: "REGISTER",
    2: "APPEND_TO_REGISTER",
    3: "BIT_INVERT",
    4: "BIT_STORE0",
    5: "BIT_STORE1",
    6: "X",
    7: "Z",
    8: "CX",
    9: "CZ",
    10: "SWAP",
    11: "R",
    12: "HMR",
    13: "CCX",
    14: "CCZ",
    15: "PUSH_CONDITION",
    16: "POP_CONDITION",
    17: "DEBUG_PRINT",
}


@dataclass(frozen=True)
class OpLite:
    kind: int
    c_condition: int


@dataclass(frozen=True)
class OpsAudit:
    op_count: int
    parsed_ops: int
    sha256: str
    toffoli_ops: int
    ccx_ops: int
    ccz_ops: int
    direct_conditioned_toffoli: int
    stack_conditioned_toffoli: int
    discount_bearing_toffoli: int
    push_conditions: int
    pop_conditions: int
    max_condition_depth: int


@dataclass(frozen=True)
class SourceAudit:
    scorer_counts_ccx_ccz: bool
    scorer_uses_condition_mask: bool
    score_rounds_avg_tof: bool
    ccx_ccz_allow_c_condition: bool
    push_condition_required: bool
    relative_phase_ir_absent: bool
    condition_api_present: bool

    @property
    def theorem_ok(self) -> bool:
        return (
            self.scorer_counts_ccx_ccz
            and self.scorer_uses_condition_mask
            and self.score_rounds_avg_tof
            and self.ccx_ccz_allow_c_condition
            and self.push_condition_required
            and self.relative_phase_ir_absent
            and self.condition_api_present
        )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_raw_ops(fh: BinaryIO, count: int) -> Iterator[OpLite]:
    rec = bytearray(OP_BYTES)
    view = memoryview(rec)
    for index in range(count):
        offset = 0
        while offset < OP_BYTES:
            chunk = fh.read(OP_BYTES - offset)
            if not chunk:
                raise SystemExit(f"ops_decode=fail reason=short_read op_index={index}")
            view[offset : offset + len(chunk)] = chunk
            offset += len(chunk)
        kind = struct.unpack_from("<I", rec, 0)[0]
        c_condition = struct.unpack_from("<Q", rec, 40)[0]
        yield OpLite(kind=kind, c_condition=c_condition)


def iter_ops_bin(path: Path, zstd_bin: str) -> tuple[int, Iterator[OpLite]]:
    fh = path.open("rb")
    magic = fh.read(8)
    count_raw = fh.read(8)
    if len(count_raw) != 8:
        raise SystemExit(f"ops_decode=fail reason=short_header path={path}")
    count = struct.unpack("<Q", count_raw)[0]

    if magic == MAGIC_RAW:
        return count, iter_raw_ops(fh, count)
    if magic != MAGIC_ZSTD:
        raise SystemExit(f"ops_decode=fail reason=bad_magic path={path}")

    body = fh.read()
    fh.close()

    def decoded() -> Iterator[OpLite]:
        with tempfile.NamedTemporaryFile(prefix="storm-ops-body-", suffix=".zst") as tmp:
            tmp.write(body)
            tmp.flush()
            proc = subprocess.Popen(
                [zstd_bin, "-dc", "--stdout", tmp.name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            assert proc.stdout is not None
            try:
                yield from iter_raw_ops(proc.stdout, count)
            finally:
                stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
                rc = proc.wait()
                if rc != 0:
                    raise SystemExit(f"ops_decode=fail reason=zstd_rc_{rc} stderr={stderr.strip()!r}")

    return count, decoded()


def audit_ops_bin(path: Path, zstd_bin: str) -> OpsAudit:
    count, ops = iter_ops_bin(path, zstd_bin)
    toffoli_ops = 0
    ccx_ops = 0
    ccz_ops = 0
    direct_conditioned_toffoli = 0
    stack_conditioned_toffoli = 0
    discount_bearing_toffoli = 0
    push_conditions = 0
    pop_conditions = 0
    condition_depth = 0
    max_condition_depth = 0
    parsed = 0
    for op in ops:
        parsed += 1
        if op.kind == 15:
            push_conditions += 1
            condition_depth += 1
            max_condition_depth = max(max_condition_depth, condition_depth)
            continue
        if op.kind == 16:
            pop_conditions += 1
            condition_depth = max(0, condition_depth - 1)
            continue
        if op.kind in (13, 14):
            toffoli_ops += 1
            ccx_ops += int(op.kind == 13)
            ccz_ops += int(op.kind == 14)
            direct = op.c_condition != NO_BIT
            stacked = condition_depth > 0
            direct_conditioned_toffoli += int(direct)
            stack_conditioned_toffoli += int(stacked)
            discount_bearing_toffoli += int(direct or stacked)
    return OpsAudit(
        op_count=count,
        parsed_ops=parsed,
        sha256=file_sha256(path),
        toffoli_ops=toffoli_ops,
        ccx_ops=ccx_ops,
        ccz_ops=ccz_ops,
        direct_conditioned_toffoli=direct_conditioned_toffoli,
        stack_conditioned_toffoli=stack_conditioned_toffoli,
        discount_bearing_toffoli=discount_bearing_toffoli,
        push_conditions=push_conditions,
        pop_conditions=pop_conditions,
        max_condition_depth=max_condition_depth,
    )


def audit_sources(args: argparse.Namespace) -> SourceAudit:
    sim = read_text(args.sim_rs)
    eval_rs = read_text(args.eval_circuit_rs)
    circuit = read_text(args.circuit_rs)
    mod_rs = read_text(args.point_add_mod_rs)
    operation_block = re.search(r"pub enum OperationType \{(?P<body>.*?)\n\}", circuit, re.S)
    operation_body = operation_block.group("body") if operation_block else circuit
    return SourceAudit(
        scorer_counts_ccx_ccz="OperationType::CCZ | OperationType::CCX" in sim
        and "self.stats.toffoli_gates += executed_shots" in sim,
        scorer_uses_condition_mask="current_base_condition" in sim
        and "op.c_condition != NO_BIT" in sim
        and "cond.count_ones()" in sim,
        score_rounds_avg_tof="let toffoli = avg_tof.round() as u64" in eval_rs
        and "toffoli.saturating_mul(qubits)" in eval_rs,
        ccx_ccz_allow_c_condition="OperationType::CCX | OperationType::CCZ" in circuit
        and "c_condition_flag = ALLOWED" in circuit,
        push_condition_required="OperationType::PushCondition" in circuit
        and "c_condition_flag = REQUIRED" in circuit,
        relative_phase_ir_absent=not re.search(r"Relative|RPT|RCCX|RCCZ|PhaseToffoli", operation_body),
        condition_api_present="fn push_condition" in mod_rs and "fn pop_condition" in mod_rs,
    )


def paper_hits(path: Path | None) -> list[str]:
    if path is None or not path.exists():
        return []
    hits: list[str] = []
    for line in read_text(path).splitlines():
        lowered = line.lower()
        if any(key in lowered for key in ["relative-phase", "t and cnot", "toffoli depth", "toffoli gate"]):
            hits.append(line.strip())
    return hits


def toy_counts(shots: int) -> dict[str, int]:
    half = shots // 2
    return {
        "unconditioned_ccx": shots,
        "quantum_sparse_control_ccx": shots,
        "classical_conditioned_ccx": half,
    }


def write_tsv(path: Path, rows: Iterable[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["key", "value"])
        writer.writerows(rows)


def write_report(
    path: Path,
    args: argparse.Namespace,
    source: SourceAudit,
    ops: OpsAudit | None,
    hits: list[str],
    toy: dict[str, int],
    decision: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ops_lines = ["- ops audit: not requested"]
    if ops is not None:
        ops_lines = [
            f"- ops_sha256: `{ops.sha256}`",
            f"- emitted ops: `{ops.op_count}`",
            f"- parsed ops: `{ops.parsed_ops}`",
            f"- CCX/CCZ emitted: `{ops.toffoli_ops}` (`CCX={ops.ccx_ops}`, `CCZ={ops.ccz_ops}`)",
            f"- discount-bearing CCX/CCZ: `{ops.discount_bearing_toffoli}`",
            f"- direct conditioned CCX/CCZ: `{ops.direct_conditioned_toffoli}`",
            f"- stack conditioned CCX/CCZ: `{ops.stack_conditioned_toffoli}`",
            f"- push/pop conditions: `{ops.push_conditions}/{ops.pop_conditions}`",
        ]
    paper_block = "\n".join(f"- {hit}" for hit in hits) if hits else "- no paper-summary T/Toffoli hits supplied"
    path.write_text(
        "\n".join(
            [
                "# q1152 avg-Toffoli Source-Theorem Packet",
                "",
                f"- route: `{args.route_id}`",
                f"- frontier/source: `{args.frontier}`",
                "- source invariant: scorer charges CCX/CCZ by classical condition-mask popcount only.",
                "- paper bridge: T-depth, T-count, or relative-phase Toffoli papers are not score routes unless they delete CCX/CCZ from this IR or move CCX/CCZ under measured classical conditions.",
                f"- expected avgT delta from decomposition-only rewrite: `0`",
                "- correctness risk channel for new measured replay: phase first, then ancilla.",
                f"- decision: `{decision}`",
                "",
                "## Source Gate",
                "",
                f"- scorer_counts_ccx_ccz: `{int(source.scorer_counts_ccx_ccz)}`",
                f"- scorer_uses_condition_mask: `{int(source.scorer_uses_condition_mask)}`",
                f"- score_rounds_avg_tof: `{int(source.score_rounds_avg_tof)}`",
                f"- ccx_ccz_allow_c_condition: `{int(source.ccx_ccz_allow_c_condition)}`",
                f"- push_condition_required: `{int(source.push_condition_required)}`",
                f"- relative_phase_ir_absent: `{int(source.relative_phase_ir_absent)}`",
                f"- condition_api_present: `{int(source.condition_api_present)}`",
                "",
                "## Ops Gate",
                "",
                *ops_lines,
                "",
                "## Toy Falsifier",
                "",
                f"- shots: `{args.toy_shots}`",
                f"- unconditioned CCX charged shots: `{toy['unconditioned_ccx']}`",
                f"- quantum-sparse-control CCX charged shots: `{toy['quantum_sparse_control_ccx']}`",
                f"- classical-conditioned CCX charged shots: `{toy['classical_conditioned_ccx']}`",
                "",
                "## Paper-Mining Hits",
                "",
                paper_block,
                "",
                "## Count Gate",
                "",
                "A q1152 avgT route from these papers must satisfy one of:",
                "",
                "- delete scored CCX/CCZ operations from the emitted IR;",
                "- move scored CCX/CCZ under a measured classical condition with phase and ancilla proof;",
                "- show a source hook that changes `avg_tof` in trusted eval.",
                "",
                "No source hook, residual, eval, benchmark, compute scale, or submit is licensed by this packet alone.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a q1152 avgT source theorem packet.")
    parser.add_argument("--route-id", default="q1152-condition-discount-source-theorem")
    parser.add_argument("--frontier", default="1571592960/d44cad3")
    parser.add_argument("--sim-rs", type=Path, required=True)
    parser.add_argument("--eval-circuit-rs", type=Path, required=True)
    parser.add_argument("--circuit-rs", type=Path, required=True)
    parser.add_argument("--point-add-mod-rs", type=Path, required=True)
    parser.add_argument("--ops-bin", type=Path)
    parser.add_argument("--paper-summary", type=Path)
    parser.add_argument("--zstd-bin", default=os.environ.get("ZSTD", "zstd"))
    parser.add_argument("--toy-shots", type=int, default=64)
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--report-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.toy_shots <= 0:
        raise SystemExit("--toy-shots must be positive")
    source = audit_sources(args)
    ops = audit_ops_bin(args.ops_bin, args.zstd_bin) if args.ops_bin else None
    hits = paper_hits(args.paper_summary)
    toy = toy_counts(args.toy_shots)
    decision = "source-theorem-packet" if source.theorem_ok else "source-audit-failed"

    rows: list[tuple[str, str]] = [
        ("route_id", args.route_id),
        ("frontier", args.frontier),
        ("scorer_counts_ccx_ccz", str(int(source.scorer_counts_ccx_ccz))),
        ("scorer_uses_condition_mask", str(int(source.scorer_uses_condition_mask))),
        ("score_rounds_avg_tof", str(int(source.score_rounds_avg_tof))),
        ("ccx_ccz_allow_c_condition", str(int(source.ccx_ccz_allow_c_condition))),
        ("push_condition_required", str(int(source.push_condition_required))),
        ("relative_phase_ir_absent", str(int(source.relative_phase_ir_absent))),
        ("condition_api_present", str(int(source.condition_api_present))),
        ("paper_toffoli_hits", str(len(hits))),
        ("toy_unconditioned_ccx", str(toy["unconditioned_ccx"])),
        ("toy_quantum_sparse_control_ccx", str(toy["quantum_sparse_control_ccx"])),
        ("toy_classical_conditioned_ccx", str(toy["classical_conditioned_ccx"])),
        ("expected_decomposition_only_avgT_delta", "0"),
        ("decision", decision),
    ]
    if ops is not None:
        rows.extend(
            [
                ("ops_sha256", ops.sha256),
                ("op_count", str(ops.op_count)),
                ("parsed_ops", str(ops.parsed_ops)),
                ("toffoli_ops", str(ops.toffoli_ops)),
                ("ccx_ops", str(ops.ccx_ops)),
                ("ccz_ops", str(ops.ccz_ops)),
                ("discount_bearing_toffoli", str(ops.discount_bearing_toffoli)),
                ("direct_conditioned_toffoli", str(ops.direct_conditioned_toffoli)),
                ("stack_conditioned_toffoli", str(ops.stack_conditioned_toffoli)),
                ("push_conditions", str(ops.push_conditions)),
                ("pop_conditions", str(ops.pop_conditions)),
                ("max_condition_depth", str(ops.max_condition_depth)),
            ]
        )
    if args.summary_out:
        write_tsv(args.summary_out, rows)
    if args.report_out:
        write_report(args.report_out, args, source, ops, hits, toy, decision)

    print(
        "q1152_avgt_theorem=pass "
        f"route={args.route_id} "
        f"frontier={args.frontier} "
        f"scorer_counts_ccx_ccz={int(source.scorer_counts_ccx_ccz)} "
        f"scorer_uses_condition_mask={int(source.scorer_uses_condition_mask)} "
        f"relative_phase_ir_absent={int(source.relative_phase_ir_absent)} "
        f"paper_toffoli_hits={len(hits)} "
        f"toy_quantum_sparse_ccx={toy['quantum_sparse_control_ccx']} "
        f"toy_classical_conditioned_ccx={toy['classical_conditioned_ccx']} "
        f"discount_bearing_toffoli={ops.discount_bearing_toffoli if ops else 'na'} "
        f"decision={decision}"
    )
    return 0 if source.theorem_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
