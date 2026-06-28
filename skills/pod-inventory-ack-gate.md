# Pod Inventory ACK Gate

Use this after a fleet stop directive requires workers to refresh provider-side
pod inventory.

## Command

    python3 scripts/storm-pod-inventory-ack-gate.py \
      <redacted-pod-inventory-ack.txt> \
      --require-pass

## Pass Requirements

- owner is present and not unknown;
- provider is present;
- pod_id or instance id is present;
- status is running, stopped, or terminated;
- job is present;
- stop_condition is present;
- no_submit_ack=yes is present;
- no_start=yes, do_not_start=true, no_compute=yes, or compute_closed=true is
  present;
- no local-heavy context, compute start request, submit, alert, or Akash
  language appears.

For account-level empty-provider inventory, pod_id and job are replaced by:

- account is present;
- status=0-pods, pod_count=0, running_pods=0, or equivalent zero-pod evidence;
- currentSpendPerHr=0, spend_per_hr=0, or equivalent spend-zero evidence;
- verification_reads>=2, consecutive_reads>=2, or equivalent double-read
  provider evidence.

## Decisions

- pass: inventory-ack-accepted-no-compute.
- hold: owner/status cannot be verified, or required inventory fields are
  missing.
- fail: running pod is ownerless/unknown, stop condition is missing, or the
  packet asks to start compute. Empty-account rows also fail if reported spend
  is nonzero.

This gate does not call provider APIs or stop pods. It checks that the mailbox
ACK is complete enough for Storm to decide whether a watcher should stop,
verify, or keep monitoring a pod.
