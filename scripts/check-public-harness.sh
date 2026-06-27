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
  scripts/storm-exact-miner.py \
  examples/audit-card.example.md \
  examples/operator-card.example.md \
  examples/mailbox-entry.example.md \
  examples/mailbox-entry.kimi-deep.example.md \
  examples/kimi-handoff.example.md \
  examples/route-packet.example.md \
  examples/compute-request.example.md \
  examples/public-note.example.md \
  examples/op-trace-facts.example.jsonl \
  examples/exact-skip-candidates.example.jsonl \
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
need_text scripts/storm-exact-miner.py "exact miner command" "trace-facts"
need_text scripts/storm-exact-miner.py "public safety scan" "redaction_risk"

need_text examples/operator-card.example.md "falsifiable decision" "Falsifiable decision"
need_text examples/audit-card.example.md "rci tony" "RCI/Tony"
need_text examples/audit-card.example.md "redsky" "Redsky Pass"
need_text examples/audit-card.example.md "bluesky" "Bluesky Pass"
need_text examples/mailbox-entry.example.md "read receipt requested" "Read receipt requested"
need_text examples/route-packet.example.md "stop condition" "Stop condition"
need_text examples/compute-request.example.md "zero paid compute" "zero"
need_text examples/public-note.example.md "not a candidate" "not a candidate"
need_text examples/op-trace-facts.example.jsonl "public demo source" "public-demo-source"
need_text examples/exact-skip-candidates.example.jsonl "proof packet" "proof_status"
need_text templates/exact-skip-candidate.json "allocator unchanged" "allocator_unchanged"
need_text docs/exact-support-miner.md "exact support miner" "Exact Support Miner"
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
need_text skills/nasqret-playbook.md "route slate" "route slate"
need_text skills/deepseek-pressure-test.md "pressure test" "pressure-test"
need_text skills/pip-discipline.md "pip discipline" "PIP Evidence Discipline"
need_text skills/exact-support-miner.md "exact miner" "storm-exact-miner.py"
need_text .agents/skills/exact-support-miner/SKILL.md "bridge" "Codex-discoverable bridge"

if [ "$fail" -ne 0 ]; then
  exit 1
fi

printf 'public_harness_check=pass\n'
