#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail=0

need_file() {
  local path="$1"
  if [ ! -f "$path" ]; then
    printf 'public_harness_check=fail missing_file=%s\n' "$path" >&2
    fail=1
  fi
}

need_text() {
  local path="$1"
  local label="$2"
  local pattern="$3"
  if ! grep -qiE "$pattern" "$path"; then
    printf 'public_harness_check=fail file=%s missing=%s\n' "$path" "$label" >&2
    fail=1
  fi
}

for path in \
  templates/operator-card.md \
  templates/audit-card.md \
  templates/mailbox-entry.md \
  templates/kimi-handoff.md \
  templates/route-packet.md \
  templates/compute-request.md \
  templates/public-note.md \
  skills/tony-rci-audit.md \
  skills/bluesky-audit.md \
  skills/redsky-audit.md \
  .agents/skills/tony-rci-audit/SKILL.md \
  .agents/skills/bluesky-audit/SKILL.md \
  .agents/skills/redsky-audit/SKILL.md \
  docs/production-shape.md \
  scripts/active-volume-ledger.sh \
  scripts/pebble-memory-ledger.sh \
  scripts/vandaele-comparator-ledger.sh \
  scripts/resident-footprint-ledger.sh \
  scripts/uncompute-window-ledger.sh \
  scripts/dirty-borrow-ledger.sh \
  scripts/dialog-codec-entropy-ledger.sh \
  scripts/apply-overlap-ledger.sh \
  scripts/qcut-candidate-prefilter.sh \
  scripts/storm-exact-miner.py \
  scripts/storm-audit-impact.py \
  scripts/storm-mailbox-action-scan.py \
  scripts/storm-wall-owner-summary.py \
  scripts/storm-source-certificate-scout.py \
  scripts/storm-alloc-owner-summary.py \
  scripts/storm-peak-lifetime-ledger.py \
  scripts/storm-gidney-thread-join.py \
  scripts/storm-windowed-carry-toy.py \
  examples/audit-card.example.md \
  examples/operator-card.example.md \
  examples/mailbox-entry.example.md \
  examples/mailbox-entry.kimi-deep.example.md \
  examples/kimi-handoff.example.md \
  examples/route-packet.example.md \
  examples/compute-request.example.md \
  examples/public-note.example.md \
  examples/op-trace-facts.example.jsonl \
  examples/site-audit.example.tsv \
  examples/support-facts.example.jsonl \
  examples/nack-ledger.example.jsonl \
  examples/exact-skip-candidates.example.jsonl \
  examples/cycle48-audit-impact.example.json \
  examples/apply-overlap-trace.example.txt \
  examples/apply-overlap-restore-missing.example.txt \
  templates/exact-skip-candidate.json \
  docs/exact-support-miner.md \
  docs/redsky-stormgate-audit-2026-06-20-f8e215b-current.md \
  operators/codex-storm.md \
  operators/deep-storm.md \
  operators/file-handoff-protocol.md \
  operators/handoff-protocol.md \
  operators/kimi-storm.md \
  routes/tobitvector-cswap-body-trim-q1170.md \
  routes/tobitvector-cswap-body-trim-q1170.rci-audit.md \
  skills/nasqret-playbook.md \
  skills/deepseek-pressure-test.md \
  skills/pip-discipline.md \
  skills/exact-support-miner.md \
  skills/frontier-lock.md \
  skills/validation-submit-gate.md \
  skills/route-compute-gate.md \
  skills/multi-agent-handoff.md \
  skills/circuit-diff-mining.md \
  skills/submission-forensics.md \
  skills/bluesky-route-salvage.md \
  skills/redsky-frontier-audit.md \
  skills/ecdsafail-cli-ops.md \
  skills/stormgate-prefilter.md \
  skills/q1152-structural-core.md \
  skills/support-bounded-vented-dead-carry.md \
  skills/paper-gidney-constant-workspace-adder.md \
  skills/paper-mbu-modular-arithmetic.md \
  skills/paper-hrs-dirty-constant-adder.md \
  skills/paper-gidney-temporary-logical-and.md \
  skills/paper-haner-ecdlp-circuits.md \
  skills/paper-schrottenloher-point-addition.md \
  skills/paper-schrottenloher-dialog-codec-audit.md \
  skills/paper-luo-register-sharing-eea.md \
  skills/conditionally-clean-cascade-cut.md \
  skills/paper-conditionally-clean-ancillae.md \
  skills/paper-reversible-pebbling-memory-management.md \
  skills/paper-square-active-volume.md \
  skills/paper-vandaele-optimal-comparator.md \
  skills/paper-reqomp-space-constrained-uncompute.md \
  skills/paper-remaud-ancilla-free-adder.md \
  skills/paper-takahashi-no-ancilla-adder.md \
  skills/paper-roetteler-ecdlp-resource-estimate.md \
  skills/paper-garn-kan-windowed-binary-ecdlp.md \
  skills/paper-wire-recycling-lifetime-graph.md \
  skills/paper-dirty-borrowing-entanglement.md \
  skills/paper-dead-gate-elimination.md \
  skills/apply-overlap-ledger.md \
  .agents/skills/nasqret-playbook/SKILL.md \
  .agents/skills/deepseek-pressure-test/SKILL.md \
  .agents/skills/pip-discipline/SKILL.md \
  .agents/skills/exact-support-miner/SKILL.md \
  .agents/skills/frontier-lock/SKILL.md \
  .agents/skills/validation-submit-gate/SKILL.md \
  .agents/skills/route-compute-gate/SKILL.md \
  .agents/skills/multi-agent-handoff/SKILL.md \
  .agents/skills/circuit-diff-mining/SKILL.md \
  .agents/skills/submission-forensics/SKILL.md \
  .agents/skills/bluesky-route-salvage/SKILL.md \
  .agents/skills/redsky-frontier-audit/SKILL.md \
  .agents/skills/ecdsafail-cli-ops/SKILL.md \
  .agents/skills/stormgate-prefilter/SKILL.md \
  .agents/skills/q1152-structural-core/SKILL.md \
  .agents/skills/paper-gidney-constant-workspace-adder/SKILL.md \
  .agents/skills/paper-mbu-modular-arithmetic/SKILL.md \
  .agents/skills/paper-hrs-dirty-constant-adder/SKILL.md \
  .agents/skills/paper-gidney-temporary-logical-and/SKILL.md \
  .agents/skills/paper-haner-ecdlp-circuits/SKILL.md \
  .agents/skills/paper-schrottenloher-point-addition/SKILL.md \
  .agents/skills/paper-schrottenloher-dialog-codec-audit/SKILL.md \
  .agents/skills/paper-luo-register-sharing-eea/SKILL.md \
  .agents/skills/conditionally-clean-cascade-cut/SKILL.md \
  .agents/skills/paper-conditionally-clean-ancillae/SKILL.md \
  .agents/skills/paper-reversible-pebbling-memory-management/SKILL.md \
  .agents/skills/paper-square-active-volume/SKILL.md \
  .agents/skills/paper-vandaele-optimal-comparator/SKILL.md \
  .agents/skills/paper-reqomp-space-constrained-uncompute/SKILL.md \
  .agents/skills/paper-remaud-ancilla-free-adder/SKILL.md \
  .agents/skills/paper-takahashi-no-ancilla-adder/SKILL.md \
  .agents/skills/paper-roetteler-ecdlp-resource-estimate/SKILL.md \
  .agents/skills/paper-garn-kan-windowed-binary-ecdlp/SKILL.md \
  .agents/skills/paper-wire-recycling-lifetime-graph/SKILL.md \
  .agents/skills/paper-dirty-borrowing-entanglement/SKILL.md \
  .agents/skills/paper-dead-gate-elimination/SKILL.md \
  .agents/skills/apply-overlap-ledger/SKILL.md \
  dashboard/fixtures/status.json; do
  need_file "$path"
done

