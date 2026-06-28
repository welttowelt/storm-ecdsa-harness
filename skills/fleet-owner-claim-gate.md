# Fleet Owner Claim Gate

Use this before a paid instance survives audit. That includes RunPod, Vast, or
other worker machines that need an owner, route, watcher, and no-submit ACK.

## Gate

Run a proposed mailbox entry or owner packet through:

    python3 scripts/storm-fleet-owner-claim-gate.py owner-packet.txt --require-pass

For mailbox-tail audits, require one coherent packet instead of allowing
unrelated lines to combine into a false pass:

    python3 scripts/storm-fleet-owner-claim-gate.py owner-packet.txt --strict-single-packet --require-pass

The packet must contain:

- owner or claiming worker,
- pod or instance identity,
- route, shard, target, or range,
- active process, watcher, or log path evidence,
- next action,
- no_submit_ack=yes.

## Discipline

- Missing owner metadata means terminate or hold the paid instance before more
  spend.
- Do not run this on a whole mailbox tail unless strict-single-packet is set.
  Otherwise separate entries can combine into a false pass.
- A passing owner claim is not a route-quality pass. Still use route-compute,
  survivor, isolation, and submit gates.
- Keep private endpoints, credentials, and raw private logs out of public
  examples.

## Output

    fleet_owner_claim_gate=<pass|fail> owner=... pod_identity=... route_or_range=... active_process_or_log=... next_action=... no_submit_ack=... decision=...
