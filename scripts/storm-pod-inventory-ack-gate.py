#!/usr/bin/env python3
"""Gate provider-side pod inventory ACKs after fleet stop directives.

This public-safe parser checks redacted provider inventory acknowledgements. It
does not call provider APIs, start/stop pods, run SSH job control, alert, or
submit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Iterable


OWNER_FIELD_RE = re.compile(r"\bowner\s*[=:]\s*([A-Za-z0-9_.-]+)\b", re.IGNORECASE)
ACK_OWNER_RE = re.compile(r"\bACK\s+([A-Za-z0-9_.-]+)\b", re.IGNORECASE)
PROVIDER_RE = re.compile(r"\b(?:provider|cloud|fleet)\s*[=:]\s*([A-Za-z0-9_.:-]+)\b", re.IGNORECASE)
POD_RE = re.compile(r"\b(?:pod_id|pod|instance_id|instance|machine)\s*[=:]\s*([A-Za-z0-9_.:-]+)\b", re.IGNORECASE)
STATUS_RE = re.compile(r"\bstatus\s*[=:]\s*(running|stopped|terminated|unreachable|unknown)\b", re.IGNORECASE)
JOB_RE = re.compile(r"\bjob\s*[=:]\s*([A-Za-z0-9_.:/@,+-]+)\b", re.IGNORECASE)
STOP_RE = re.compile(r"\b(?:stop_condition|kill_gate|stop)\s*[=:]\s*([A-Za-z0-9_.:/@,+-]+)\b", re.IGNORECASE)
NO_SUBMIT_RE = re.compile(r"\bno_submit_ack\s*=\s*yes\b", re.IGNORECASE)
NO_START_RE = re.compile(r"\b(?:no_start|do_not_start|no_compute|compute_closed)\s*[=:]\s*(?:yes|true|1)\b", re.IGNORECASE)
ROUTE_RE = re.compile(r"\b(?:route|range|shard|target)\s*[=:]\s*([A-Za-z0-9_.:/@,+\\[\\]-]+)\b", re.IGNORECASE)
LOCAL_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:mac|macbook|local|darwin)\b|\b(?:MacBook|mac-local|/Users/[A-Za-z0-9_.-]+)\b", re.IGNORECASE)
COMPUTE_REQUEST_RE = re.compile(
    r"\b(?:launch|start|restart|rearm|scale|dispatch|benchmark|run)\b.{0,100}\b(?:pods?|runpod|vast|gpus?|cpus?|scanner|benchmark|eval)\b|"
    r"\b(?:gpu_forever|gpu_island2|fanout_nonce_eval|build_circuit|eval_circuit|count_tof|storm-exact-miner)\b",
    re.IGNORECASE,
)
PREMATURE_RE = re.compile(r"\b(?:FOR[- ]AKASH|WINNER|mobile alert|submit(?:ted)?|ready[- ]to[- ]submit|Akash-ready)\b", re.IGNORECASE)

UNKNOWN_OWNER = {"unknown", "none", "unowned", "ownerless", "missing", "na", "n/a", "-"}
STOPPED_STATUSES = {"stopped", "terminated"}


def read_text(paths: Iterable[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths)


def first_match(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    if not match:
        return ""
    return next((group for group in match.groups() if group), "")


def normalized(value: str) -> str:
    return value.strip().lower()


def inspect(text: str) -> dict[str, object]:
    owner = first_match(OWNER_FIELD_RE, text) or first_match(ACK_OWNER_RE, text)
    provider = first_match(PROVIDER_RE, text)
    pod_id = first_match(POD_RE, text)
    status = normalized(first_match(STATUS_RE, text))
    job = first_match(JOB_RE, text)
    stop_condition = first_match(STOP_RE, text)
    route = first_match(ROUTE_RE, text)
    has_no_submit = bool(NO_SUBMIT_RE.search(text))
    has_no_start = bool(NO_START_RE.search(text))
    has_local = bool(LOCAL_RE.search(text))
    has_compute_request = bool(COMPUTE_REQUEST_RE.search(text))
    has_premature = bool(PREMATURE_RE.search(text))
    owner_unknown = normalized(owner) in UNKNOWN_OWNER
    job_none = normalized(job) in {"none", "idle", "no-job", "no_job"}

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []

    if has_local:
        failures.append("local_heavy_context")
    if has_compute_request:
        failures.append("premature_compute_or_start_request")
    if has_premature:
        failures.append("premature_submit_or_alert_language")
    if not has_no_submit:
        failures.append("missing_no_submit_ack")
    if status == "running" and (not owner or owner_unknown):
        failures.append("ownerless_running_pod")
    if status == "running" and not stop_condition:
        failures.append("running_pod_missing_stop_condition")

    if not owner:
        holds.append("missing_owner")
    elif owner_unknown and status != "running":
        holds.append("owner_unknown")
    if not provider:
        holds.append("missing_provider")
    if not pod_id:
        holds.append("missing_pod_id")
    if not status:
        holds.append("missing_status")
    elif status not in {"running", "stopped", "terminated", "unreachable", "unknown"}:
        holds.append("unsupported_status")
    if not job:
        holds.append("missing_job")
    if not stop_condition:
        holds.append("missing_stop_condition")
    if status in {"unknown", "unreachable"}:
        holds.append("provider_inventory_not_verified")
    if status == "running" and job_none and not route:
        warnings.append("running_idle_without_route")
    if not has_no_start:
        holds.append("missing_no_start_or_compute_closed_ack")

    if failures:
        gate = "fail"
        decision = "stop-ownerless-or-overclaiming-pod"
    elif holds:
        gate = "hold"
        decision = "complete-provider-inventory-ack"
    else:
        gate = "pass"
        decision = "inventory-ack-accepted-no-compute"

    return {
        "gate": gate,
        "decision": decision,
        "owner": owner,
        "provider": provider,
        "pod_id": pod_id,
        "status": status,
        "job": job,
        "route": route,
        "stop_condition": stop_condition,
        "no_submit_ack": has_no_submit,
        "no_start_ack": has_no_start,
        "owner_unknown": owner_unknown,
        "compute_request": has_compute_request,
        "failures": failures,
        "holds": holds,
        "warnings": warnings,
    }


def join(values: object) -> str:
    if not values:
        return "none"
    if isinstance(values, list):
        return ",".join(str(value) for value in values) if values else "none"
    return str(values)


def text_summary(row: dict[str, object]) -> str:
    return (
        f"pod_inventory_ack_gate={row['gate']} owner={row['owner'] or 'missing'} "
        f"provider={row['provider'] or 'missing'} pod_id={row['pod_id'] or 'missing'} "
        f"status={row['status'] or 'missing'} job={row['job'] or 'missing'} "
        f"route={row['route'] or 'none'} stop_condition={row['stop_condition'] or 'missing'} "
        f"no_submit_ack={str(row['no_submit_ack']).lower()} no_start_ack={str(row['no_start_ack']).lower()} "
        f"owner_unknown={str(row['owner_unknown']).lower()} compute_request={str(row['compute_request']).lower()} "
        f"decision={row['decision']} failures={join(row['failures'])} holds={join(row['holds'])} "
        f"warnings={join(row['warnings'])}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    missing = [str(path) for path in args.inputs if not path.is_file()]
    if missing:
        print(f"pod_inventory_ack_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
        return 2

    row = inspect(read_text(args.inputs))
    if args.json:
        print(json.dumps(row, sort_keys=True))
    else:
        print(text_summary(row))

    if row["gate"] == "fail":
        return 1
    if args.require_pass and row["gate"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