need_text templates/operator-card.md "read receipt" "Read receipt requested"
need_text templates/operator-card.md "kill gate" "Kill gate"
need_text templates/audit-card.md "audit type" "Audit type"
need_text templates/audit-card.md "bluesky pass" "Bluesky Pass"
need_text templates/audit-card.md "redsky pass" "Redsky Pass"
need_text templates/audit-card.md "smallest useful fix" "Smallest useful fix"
need_text templates/route-packet.md "evidence label" "Evidence label"
need_text templates/route-packet.md "submit gate" "Submit gate"
need_text templates/compute-request.md "validator" "Validator"
need_text templates/compute-request.md "kill condition" "Kill condition"
need_text templates/mailbox-entry.md "purpose limits" "Purpose/limits"
need_text templates/mailbox-entry.md "read receipt requested" "Read receipt requested"
need_text templates/kimi-handoff.md "kimi handoff" "KIMI_HANDOFF"
need_text templates/kimi-handoff.md "ack status" "ack"
need_text templates/public-note.md "purpose and limits" "Purpose And Limits"
need_text templates/public-note.md "evidence label" "Evidence label"
need_text skills/tony-rci-audit.md "smallest useful fix" "Smallest useful fix"
need_text skills/tony-rci-audit.md "completion gate" "Completion Gate"
need_text skills/bluesky-audit.md "bounded experiment" "bounded experiment"
need_text skills/bluesky-audit.md "stop condition" "Stop condition"
need_text skills/redsky-audit.md "strongest objection" "Strongest objection"
need_text skills/redsky-audit.md "fastest falsifier" "Fastest falsifier"
need_text .agents/skills/tony-rci-audit/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/bluesky-audit/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/redsky-audit/SKILL.md "bridge" "Codex-discoverable bridge"
need_text docs/production-shape.md "storm production" "STORM harness in production"
need_text docs/production-shape.md "prefilter label" "Prefilter"
need_text docs/production-shape.md "private boundary" "private fleet config"
need_text scripts/active-volume-ledger.sh "square ledger output" "SQUARE active-volume gate"
need_text scripts/pebble-memory-ledger.sh "pebble ledger output" "Reversible pebbling memory gate"
need_text scripts/pebble-memory-ledger.sh "trace ledger" "TLM_TAPE"
need_text scripts/vandaele-comparator-ledger.sh "vandaele ledger output" "Vandaele comparator gate"
need_text scripts/resident-footprint-ledger.sh "resident footprint output" "Resident footprint gate"
need_text scripts/uncompute-window-ledger.sh "reqomp ledger output" "Reqomp uncompute window gate"
need_text scripts/dirty-borrow-ledger.sh "dirty borrow ledger output" "Dirty borrow entanglement gate"
need_text scripts/dialog-codec-entropy-ledger.sh "dialog codec ledger output" "Dialog codec entropy gate"
need_text scripts/apply-overlap-ledger.sh "apply overlap ledger output" "Apply overlap ledger"
need_text scripts/apply-overlap-ledger.sh "live d44 tail rows" "TLM_\\(TAPE|TAIL\\)"
need_text scripts/qcut-candidate-prefilter.sh "qcut gate output" "KILL \\(gate 3\\)"
need_text scripts/storm-exact-miner.py "exact miner command" "trace-facts"
need_text scripts/storm-exact-miner.py "support checker command" "support-check"
need_text scripts/storm-exact-miner.py "falsify command" "falsify"
need_text scripts/storm-exact-miner.py "ledger command" "ledger"
need_text scripts/storm-exact-miner.py "public safety scan" "redaction_risk"
need_text scripts/storm-exact-miner.py "Gidney trace context decoding" "trace_context_family"
need_text scripts/storm-audit-impact.py "machine-readable audit metrics" "unknown_weight_abs_avgT_delta"
need_text scripts/storm-mailbox-action-scan.py "mailbox direct ask scanner" "mailbox_action_scan"
need_text scripts/storm-wall-owner-summary.py "wall owner summary" "wall_owner_summary=pass"
need_text scripts/storm-source-certificate-scout.py "source certificate scout" "source_certificate_scout=pass"
need_text scripts/storm-alloc-owner-summary.py "alloc owner summary" "alloc_owner_summary=pass"
need_text scripts/storm-peak-lifetime-ledger.py "peak lifetime ledger" "peak_lifetime_ledger=pass"
need_text scripts/storm-gidney-thread-join.py "gidney thread join" "gidney_thread_join=pass"
need_text scripts/storm-windowed-carry-toy.py "windowed carry toy" "windowed_carry_toy="

need_text examples/operator-card.example.md "falsifiable decision" "Falsifiable decision"
need_text examples/audit-card.example.md "rci tony" "RCI/Tony"
need_text examples/audit-card.example.md "redsky" "Redsky Pass"
need_text examples/audit-card.example.md "bluesky" "Bluesky Pass"
need_text examples/mailbox-entry.example.md "read receipt requested" "Read receipt requested"
need_text examples/route-packet.example.md "stop condition" "Stop condition"
need_text examples/compute-request.example.md "zero paid compute" "zero"
need_text examples/public-note.example.md "not a candidate" "not a candidate"
need_text examples/op-trace-facts.example.jsonl "public demo source" "public-demo-source"
need_text examples/site-audit.example.tsv "site audit fixture" "src/point_add/trailmix_ludicrous/gcd.rs"
need_text examples/support-facts.example.jsonl "support fixture" "dirty_host"
need_text examples/nack-ledger.example.jsonl "nack ledger fixture" "nack_note"
need_text examples/exact-skip-candidates.example.jsonl "proof packet" "proof_status"
need_text examples/cycle48-audit-impact.example.json "machine-readable improvement" "ranked_unknown_rows_reduction_pct"
need_text examples/apply-overlap-trace.example.txt "apply overlap fixture" "TLM_OVERLAP_CHECK"
need_text examples/apply-overlap-trace.example.txt "apply overlap tail fixture" "TLM_TAIL"
need_text examples/apply-overlap-restore-missing.example.txt "apply overlap restore-missing fixture" "restore_proof=0"
need_text examples/apply-overlap-restore-missing.example.txt "apply overlap tape-tail fixture" "tape_tail_code"
need_text templates/exact-skip-candidate.json "allocator unchanged" "allocator_unchanged"
need_text templates/exact-skip-candidate.json "support status" "support_status"
need_text templates/exact-skip-candidate.json "trace context family" "trace_context_family"
need_text templates/exact-skip-candidate.json "source hash" "source_hash"
need_text docs/exact-support-miner.md "exact support miner" "Exact Support Miner"
need_text docs/exact-support-miner.md "support checker" "support-check"
need_text docs/exact-support-miner.md "redsky gate" "Redsky"
need_text docs/exact-support-miner.md "pip gate" "PIP"
need_text docs/redsky-stormgate-audit-2026-06-20-f8e215b-current.md "current source" "f8e215b"
need_text docs/redsky-stormgate-audit-2026-06-20-f8e215b-current.md "no submit gate" "No clean winning candidate"
need_text operators/kimi-storm.md "kimi boss" "operator boss"
need_text operators/deep-storm.md "deep reviewer" "Redsky auditor"
need_text operators/codex-storm.md "codex pressure test" "pressure-test"
need_text operators/handoff-protocol.md "prefilter boundary" "Prefilter"
need_text operators/file-handoff-protocol.md "private file boundary" "Keep the file outside the public repo"
need_text routes/tobitvector-cswap-body-trim-q1170.md "parked route" "parked / falsified"
need_text routes/tobitvector-cswap-body-trim-q1170.rci-audit.md "rci fixes applied" "Fixes applied"
need_text dashboard/fixtures/status.json "public fixture" "public fixture|fixture data"
need_text skills/bluesky-route-salvage.md "bluesky salvage" "Bluesky salvage"
need_text skills/redsky-frontier-audit.md "redsky audit" "Redsky audit"
need_text skills/ecdsafail-cli-ops.md "ecdsafail command" "ecdsafail benchmark"
need_text skills/stormgate-prefilter.md "prefilter label" "stage-1 survivor"
need_text skills/q1152-structural-core.md "q1152 structural core" "wall-gated count/eval loop"
need_text skills/q1152-structural-core.md "trusted eval" "Trusted eval"
need_text skills/support-bounded-vented-dead-carry.md "support bounded vent" "Support-Bounded Vented Dead-Carry"
need_text skills/support-bounded-vented-dead-carry.md "dead predicate" "source-hash-bound"
need_text skills/support-bounded-vented-dead-carry.md "headroom cap" "TLM_SQUARE_PEAK_CAP"
need_text .agents/skills/q1152-structural-core/SKILL.md "bridge" "Codex-discoverable bridge"
need_text skills/paper-gidney-constant-workspace-adder.md "gidney source" "arXiv:2507.23079"
need_text skills/paper-mbu-modular-arithmetic.md "mbu phase cleanup" "phase correction"
need_text skills/paper-hrs-dirty-constant-adder.md "dirty host" "not scratch"
need_text skills/paper-gidney-temporary-logical-and.md "temporary logical and" "temporary logical-AND"
need_text skills/paper-haner-ecdlp-circuits.md "ecdlp tradeoff" "Q/T/depth"
need_text skills/paper-schrottenloher-point-addition.md "secp256k1" "secp256k1"
need_text skills/paper-schrottenloher-dialog-codec-audit.md "dialog codec entropy" "entropy lower bound"
need_text skills/paper-luo-register-sharing-eea.md "register sharing" "register-sharing EEA"
need_text skills/conditionally-clean-cascade-cut.md "conditionally clean cascade" "conditionally-clean cascade"
need_text skills/paper-conditionally-clean-ancillae.md "conditionally clean" "conditionally clean"
need_text skills/paper-reversible-pebbling-memory-management.md "reversible pebbling" "reversible pebbling"
need_text skills/paper-square-active-volume.md "square active volume" "SQUARE active-volume"
need_text skills/paper-vandaele-optimal-comparator.md "vandaele comparator" "arXiv:2603.12917"
need_text skills/paper-reqomp-space-constrained-uncompute.md "reqomp uncompute" "Reqomp"
need_text skills/paper-remaud-ancilla-free-adder.md "ancilla free" "no ancilla"
need_text skills/paper-takahashi-no-ancilla-adder.md "no ancilla baseline" "no-ancilla"
need_text skills/paper-roetteler-ecdlp-resource-estimate.md "prime field" "prime-field ECDLP"
need_text skills/paper-garn-kan-windowed-binary-ecdlp.md "binary field" "binary-field"
need_text skills/paper-wire-recycling-lifetime-graph.md "wire recycling" "lifetime graph"
need_text skills/paper-dirty-borrowing-entanglement.md "dirty borrow entanglement" "external entanglement"
need_text skills/paper-dead-gate-elimination.md "dead gate elimination" "Dead Gate Elimination"
need_text skills/apply-overlap-ledger.md "apply overlap" "apply/codec/fold overlap"
need_text skills/nasqret-playbook.md "route slate" "route slate"
need_text skills/deepseek-pressure-test.md "pressure test" "pressure-test"
need_text skills/pip-discipline.md "pip discipline" "PIP Evidence Discipline"
need_text skills/exact-support-miner.md "exact miner" "storm-exact-miner.py"
need_text .agents/skills/exact-support-miner/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/apply-overlap-ledger/SKILL.md "bridge" "Codex-discoverable bridge"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

