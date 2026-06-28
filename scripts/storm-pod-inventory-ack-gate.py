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
ACCOUNT_RE = re.compile(r"\baccount\s*[=:]\s*([A-Za-z0-9_.:-]+)\b", re.IGNORECASE)
POD_RE = re.compile(r"\b(?:pod_id|pod|instance_id|instance|machine)\s*[=:]\s*([A-Za-z0-9_.:-]+)\b", re.IGNORECASE)
STATUS_RE = re.compile(r"\bstatus\s*[=:]\s*(running|stopped|terminated|unreachable|unknown)\b", re.IGNORECASE)
JOB_RE = re.compile(r"\bjob\s*[=:]\s*([A-Za-z0-9_.:/@,+-]+)\b", re.IGNORECASE)
STOP_RE = re.compile(r"\b(?:stop_condition|kill_gate|stop)\s*[=:]\s*([A-Za-z0-9_.:/@,+-]+)\b", re.IGNORECASE)
ZERO_PODS_RE = re.compile(r"\b(?:status|pods|pod_count|running_pods)\s*[=:]\s*(?:0-pods|0|zero|none)\b", re.IGNORECASE)
SPEND_RE = re.compile(r"\b(?:currentSpendPerHr|spend_per_hr|current_spend_per_hr|cost_per_hr|burn_per_hr)\s*[=:]\s*\$?([0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
READS_RE = re.compile(r"\b(?:verification_reads|consecutive_reads|provider_reads|reads)\s*[=:]\s*([0-9]+)\b", re.IGNORECASE)
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


def first_float(pattern: re.Pattern[str], text: str) -> float | None:
    value = first_match(pattern, text)
    if not value:
        return None
    return float(value)


def first_int(pattern: re.Pattern[str], text: str) -> int | None:
    value = first_match(pattern, text)
    if not value:
        return None
    return int(value)


def inspect(text: str) -> dict[str, object]:
    owner = first_match(OWNER_FIELD_RE, text) or first_match(ACK_OWNER_RE, text)
    provider = first_match(PROVIDER_RE, text)
    account = first_match(ACCOUNT_RE, text)
    pod_id = first_match(POD_RE, text)
    zero_pods = bool(ZERO_PODS_RE.search(text))
    status = "0-pods" if zero_pods else normalized(first_match(STATUS_RE, text))
    job = first_match(JOB_RE, text)
    stop_condition = first_match(STOP_RE, text)
    route = first_match(ROUTE_RE, text)
    spend_per_hr = first_float(SPEND_RE, text)
    verification_reads = first_int(READS_RE, text)
    has_no_submit = bool(NO_SUBMIT_RE.search(text))
    has_no_start = bool(NO_START_RE.search(text))
    has_local = bool(LOCAL_RE.search(text))
    has_compute_request = bool(COMPUTE_REQUEST_RE.search(text))
    has_premature = bool(PREMATURE_RE.search(text))
    owner_unknown = normalized(owner) in UNKNOWN_OWNER
    job_none = normalized(job) in {"none", "idle", "no-job", "no_job"}
    account_empty = bool(zero_pods and account)
    spend_zero = spend_per_hr is not None and spend_per_hr == 0
    double_read_verified = verification_reads is not None and verification_reads >= 2

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
    if account_empty and spend_per_hr is not None and spend_per_hr > 0:
        failures.append("account_empty_nonzero_spend")

    if not owner:
        holds.append("missing_owner")
    elif owner_unknown and status != "running":
        holds.append("owner_unknown")
    if not provider:
        holds.append("missing_provider")
    if zero_pods and not account:
        holds.append("missing_account")
    if not pod_id and not account_empty:
        holds.append("missing_pod_id")
    if not status:
        holds.append("missing_status")
    elif status not in {"running", "stopped", "terminated", "unreachable", "unknown", "0-pods"}:
        holds.append("unsupported_status")
    if not job and not account_empty:
        holds.append("missing_job")
    if not stop_condition:
        holds.append("missing_stop_condition")
    if status in {"unknown", "unreachable"}:
        holds.append("provider_inventory_not_verified")
    if account_empty and spend_per_hr is None:
        holds.append("missing_zero_spend_evidence")
    if account_empty and not double_read_verified:
        holds.append("missing_double_read_verification")
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
        "account": account,
        "pod_id": pod_id,
        "status": status,
        "job": job,
        "route": route,
        "stop_condition": stop_condition,
        "zero_pods": zero_pods,
        "account_empty": account_empty,
        "spend_per_hr": spend_per_hr,
        "spend_zero": spend_zero,
        "verification_reads": verification_reads,
        "double_read_verified": double_read_verified,
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
        f"provider={row['provider'] or 'missing'} account={row['account'] or 'none'} "
        f"pod_id={row['pod_id'] or 'missing'} "
        f"status={row['status'] or 'missing'} job={row['job'] or 'missing'} "
        f"route={row['route'] or 'none'} stop_condition={row['stop_condition'] or 'missing'} "
        f"zero_pods={str(row['zero_pods']).lower()} account_empty={str(row['account_empty']).lower()} "
        f"spend_per_hr={row['spend_per_hr']} spend_zero={str(row['spend_zero']).lower()} "
        f"verification_reads={row['verification_reads']} double_read_verified={str(row['double_read_verified']).lower()} "
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