if ! python3 scripts/storm-exact-miner.py support-check \
  --facts examples/support-facts.example.jsonl \
  --out "$tmpdir/support.jsonl" >"$tmpdir/support.out" 2>"$tmpdir/support.err"; then
  printf 'public_harness_check=fail exact_miner_support_check_failed\n' >&2
  cat "$tmpdir/support.err" >&2
  fail=1
elif ! grep -q 'certified=0 unknown=1 counterexample=2' "$tmpdir/support.out"; then
  printf 'public_harness_check=fail exact_miner_support_counts\n' >&2
  cat "$tmpdir/support.out" >&2
  fail=1
fi

cat >"$tmpdir/mailbox-action-tail.md" <<'EOF'
## 2026-06-27T00:00:00Z from: Worker-A - bounded check

ACK Worker-A NACK demo-lane skill=redsky file=demo.rs next=needs-operator no_submit_ack=yes
Storm-Codex: confirm whether I should produce one fresh trace or hold.

## 2026-06-27T00:01:00Z from: Worker-B - status

Boss Storm: want me to stop the idle proof host?
EOF
if ! python3 scripts/storm-mailbox-action-scan.py \
  --input "$tmpdir/mailbox-action-tail.md" >"$tmpdir/mailbox-action.out" 2>"$tmpdir/mailbox-action.err"; then
  printf 'public_harness_check=fail mailbox_action_scan_failed\n' >&2
  cat "$tmpdir/mailbox-action.err" >&2
  fail=1
elif ! grep -q 'mailbox_action_scan=review count=2' "$tmpdir/mailbox-action.out"; then
  printf 'public_harness_check=fail mailbox_action_scan_counts\n' >&2
  cat "$tmpdir/mailbox-action.out" >&2
  fail=1
fi

cat >"$tmpdir/mailbox-action-answered.md" <<'EOF'
## 2026-06-27T00:00:00Z from: Worker-A - bounded check

Storm-Codex: confirm whether I should produce one fresh trace or hold.

## 2026-06-27T00:03:00Z from: Storm-Codex - ACK

ACK Storm-Codex CLAIM worker-a-fresh-trace skill=redsky file=demo next=produce-one-trace no_submit_ack=yes
Worker-A is authorized for one bounded trace. No submit.
EOF
if ! python3 scripts/storm-mailbox-action-scan.py \
  --input "$tmpdir/mailbox-action-answered.md" >"$tmpdir/mailbox-action-answered.out" 2>"$tmpdir/mailbox-action-answered.err"; then
  printf 'public_harness_check=fail mailbox_action_scan_answered_failed\n' >&2
  cat "$tmpdir/mailbox-action-answered.err" >&2
  fail=1
elif ! grep -q 'mailbox_action_scan=pass count=0' "$tmpdir/mailbox-action-answered.out"; then
  printf 'public_harness_check=fail mailbox_action_scan_answered_counts\n' >&2
  cat "$tmpdir/mailbox-action-answered.out" >&2
  fail=1
fi

cat >"$tmpdir/mailbox-action-clean.md" <<'EOF'
## 2026-06-27T00:02:00Z from: Worker-C - status

ACK Worker-C NACK demo-lane skill=redsky file=demo.rs next=local-falsifier no_submit_ack=yes
No operator decision requested.
EOF
if ! python3 scripts/storm-mailbox-action-scan.py \
  --input "$tmpdir/mailbox-action-clean.md" >"$tmpdir/mailbox-action-clean.out" 2>"$tmpdir/mailbox-action-clean.err"; then
  printf 'public_harness_check=fail mailbox_action_scan_clean_failed\n' >&2
  cat "$tmpdir/mailbox-action-clean.err" >&2
  fail=1
elif ! grep -q 'mailbox_action_scan=pass count=0' "$tmpdir/mailbox-action-clean.out"; then
  printf 'public_harness_check=fail mailbox_action_scan_clean_counts\n' >&2
  cat "$tmpdir/mailbox-action-clean.out" >&2
  fail=1
fi

printf '%s\n' \
  'rank	count	kind	file	line	context	first_idx	last_idx' \
  '1	2	CCX	src/point_add/trailmix_ludicrous/gcd.rs	1246	0x12002a07	10	20' \
  '2	3	CCX	src/point_add/trailmix_ludicrous/comparator.rs	864	0x13000102	30	40' \
  > "$tmpdir/context-sites.tsv"
if ! python3 scripts/storm-exact-miner.py trace-facts \
  --input "$tmpdir/context-sites.tsv" \
  --frontier fixture-frontier/demo-source \
  --source-base public-demo-source \
  --stream-hash context-site-demo \
  --out "$tmpdir/context-facts.jsonl" >"$tmpdir/context-trace.out" 2>"$tmpdir/context-trace.err"; then
  printf 'public_harness_check=fail exact_miner_context_trace_failed\n' >&2
  cat "$tmpdir/context-trace.err" >&2
  fail=1
elif ! grep -q 'gcd_reverse_cswap' "$tmpdir/context-facts.jsonl" \
  || ! grep -q 'compare_cin_carry' "$tmpdir/context-facts.jsonl"; then
  printf 'public_harness_check=fail exact_miner_context_decode\n' >&2
  cat "$tmpdir/context-facts.jsonl" >&2
  fail=1
elif ! python3 scripts/storm-exact-miner.py support-check \
  --facts "$tmpdir/context-facts.jsonl" \
  --out "$tmpdir/context-support.jsonl" >"$tmpdir/context-support.out" 2>"$tmpdir/context-support.err"; then
  printf 'public_harness_check=fail exact_miner_context_support_failed\n' >&2
  cat "$tmpdir/context-support.err" >&2
  fail=1
elif ! grep -q 'certified=0 unknown=0 counterexample=2' "$tmpdir/context-support.out"; then
  printf 'public_harness_check=fail exact_miner_context_support_counts\n' >&2
  cat "$tmpdir/context-support.out" >&2
  fail=1
fi

printf '%s\n' \
  '{"fact_id":"stale-context-demo","frontier":"fixture-frontier/demo-source","source_base":"public-demo-source","stream_hash":"stale-context-demo","op_id":"stale-context","source_location":"src/point_add/trailmix_ludicrous/gcd.rs:1246","op_class":"ccx","executed_weight":1,"allocator_unchanged":true,"trace_context_value":"0x12002a07","primitive_family":"","support_domain":"","falsifier_template":"","witness":"","phase_obligation":"","restoration_obligation":"","proof_method":"","support_status":""}' \
  > "$tmpdir/stale-context.jsonl"
if ! python3 scripts/storm-exact-miner.py support-check \
  --facts "$tmpdir/stale-context.jsonl" \
  --out "$tmpdir/stale-context-support.jsonl" >"$tmpdir/stale-context-support.out" 2>"$tmpdir/stale-context-support.err"; then
  printf 'public_harness_check=fail exact_miner_stale_context_support_failed\n' >&2
  cat "$tmpdir/stale-context-support.err" >&2
  fail=1
elif ! grep -q 'certified=0 unknown=0 counterexample=1' "$tmpdir/stale-context-support.out"; then
  printf 'public_harness_check=fail exact_miner_stale_context_support_counts\n' >&2
  cat "$tmpdir/stale-context-support.out" >&2
  cat "$tmpdir/stale-context-support.jsonl" >&2
  fail=1
fi

printf '%s\n' \
  'rank	count	kind	file	line	context	first_idx	last_idx' \
  '1	5	CCX	src/point_add/trailmix_ludicrous/arith.rs	834	none	10	20' \
  '2	4	CCX	src/point_add/trailmix_ludicrous/comparator.rs	702	none	30	40' \
  '3	3	CCX	src/point_add/trailmix_ludicrous/new_unknown.rs	42	none	50	60' \
  '4	2	CCX	src/point_add/trailmix_ludicrous/another_unknown.rs	9	none	70	80' \
  > "$tmpdir/max-unknown-sites.tsv"
if ! python3 scripts/storm-exact-miner.py trace-facts \
  --input "$tmpdir/max-unknown-sites.tsv" \
  --frontier fixture-frontier/demo-source \
  --source-base public-demo-source \
  --stream-hash max-unknown-sites-demo \
  --out "$tmpdir/max-unknown-sites-facts.jsonl" >"$tmpdir/max-unknown-sites-trace.out" 2>"$tmpdir/max-unknown-sites-trace.err"; then
  printf 'public_harness_check=fail exact_miner_max_unknown_sites_trace_failed\n' >&2
  cat "$tmpdir/max-unknown-sites-trace.err" >&2
  fail=1
elif ! python3 scripts/storm-exact-miner.py support-check \
  --facts "$tmpdir/max-unknown-sites-facts.jsonl" \
  --out "$tmpdir/max-unknown-sites-support.jsonl" >"$tmpdir/max-unknown-sites-support.out" 2>"$tmpdir/max-unknown-sites-support.err"; then
  printf 'public_harness_check=fail exact_miner_max_unknown_sites_support_failed\n' >&2
  cat "$tmpdir/max-unknown-sites-support.err" >&2
  fail=1
elif ! python3 scripts/storm-exact-miner.py mine \
  --facts "$tmpdir/max-unknown-sites-support.jsonl" \
  --include-unknown-sites \
  --max-unknown-sites 1 \
  --out "$tmpdir/max-unknown-sites-candidates.jsonl" >"$tmpdir/max-unknown-sites-mine.out" 2>"$tmpdir/max-unknown-sites-mine.err"; then
  printf 'public_harness_check=fail exact_miner_max_unknown_sites_mine_failed\n' >&2
  cat "$tmpdir/max-unknown-sites-mine.err" >&2
  fail=1
elif [ "$(grep -c '"proof_kind":"manual_source_invariant"' "$tmpdir/max-unknown-sites-candidates.jsonl")" -ne 1 ] \
  || [ "$(grep -c '"proof_kind":"source_counterexample"' "$tmpdir/max-unknown-sites-candidates.jsonl")" -ne 2 ] \
  || ! grep -q 'new_unknown.rs:42' "$tmpdir/max-unknown-sites-candidates.jsonl"; then
  printf 'public_harness_check=fail exact_miner_max_unknown_sites_quota\n' >&2
  cat "$tmpdir/max-unknown-sites-candidates.jsonl" >&2
  fail=1
fi

printf '%s\n' \
  '{"frontier":"fixture-frontier/demo-source","source_base":"public-demo-source","source_hash":"fixture-source-hash","stream_hash":"context-cert-demo","op_id":"context-cert","source_location":"src/point_add/trailmix_ludicrous/gidney.rs:1233","context":"0x05002a07","op_class":"ccx","executed_weight":1,"support_status":"CERTIFIED","support_certificate":"public route-specific certificate"}' \
  > "$tmpdir/context-cert.jsonl"
if ! python3 scripts/storm-exact-miner.py trace-facts \
  --input "$tmpdir/context-cert.jsonl" \
  --out "$tmpdir/context-cert-facts.jsonl" >"$tmpdir/context-cert-trace.out" 2>"$tmpdir/context-cert-trace.err"; then
  printf 'public_harness_check=fail exact_miner_context_cert_trace_failed\n' >&2
  cat "$tmpdir/context-cert-trace.err" >&2
  fail=1
elif ! python3 scripts/storm-exact-miner.py support-check \
  --facts "$tmpdir/context-cert-facts.jsonl" \
  --out "$tmpdir/context-cert-support.jsonl" >"$tmpdir/context-cert-support.out" 2>"$tmpdir/context-cert-support.err"; then
  printf 'public_harness_check=fail exact_miner_context_cert_support_failed\n' >&2
  cat "$tmpdir/context-cert-support.err" >&2
  fail=1
elif ! grep -q 'certified=1 unknown=0 counterexample=0' "$tmpdir/context-cert-support.out"; then
  printf 'public_harness_check=fail exact_miner_context_cert_support_counts\n' >&2
  cat "$tmpdir/context-cert-support.out" >&2
  cat "$tmpdir/context-cert-support.jsonl" >&2
  fail=1
fi

printf '%s\n' \
  '{"frontier":"fixture-frontier/demo-source","source_base":"public-demo-source","stream_hash":"unbound-cert-demo","op_id":"unbound-cert","source_location":"src/point_add/trailmix_ludicrous/demo.rs:7","op_class":"ccx","executed_weight":1,"support_status":"CERTIFIED","support_certificate":"floating certificate without source hash"}' \
  > "$tmpdir/unbound-cert.jsonl"
if ! python3 scripts/storm-exact-miner.py support-check \
  --facts "$tmpdir/unbound-cert.jsonl" \
  --out "$tmpdir/unbound-cert-support.jsonl" >"$tmpdir/unbound-cert-support.out" 2>"$tmpdir/unbound-cert-support.err"; then
  printf 'public_harness_check=fail exact_miner_unbound_cert_support_failed\n' >&2
  cat "$tmpdir/unbound-cert-support.err" >&2
  fail=1
elif ! grep -q 'certified=0 unknown=1 counterexample=0' "$tmpdir/unbound-cert-support.out"; then
  printf 'public_harness_check=fail exact_miner_unbound_cert_support_counts\n' >&2
  cat "$tmpdir/unbound-cert-support.out" >&2
  cat "$tmpdir/unbound-cert-support.jsonl" >&2
  fail=1
fi

printf '%s\n' \
  '{"frontier":"fixture-frontier/demo-source","source_base":"public-demo-source","source_hash":"fixture-source-hash","stream_hash":"dirty-host-obligation-demo","op_id":"dirty-host-obligation","source_location":"src/point_add/trailmix_ludicrous/demo.rs:12","op_class":"ccx","executed_weight":1,"primitive_family":"dirty_host","restoration_obligation":"restore text only","phase_obligation":"phase text only","support_status":"CERTIFIED","support_certificate":"bound but proof flags absent"}' \
  > "$tmpdir/dirty-host-obligation.jsonl"
if ! python3 scripts/storm-exact-miner.py support-check \
  --facts "$tmpdir/dirty-host-obligation.jsonl" \
  --out "$tmpdir/dirty-host-obligation-support.jsonl" >"$tmpdir/dirty-host-obligation-support.out" 2>"$tmpdir/dirty-host-obligation-support.err"; then
  printf 'public_harness_check=fail exact_miner_dirty_host_obligation_support_failed\n' >&2
  cat "$tmpdir/dirty-host-obligation-support.err" >&2
  fail=1
elif ! grep -q 'certified=0 unknown=1 counterexample=0' "$tmpdir/dirty-host-obligation-support.out"; then
  printf 'public_harness_check=fail exact_miner_dirty_host_obligation_counts\n' >&2
  cat "$tmpdir/dirty-host-obligation-support.out" >&2
  cat "$tmpdir/dirty-host-obligation-support.jsonl" >&2
  fail=1
fi

printf '%s\n' \
  '{"frontier":"fixture-frontier/demo-source","source_base":"public-demo-source","source_hash":"fixture-source-hash","stream_hash":"dirty-host-proof-demo","op_id":"dirty-host-proof","source_location":"src/point_add/trailmix_ludicrous/demo.rs:13","op_class":"ccx","executed_weight":1,"primitive_family":"dirty_host","restore_proof":"1","phase_proof":"1","support_certificate":"bound public dirty-host certificate"}' \
  > "$tmpdir/dirty-host-proof.jsonl"
if ! python3 scripts/storm-exact-miner.py support-check \
  --facts "$tmpdir/dirty-host-proof.jsonl" \
  --out "$tmpdir/dirty-host-proof-support.jsonl" >"$tmpdir/dirty-host-proof-support.out" 2>"$tmpdir/dirty-host-proof-support.err"; then
  printf 'public_harness_check=fail exact_miner_dirty_host_proof_support_failed\n' >&2
  cat "$tmpdir/dirty-host-proof-support.err" >&2
  fail=1
elif ! grep -q 'certified=1 unknown=0 counterexample=0' "$tmpdir/dirty-host-proof-support.out"; then
  printf 'public_harness_check=fail exact_miner_dirty_host_proof_counts\n' >&2
  cat "$tmpdir/dirty-host-proof-support.out" >&2
  cat "$tmpdir/dirty-host-proof-support.jsonl" >&2
  fail=1
fi

printf '%s\n' \
  '{"route_id":"dirty-host-packet-demo","frontier":"fixture-frontier/demo-source","source_base":"public-demo-source","source_hash":"fixture-source-hash","stream_hash":"dirty-host-packet-demo","fact_id":"dirty-host-packet-demo","source_location":"src/point_add/trailmix_ludicrous/demo.rs:14","op_class":"ccx","executed_weight":1,"allocator_unchanged":true,"proof_kind":"support_certificate","proof_status":"UNPROVEN","proof_inputs":{"source_hash":"fixture-source-hash","support_certificate":"bound packet cert","primitive_family":"dirty_host","support_status":"CERTIFIED"},"expected_avgT_delta":-1,"evidence_label":"Prefilter","validation_target":"trusted full 0/0/0 after source proof","kill_gate":"block compute if proof is UNKNOWN","primitive_family":"dirty_host"}' \
  > "$tmpdir/dirty-host-packet.jsonl"
if ! python3 scripts/storm-exact-miner.py prove \
  --candidates "$tmpdir/dirty-host-packet.jsonl" \
  --out "$tmpdir/dirty-host-packet-proof.jsonl" >"$tmpdir/dirty-host-packet-proof.out" 2>"$tmpdir/dirty-host-packet-proof.err"; then
  printf 'public_harness_check=fail exact_miner_dirty_host_packet_prove_failed\n' >&2
  cat "$tmpdir/dirty-host-packet-proof.err" >&2
  fail=1
elif ! grep -q '"proof_status":"UNKNOWN"' "$tmpdir/dirty-host-packet-proof.jsonl"; then
  printf 'public_harness_check=fail exact_miner_dirty_host_packet_promoted\n' >&2
  cat "$tmpdir/dirty-host-packet-proof.jsonl" >&2
  fail=1
fi

if ! scripts/apply-overlap-ledger.sh \
  --trace examples/apply-overlap-trace.example.txt \
  --frontier 1571592960 \
  --q 1147 \
  --target-q 1146 \
  --route fixture \
  --candidate pending_symbols >"$tmpdir/apply-overlap.out" 2>"$tmpdir/apply-overlap.err"; then
  printf 'public_harness_check=fail apply_overlap_certified_failed\n' >&2
  cat "$tmpdir/apply-overlap.err" >&2
  fail=1
elif ! grep -q 'Decision: support-certified-binder-fact' "$tmpdir/apply-overlap.out"; then
  printf 'public_harness_check=fail apply_overlap_certified_decision\n' >&2
  cat "$tmpdir/apply-overlap.out" >&2
  fail=1
fi

if ! scripts/apply-overlap-ledger.sh \
  --trace examples/apply-overlap-trace.example.txt \
  --frontier 1571592960 \
  --q 1147 \
  --target-q 1146 \
  --route fixture \
  --candidate last_tape_window >"$tmpdir/apply-overlap-nack.out" 2>"$tmpdir/apply-overlap-nack.err"; then
  printf 'public_harness_check=fail apply_overlap_nack_failed\n' >&2
  cat "$tmpdir/apply-overlap-nack.err" >&2
  fail=1
elif ! grep -q 'Decision: overlap-nacked-read-during-fold' "$tmpdir/apply-overlap-nack.out"; then
  printf 'public_harness_check=fail apply_overlap_nack_decision\n' >&2
  cat "$tmpdir/apply-overlap-nack.out" >&2
  fail=1
fi

if ! scripts/apply-overlap-ledger.sh \
  --trace examples/apply-overlap-restore-missing.example.txt \
  --frontier 1571592960 \
  --q 1147 \
  --target-q 1146 \
  --route fixture-restore-missing \
  --candidate pending_symbols >"$tmpdir/apply-overlap-restore-missing.out" 2>"$tmpdir/apply-overlap-restore-missing.err"; then
  printf 'public_harness_check=fail apply_overlap_restore_missing_failed\n' >&2
  cat "$tmpdir/apply-overlap-restore-missing.err" >&2
  fail=1
elif ! grep -q 'Decision: overlap-restore-proof-missing' "$tmpdir/apply-overlap-restore-missing.out"; then
  printf 'public_harness_check=fail apply_overlap_restore_missing_decision\n' >&2
  cat "$tmpdir/apply-overlap-restore-missing.out" >&2
  fail=1
fi

cat >"$tmpdir/source-line-family-summary.tsv" <<'EOF'
file	line	family	kind	count	source_hash
src/point_add/trailmix_ludicrous/gidney.rs	1297	gidney_thread_sum	CCX	100	fixture-source
src/point_add/trailmix_ludicrous/gidney.rs	1297	gidney_thread_sum	CCX	90	changed-source
src/point_add/trailmix_ludicrous/comparator.rs	717	comparator_top_carry	CCX	40	fixture-source
src/point_add/trailmix_ludicrous/arith.rs	834	unclassified	CCX	20	fixture-source
EOF
cat >"$tmpdir/wall-owner-contexts.tsv" <<'EOF'
source_location	file	line	context_hex	trace_context_value	family	call	bit	kind	count	executed_weight	source_hash
	src/point_add/trailmix_ludicrous/gidney.rs	1297	0x07000000		gidney_thread_sum	0	0	CCX	60		fixture-source
src/point_add/trailmix_ludicrous/gidney.rs:1297				0x07000001		0	1	CCX		40	fixture-source
	src/point_add/trailmix_ludicrous/gidney.rs	1297	0x07000002		gidney_thread_sum	0	2	CCX	90		changed-source
	src/point_add/trailmix_ludicrous/comparator.rs	717	0x04000000		comparator_top_carry	0	0	CCX	40		fixture-source
	src/point_add/trailmix_ludicrous/arith.rs	834	0x00000000		unclassified	0	0	CCX	20		fixture-source
EOF
if ! python3 scripts/storm-wall-owner-summary.py \
  --contexts "$tmpdir/wall-owner-contexts.tsv" \
  --source-line-out "$tmpdir/generated-source-line-family-summary.tsv" \
  --family-kind-out "$tmpdir/generated-family-kind-summary.tsv" >"$tmpdir/wall-owner-summary.out" 2>"$tmpdir/wall-owner-summary.err"; then
  printf 'public_harness_check=fail wall_owner_summary_failed\n' >&2
  cat "$tmpdir/wall-owner-summary.err" >&2
  fail=1
elif ! grep -q 'wall_owner_summary=pass input_rows=5 source_rows=4 family_rows=3' "$tmpdir/wall-owner-summary.out" ||
     ! grep -q $'gidney.rs\t1297\tgidney_thread_sum\tCCX\t100\tfixture-source' "$tmpdir/generated-source-line-family-summary.tsv" ||
     ! grep -q $'gidney.rs\t1297\tgidney_thread_sum\tCCX\t90\tchanged-source' "$tmpdir/generated-source-line-family-summary.tsv" ||
     ! grep -q $'gidney_thread_sum\tCCX\t190' "$tmpdir/generated-family-kind-summary.tsv"; then
  printf 'public_harness_check=fail wall_owner_summary_output\n' >&2
  cat "$tmpdir/wall-owner-summary.out" >&2
  cat "$tmpdir/generated-source-line-family-summary.tsv" >&2
  cat "$tmpdir/generated-family-kind-summary.tsv" >&2
  fail=1
fi

cat >"$tmpdir/alloc-near.raw" <<'EOF'
ALLOC_NEAR active=1146 next_idx=1145 phase='tlm_apply_inverse_mod_sub_register' ops_idx=10 free_pool=0 caller=src/point_add/trailmix_ludicrous/gidney.rs:1217
ALLOC_NEAR active=1152 next_idx=1151 phase='tlm_apply_inverse_mod_sub_register' ops_idx=11 free_pool=0 caller=src/point_add/trailmix_ludicrous/gidney.rs:1217
ALLOC_NEAR active=1152 next_idx=1151 phase='tlm_apply_forward_mod_add_fold' ops_idx=12 free_pool=0 caller=src/point_add/trailmix_ludicrous/arith.rs:1077
ALLOC_NEAR active=1151 next_idx=1150 phase='tlm_inverse_gcd_forward_compare' ops_idx=13 free_pool=1 caller=src/point_add/trailmix_ludicrous/comparator.rs:707
CONSTPROP TOTAL iters=1 dropped=0
EOF
if ! python3 scripts/storm-alloc-owner-summary.py \
  --input "$tmpdir/alloc-near.raw" \
  --summary-out "$tmpdir/alloc-owner-summary.tsv" \
  --peak 1152 >"$tmpdir/alloc-owner-summary.out" 2>"$tmpdir/alloc-owner-summary.err"; then
  printf 'public_harness_check=fail alloc_owner_summary_failed\n' >&2
  cat "$tmpdir/alloc-owner-summary.err" >&2
  fail=1
elif ! grep -q 'alloc_owner_summary=pass input_rows=4 caller_rows=3 peak_owner_rows=2 peak_phase_rows=2' "$tmpdir/alloc-owner-summary.out" ||
     ! grep -q $'gidney.rs\t1217\ttlm_apply_inverse_mod_sub_register\t2\t1146\t1152\t1\t1\ttlm_apply_inverse_mod_sub_register' "$tmpdir/alloc-owner-summary.tsv" ||
     ! grep -q $'arith.rs\t1077\ttlm_apply_forward_mod_add_fold\t1\t1152\t1152\t1\t1\ttlm_apply_forward_mod_add_fold' "$tmpdir/alloc-owner-summary.tsv" ||
     ! grep -q $'comparator.rs\t707\ttlm_inverse_gcd_forward_compare\t1\t1151\t1151\t0\t0\t' "$tmpdir/alloc-owner-summary.tsv"; then
  printf 'public_harness_check=fail alloc_owner_summary_output\n' >&2
  cat "$tmpdir/alloc-owner-summary.out" >&2
  cat "$tmpdir/alloc-owner-summary.tsv" >&2
  fail=1
fi

cat >"$tmpdir/peak-lifetime.raw" <<'EOF'
ALLOC_NEAR active=1146 next_idx=1145 phase='tlm_apply_inverse_mod_sub_register' ops_idx=10 free_pool=0 caller=src/point_add/trailmix_ludicrous/gidney.rs:1217
ALLOC_NEAR active=1152 next_idx=1151 phase='tlm_apply_inverse_mod_sub_register' ops_idx=11 free_pool=0 caller=src/point_add/trailmix_ludicrous/gidney.rs:1217
ALLOC_NEAR active=1152 next_idx=1151 phase='tlm_apply_forward_mod_add_fold' ops_idx=11 free_pool=0 caller=src/point_add/trailmix_ludicrous/arith.rs:1077
ALLOC_NEAR active=1152 next_idx=1151 phase='tlm_apply_forward_mod_add_fold' ops_idx=12 free_pool=0 caller=src/point_add/trailmix_ludicrous/arith.rs:1077
ALLOC_NEAR active=1151 next_idx=1150 phase='tlm_inverse_gcd_forward_compare' ops_idx=13 free_pool=1 caller=src/point_add/trailmix_ludicrous/comparator.rs:707
EOF
if ! python3 scripts/storm-peak-lifetime-ledger.py \
  --input "$tmpdir/peak-lifetime.raw" \
  --caller-out "$tmpdir/peak-lifetime-callers.tsv" \
  --phase-out "$tmpdir/peak-lifetime-phases.tsv" \
  --active-out "$tmpdir/peak-lifetime-active.tsv" \
  --peak 1152 >"$tmpdir/peak-lifetime.out" 2>"$tmpdir/peak-lifetime.err"; then
  printf 'public_harness_check=fail peak_lifetime_ledger_failed\n' >&2
  cat "$tmpdir/peak-lifetime.err" >&2
  fail=1
elif ! grep -q 'peak_lifetime_ledger=pass input_rows=5 active_min=1146 active_max=1152 peak=1152 peak_allocs=3 peak_ops=2 peak_ops_allocs_min=1 peak_ops_allocs_max=2 peak_ops_allocs_median=1.5 caller_rows=3 phase_rows=3' "$tmpdir/peak-lifetime.out" ||
     ! grep -q $'src/point_add/trailmix_ludicrous/arith.rs\t1077\ttlm_apply_forward_mod_add_fold\t2\t2\t2\t11\t12\t1\t1152\t1152\t1\ttlm_apply_forward_mod_add_fold' "$tmpdir/peak-lifetime-callers.tsv" ||
     ! grep -q $'src/point_add/trailmix_ludicrous/gidney.rs\t1217\ttlm_apply_inverse_mod_sub_register\t2\t1\t1\t1146\t1152\t1' "$tmpdir/peak-lifetime-phases.tsv" ||
     ! grep -q $'1152\t3' "$tmpdir/peak-lifetime-active.tsv"; then
  printf 'public_harness_check=fail peak_lifetime_ledger_output\n' >&2
  cat "$tmpdir/peak-lifetime.out" >&2
  cat "$tmpdir/peak-lifetime-callers.tsv" >&2
  cat "$tmpdir/peak-lifetime-phases.tsv" >&2
  cat "$tmpdir/peak-lifetime-active.tsv" >&2
  fail=1
fi

cat >"$tmpdir/gidney-thread-trace.raw" <<'EOF'
TLM_GIDNEY_THREAD call=7 phase=tlm_apply_inverse_mod_sub_register width=8 cin=1 cout=1 vents=0 ops_start=100 ops_end=180
ALLOC_NEAR active=1151 next_idx=1150 phase='tlm_apply_inverse_mod_sub_register' ops_idx=100 free_pool=0 caller=src/point_add/trailmix_ludicrous/gidney.rs:1217
ALLOC_NEAR active=1152 next_idx=1151 phase='tlm_apply_inverse_mod_sub_register' ops_idx=100 free_pool=0 caller=src/point_add/trailmix_ludicrous/gidney.rs:1217
TLM_GIDNEY_THREAD call=9 phase=tlm_apply_forward_mod_add_register width=8 cin=1 cout=1 vents=0 ops_start=200 ops_end=280
ALLOC_NEAR active=1152 next_idx=1151 phase='tlm_apply_forward_mod_add_register' ops_idx=200 free_pool=0 caller=src/point_add/trailmix_ludicrous/gidney.rs:1217
ALLOC_NEAR active=1152 next_idx=1151 phase='tlm_apply_inverse_mod_sub_fold' ops_idx=300 free_pool=0 caller=src/point_add/trailmix_ludicrous/arith.rs:1077
EOF
cat >"$tmpdir/gidney.rs" <<'EOF'
const GIDNEY_THREAD_BOUNDARY_DEAD_CALLS: &[usize] = &[
    7,
];
EOF
if ! python3 scripts/storm-gidney-thread-join.py \
  --input "$tmpdir/gidney-thread-trace.raw" \
  --out "$tmpdir/gidney-thread-join.tsv" \
  --gidney-source "$tmpdir/gidney.rs" \
  --peak 1152 >"$tmpdir/gidney-thread-join.out" 2>"$tmpdir/gidney-thread-join.err"; then
  printf 'public_harness_check=fail gidney_thread_join_failed\n' >&2
  cat "$tmpdir/gidney-thread-join.err" >&2
  fail=1
elif ! grep -q 'gidney_thread_join=pass thread_rows=2 alloc_rows=3 alloc_ops=2 joined_rows=2 unmatched_alloc_ops=0 dead_calls=1 dead_boundary_peak_candidates=1' "$tmpdir/gidney-thread-join.out" ||
     ! grep -q $'7\ttlm_apply_inverse_mod_sub_register\t8\t1\t1\t0\t100\t180\t2\t1\t1151\t1152\t1\t1\t1152:1,1151:1' "$tmpdir/gidney-thread-join.tsv" ||
     ! grep -q $'9\ttlm_apply_forward_mod_add_register\t8\t1\t1\t0\t200\t280\t1\t1\t1152\t1152\t0\t0\t1152:1' "$tmpdir/gidney-thread-join.tsv"; then
  printf 'public_harness_check=fail gidney_thread_join_output\n' >&2
  cat "$tmpdir/gidney-thread-join.out" >&2
  cat "$tmpdir/gidney-thread-join.tsv" >&2
  fail=1
fi
cat >"$tmpdir/closed-site-audit.tsv" <<'EOF'
rank	count	kind	file	line	context	source_hash
1	100	CCX	src/point_add/trailmix_ludicrous/gidney.rs	1297	none	fixture-source
EOF
if ! python3 scripts/storm-source-certificate-scout.py \
  --summary "$tmpdir/source-line-family-summary.tsv" \
  --closed "$tmpdir/closed-site-audit.tsv" \
  --source-hash fixture-source \
  --out "$tmpdir/context-scout.tsv" >"$tmpdir/context-scout.out" 2>"$tmpdir/context-scout.err"; then
  printf 'public_harness_check=fail source_certificate_scout_failed\n' >&2
  cat "$tmpdir/context-scout.err" >&2
  fail=1
elif ! grep -q 'source_certificate_scout=pass rows=2' "$tmpdir/context-scout.out" ||
     ! grep -q 'changed-source' "$tmpdir/context-scout.tsv" ||
     ! grep -q 'comparator_top_carry' "$tmpdir/context-scout.tsv" ||
     grep -q 'unclassified' "$tmpdir/context-scout.tsv"; then
  printf 'public_harness_check=fail source_certificate_scout_output\n' >&2
  cat "$tmpdir/context-scout.out" >&2
  cat "$tmpdir/context-scout.tsv" >&2
  fail=1
fi

cat >"$tmpdir/vandaele-plateau.trace" <<'EOF'
ALLOC_NEAR active=1152 next_idx=1151 phase='tlm_apply_inverse_mod_sub_register' ops_idx=10 free_pool=0 caller=src/point_add/trailmix_ludicrous/arith.rs:875
ALLOC_NEAR active=1152 next_idx=1151 phase='tlm_inverse_gcd_forward_compare' ops_idx=20 free_pool=1 caller=src/point_add/trailmix_ludicrous/comparator.rs:707
ALLOC_NEAR active=1151 next_idx=1151 phase='tlm_apply_inverse_mod_sub_fold' ops_idx=30 free_pool=1 caller=src/point_add/trailmix_ludicrous/arith.rs:1085
EOF
if ! scripts/vandaele-comparator-ledger.sh \
  --trace "$tmpdir/vandaele-plateau.trace" \
  --frontier 1571592960 \
  --q 1152 \
  --route fixture \
  --candidate comparator-only >"$tmpdir/vandaele-plateau.out" 2>"$tmpdir/vandaele-plateau.err"; then
  printf 'public_harness_check=fail vandaele_plateau_failed\n' >&2
  cat "$tmpdir/vandaele-plateau.err" >&2
  fail=1
elif ! grep -q 'Decision: plateau-cut-required' "$tmpdir/vandaele-plateau.out"; then
  printf 'public_harness_check=fail vandaele_plateau_decision\n' >&2
  cat "$tmpdir/vandaele-plateau.out" >&2
  fail=1
fi
cat >"$tmpdir/vandaele-q1147-plateau.trace" <<'EOF'
ALLOC_NEAR active=1147 next_idx=1146 phase='tlm_apply_inverse_mod_sub_fold' ops_idx=10 free_pool=1 caller=src/point_add/trailmix_ludicrous/arith.rs:875
ALLOC_NEAR active=1147 next_idx=1146 phase='tlm_apply_inverse_mod_sub_fold' ops_idx=20 free_pool=1 caller=src/point_add/trailmix_ludicrous/comparator.rs:191
ALLOC_NEAR active=1146 next_idx=1146 phase='tlm_apply_inverse_mod_sub_fold' ops_idx=30 free_pool=1 caller=src/point_add/trailmix_ludicrous/arith.rs:1085
EOF
if ! scripts/vandaele-comparator-ledger.sh \
  --trace "$tmpdir/vandaele-q1147-plateau.trace" \
  --frontier 1571592960 \
  --q 1147 \
  --route fixture-q1147 \
  --candidate comparator-only >"$tmpdir/vandaele-q1147-plateau.out" 2>"$tmpdir/vandaele-q1147-plateau.err"; then
  printf 'public_harness_check=fail vandaele_q1147_plateau_failed\n' >&2
  cat "$tmpdir/vandaele-q1147-plateau.err" >&2
  fail=1
elif ! grep -q 'Decision: plateau-cut-required' "$tmpdir/vandaele-q1147-plateau.out"; then
  printf 'public_harness_check=fail vandaele_q1147_plateau_decision\n' >&2
  cat "$tmpdir/vandaele-q1147-plateau.out" >&2
  fail=1
fi
if ! scripts/qcut-candidate-prefilter.sh bennett 126 2.0 >"$tmpdir/qcut-factor2.out" 2>"$tmpdir/qcut-factor2.err"; then
  printf 'public_harness_check=fail qcut_factor2_failed\n' >&2
  cat "$tmpdir/qcut-factor2.err" >&2
  fail=1
elif ! grep -q 'KILL-g3' "$tmpdir/qcut-factor2.out" ||
   ! grep -q 'KILL (gate 3)' "$tmpdir/qcut-factor2.out"; then
  printf 'public_harness_check=fail qcut_factor2_decision\n' >&2
  cat "$tmpdir/qcut-factor2.out" >&2
  fail=1
fi

if ! python3 scripts/storm-exact-miner.py trace-facts \
  --input "$tmpdir/context-scout.tsv" \
  --frontier fixture-frontier/demo-source \
  --source-base public-demo-source \
  --stream-hash source-certificate-scout-demo \
  --out "$tmpdir/context-scout-facts.jsonl" >"$tmpdir/context-scout-facts.out" 2>"$tmpdir/context-scout-facts.err"; then
  printf 'public_harness_check=fail source_certificate_scout_trace_failed\n' >&2
  cat "$tmpdir/context-scout-facts.err" >&2
  fail=1
elif ! python3 scripts/storm-exact-miner.py support-check \
  --facts "$tmpdir/context-scout-facts.jsonl" \
  --out "$tmpdir/context-scout-supported.jsonl" >"$tmpdir/context-scout-supported.out" 2>"$tmpdir/context-scout-supported.err"; then
  printf 'public_harness_check=fail source_certificate_scout_support_failed\n' >&2
  cat "$tmpdir/context-scout-supported.err" >&2
  fail=1
elif ! grep -q 'counterexample=2' "$tmpdir/context-scout-supported.out"; then
  printf 'public_harness_check=fail source_certificate_scout_support_counts\n' >&2
  cat "$tmpdir/context-scout-supported.out" >&2
  cat "$tmpdir/context-scout-supported.jsonl" >&2
  fail=1
fi

cat >"$tmpdir/source-hash-bound-scout.tsv" <<'EOF'
rank	count	kind	file	line	context	source_hash
1	264146	CCX	src/point_add/trailmix_ludicrous/gidney.rs	344	none	b9b8bfcd03cc3e53
2	263344	CCX	src/point_add/trailmix_ludicrous/gidney.rs	302	none	a3ba4f6fc6be9865
3	121702	CCX	src/point_add/trailmix_ludicrous/comparator.rs	196	none	c9c97c7ce21070ea
4	70900	CCX	src/point_add/trailmix_ludicrous/gcd.rs	690	none	870820f1ca5c6974
5	70900	CCX	src/point_add/trailmix_ludicrous/gcd.rs	697	none	7ff9c8a1b028c409
6	70390	CCX	src/point_add/trailmix_ludicrous/gcd.rs	904	none	ee3a5c0b13bf21e2
7	70372	CCX	src/point_add/trailmix_ludicrous/gcd.rs	1386	none	f76620b45753b899
8	65792	CCX	src/point_add/trailmix_ludicrous/fused.rs	1223	none	e517488039d4acc3
9	65792	CCX	src/point_add/trailmix_ludicrous/fused.rs	1284	none	0f9cad42c142861b
10	65792	CCX	src/point_add/trailmix_ludicrous/gcd.rs	1640	none	6463a039e5848198
11	65536	CCX	src/point_add/trailmix_ludicrous/gcd.rs	1591	none	7b33ab8a221f932f
12	51579	CCX	src/point_add/trailmix_ludicrous/arith.rs	563	none	324e34afb8598e19
13	21985	CCX	src/point_add/trailmix_ludicrous/arith.rs	1331	none	dcadba8e31258bc4
14	16932	CCX	src/point_add/trailmix_ludicrous/fused.rs	194	none	92464e1dbe395025
15	12989	CCX	src/point_add/trailmix_ludicrous/arith.rs	274	none	72d7ae23d4404ca9
16	12989	CCX	src/point_add/trailmix_ludicrous/arith.rs	281	none	33ad60de0fa8e78f
17	7792	CCX	src/point_add/trailmix_ludicrous/arith.rs	895	none	e70d0e40e1654d5f
18	7054	CCX	src/point_add/trailmix_ludicrous/arith.rs	258	none	af5bcd7ca1721225
19	6023	CCX	src/point_add/trailmix_ludicrous/arith.rs	1087	none	0fc7492380703c0e
20	1769	CCZ	src/point_add/trailmix_ludicrous/arith.rs	1139	none	0d02314f3d7bd53b
21	1133	CCX	src/point_add/trailmix_ludicrous/arith.rs	719	none	81fee66b262069d5
22	572	CCX	src/point_add/trailmix_ludicrous/arith.rs	799	none	d94ad239f6ca414a
23	5610	CCX	src/point_add/trailmix_ludicrous/codec.rs	304	none	011131e1db1721fe
24	5291	CCX	src/point_add/trailmix_ludicrous/gidney.rs	311	none	799c8637a66df13e
25	4212	CCX	src/point_add/trailmix_ludicrous/fused.rs	486	none	8b76aa5ce391d117
26	3754	CCZ	src/point_add/trailmix_ludicrous/gidney.rs	409	none	356b38b25111b2a7
27	2916	CCX	src/point_add/trailmix_ludicrous/fused.rs	611	none	e3de4982bd64ef97
28	1134	CCZ	src/point_add/trailmix_ludicrous/gidney.rs	461	none	2e66556410223ed7
29	802	CCX	src/point_add/trailmix_ludicrous/gidney.rs	305	none	f21177d38c09d92e
30	632	CCX	src/point_add/trailmix_ludicrous/gidney.rs	321	none	1a890341ccf9e47c
31	3364	CCX	src/point_add/trailmix_ludicrous/comparator.rs	57	none	d1a924ee4e28795f
32	49510	CCX	src/point_add/trailmix_ludicrous/comparator.rs	68	none	e2d291034f536196
33	3364	CCX	src/point_add/trailmix_ludicrous/comparator.rs	89	none	a0915e629bb82568
34	2624	CCX	src/point_add/trailmix_ludicrous/mcx.rs	80	none	4ccf2146ceb1eb50
35	2556	CCX	src/point_add/trailmix_ludicrous/fused.rs	832	none	30dc96d7748fab35
36	1404	CCX	src/point_add/trailmix_ludicrous/fused.rs	463	none	34d28414151b35be
37	1300	CCX	src/point_add/trailmix_ludicrous/fused.rs	918	none	42b00b29dd897893
38	946	CCX	src/point_add/trailmix_ludicrous/fused.rs	998	none	699d76d17355db42
39	24512	CCX	src/point_add/trailmix_ludicrous/square.rs	154	none	5db1c7a68cd9a333
40	24512	CCX	src/point_add/trailmix_ludicrous/square.rs	183	none	dfd7339142550728
41	514	CCX	src/point_add/trailmix_ludicrous/comparator.rs	158	none	471606852bc5024a
42	512	CCX	src/point_add/trailmix_ludicrous/gcd.rs	734	none	04ff46f341beed08
43	512	CCX	src/point_add/trailmix_ludicrous/gcd.rs	762	none	d11d7bb4ae684f23
EOF
if ! python3 scripts/storm-exact-miner.py trace-facts \
  --input "$tmpdir/source-hash-bound-scout.tsv" \
  --frontier fixture-frontier/demo-source \
  --source-base public-demo-source \
  --stream-hash source-hash-bound-scout-backlog \
  --out "$tmpdir/source-hash-bound-scout-facts.jsonl" >"$tmpdir/source-hash-bound-scout-facts.out" 2>"$tmpdir/source-hash-bound-scout-facts.err"; then
  printf 'public_harness_check=fail source_hash_bound_scout_trace_failed\n' >&2
  cat "$tmpdir/source-hash-bound-scout-facts.err" >&2
  fail=1
elif ! python3 scripts/storm-exact-miner.py support-check \
  --facts "$tmpdir/source-hash-bound-scout-facts.jsonl" \
  --out "$tmpdir/source-hash-bound-scout-supported.jsonl" >"$tmpdir/source-hash-bound-scout-supported.out" 2>"$tmpdir/source-hash-bound-scout-supported.err"; then
  printf 'public_harness_check=fail source_hash_bound_scout_support_failed\n' >&2
  cat "$tmpdir/source-hash-bound-scout-supported.err" >&2
  fail=1
elif ! grep -q 'counterexample=43' "$tmpdir/source-hash-bound-scout-supported.out" ||
     ! grep -q 'unknown=0' "$tmpdir/source-hash-bound-scout-supported.out"; then
  printf 'public_harness_check=fail source_hash_bound_scout_support_counts\n' >&2
  cat "$tmpdir/source-hash-bound-scout-supported.out" >&2
  cat "$tmpdir/source-hash-bound-scout-supported.jsonl" >&2
  fail=1
fi

if ! python3 scripts/storm-gidney-boundary-toy.py \
  --max-width 4 >"$tmpdir/gidney-boundary-toy.out" 2>"$tmpdir/gidney-boundary-toy.err"; then
  printf 'public_harness_check=fail gidney_boundary_toy_failed\n' >&2
  cat "$tmpdir/gidney-boundary-toy.err" >&2
  fail=1
elif ! grep -q 'gidney_boundary_toy=pass' "$tmpdir/gidney-boundary-toy.out" ||
     ! grep -q 'dead_boundary_mismatches=0' "$tmpdir/gidney-boundary-toy.out" ||
     ! grep -q 'nondead_formula_mismatches=0' "$tmpdir/gidney-boundary-toy.out" ||
     ! grep -q 'nondead_degree_with_cin=3' "$tmpdir/gidney-boundary-toy.out" ||
     ! grep -q 'needs_degree3_or_product_scratch=1' "$tmpdir/gidney-boundary-toy.out" ||
     ! grep -q 'phase_proof=0 ancilla_proof=0' "$tmpdir/gidney-boundary-toy.out"; then
  printf 'public_harness_check=fail gidney_boundary_toy_summary\n' >&2
  cat "$tmpdir/gidney-boundary-toy.out" >&2
  fail=1
fi

if ! python3 scripts/storm-windowed-carry-toy.py \
  --max-width 4 \
  --window 3 \
  --count-width 16 \
  --count-window 15 >"$tmpdir/windowed-carry-toy.out" 2>"$tmpdir/windowed-carry-toy.err"; then
  printf 'public_harness_check=fail windowed_carry_toy_failed\n' >&2
  cat "$tmpdir/windowed-carry-toy.err" >&2
  fail=1
elif ! grep -q 'windowed_carry_toy=pass' "$tmpdir/windowed-carry-toy.out" ||
     ! grep -q 'value_mismatches=0' "$tmpdir/windowed-carry-toy.out" ||
     ! grep -q 'restore_mismatches=0' "$tmpdir/windowed-carry-toy.out" ||
     ! grep -q 'phase_mismatches=0' "$tmpdir/windowed-carry-toy.out" ||
     ! grep -q 'ancilla_mismatches=0' "$tmpdir/windowed-carry-toy.out" ||
     ! grep -q 'width=16 window=15 cout=1' "$tmpdir/windowed-carry-toy.out" ||
     ! grep -q 'saved_carries=1' "$tmpdir/windowed-carry-toy.out" ||
     ! grep -q 'delta_toffoli=1' "$tmpdir/windowed-carry-toy.out" ||
     ! grep -q 'score_positive=0' "$tmpdir/windowed-carry-toy.out" ||
     ! grep -q 'source_edit_ready=0' "$tmpdir/windowed-carry-toy.out"; then
  printf 'public_harness_check=fail windowed_carry_toy_output\n' >&2
  cat "$tmpdir/windowed-carry-toy.out" >&2
  fail=1
fi

printf '%s\n' \
  'i=180 candidate=pending_symbols TLM_OVERLAP_CHECK candidate=pending_symbols i=180 target_phase=tlm_apply_inverse_mod_sub_fold reads_during_fold=0 restore_proof=1 phase_proof=1 support_certificate=public-cert active=1107 tape=415 pending=6 win_idx=60 fold_ops=2793965..2794746 qids=88,89 touched_qids=none sample=none' \
  > "$tmpdir/apply-overlap-prefixed-only.summary"
if ! scripts/apply-overlap-ledger.sh \
  --trace "$tmpdir/apply-overlap-prefixed-only.summary" \
  --frontier 1571592960 \
  --q 1147 \
  --target-q 1146 \
  --route fixture-prefixed-only \
  --candidate pending_symbols \
  --target-i any >"$tmpdir/apply-overlap-prefixed-only.out" 2>"$tmpdir/apply-overlap-prefixed-only.err"; then
  printf 'public_harness_check=fail apply_overlap_prefixed_only_failed\n' >&2
  cat "$tmpdir/apply-overlap-prefixed-only.err" >&2
  fail=1
elif ! grep -q 'Decision: missing-tape-overlap-trace' "$tmpdir/apply-overlap-prefixed-only.out" ||
     ! grep -q 'Evidence rows: 1' "$tmpdir/apply-overlap-prefixed-only.out"; then
  printf 'public_harness_check=fail apply_overlap_prefixed_only_gate\n' >&2
  cat "$tmpdir/apply-overlap-prefixed-only.out" >&2
  fail=1
fi

if [ "$fail" -ne 0 ]; then
  exit 1
fi

printf 'public_harness_check=pass\n'
