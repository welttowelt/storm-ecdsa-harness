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
  docs/bluesky-redsky-loop-gate-2026-06-28.md \
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
  scripts/storm-claim-ledger.py \
  scripts/storm-audit-impact.py \
  scripts/storm-bluesky-redsky-loop-gate.py \
  scripts/storm-mailbox-action-scan.py \
  scripts/storm-wall-owner-summary.py \
  scripts/storm-source-certificate-scout.py \
  scripts/storm-alloc-owner-summary.py \
  scripts/storm-peak-lifetime-ledger.py \
  scripts/storm-gidney-thread-join.py \
  scripts/storm-windowed-carry-toy.py \
  scripts/storm-ffg-pair-complete-toy.py \
  scripts/storm-const-chunk-prefix-ledger.py \
  scripts/storm-q1152-binder-ledger.py \
  scripts/storm-mcx-incrementer-budget.py \
  scripts/storm-construction-package-gate.py \
  scripts/storm-construction-intake-gate.py \
  scripts/storm-anvil-mass-ledger-gate.py \
  scripts/storm-anvil-namespace-gate.py \
  scripts/storm-anvil-exact-redundancy-gate.py \
  scripts/storm-pebbling-theorem-gate.py \
  scripts/storm-frontier-escape-gate.py \
  scripts/storm-square-static-gap-audit.py \
  scripts/storm-single-ccx-fanout-ledger.py \
  scripts/storm-fanout-qstate-guard.py \
  scripts/storm-fanout-survivor-phase-gate.py \
  scripts/storm-fanout-burst-triage-gate.py \
  scripts/storm-official-eval-isolation-gate.py \
  scripts/storm-fleet-owner-claim-gate.py \
  scripts/storm-pod-wrapper-dup-gate.py \
  scripts/storm-local-heavy-compute-gate.py \
  scripts/storm-pod-inventory-ack-gate.py \
  scripts/storm-candidate-validation-packet-gate.py \
  scripts/storm-apply-cswap-support-gate.py \
  scripts/storm-source-packet-novelty-gate.py \
  scripts/storm-source-row-routing-gate.py \
  scripts/storm-gidney-ccz-residual-gate.py \
  scripts/storm-qoffset-host-accounting-gate.py \
  scripts/storm-emit-bundle-support-gate.py \
  scripts/storm-transcript-overlap-gate.py \
  scripts/storm-compute-restart-gate.py \
  scripts/storm-compute-unlock-gate.py \
  examples/fleet-owner-claim-vague-token.example.txt \
  examples/official-eval-isolation-helper-storm.example.sh \
  scripts/storm-q1152-avgt-theorem.py \
  scripts/storm-cout-host-row-gate.py \
  scripts/storm-zero-host-accounting-gate.py \
  scripts/storm-dead-drop-fixedpoint-gate.py \
  scripts/storm-route-compare-admission.py \
  scripts/storm-ffg-pair-proof-gate.py \
  scripts/storm-paper-invariant-intake-gate.py \
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
  examples/bluesky-redsky-loop-pass.example.json \
  examples/bluesky-redsky-loop-overclaim.example.json \
  examples/apply-overlap-trace.example.txt \
  examples/apply-overlap-restore-missing.example.txt \
  examples/fanout-survivor-phase-gate.example.txt \
  examples/fanout-burst-triage-nack.example.txt \
  examples/fanout-burst-triage-candidate.example.txt \
  examples/official-eval-isolation-unsafe.example.sh \
  examples/official-eval-isolation-locked.example.sh \
  examples/official-eval-isolation-workdir.example.sh \
  examples/fleet-owner-claim-pass.example.txt \
  examples/fleet-owner-claim-missing.example.txt \
  examples/fleet-owner-claim-combined-tail.example.txt \
  examples/pod-wrapper-dup-pass.example.txt \
  examples/pod-wrapper-dup-fail.example.txt \
  examples/local-heavy-compute-pass.example.txt \
  examples/local-heavy-compute-fail.example.txt \
  examples/local-heavy-compute-hold.example.txt \
  examples/pod-inventory-ack-pass.example.txt \
  examples/pod-inventory-ack-hold.example.txt \
  examples/pod-inventory-ack-fail.example.txt \
  examples/pod-inventory-ack-account-empty-pass.example.txt \
  examples/pod-inventory-ack-account-empty-hold.example.txt \
  examples/pod-inventory-ack-account-empty-fail.example.txt \
  examples/candidate-validation-packet-pass.example.txt \
  examples/candidate-validation-packet-hold.example.txt \
  examples/candidate-validation-packet-fail.example.txt \
  examples/candidate-validation-packet-stale.example.txt \
  examples/apply-cswap-support-pass.example.txt \
  examples/apply-cswap-support-hold.example.txt \
  examples/apply-cswap-support-fail.example.txt \
  examples/apply-cswap-support-stale.example.txt \
  examples/source-packet-novelty-pass.example.txt \
  examples/source-packet-novelty-arith-pass.example.txt \
  examples/source-packet-novelty-hold.example.txt \
  examples/source-packet-novelty-fail.example.txt \
  examples/source-packet-novelty-family-exhausted.example.txt \
  examples/source-packet-novelty-stale.example.txt \
  examples/source-row-routing-packet.example.txt \
  examples/source-row-routing-closure.example.txt \
  examples/source-row-routing-hold.example.txt \
  examples/source-row-routing-fail.example.txt \
  examples/gidney-ccz-residual-pass.example.txt \
  examples/gidney-ccz-residual-hold.example.txt \
  examples/gidney-ccz-residual-fail.example.txt \
  examples/qoffset-host-accounting-pass.example.txt \
  examples/qoffset-host-accounting-closure.example.txt \
  examples/qoffset-host-accounting-hold.example.txt \
  examples/qoffset-host-accounting-fail.example.txt \
  examples/emit-bundle-support-pass.example.txt \
  examples/emit-bundle-support-closure.example.txt \
  examples/emit-bundle-support-hold.example.txt \
  examples/emit-bundle-support-fail.example.txt \
  examples/construction-intake-pass.example.txt \
  examples/construction-intake-hold.example.txt \
  examples/construction-intake-fail.example.txt \
  examples/anvil-mass-ledger-pass.example.tsv \
  examples/anvil-mass-ledger-raw-pass.example.tsv \
  examples/anvil-mass-ledger-hold.example.tsv \
  examples/anvil-mass-ledger-fail.example.tsv \
  examples/anvil-namespace-pass.example.txt \
  examples/anvil-namespace-closure.example.txt \
  examples/anvil-namespace-hold.example.txt \
  examples/anvil-namespace-fail.example.txt \
  examples/anvil-exact-redundancy-pass.example.txt \
  examples/anvil-exact-redundancy-hold.example.txt \
  examples/anvil-exact-redundancy-fail.example.txt \
  examples/pebbling-theorem-pass.example.txt \
  examples/pebbling-theorem-hold.example.txt \
  examples/pebbling-theorem-fail.example.txt \
  examples/ffg-pair-complete-no-recompute.example.txt \
  examples/ffg-pair-complete-recompute-hold.example.txt \
  examples/transcript-overlap-pass.example.txt \
  examples/transcript-overlap-hold.example.txt \
  examples/transcript-overlap-fail.example.txt \
  examples/transcript-overlap-stale.example.txt \
  examples/ffg-pair-proof-pass.example.txt \
  examples/ffg-pair-proof-hold.example.txt \
  examples/ffg-pair-proof-fail.example.txt \
  examples/paper-invariant-intake-pass.example.txt \
  examples/paper-invariant-intake-hold.example.txt \
  examples/paper-invariant-intake-fail.example.txt \
  examples/compute-restart-pass.example.txt \
  examples/compute-restart-hold.example.txt \
  examples/compute-restart-fail.example.txt \
  examples/compute-restart-eval-pass.example.txt \
  examples/compute-unlock-pass.example.txt \
  examples/compute-unlock-hold.example.txt \
  examples/compute-unlock-fail.example.txt \
  examples/compute-unlock-stale.example.txt \
  templates/exact-skip-candidate.json \
  docs/exact-support-miner.md \
  docs/bluesky-redsky-ffg-pair-complete-toy-2026-06-28.md \
  docs/bluesky-redsky-ffg-pair-proof-gate-2026-06-28.md \
  docs/bluesky-redsky-paper-invariant-intake-2026-06-28.md \
  docs/bluesky-redsky-pod-inventory-ack-2026-06-28.md \
  docs/bluesky-redsky-pod-inventory-ack-2026-06-28.json \
  docs/bluesky-redsky-source-row-routing-2026-06-28.md \
  docs/redsky-stormgate-audit-2026-06-20-f8e215b-current.md \
  operators/codex-storm.md \
  operators/deep-storm.md \
  operators/file-handoff-protocol.md \
  operators/handoff-protocol.md \
  operators/kimi-storm.md \
  routes/tobitvector-cswap-body-trim-q1170.md \
  routes/tobitvector-cswap-body-trim-q1170.rci-audit.md \
  patches/fanout-no-clone-d44.patch \
  patches/eval-fast-exit-dirty-triage.patch \
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
  skills/construction-package-gate.md \
  skills/frontier-escape-gate.md \
  skills/single-ccx-fanout-throughput.md \
  skills/fanout-runpod-qstate-guard.md \
  skills/fanout-survivor-phase-gate.md \
  skills/fanout-burst-triage-gate.md \
  skills/official-fast-exit-eval.md \
  skills/official-eval-isolation-gate.md \
  skills/fleet-owner-claim-gate.md \
  skills/pod-wrapper-dup-gate.md \
  skills/local-heavy-compute-gate.md \
  skills/pod-inventory-ack-gate.md \
  skills/route-compare-admission-gate.md \
  skills/ffg-pair-proof-gate.md \
  skills/candidate-validation-packet-gate.md \
  skills/apply-cswap-support-gate.md \
  skills/source-packet-novelty-gate.md \
  skills/source-row-routing-gate.md \
  skills/gidney-ccz-residual-gate.md \
  skills/qoffset-host-accounting-gate.md \
  skills/emit-bundle-support-gate.md \
  skills/construction-intake-gate.md \
  skills/anvil-mass-ledger-gate.md \
  skills/anvil-namespace-gate.md \
  skills/anvil-exact-redundancy-gate.md \
  skills/pebbling-theorem-gate.md \
  skills/transcript-overlap-gate.md \
  skills/compute-unlock-gate.md \
  skills/compute-restart-gate.md \
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
  skills/paper-invariant-intake-gate.md \
  skills/paper-roetteler-ecdlp-resource-estimate.md \
  skills/paper-garn-kan-windowed-binary-ecdlp.md \
  skills/paper-wire-recycling-lifetime-graph.md \
  skills/paper-dirty-borrowing-entanglement.md \
  skills/paper-dead-gate-elimination.md \
  skills/paper-score-condition-discount.md \
  skills/zero-host-accounting.md \
  skills/dead-drop-fixedpoint.md \
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
  .agents/skills/construction-package-gate/SKILL.md \
  .agents/skills/frontier-escape-gate/SKILL.md \
  .agents/skills/single-ccx-fanout-throughput/SKILL.md \
  .agents/skills/fanout-survivor-phase-gate/SKILL.md \
  .agents/skills/fanout-burst-triage-gate/SKILL.md \
  .agents/skills/official-fast-exit-eval/SKILL.md \
  .agents/skills/official-eval-isolation-gate/SKILL.md \
  .agents/skills/fleet-owner-claim-gate/SKILL.md \
  .agents/skills/pod-wrapper-dup-gate/SKILL.md \
  .agents/skills/local-heavy-compute-gate/SKILL.md \
  .agents/skills/pod-inventory-ack-gate/SKILL.md \
  .agents/skills/route-compare-admission-gate/SKILL.md \
  .agents/skills/ffg-pair-proof-gate/SKILL.md \
  .agents/skills/candidate-validation-packet-gate/SKILL.md \
  .agents/skills/apply-cswap-support-gate/SKILL.md \
  .agents/skills/source-packet-novelty-gate/SKILL.md \
  .agents/skills/source-row-routing-gate/SKILL.md \
  .agents/skills/gidney-ccz-residual-gate/SKILL.md \
  .agents/skills/qoffset-host-accounting-gate/SKILL.md \
  .agents/skills/emit-bundle-support-gate/SKILL.md \
  .agents/skills/construction-intake-gate/SKILL.md \
  .agents/skills/anvil-mass-ledger-gate/SKILL.md \
  .agents/skills/anvil-namespace-gate/SKILL.md \
  .agents/skills/anvil-exact-redundancy-gate/SKILL.md \
  .agents/skills/pebbling-theorem-gate/SKILL.md \
  .agents/skills/transcript-overlap-gate/SKILL.md \
  .agents/skills/compute-unlock-gate/SKILL.md \
  .agents/skills/compute-restart-gate/SKILL.md \
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
  .agents/skills/paper-invariant-intake-gate/SKILL.md \
  .agents/skills/paper-roetteler-ecdlp-resource-estimate/SKILL.md \
  .agents/skills/paper-garn-kan-windowed-binary-ecdlp/SKILL.md \
  .agents/skills/paper-wire-recycling-lifetime-graph/SKILL.md \
  .agents/skills/paper-dirty-borrowing-entanglement/SKILL.md \
  .agents/skills/paper-dead-gate-elimination/SKILL.md \
  .agents/skills/paper-score-condition-discount/SKILL.md \
  .agents/skills/zero-host-accounting/SKILL.md \
  .agents/skills/dead-drop-fixedpoint/SKILL.md \
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
need_text docs/bluesky-redsky-loop-gate-2026-06-28.md "five-loop gate doc" "implemented=5 verified=5"
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
need_text scripts/storm-bluesky-redsky-loop-gate.py "bluesky redsky loop gate" "bluesky_redsky_loop_gate="
need_text scripts/storm-bluesky-redsky-loop-gate.py "compute dispatch guard" "compute_dispatch_allowed"
need_text scripts/storm-mailbox-action-scan.py "mailbox direct ask scanner" "mailbox_action_scan"
need_text scripts/storm-wall-owner-summary.py "wall owner summary" "wall_owner_summary=pass"
need_text scripts/storm-source-certificate-scout.py "source certificate scout" "source_certificate_scout=pass"
need_text scripts/storm-alloc-owner-summary.py "alloc owner summary" "alloc_owner_summary=pass"
need_text scripts/storm-peak-lifetime-ledger.py "peak lifetime ledger" "peak_lifetime_ledger=pass"
need_text scripts/storm-gidney-thread-join.py "gidney thread join" "gidney_thread_join=pass"
need_text scripts/storm-windowed-carry-toy.py "windowed carry toy" "windowed_carry_toy="
need_text scripts/storm-ffg-pair-complete-toy.py "ffg pair complete toy" "ffg_pair_complete_toy="
need_text scripts/storm-ffg-pair-complete-toy.py "no recompute nack" "no-recompute-pair-complete-nack"
need_text scripts/storm-ffg-pair-complete-toy.py "recompute hold" "recompute-plan-needs-source-phase-score-proof"
need_text scripts/storm-q1152-binder-ledger.py "q1152 binder ledger" "q1152_binder_ledger=pass"
need_text scripts/storm-q1152-binder-ledger.py "mcx floor" "none_kg_prefix_ancilla"
need_text scripts/storm-mcx-incrementer-budget.py "mcx incrementer budget" "mcx_incrementer_budget=pass"
need_text scripts/storm-mcx-incrementer-budget.py "candidate budget fail" "candidate-budget-fail"
need_text scripts/storm-construction-package-gate.py "construction package gate" "construction_package_gate=pass"
need_text scripts/storm-construction-intake-gate.py "construction intake gate" "construction_intake_gate="
need_text scripts/storm-construction-intake-gate.py "paper-only failure" "paper_only_or_scout_only"
need_text scripts/storm-anvil-mass-ledger-gate.py "anvil mass ledger gate" "anvil_mass_ledger_gate="
need_text scripts/storm-anvil-mass-ledger-gate.py "counterexample routing failure" "counterexample_routed_to_positive_gate"
need_text scripts/storm-anvil-namespace-gate.py "anvil namespace gate" "anvil_namespace_gate"
need_text scripts/storm-anvil-namespace-gate.py "namespace binding hold" "complete-anvil-namespace-binding"
need_text scripts/storm-anvil-exact-redundancy-gate.py "anvil exact redundancy gate" "anvil_exact_redundancy_gate="
need_text scripts/storm-anvil-exact-redundancy-gate.py "exact redundancy review decision" "anvil-exact-redundancy-review-no-compute"
need_text scripts/storm-pebbling-theorem-gate.py "pebbling theorem gate" "pebbling_theorem_gate="
need_text scripts/storm-pebbling-theorem-gate.py "stale drop state failure" "stale_drop_state"
need_text scripts/storm-construction-package-gate.py "package nack" "package-nack"
need_text scripts/storm-frontier-escape-gate.py "frontier escape gate" "frontier_escape_gate=pass"
need_text scripts/storm-frontier-escape-gate.py "escape nack" "escape-nack"
need_text scripts/storm-square-static-gap-audit.py "square static gap audit" "square_static_gap_audit=pass"
need_text scripts/storm-square-static-gap-audit.py "zero bit trim decision" "no-executable-zero-bit-trim"
need_text scripts/storm-single-ccx-fanout-ledger.py "single ccx fanout ledger" "single_ccx_fanout_ledger=pass"
need_text scripts/storm-single-ccx-fanout-ledger.py "trusted eval nack" "trusted-eval-nack"
need_text scripts/storm-fanout-qstate-guard.py "qstate guard" "qstate_guard=ok"
need_text scripts/storm-fanout-survivor-phase-gate.py "survivor phase gate" "fanout_survivor_phase_gate="
need_text scripts/storm-fanout-survivor-phase-gate.py "phase gap" "phase_gap"
need_text scripts/storm-fanout-burst-triage-gate.py "fanout burst triage gate" "fanout_burst_triage_gate="
need_text scripts/storm-fanout-burst-triage-gate.py "full validation decision" "full-local-validation-required"
need_text scripts/storm-official-eval-isolation-gate.py "official eval isolation gate" "official_eval_isolation_gate="
need_text scripts/storm-official-eval-isolation-gate.py "shared artifact race" "shared_artifact_without_lock_or_isolation"
need_text scripts/storm-fleet-owner-claim-gate.py "fleet owner claim gate" "fleet_owner_claim_gate="
need_text scripts/storm-fleet-owner-claim-gate.py "no submit ack" "no_submit_ack"
need_text scripts/storm-fleet-owner-claim-gate.py "strict packet mode" "strict-single-packet"
need_text scripts/storm-pod-wrapper-dup-gate.py "pod wrapper duplicate gate" "pod_wrapper_dup_gate="
need_text scripts/storm-pod-wrapper-dup-gate.py "duplicate eval failure" "duplicate_eval_nonce_wrapper"
need_text scripts/storm-local-heavy-compute-gate.py "local heavy compute gate" "local_heavy_compute_gate="
need_text scripts/storm-local-heavy-compute-gate.py "mac stop decision" "stop-mac-local-heavy-compute"
need_text scripts/storm-local-heavy-compute-gate.py "storm exact miner heat stop" "storm-exact-miner"
need_text scripts/storm-pod-inventory-ack-gate.py "pod inventory ack gate" "pod_inventory_ack_gate="
need_text scripts/storm-pod-inventory-ack-gate.py "pod inventory no compute" "inventory-ack-accepted-no-compute"
need_text scripts/storm-pod-inventory-ack-gate.py "account empty inventory" "account_empty"
need_text scripts/storm-pod-inventory-ack-gate.py "nonzero empty spend failure" "account_empty_nonzero_spend"
need_text scripts/storm-candidate-validation-packet-gate.py "candidate validation packet gate" "candidate_validation_packet_gate="
need_text scripts/storm-candidate-validation-packet-gate.py "akash handoff decision" "candidate-for-akash-handoff-no-submit"
need_text scripts/storm-candidate-validation-packet-gate.py "stale source failure" "stale_source_base"
need_text scripts/storm-apply-cswap-support-gate.py "apply cswap support gate" "apply_cswap_support_gate="
need_text scripts/storm-apply-cswap-support-gate.py "per step bit decision" "complete-per-step-per-bit-proof"
need_text scripts/storm-apply-cswap-support-gate.py "stale source decision" "stale_source_base"
need_text scripts/storm-source-packet-novelty-gate.py "source packet novelty gate" "source_packet_novelty_gate="
need_text scripts/storm-source-packet-novelty-gate.py "bounded source proof decision" "admit-one-bounded-source-proof-no-compute"
need_text scripts/storm-source-packet-novelty-gate.py "closed ledger failure" "all_current_unknowns_closed"
need_text scripts/storm-source-packet-novelty-gate.py "family exhaustion failure" "source_family_exhausted"
need_text scripts/storm-source-packet-novelty-gate.py "candidate hash field" "candidate_hash"
need_text scripts/storm-source-packet-novelty-gate.py "point add source location" "src/point_add"
need_text scripts/storm-source-row-routing-gate.py "source row routing gate" "source_row_routing_gate="
need_text scripts/storm-source-row-routing-gate.py "source row closure decision" "source-row-closed-advance-next-no-compute"
need_text scripts/storm-gidney-ccz-residual-gate.py "gidney ccz residual gate" "gidney_ccz_residual_gate="
need_text scripts/storm-gidney-ccz-residual-gate.py "default remainder failure" "default_on_remainder_not_new_edge"
need_text scripts/storm-qoffset-host-accounting-gate.py "qoffset host accounting gate" "qoffset_host_accounting_gate="
need_text scripts/storm-qoffset-host-accounting-gate.py "qoffset unknown close failure" "proof_unknown_close_as_nack"
need_text scripts/storm-emit-bundle-support-gate.py "emit bundle support gate" "emit_bundle_support_gate="
need_text scripts/storm-emit-bundle-support-gate.py "bundle mass bar" "bundle_mass_below_rounding_bar"
need_text scripts/storm-transcript-overlap-gate.py "transcript overlap gate" "transcript_overlap_gate="
need_text scripts/storm-transcript-overlap-gate.py "source theorem review decision" "source-theorem-review-no-compute"
need_text scripts/storm-transcript-overlap-gate.py "score edge failure" "score_no_edge"
need_text scripts/storm-compute-restart-gate.py "compute restart gate" "compute_restart_gate="
need_text scripts/storm-compute-restart-gate.py "scanner closed failure" "scanner_restart_under_closed_compute_gate"
need_text scripts/storm-compute-restart-gate.py "scanner route ack failure" "scanner_without_route_ack_and_certified_evidence"
need_text scripts/storm-compute-restart-gate.py "restart budget gate" "missing_budget"
need_text scripts/storm-compute-unlock-gate.py "compute unlock gate" "compute_unlock_gate="
need_text scripts/storm-compute-unlock-gate.py "no submit dispatch decision" "compute-unlock-ready-for-storm-dispatch-no-submit"
need_text scripts/storm-compute-unlock-gate.py "closed compute failure" "compute_closed_without_unlock_packet"
need_text scripts/storm-claim-ledger.py "claim ledger summary" "claim_ledger_summary"
need_text scripts/storm-q1152-avgt-theorem.py "q1152 avgT theorem" "q1152_avgt_theorem=pass"
need_text scripts/storm-q1152-avgt-theorem.py "condition discount" "classical condition"
need_text scripts/storm-paper-invariant-intake-gate.py "paper invariant intake gate" "paper_invariant_intake_gate="
need_text scripts/storm-paper-invariant-intake-gate.py "source backed skill review" "source-backed-skill-review-no-compute"
need_text patches/fanout-no-clone-d44.patch "fanout no clone patch" "rewrite_first_target_fanout\\(&ops"
need_text patches/eval-fast-exit-dirty-triage.patch "fast exit patch" "ISLAND_FAST_EXIT"
need_text patches/eval-fast-exit-dirty-triage.patch "tested shots" "tested_shots"
need_text skills/single-ccx-fanout-throughput.md "fanout throughput skill" "throughput helper only"
need_text skills/single-ccx-fanout-throughput.md "fanout not winner" "not a winner"
need_text skills/fanout-runpod-qstate-guard.md "qstate guard skill" "qstate_guard=ok"
need_text skills/fanout-survivor-phase-gate.md "survivor phase skill" "phase-aware official eval"
need_text skills/fanout-burst-triage-gate.md "fanout burst skill" "FANOUT_NONCE_LIST"
need_text skills/official-fast-exit-eval.md "official fast exit" "dirty-triage"
need_text skills/official-eval-isolation-gate.md "official eval isolation skill" "triage-only evidence"
need_text skills/fleet-owner-claim-gate.md "fleet owner claim skill" "paid instance survives audit"
need_text skills/fleet-owner-claim-gate.md "strict packet skill" "strict-single-packet"
need_text skills/pod-wrapper-dup-gate.md "pod wrapper duplicate skill" "Duplicate GPU wrappers"
need_text skills/local-heavy-compute-gate.md "local heavy compute skill" "Mac-local heavy compute"
need_text skills/local-heavy-compute-gate.md "local heavy storm exact miner" "storm-exact-miner"
need_text skills/pod-inventory-ack-gate.md "pod inventory skill" "Pod Inventory ACK Gate"
need_text skills/pod-inventory-ack-gate.md "pod inventory no compute" "inventory-ack-accepted-no-compute"
need_text skills/route-compare-admission-gate.md "route compare admission skill" "Route Compare Admission Gate"
need_text skills/route-compare-admission-gate.md "strict admission flag" "require-admission"
need_text skills/ffg-pair-proof-gate.md "ffg pair proof skill" "FFG Pair Proof Gate"
need_text skills/ffg-pair-proof-gate.md "pair complete calls" "178,180,181"
need_text skills/candidate-validation-packet-gate.md "candidate validation skill" "FOR-AKASH"
need_text skills/apply-cswap-support-gate.md "apply cswap support skill" "per-step and per-bit"
need_text skills/apply-cswap-support-gate.md "machine readable packet" "frontier_score"
need_text skills/source-packet-novelty-gate.md "source packet novelty skill" "outside_closed_ledger"
need_text skills/source-packet-novelty-gate.md "source packet no compute" "no compute"
need_text skills/source-packet-novelty-gate.md "source packet candidate hash" "candidate index/diff hash"
need_text skills/source-packet-novelty-gate.md "source family exhausted" "exhausted source-family"
need_text skills/source-row-routing-gate.md "source row routing skill" "Source Row Routing Gate"
need_text skills/source-row-routing-gate.md "source row no compute" "no-compute"
need_text skills/gidney-ccz-residual-gate.md "gidney ccz residual skill" "Gidney CCZ Residual Gate"
need_text skills/gidney-ccz-residual-gate.md "gidney ccz no auto compute" "no automatic compute"
need_text skills/qoffset-host-accounting-gate.md "qoffset host accounting skill" "Qoffset Host Accounting Gate"
need_text skills/qoffset-host-accounting-gate.md "qoffset no compute" "no-compute"
need_text skills/emit-bundle-support-gate.md "emit bundle support skill" "Emit Bundle Support Gate"
need_text skills/emit-bundle-support-gate.md "emit bundle no compute" "no-compute"
need_text skills/transcript-overlap-gate.md "transcript overlap skill" "transcript peak-overlap"
need_text skills/transcript-overlap-gate.md "active only failure" "active-only"
need_text skills/compute-restart-gate.md "compute restart skill" "scanner restart"
need_text skills/compute-restart-gate.md "compute restart no submit" "no submit authority"
need_text skills/compute-unlock-gate.md "compute unlock skill" "storm_route_ack"
need_text skills/compute-unlock-gate.md "compute unlock no submit" "no-submit"
need_text .agents/skills/single-ccx-fanout-throughput/SKILL.md "bridge" "fanout-no-clone-d44.patch"
need_text .agents/skills/fanout-survivor-phase-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/fanout-burst-triage-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/official-fast-exit-eval/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/official-eval-isolation-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/fleet-owner-claim-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/pod-wrapper-dup-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/local-heavy-compute-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/pod-inventory-ack-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/route-compare-admission-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/ffg-pair-proof-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/candidate-validation-packet-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/apply-cswap-support-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/source-packet-novelty-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/source-packet-novelty-gate/SKILL.md "bridge candidate hash" "candidate index/diff hash"
need_text .agents/skills/source-row-routing-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/gidney-ccz-residual-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/qoffset-host-accounting-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/emit-bundle-support-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/transcript-overlap-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/compute-unlock-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/compute-restart-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text scripts/storm-cout-host-row-gate.py "cout host row gate" "cout_host_row_gate=pass"
need_text scripts/storm-cout-host-row-gate.py "safe host row" "SAFE_HOST_ROW"
need_text scripts/storm-zero-host-accounting-gate.py "zero host accounting" "zero_host_accounting_gate=pass"
need_text scripts/storm-zero-host-accounting-gate.py "source accounting nack" "source-accounting-nack"
need_text scripts/storm-dead-drop-fixedpoint-gate.py "dead drop fixedpoint" "dead_drop_fixedpoint_gate=pass"
need_text scripts/storm-dead-drop-fixedpoint-gate.py "fixedpoint required" "fixedpoint-required"
need_text scripts/storm-route-compare-admission.py "route compare admission gate" "route_compare_admission="
need_text scripts/storm-route-compare-admission.py "route compare admitted flag" "admitted="
need_text scripts/storm-route-compare-admission.py "route compare min shots" "min_shots"
need_text scripts/storm-route-compare-admission.py "route compare rounded score" "avg_tof_rounded"
need_text scripts/storm-ffg-pair-proof-gate.py "ffg pair proof gate" "ffg_pair_proof_gate="
need_text scripts/storm-ffg-pair-proof-gate.py "ffg pair calls" "required_calls"

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
need_text examples/bluesky-redsky-loop-pass.example.json "five-loop process fixture" "process-bluesky-redsky-five-loop"
need_text examples/ffg-pair-complete-no-recompute.example.txt "ffg no recompute fixture" "no-recompute-pair-complete-nack"
need_text examples/ffg-pair-complete-recompute-hold.example.txt "ffg recompute fixture" "recompute-plan-needs-source-phase-score-proof"
need_text examples/apply-overlap-trace.example.txt "apply overlap fixture" "TLM_OVERLAP_CHECK"
need_text examples/apply-overlap-trace.example.txt "apply overlap tail fixture" "TLM_TAIL"
need_text examples/apply-overlap-restore-missing.example.txt "apply overlap restore-missing fixture" "restore_proof=0"
need_text examples/apply-overlap-restore-missing.example.txt "apply overlap tape-tail fixture" "tape_tail_code"
need_text examples/ffg-pair-proof-pass.example.txt "ffg pair pass fixture" "pair_complete=yes"
need_text examples/ffg-pair-proof-hold.example.txt "ffg pair hold fixture" "candidate"
need_text examples/ffg-pair-proof-fail.example.txt "ffg pair fail fixture" "covered_calls=192"
need_text examples/paper-invariant-intake-pass.example.txt "paper invariant pass fixture" "source_backed=yes"
need_text examples/paper-invariant-intake-hold.example.txt "paper invariant hold fixture" "complete-source-hash"
need_text examples/paper-invariant-intake-fail.example.txt "paper invariant fail fixture" "paper_only=yes"
need_text examples/pod-inventory-ack-pass.example.txt "pod inventory pass fixture" "status=stopped"
need_text examples/pod-inventory-ack-hold.example.txt "pod inventory hold fixture" "status=unreachable"
need_text examples/pod-inventory-ack-fail.example.txt "pod inventory fail fixture" "owner=unknown"
need_text examples/pod-inventory-ack-account-empty-pass.example.txt "account empty pass fixture" "status=0-pods"
need_text examples/pod-inventory-ack-account-empty-hold.example.txt "account empty hold fixture" "status=0-pods"
need_text examples/pod-inventory-ack-account-empty-fail.example.txt "account empty fail fixture" "currentSpendPerHr=0.22"
need_text examples/source-row-routing-packet.example.txt "source row packet fixture" "gidney-344-source-packet"
need_text examples/source-row-routing-closure.example.txt "source row closure fixture" "source-closure"
need_text examples/source-row-routing-hold.example.txt "source row hold fixture" "closure-incomplete"
need_text examples/source-row-routing-fail.example.txt "source row fail fixture" "launch runpod gpu scanner"
need_text examples/gidney-ccz-residual-pass.example.txt "gidney ccz pass fixture" "gidney-ccz-residual-certified"
need_text examples/gidney-ccz-residual-hold.example.txt "gidney ccz hold fixture" "support_status=UNKNOWN"
need_text examples/gidney-ccz-residual-fail.example.txt "gidney ccz fail fixture" "gidney_erase_capped_ccz_remainder"
need_text examples/qoffset-host-accounting-pass.example.txt "qoffset pass fixture" "qoffset-host-accounting-certified"
need_text examples/qoffset-host-accounting-closure.example.txt "qoffset closure fixture" "qoffset-host-accounting-counterexample"
need_text examples/qoffset-host-accounting-hold.example.txt "qoffset hold fixture" "restore_proof=0"
need_text examples/qoffset-host-accounting-fail.example.txt "qoffset fail fixture" "proof_status=UNPROVEN"
need_text examples/emit-bundle-support-pass.example.txt "emit bundle pass fixture" "emit-bundle-certified"
need_text examples/emit-bundle-support-closure.example.txt "emit bundle closure fixture" "emit-bundle-counterexample"
need_text examples/emit-bundle-support-hold.example.txt "emit bundle hold fixture" "complete-shared-invariant-packet"
need_text examples/emit-bundle-support-fail.example.txt "emit bundle fail fixture" "launch runpod gpu scanner"
need_text examples/construction-intake-pass.example.txt "construction intake pass fixture" "construction-intake-source-bound"
need_text examples/construction-intake-hold.example.txt "construction intake hold fixture" "construction-intake-incomplete"
need_text examples/construction-intake-fail.example.txt "construction intake fail fixture" "paper_only=yes"
need_text examples/anvil-mass-ledger-pass.example.tsv "anvil mass ledger pass fixture" "d44cad3_mass_row_new"
need_text examples/anvil-mass-ledger-raw-pass.example.tsv "anvil raw mass ledger pass fixture" "2273872"
need_text examples/anvil-mass-ledger-hold.example.tsv "anvil mass ledger hold fixture" "d44cad3_mass_row_incomplete"
need_text examples/anvil-mass-ledger-fail.example.tsv "anvil mass ledger fail fixture" "58866a2"
need_text examples/anvil-namespace-pass.example.txt "anvil namespace pass fixture" "anvil-630621-namespace-bound"
need_text examples/anvil-namespace-closure.example.txt "anvil namespace closure fixture" "anvil-630625-namespace-closure"
need_text examples/anvil-namespace-hold.example.txt "anvil namespace hold fixture" "namespace_status=MISSING"
need_text examples/anvil-namespace-fail.example.txt "anvil namespace fail fixture" "launch runpod gpu scanner"
need_text examples/anvil-exact-redundancy-pass.example.txt "anvil exact pass fixture" "anvil-2273872-exact-redundancy"
need_text examples/anvil-exact-redundancy-hold.example.txt "anvil exact hold fixture" "proof-incomplete"
need_text examples/anvil-exact-redundancy-fail.example.txt "anvil exact fail fixture" "stale-overclaim-anvil-op"
need_text examples/pebbling-theorem-pass.example.txt "pebbling theorem pass fixture" "pebbling-theorem-source-bound"
need_text examples/pebbling-theorem-hold.example.txt "pebbling theorem hold fixture" "pebbling-theorem-incomplete"
need_text examples/pebbling-theorem-fail.example.txt "pebbling theorem fail fixture" "drop_state=historical"
need_text templates/exact-skip-candidate.json "allocator unchanged" "allocator_unchanged"
need_text templates/exact-skip-candidate.json "support status" "support_status"
need_text templates/exact-skip-candidate.json "trace context family" "trace_context_family"
need_text templates/exact-skip-candidate.json "source hash" "source_hash"
need_text docs/exact-support-miner.md "exact support miner" "Exact Support Miner"
need_text docs/exact-support-miner.md "support checker" "support-check"
need_text docs/exact-support-miner.md "redsky gate" "Redsky"
need_text docs/exact-support-miner.md "pip gate" "PIP"
need_text docs/bluesky-redsky-ffg-pair-complete-toy-2026-06-28.md "ffg pair complete audit" "FFG Pair-Complete Toy"
need_text docs/bluesky-redsky-ffg-pair-complete-toy-2026-06-28.md "ffg no compute" "No candidate, no official clean run"
need_text docs/bluesky-redsky-ffg-pair-proof-gate-2026-06-28.md "ffg pair proof audit" "FFG Pair Proof Gate"
need_text docs/bluesky-redsky-ffg-pair-proof-gate-2026-06-28.md "ffg proof no compute" "no compute unlock"
need_text docs/bluesky-redsky-paper-invariant-intake-2026-06-28.md "paper invariant audit" "Paper Invariant Intake"
need_text docs/bluesky-redsky-paper-invariant-intake-2026-06-28.md "paper invariant no compute" "does not open residual"
need_text docs/bluesky-redsky-pod-inventory-ack-2026-06-28.md "pod inventory audit" "Pod Inventory ACK Gate"
need_text docs/bluesky-redsky-pod-inventory-ack-2026-06-28.md "pod inventory no compute" "does not unlock"
need_text docs/bluesky-redsky-pod-inventory-ack-2026-06-28.json "pod inventory loop packet" "process-pod-inventory-ack-five-loop"
need_text docs/bluesky-redsky-pod-inventory-ack-2026-06-28.json "pod inventory loop no compute" "inventory-ack-accepted-no-compute"
need_text docs/bluesky-redsky-source-row-routing-2026-06-28.md "source row audit" "Source Row Routing Gate"
need_text docs/bluesky-redsky-source-row-routing-2026-06-28.md "source row no compute" "no-compute"
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
need_text skills/construction-package-gate.md "construction package gate" "Construction Package Gate"
need_text skills/construction-package-gate.md "package nack" "package-nack"
need_text skills/construction-intake-gate.md "construction intake gate" "Construction Intake Gate"
need_text skills/construction-intake-gate.md "construction intake no compute" "no-compute"
need_text skills/anvil-mass-ledger-gate.md "anvil mass ledger gate" "Anvil Mass Ledger Gate"
need_text skills/anvil-mass-ledger-gate.md "anvil mass ledger no compute" "no compute"
need_text skills/anvil-namespace-gate.md "anvil namespace gate" "Anvil Namespace Gate"
need_text skills/anvil-namespace-gate.md "anvil namespace no compute" "no compute"
need_text skills/anvil-exact-redundancy-gate.md "anvil exact gate" "Anvil Exact Redundancy Gate"
need_text skills/anvil-exact-redundancy-gate.md "anvil exact no compute" "No pod"
need_text skills/pebbling-theorem-gate.md "pebbling theorem gate" "Pebbling Theorem Gate"
need_text skills/pebbling-theorem-gate.md "pebbling theorem no compute" "no-compute"
need_text skills/frontier-escape-gate.md "frontier escape gate" "Frontier Escape Gate"
need_text skills/frontier-escape-gate.md "ready for validation" "ready-for-validation"
need_text skills/support-bounded-vented-dead-carry.md "support bounded vent" "Support-Bounded Vented Dead-Carry"
need_text skills/support-bounded-vented-dead-carry.md "dead predicate" "source-hash-bound"
need_text skills/support-bounded-vented-dead-carry.md "headroom cap" "TLM_SQUARE_PEAK_CAP"
need_text .agents/skills/q1152-structural-core/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/construction-package-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/construction-intake-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/anvil-mass-ledger-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/anvil-namespace-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/anvil-exact-redundancy-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/pebbling-theorem-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/frontier-escape-gate/SKILL.md "bridge" "Codex-discoverable bridge"
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
need_text skills/paper-score-condition-discount.md "score condition discount" "Score Condition Discount"
need_text skills/paper-score-condition-discount.md "average toffoli scorer" "average-Toffoli"
need_text skills/paper-invariant-intake-gate.md "paper invariant intake skill" "Paper Invariant Intake Gate"
need_text skills/paper-invariant-intake-gate.md "paper invariant no compute" "no skill card, route, compute"
need_text .agents/skills/paper-invariant-intake-gate/SKILL.md "bridge" "Codex-discoverable bridge"
need_text skills/zero-host-accounting.md "zero host accounting" "Zero Host Accounting"
need_text skills/zero-host-accounting.md "source accounting nack" "source-accounting-nack"
need_text skills/dead-drop-fixedpoint.md "dead drop fixed point" "Dead-Drop Fixed Point"
need_text skills/dead-drop-fixedpoint.md "fixedpoint ready" "FIXEDPOINT_READY"
need_text skills/apply-overlap-ledger.md "apply overlap" "apply/codec/fold overlap"
need_text skills/nasqret-playbook.md "route slate" "route slate"
need_text skills/deepseek-pressure-test.md "pressure test" "pressure-test"
need_text skills/pip-discipline.md "pip discipline" "PIP Evidence Discipline"
need_text skills/exact-support-miner.md "exact miner" "storm-exact-miner.py"
need_text .agents/skills/exact-support-miner/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/zero-host-accounting/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/dead-drop-fixedpoint/SKILL.md "bridge" "Codex-discoverable bridge"
need_text .agents/skills/apply-overlap-ledger/SKILL.md "bridge" "Codex-discoverable bridge"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

cat >"$tmpdir/gidney-ccz-fixture.rs" <<'EOF'
const GIDNEY_ERASE_CCZ_RESIDUAL_CALLS: &[usize] = &[101, 102];
const GIDNEY_ERASE_CAPPED_CCZ_RESIDUAL_CALLS: &[usize] = &[201, 202];
const GIDNEY_ERASE_CCZ_REMAINDER_CALLS: &[usize] = &[301, 302];
const GIDNEY_ERASE_CAPPED_CCZ_REMAINDER_CALLS: &[usize] = &[401, 402, 867];
EOF
cat >"$tmpdir/gidney-ccz-mod.rs" <<'EOF'
fn defaults() {
    set_default_env("TLM_GIDNEY_SKIP_EXACT_ERASE_ALL_CCZ", "1");
    set_default_env("TLM_GIDNEY_SKIP_SMALL_RESIDUAL_DEAD", "1");
}
EOF
if ! python3 scripts/storm-gidney-ccz-residual-gate.py \
  --gidney-rs "$tmpdir/gidney-ccz-fixture.rs" \
  --point-add-mod-rs "$tmpdir/gidney-ccz-mod.rs" >"$tmpdir/gidney-ccz-source-screen.out" 2>"$tmpdir/gidney-ccz-source-screen.err"; then
  printf 'public_harness_check=fail gidney_ccz_source_screen_failed\n' >&2
  cat "$tmpdir/gidney-ccz-source-screen.err" >&2
  fail=1
elif ! grep -q 'gidney_ccz_residual_gate=pass' "$tmpdir/gidney-ccz-source-screen.out" ||
     ! grep -q 'decision=source-screen-only-no-compute' "$tmpdir/gidney-ccz-source-screen.out" ||
     ! grep -q 'required_drop=2439' "$tmpdir/gidney-ccz-source-screen.out"; then
  printf 'public_harness_check=fail gidney_ccz_source_screen_output\n' >&2
  cat "$tmpdir/gidney-ccz-source-screen.out" >&2
  fail=1
fi
if ! python3 scripts/storm-gidney-ccz-residual-gate.py \
  --gidney-rs "$tmpdir/gidney-ccz-fixture.rs" \
  --point-add-mod-rs "$tmpdir/gidney-ccz-mod.rs" \
  --packet examples/gidney-ccz-residual-pass.example.txt \
  --require-pass >"$tmpdir/gidney-ccz-pass.out" 2>"$tmpdir/gidney-ccz-pass.err"; then
  printf 'public_harness_check=fail gidney_ccz_pass_failed\n' >&2
  cat "$tmpdir/gidney-ccz-pass.err" >&2
  cat "$tmpdir/gidney-ccz-pass.out" >&2
  fail=1
elif ! grep -q 'gidney_ccz_residual_gate=pass' "$tmpdir/gidney-ccz-pass.out" ||
     ! grep -q 'decision=eligible-for-storm-compute-unlock-review-no-auto-compute' "$tmpdir/gidney-ccz-pass.out" ||
     ! grep -q 'implied_avgT_delta=-0.270390' "$tmpdir/gidney-ccz-pass.out"; then
  printf 'public_harness_check=fail gidney_ccz_pass_output\n' >&2
  cat "$tmpdir/gidney-ccz-pass.out" >&2
  fail=1
fi
if ! python3 scripts/storm-gidney-ccz-residual-gate.py \
  --gidney-rs "$tmpdir/gidney-ccz-fixture.rs" \
  --point-add-mod-rs "$tmpdir/gidney-ccz-mod.rs" \
  --packet examples/gidney-ccz-residual-hold.example.txt >"$tmpdir/gidney-ccz-hold.out" 2>"$tmpdir/gidney-ccz-hold.err"; then
  printf 'public_harness_check=fail gidney_ccz_hold_unexpected_error\n' >&2
  cat "$tmpdir/gidney-ccz-hold.err" >&2
  fail=1
elif ! grep -q 'gidney_ccz_residual_gate=hold' "$tmpdir/gidney-ccz-hold.out" ||
     ! grep -q 'support_not_certified' "$tmpdir/gidney-ccz-hold.out" ||
     ! grep -q 'phase_proof_missing' "$tmpdir/gidney-ccz-hold.out"; then
  printf 'public_harness_check=fail gidney_ccz_hold_output\n' >&2
  cat "$tmpdir/gidney-ccz-hold.out" >&2
  fail=1
fi
if python3 scripts/storm-gidney-ccz-residual-gate.py \
  --gidney-rs "$tmpdir/gidney-ccz-fixture.rs" \
  --point-add-mod-rs "$tmpdir/gidney-ccz-mod.rs" \
  --packet examples/gidney-ccz-residual-hold.example.txt \
  --require-pass >"$tmpdir/gidney-ccz-hold-strict.out" 2>"$tmpdir/gidney-ccz-hold-strict.err"; then
  printf 'public_harness_check=fail gidney_ccz_hold_strict_unexpected_pass\n' >&2
  cat "$tmpdir/gidney-ccz-hold-strict.out" >&2
  fail=1
fi
if python3 scripts/storm-gidney-ccz-residual-gate.py \
  --gidney-rs "$tmpdir/gidney-ccz-fixture.rs" \
  --point-add-mod-rs "$tmpdir/gidney-ccz-mod.rs" \
  --packet examples/gidney-ccz-residual-fail.example.txt >"$tmpdir/gidney-ccz-fail.out" 2>"$tmpdir/gidney-ccz-fail.err"; then
  printf 'public_harness_check=fail gidney_ccz_fail_unexpected_pass\n' >&2
  cat "$tmpdir/gidney-ccz-fail.out" >&2
  fail=1
elif ! grep -q 'premature_compute_request' "$tmpdir/gidney-ccz-fail.out" ||
     ! grep -q 'default_on_remainder_not_new_edge' "$tmpdir/gidney-ccz-fail.out"; then
  printf 'public_harness_check=fail gidney_ccz_fail_output\n' >&2
  cat "$tmpdir/gidney-ccz-fail.out" >&2
  fail=1
fi
sed 's/expected_avgT_delta=-0.270390071/expected_avgT_delta=-1/' \
  examples/gidney-ccz-residual-pass.example.txt >"$tmpdir/gidney-ccz-overclaim.example.txt"
if python3 scripts/storm-gidney-ccz-residual-gate.py \
  --gidney-rs "$tmpdir/gidney-ccz-fixture.rs" \
  --point-add-mod-rs "$tmpdir/gidney-ccz-mod.rs" \
  --packet "$tmpdir/gidney-ccz-overclaim.example.txt" >"$tmpdir/gidney-ccz-overclaim.out" 2>"$tmpdir/gidney-ccz-overclaim.err"; then
  printf 'public_harness_check=fail gidney_ccz_overclaim_unexpected_pass\n' >&2
  cat "$tmpdir/gidney-ccz-overclaim.out" >&2
  fail=1
elif ! grep -q 'delta_overclaims_shot_mass' "$tmpdir/gidney-ccz-overclaim.out"; then
  printf 'public_harness_check=fail gidney_ccz_overclaim_output\n' >&2
  cat "$tmpdir/gidney-ccz-overclaim.out" >&2
  fail=1
fi

if ! python3 scripts/storm-qoffset-host-accounting-gate.py \
  examples/qoffset-host-accounting-pass.example.txt \
  --require-pass >"$tmpdir/qoffset-host-accounting-pass.out" 2>"$tmpdir/qoffset-host-accounting-pass.err"; then
  printf 'public_harness_check=fail qoffset_host_accounting_pass_failed\n' >&2
  cat "$tmpdir/qoffset-host-accounting-pass.err" >&2
  cat "$tmpdir/qoffset-host-accounting-pass.out" >&2
  fail=1
elif ! grep -q 'qoffset_host_accounting_gate=pass' "$tmpdir/qoffset-host-accounting-pass.out" ||
     ! grep -q 'decision=qoffset-host-accounting-certified-no-compute-review' "$tmpdir/qoffset-host-accounting-pass.out" ||
     ! grep -q 'counted_q1152=true' "$tmpdir/qoffset-host-accounting-pass.out"; then
  printf 'public_harness_check=fail qoffset_host_accounting_pass_output\n' >&2
  cat "$tmpdir/qoffset-host-accounting-pass.out" >&2
  fail=1
fi
if ! python3 scripts/storm-qoffset-host-accounting-gate.py \
  examples/qoffset-host-accounting-closure.example.txt \
  --require-pass >"$tmpdir/qoffset-host-accounting-closure.out" 2>"$tmpdir/qoffset-host-accounting-closure.err"; then
  printf 'public_harness_check=fail qoffset_host_accounting_closure_failed\n' >&2
  cat "$tmpdir/qoffset-host-accounting-closure.err" >&2
  cat "$tmpdir/qoffset-host-accounting-closure.out" >&2
  fail=1
elif ! grep -q 'qoffset_host_accounting_gate=pass' "$tmpdir/qoffset-host-accounting-closure.out" ||
     ! grep -q 'decision=qoffset-host-accounting-counterexample-closed-no-compute' "$tmpdir/qoffset-host-accounting-closure.out" ||
     ! grep -q 'closure=True' "$tmpdir/qoffset-host-accounting-closure.out"; then
  printf 'public_harness_check=fail qoffset_host_accounting_closure_output\n' >&2
  cat "$tmpdir/qoffset-host-accounting-closure.out" >&2
  fail=1
fi
if ! python3 scripts/storm-qoffset-host-accounting-gate.py \
  examples/qoffset-host-accounting-hold.example.txt >"$tmpdir/qoffset-host-accounting-hold.out" 2>"$tmpdir/qoffset-host-accounting-hold.err"; then
  printf 'public_harness_check=fail qoffset_host_accounting_hold_unexpected_error\n' >&2
  cat "$tmpdir/qoffset-host-accounting-hold.err" >&2
  fail=1
elif ! grep -q 'qoffset_host_accounting_gate=hold' "$tmpdir/qoffset-host-accounting-hold.out" ||
     ! grep -q 'missing_candidate_hash' "$tmpdir/qoffset-host-accounting-hold.out" ||
     ! grep -q 'restore_proof_missing' "$tmpdir/qoffset-host-accounting-hold.out"; then
  printf 'public_harness_check=fail qoffset_host_accounting_hold_output\n' >&2
  cat "$tmpdir/qoffset-host-accounting-hold.out" >&2
  fail=1
fi
if python3 scripts/storm-qoffset-host-accounting-gate.py \
  examples/qoffset-host-accounting-hold.example.txt \
  --require-pass >"$tmpdir/qoffset-host-accounting-hold-strict.out" 2>"$tmpdir/qoffset-host-accounting-hold-strict.err"; then
  printf 'public_harness_check=fail qoffset_host_accounting_hold_strict_unexpected_pass\n' >&2
  cat "$tmpdir/qoffset-host-accounting-hold-strict.out" >&2
  fail=1
fi
if python3 scripts/storm-qoffset-host-accounting-gate.py \
  examples/qoffset-host-accounting-fail.example.txt >"$tmpdir/qoffset-host-accounting-fail.out" 2>"$tmpdir/qoffset-host-accounting-fail.err"; then
  printf 'public_harness_check=fail qoffset_host_accounting_fail_unexpected_pass\n' >&2
  cat "$tmpdir/qoffset-host-accounting-fail.out" >&2
  fail=1
elif ! grep -q 'qoffset_host_accounting_gate=fail' "$tmpdir/qoffset-host-accounting-fail.out" ||
     ! grep -q 'proof_unknown_close_as_nack' "$tmpdir/qoffset-host-accounting-fail.out" ||
     ! grep -q 'premature_compute_or_residual_request' "$tmpdir/qoffset-host-accounting-fail.out"; then
  printf 'public_harness_check=fail qoffset_host_accounting_fail_output\n' >&2
  cat "$tmpdir/qoffset-host-accounting-fail.out" >&2
  fail=1
fi

if ! python3 scripts/storm-emit-bundle-support-gate.py \
  examples/emit-bundle-support-pass.example.txt \
  --require-pass >"$tmpdir/emit-bundle-support-pass.out" 2>"$tmpdir/emit-bundle-support-pass.err"; then
  printf 'public_harness_check=fail emit_bundle_support_pass_failed\n' >&2
  cat "$tmpdir/emit-bundle-support-pass.err" >&2
  cat "$tmpdir/emit-bundle-support-pass.out" >&2
  fail=1
elif ! grep -q 'emit_bundle_support_gate=pass' "$tmpdir/emit-bundle-support-pass.out" ||
     ! grep -q 'decision=emit-bundle-certified-no-compute-review' "$tmpdir/emit-bundle-support-pass.out" ||
     ! grep -q 'required_drop=2439' "$tmpdir/emit-bundle-support-pass.out"; then
  printf 'public_harness_check=fail emit_bundle_support_pass_output\n' >&2
  cat "$tmpdir/emit-bundle-support-pass.out" >&2
  fail=1
fi
if ! python3 scripts/storm-emit-bundle-support-gate.py \
  examples/emit-bundle-support-closure.example.txt \
  --require-pass >"$tmpdir/emit-bundle-support-closure.out" 2>"$tmpdir/emit-bundle-support-closure.err"; then
  printf 'public_harness_check=fail emit_bundle_support_closure_failed\n' >&2
  cat "$tmpdir/emit-bundle-support-closure.err" >&2
  cat "$tmpdir/emit-bundle-support-closure.out" >&2
  fail=1
elif ! grep -q 'emit_bundle_support_gate=pass' "$tmpdir/emit-bundle-support-closure.out" ||
     ! grep -q 'decision=emit-bundle-counterexample-closed-no-compute' "$tmpdir/emit-bundle-support-closure.out" ||
     ! grep -q 'closure=True' "$tmpdir/emit-bundle-support-closure.out"; then
  printf 'public_harness_check=fail emit_bundle_support_closure_output\n' >&2
  cat "$tmpdir/emit-bundle-support-closure.out" >&2
  fail=1
fi
if ! python3 scripts/storm-emit-bundle-support-gate.py \
  examples/emit-bundle-support-hold.example.txt >"$tmpdir/emit-bundle-support-hold.out" 2>"$tmpdir/emit-bundle-support-hold.err"; then
  printf 'public_harness_check=fail emit_bundle_support_hold_unexpected_error\n' >&2
  cat "$tmpdir/emit-bundle-support-hold.err" >&2
  fail=1
elif ! grep -q 'emit_bundle_support_gate=hold' "$tmpdir/emit-bundle-support-hold.out" ||
     ! grep -q 'missing_candidate_hash' "$tmpdir/emit-bundle-support-hold.out" ||
     ! grep -q 'restore_proof_missing' "$tmpdir/emit-bundle-support-hold.out"; then
  printf 'public_harness_check=fail emit_bundle_support_hold_output\n' >&2
  cat "$tmpdir/emit-bundle-support-hold.out" >&2
  fail=1
fi
if python3 scripts/storm-emit-bundle-support-gate.py \
  examples/emit-bundle-support-hold.example.txt \
  --require-pass >"$tmpdir/emit-bundle-support-hold-strict.out" 2>"$tmpdir/emit-bundle-support-hold-strict.err"; then
  printf 'public_harness_check=fail emit_bundle_support_hold_strict_unexpected_pass\n' >&2
  cat "$tmpdir/emit-bundle-support-hold-strict.out" >&2
  fail=1
fi
if python3 scripts/storm-emit-bundle-support-gate.py \
  examples/emit-bundle-support-fail.example.txt >"$tmpdir/emit-bundle-support-fail.out" 2>"$tmpdir/emit-bundle-support-fail.err"; then
  printf 'public_harness_check=fail emit_bundle_support_fail_unexpected_pass\n' >&2
  cat "$tmpdir/emit-bundle-support-fail.out" >&2
  fail=1
elif ! grep -q 'emit_bundle_support_gate=fail' "$tmpdir/emit-bundle-support-fail.out" ||
     ! grep -q 'proof_unknown_close_as_nack' "$tmpdir/emit-bundle-support-fail.out" ||
     ! grep -q 'bundle_mass_below_rounding_bar' "$tmpdir/emit-bundle-support-fail.out" ||
     ! grep -q 'premature_compute_or_residual_request' "$tmpdir/emit-bundle-support-fail.out"; then
  printf 'public_harness_check=fail emit_bundle_support_fail_output\n' >&2
  cat "$tmpdir/emit-bundle-support-fail.out" >&2
  fail=1
fi

if ! python3 scripts/storm-construction-intake-gate.py \
  examples/construction-intake-pass.example.txt \
  --require-pass >"$tmpdir/construction-intake-pass.out" 2>"$tmpdir/construction-intake-pass.err"; then
  printf 'public_harness_check=fail construction_intake_pass_failed\n' >&2
  cat "$tmpdir/construction-intake-pass.err" >&2
  cat "$tmpdir/construction-intake-pass.out" >&2
  fail=1
elif ! grep -q 'construction_intake_gate=pass' "$tmpdir/construction-intake-pass.out" ||
     ! grep -q 'decision=construction-intake-review-no-compute' "$tmpdir/construction-intake-pass.out" ||
     ! grep -q 'count_edge=true' "$tmpdir/construction-intake-pass.out"; then
  printf 'public_harness_check=fail construction_intake_pass_output\n' >&2
  cat "$tmpdir/construction-intake-pass.out" >&2
  fail=1
fi
if ! python3 scripts/storm-construction-intake-gate.py \
  examples/construction-intake-hold.example.txt >"$tmpdir/construction-intake-hold.out" 2>"$tmpdir/construction-intake-hold.err"; then
  printf 'public_harness_check=fail construction_intake_hold_unexpected_error\n' >&2
  cat "$tmpdir/construction-intake-hold.err" >&2
  fail=1
elif ! grep -q 'construction_intake_gate=hold' "$tmpdir/construction-intake-hold.out" ||
     ! grep -q 'missing_candidate_hash' "$tmpdir/construction-intake-hold.out" ||
     ! grep -q 'missing_phase_obligation' "$tmpdir/construction-intake-hold.out"; then
  printf 'public_harness_check=fail construction_intake_hold_output\n' >&2
  cat "$tmpdir/construction-intake-hold.out" >&2
  fail=1
fi
if python3 scripts/storm-construction-intake-gate.py \
  examples/construction-intake-hold.example.txt \
  --require-pass >"$tmpdir/construction-intake-hold-strict.out" 2>"$tmpdir/construction-intake-hold-strict.err"; then
  printf 'public_harness_check=fail construction_intake_hold_strict_unexpected_pass\n' >&2
  cat "$tmpdir/construction-intake-hold-strict.out" >&2
  fail=1
fi
if python3 scripts/storm-construction-intake-gate.py \
  examples/construction-intake-fail.example.txt >"$tmpdir/construction-intake-fail.out" 2>"$tmpdir/construction-intake-fail.err"; then
  printf 'public_harness_check=fail construction_intake_fail_unexpected_pass\n' >&2
  cat "$tmpdir/construction-intake-fail.out" >&2
  fail=1
elif ! grep -q 'construction_intake_gate=fail' "$tmpdir/construction-intake-fail.out" ||
     ! grep -q 'paper_only_or_scout_only' "$tmpdir/construction-intake-fail.out" ||
     ! grep -q 'premature_compute_or_residual_request' "$tmpdir/construction-intake-fail.out" ||
     ! grep -q 'nonpositive_score_edge' "$tmpdir/construction-intake-fail.out"; then
  printf 'public_harness_check=fail construction_intake_fail_output\n' >&2
  cat "$tmpdir/construction-intake-fail.out" >&2
  fail=1
fi

if ! python3 scripts/storm-anvil-mass-ledger-gate.py \
  examples/anvil-mass-ledger-pass.example.tsv \
  --require-pass >"$tmpdir/anvil-mass-ledger-pass.out" 2>"$tmpdir/anvil-mass-ledger-pass.err"; then
  printf 'public_harness_check=fail anvil_mass_ledger_pass_failed\n' >&2
  cat "$tmpdir/anvil-mass-ledger-pass.err" >&2
  cat "$tmpdir/anvil-mass-ledger-pass.out" >&2
  fail=1
elif ! grep -q 'anvil_mass_ledger_gate=pass' "$tmpdir/anvil-mass-ledger-pass.out" ||
     ! grep -q 'decision=mass-ledger-ready-no-compute' "$tmpdir/anvil-mass-ledger-pass.out" ||
     ! grep -q 'positive_rows=1' "$tmpdir/anvil-mass-ledger-pass.out" ||
     ! grep -q 'closure_rows=1' "$tmpdir/anvil-mass-ledger-pass.out"; then
  printf 'public_harness_check=fail anvil_mass_ledger_pass_output\n' >&2
  cat "$tmpdir/anvil-mass-ledger-pass.out" >&2
  fail=1
fi
if ! python3 scripts/storm-anvil-mass-ledger-gate.py \
  examples/anvil-mass-ledger-raw-pass.example.tsv \
  --require-pass >"$tmpdir/anvil-mass-ledger-raw-pass.out" 2>"$tmpdir/anvil-mass-ledger-raw-pass.err"; then
  printf 'public_harness_check=fail anvil_mass_ledger_raw_pass_failed\n' >&2
  cat "$tmpdir/anvil-mass-ledger-raw-pass.err" >&2
  cat "$tmpdir/anvil-mass-ledger-raw-pass.out" >&2
  fail=1
elif ! grep -q 'anvil_mass_ledger_gate=pass' "$tmpdir/anvil-mass-ledger-raw-pass.out" ||
     ! grep -q 'schema=raw' "$tmpdir/anvil-mass-ledger-raw-pass.out" ||
     ! grep -q 'decision=raw-mass-ledger-ready-no-compute' "$tmpdir/anvil-mass-ledger-raw-pass.out" ||
     ! grep -q 'over_bar_rows=3' "$tmpdir/anvil-mass-ledger-raw-pass.out"; then
  printf 'public_harness_check=fail anvil_mass_ledger_raw_pass_output\n' >&2
  cat "$tmpdir/anvil-mass-ledger-raw-pass.out" >&2
  fail=1
fi
if ! python3 scripts/storm-anvil-mass-ledger-gate.py \
  examples/anvil-mass-ledger-hold.example.tsv >"$tmpdir/anvil-mass-ledger-hold.out" 2>"$tmpdir/anvil-mass-ledger-hold.err"; then
  printf 'public_harness_check=fail anvil_mass_ledger_hold_unexpected_error\n' >&2
  cat "$tmpdir/anvil-mass-ledger-hold.err" >&2
  fail=1
elif ! grep -q 'anvil_mass_ledger_gate=hold' "$tmpdir/anvil-mass-ledger-hold.out" ||
     ! grep -q 'missing_required_support' "$tmpdir/anvil-mass-ledger-hold.out" ||
     ! grep -q 'missing_known_counterexample' "$tmpdir/anvil-mass-ledger-hold.out"; then
  printf 'public_harness_check=fail anvil_mass_ledger_hold_output\n' >&2
  cat "$tmpdir/anvil-mass-ledger-hold.out" >&2
  fail=1
fi
if python3 scripts/storm-anvil-mass-ledger-gate.py \
  examples/anvil-mass-ledger-hold.example.tsv \
  --require-pass >"$tmpdir/anvil-mass-ledger-hold-strict.out" 2>"$tmpdir/anvil-mass-ledger-hold-strict.err"; then
  printf 'public_harness_check=fail anvil_mass_ledger_hold_strict_unexpected_pass\n' >&2
  cat "$tmpdir/anvil-mass-ledger-hold-strict.out" >&2
  fail=1
fi
if python3 scripts/storm-anvil-mass-ledger-gate.py \
  examples/anvil-mass-ledger-fail.example.tsv >"$tmpdir/anvil-mass-ledger-fail.out" 2>"$tmpdir/anvil-mass-ledger-fail.err"; then
  printf 'public_harness_check=fail anvil_mass_ledger_fail_unexpected_pass\n' >&2
  cat "$tmpdir/anvil-mass-ledger-fail.out" >&2
  fail=1
elif ! grep -q 'anvil_mass_ledger_gate=fail' "$tmpdir/anvil-mass-ledger-fail.out" ||
     ! grep -q 'missing_no_submit_ack' "$tmpdir/anvil-mass-ledger-fail.out" ||
     ! grep -q 'stale_source_base' "$tmpdir/anvil-mass-ledger-fail.out" ||
     ! grep -q 'score_edge_mismatch' "$tmpdir/anvil-mass-ledger-fail.out" ||
     ! grep -q 'nonpositive_score_edge_without_nack' "$tmpdir/anvil-mass-ledger-fail.out"; then
  printf 'public_harness_check=fail anvil_mass_ledger_fail_output\n' >&2
  cat "$tmpdir/anvil-mass-ledger-fail.out" >&2
  fail=1
fi

if ! python3 scripts/storm-anvil-namespace-gate.py \
  examples/anvil-namespace-pass.example.txt \
  --require-pass >"$tmpdir/anvil-namespace-pass.out" 2>"$tmpdir/anvil-namespace-pass.err"; then
  printf 'public_harness_check=fail anvil_namespace_pass_failed\n' >&2
  cat "$tmpdir/anvil-namespace-pass.err" >&2
  cat "$tmpdir/anvil-namespace-pass.out" >&2
  fail=1
elif ! grep -q 'anvil_namespace_gate=pass' "$tmpdir/anvil-namespace-pass.out" ||
     ! grep -q 'decision=anvil-row-source-bound-ready-no-compute' "$tmpdir/anvil-namespace-pass.out" ||
     ! grep -q 'packet=true' "$tmpdir/anvil-namespace-pass.out"; then
  printf 'public_harness_check=fail anvil_namespace_pass_output\n' >&2
  cat "$tmpdir/anvil-namespace-pass.out" >&2
  fail=1
fi
if ! python3 scripts/storm-anvil-namespace-gate.py \
  examples/anvil-namespace-closure.example.txt \
  --require-pass >"$tmpdir/anvil-namespace-closure.out" 2>"$tmpdir/anvil-namespace-closure.err"; then
  printf 'public_harness_check=fail anvil_namespace_closure_failed\n' >&2
  cat "$tmpdir/anvil-namespace-closure.err" >&2
  cat "$tmpdir/anvil-namespace-closure.out" >&2
  fail=1
elif ! grep -q 'anvil_namespace_gate=pass' "$tmpdir/anvil-namespace-closure.out" ||
     ! grep -q 'decision=anvil-row-closed-advance-next-no-compute' "$tmpdir/anvil-namespace-closure.out" ||
     ! grep -q 'closure=true' "$tmpdir/anvil-namespace-closure.out"; then
  printf 'public_harness_check=fail anvil_namespace_closure_output\n' >&2
  cat "$tmpdir/anvil-namespace-closure.out" >&2
  fail=1
fi
if ! python3 scripts/storm-anvil-namespace-gate.py \
  examples/anvil-namespace-hold.example.txt >"$tmpdir/anvil-namespace-hold.out" 2>"$tmpdir/anvil-namespace-hold.err"; then
  printf 'public_harness_check=fail anvil_namespace_hold_unexpected_error\n' >&2
  cat "$tmpdir/anvil-namespace-hold.err" >&2
  fail=1
elif ! grep -q 'anvil_namespace_gate=hold' "$tmpdir/anvil-namespace-hold.out" ||
     ! grep -q 'namespace_missing' "$tmpdir/anvil-namespace-hold.out" ||
     ! grep -q 'source_binding_unbound' "$tmpdir/anvil-namespace-hold.out"; then
  printf 'public_harness_check=fail anvil_namespace_hold_output\n' >&2
  cat "$tmpdir/anvil-namespace-hold.out" >&2
  fail=1
fi
if python3 scripts/storm-anvil-namespace-gate.py \
  examples/anvil-namespace-hold.example.txt \
  --require-pass >"$tmpdir/anvil-namespace-hold-strict.out" 2>"$tmpdir/anvil-namespace-hold-strict.err"; then
  printf 'public_harness_check=fail anvil_namespace_hold_strict_unexpected_pass\n' >&2
  cat "$tmpdir/anvil-namespace-hold-strict.out" >&2
  fail=1
fi
if python3 scripts/storm-anvil-namespace-gate.py \
  examples/anvil-namespace-fail.example.txt >"$tmpdir/anvil-namespace-fail.out" 2>"$tmpdir/anvil-namespace-fail.err"; then
  printf 'public_harness_check=fail anvil_namespace_fail_unexpected_pass\n' >&2
  cat "$tmpdir/anvil-namespace-fail.out" >&2
  fail=1
elif ! grep -q 'anvil_namespace_gate=fail' "$tmpdir/anvil-namespace-fail.out" ||
     ! grep -q 'premature_compute_or_residual_request' "$tmpdir/anvil-namespace-fail.out" ||
     ! grep -q 'stale_source_base' "$tmpdir/anvil-namespace-fail.out"; then
  printf 'public_harness_check=fail anvil_namespace_fail_output\n' >&2
  cat "$tmpdir/anvil-namespace-fail.out" >&2
  fail=1
fi

if ! python3 scripts/storm-anvil-exact-redundancy-gate.py \
  examples/anvil-exact-redundancy-pass.example.txt \
  --require-pass >"$tmpdir/anvil-exact-pass.out" 2>"$tmpdir/anvil-exact-pass.err"; then
  printf 'public_harness_check=fail anvil_exact_pass_failed\n' >&2
  cat "$tmpdir/anvil-exact-pass.err" >&2
  cat "$tmpdir/anvil-exact-pass.out" >&2
  fail=1
elif ! grep -q 'anvil_exact_redundancy_gate=pass' "$tmpdir/anvil-exact-pass.out" ||
     ! grep -q 'decision=anvil-exact-redundancy-review-no-compute' "$tmpdir/anvil-exact-pass.out" ||
     ! grep -q 'certified=true' "$tmpdir/anvil-exact-pass.out"; then
  printf 'public_harness_check=fail anvil_exact_pass_output\n' >&2
  cat "$tmpdir/anvil-exact-pass.out" >&2
  fail=1
fi
if ! python3 scripts/storm-anvil-exact-redundancy-gate.py \
  examples/anvil-exact-redundancy-hold.example.txt >"$tmpdir/anvil-exact-hold.out" 2>"$tmpdir/anvil-exact-hold.err"; then
  printf 'public_harness_check=fail anvil_exact_hold_unexpected_error\n' >&2
  cat "$tmpdir/anvil-exact-hold.err" >&2
  fail=1
elif ! grep -q 'anvil_exact_redundancy_gate=hold' "$tmpdir/anvil-exact-hold.out" ||
     ! grep -q 'phase_proof_missing' "$tmpdir/anvil-exact-hold.out" ||
     ! grep -q 'ancilla_proof_missing' "$tmpdir/anvil-exact-hold.out"; then
  printf 'public_harness_check=fail anvil_exact_hold_output\n' >&2
  cat "$tmpdir/anvil-exact-hold.out" >&2
  fail=1
fi
if python3 scripts/storm-anvil-exact-redundancy-gate.py \
  examples/anvil-exact-redundancy-hold.example.txt \
  --require-pass >"$tmpdir/anvil-exact-hold-strict.out" 2>"$tmpdir/anvil-exact-hold-strict.err"; then
  printf 'public_harness_check=fail anvil_exact_hold_strict_unexpected_pass\n' >&2
  cat "$tmpdir/anvil-exact-hold-strict.out" >&2
  fail=1
fi
if python3 scripts/storm-anvil-exact-redundancy-gate.py \
  examples/anvil-exact-redundancy-fail.example.txt >"$tmpdir/anvil-exact-fail.out" 2>"$tmpdir/anvil-exact-fail.err"; then
  printf 'public_harness_check=fail anvil_exact_fail_unexpected_pass\n' >&2
  cat "$tmpdir/anvil-exact-fail.out" >&2
  fail=1
elif ! grep -q 'anvil_exact_redundancy_gate=fail' "$tmpdir/anvil-exact-fail.out" ||
     ! grep -q 'premature_compute_or_residual_request' "$tmpdir/anvil-exact-fail.out" ||
     ! grep -q 'stale_source_base' "$tmpdir/anvil-exact-fail.out" ||
     ! grep -q 'q_cut_claim_not_single_op_redundancy' "$tmpdir/anvil-exact-fail.out"; then
  printf 'public_harness_check=fail anvil_exact_fail_output\n' >&2
  cat "$tmpdir/anvil-exact-fail.out" >&2
  fail=1
fi

if ! python3 scripts/storm-pebbling-theorem-gate.py \
  examples/pebbling-theorem-pass.example.txt \
  --require-pass >"$tmpdir/pebbling-theorem-pass.out" 2>"$tmpdir/pebbling-theorem-pass.err"; then
  printf 'public_harness_check=fail pebbling_theorem_pass_failed\n' >&2
  cat "$tmpdir/pebbling-theorem-pass.err" >&2
  cat "$tmpdir/pebbling-theorem-pass.out" >&2
  fail=1
elif ! grep -q 'pebbling_theorem_gate=pass' "$tmpdir/pebbling-theorem-pass.out" ||
     ! grep -q 'decision=pebbling-theorem-review-no-compute' "$tmpdir/pebbling-theorem-pass.out" ||
     ! grep -q 'score_edge_ok=true' "$tmpdir/pebbling-theorem-pass.out" ||
     ! grep -q 'restore_proof=true' "$tmpdir/pebbling-theorem-pass.out"; then
  printf 'public_harness_check=fail pebbling_theorem_pass_output\n' >&2
  cat "$tmpdir/pebbling-theorem-pass.out" >&2
  fail=1
fi
if ! python3 scripts/storm-pebbling-theorem-gate.py \
  examples/pebbling-theorem-hold.example.txt >"$tmpdir/pebbling-theorem-hold.out" 2>"$tmpdir/pebbling-theorem-hold.err"; then
  printf 'public_harness_check=fail pebbling_theorem_hold_unexpected_error\n' >&2
  cat "$tmpdir/pebbling-theorem-hold.err" >&2
  fail=1
elif ! grep -q 'pebbling_theorem_gate=hold' "$tmpdir/pebbling-theorem-hold.out" ||
     ! grep -q 'missing_candidate_hash' "$tmpdir/pebbling-theorem-hold.out" ||
     ! grep -q 'missing_consumers' "$tmpdir/pebbling-theorem-hold.out" ||
     ! grep -q 'missing_exact_support_certified' "$tmpdir/pebbling-theorem-hold.out"; then
  printf 'public_harness_check=fail pebbling_theorem_hold_output\n' >&2
  cat "$tmpdir/pebbling-theorem-hold.out" >&2
  fail=1
fi
if python3 scripts/storm-pebbling-theorem-gate.py \
  examples/pebbling-theorem-hold.example.txt \
  --require-pass >"$tmpdir/pebbling-theorem-hold-strict.out" 2>"$tmpdir/pebbling-theorem-hold-strict.err"; then
  printf 'public_harness_check=fail pebbling_theorem_hold_strict_unexpected_pass\n' >&2
  cat "$tmpdir/pebbling-theorem-hold-strict.out" >&2
  fail=1
fi
if python3 scripts/storm-pebbling-theorem-gate.py \
  examples/pebbling-theorem-fail.example.txt >"$tmpdir/pebbling-theorem-fail.out" 2>"$tmpdir/pebbling-theorem-fail.err"; then
  printf 'public_harness_check=fail pebbling_theorem_fail_unexpected_pass\n' >&2
  cat "$tmpdir/pebbling-theorem-fail.out" >&2
  fail=1
elif ! grep -q 'pebbling_theorem_gate=fail' "$tmpdir/pebbling-theorem-fail.out" ||
     ! grep -q 'support_counterexample' "$tmpdir/pebbling-theorem-fail.out" ||
     ! grep -q 'nonpositive_score_edge' "$tmpdir/pebbling-theorem-fail.out" ||
     ! grep -q 'stale_drop_state' "$tmpdir/pebbling-theorem-fail.out" ||
     ! grep -q 'premature_compute_or_residual_request' "$tmpdir/pebbling-theorem-fail.out"; then
  printf 'public_harness_check=fail pebbling_theorem_fail_output\n' >&2
  cat "$tmpdir/pebbling-theorem-fail.out" >&2
  fail=1
fi

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

cat >"$tmpdir/dead-drop-bad.tsv" <<'EOF'
route_id	stream_hash	pre_drop_ops_hash	candidate_indices_sha256	source_hash	support_status	support_certificate	dynamic_deadness	sampled_shots	rebuilt_after_edit	residual_probe_rebuilt	fixed_point	eval_classical	eval_phase	eval_ancilla
salted4-dynamic	stream-a	pre-a	idx-a	source-a	UNKNOWN	cert-a	yes	36096	no	no	no	0	0	0
stale-residual	stream-b	pre-b	idx-b	source-b	CERTIFIED	cert-b	no	0	yes	no	yes	0	0	0
no-fixedpoint	stream-c	pre-c	idx-c	source-c	CERTIFIED	cert-c	no	0	yes	yes	no	0	0	0
dirty-eval	stream-d	pre-d	idx-d	source-d	CERTIFIED	cert-d	no	0	yes	yes	yes	1	0	0
EOF
if ! python3 scripts/storm-dead-drop-fixedpoint-gate.py \
  --packets "$tmpdir/dead-drop-bad.tsv" \
  --summary-out "$tmpdir/dead-drop-bad-summary.tsv" >"$tmpdir/dead-drop-bad.out" 2>"$tmpdir/dead-drop-bad.err"; then
  printf 'public_harness_check=fail dead_drop_bad_failed\n' >&2
  cat "$tmpdir/dead-drop-bad.err" >&2
  fail=1
elif ! grep -q 'dead_drop_fixedpoint_gate=pass' "$tmpdir/dead-drop-bad.out" ||
     ! grep -q 'ready=0' "$tmpdir/dead-drop-bad.out" ||
     ! grep -q 'dynamic_only=1' "$tmpdir/dead-drop-bad.out" ||
     ! grep -q 'stale_residual=1' "$tmpdir/dead-drop-bad.out" ||
     ! grep -q 'no_fixedpoint=1' "$tmpdir/dead-drop-bad.out" ||
     ! grep -q 'dirty_eval=1' "$tmpdir/dead-drop-bad.out" ||
     ! grep -q 'decision=fixedpoint-required' "$tmpdir/dead-drop-bad.out" ||
     ! grep -q $'salted4-dynamic\tDYNAMIC_ONLY\tsampled_deadness_without_source_invariant' "$tmpdir/dead-drop-bad-summary.tsv" ||
     ! grep -q $'stale-residual\tSTALE_RESIDUAL\tresidual_probe_not_rebuilt_from_candidate_stream' "$tmpdir/dead-drop-bad-summary.tsv"; then
  printf 'public_harness_check=fail dead_drop_bad_output\n' >&2
  cat "$tmpdir/dead-drop-bad.out" >&2
  cat "$tmpdir/dead-drop-bad-summary.tsv" >&2
  fail=1
fi

cat >"$tmpdir/dead-drop-ready.tsv" <<'EOF'
route_id	stream_hash	pre_drop_ops_hash	candidate_indices_sha256	source_hash	support_status	support_certificate	dynamic_deadness	sampled_shots	rebuilt_after_edit	residual_probe_rebuilt	fixed_point	eval_classical	eval_phase	eval_ancilla
ready-demo	stream-ready	pre-ready	idx-ready	source-ready	CERTIFIED	cert-ready	no	0	yes	yes	yes	0	0	0
EOF
if ! python3 scripts/storm-dead-drop-fixedpoint-gate.py \
  --packets "$tmpdir/dead-drop-ready.tsv" >"$tmpdir/dead-drop-ready.out" 2>"$tmpdir/dead-drop-ready.err"; then
  printf 'public_harness_check=fail dead_drop_ready_failed\n' >&2
  cat "$tmpdir/dead-drop-ready.err" >&2
  fail=1
elif ! grep -q 'ready=1' "$tmpdir/dead-drop-ready.out" ||
     ! grep -q 'decision=ready-for-validation' "$tmpdir/dead-drop-ready.out"; then
  printf 'public_harness_check=fail dead_drop_ready_output\n' >&2
  cat "$tmpdir/dead-drop-ready.out" >&2
  fail=1
fi

cat >"$tmpdir/mailbox-action-tail.md" <<'EOF'
## 2026-06-27T00:00:00Z from: Worker-A - bounded check

ACK Worker-A NACK demo-lane skill=redsky file=demo.rs next=needs-operator no_submit_ack=yes
Storm-Codex: confirm whether I should produce one fresh trace or hold.

## 2026-06-27T00:01:00Z from: Worker-B - status

Boss Storm: want me to stop the idle proof host?

## 2026-06-27T00:02:00Z from: Claude-Kiln - status

TL;DR: first bounded check is done. Awaiting Storm-Codex's call on whether I should produce a fresh wall-owner trace now or hold.
EOF
if ! python3 scripts/storm-mailbox-action-scan.py \
  --input "$tmpdir/mailbox-action-tail.md" >"$tmpdir/mailbox-action.out" 2>"$tmpdir/mailbox-action.err"; then
  printf 'public_harness_check=fail mailbox_action_scan_failed\n' >&2
  cat "$tmpdir/mailbox-action.err" >&2
  fail=1
elif ! grep -q 'mailbox_action_scan=review count=3' "$tmpdir/mailbox-action.out"; then
  printf 'public_harness_check=fail mailbox_action_scan_counts\n' >&2
  cat "$tmpdir/mailbox-action.out" >&2
  fail=1
fi
if ! printf 'Storm-Codex: should I produce one fresh trace?\n' | \
  python3 scripts/storm-mailbox-action-scan.py - >"$tmpdir/mailbox-action-stdin.out" 2>"$tmpdir/mailbox-action-stdin.err"; then
  printf 'public_harness_check=fail mailbox_action_scan_stdin_failed\n' >&2
  cat "$tmpdir/mailbox-action-stdin.err" >&2
  fail=1
elif ! grep -q 'mailbox_action_scan=review count=1' "$tmpdir/mailbox-action-stdin.out"; then
  printf 'public_harness_check=fail mailbox_action_scan_stdin_counts\n' >&2
  cat "$tmpdir/mailbox-action-stdin.out" >&2
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
  'rank	count	kind	file	line	family	source_hash' \
  '1	100	CCX	src/point_add/trailmix_ludicrous/gidney.rs	1297	gidney_thread_sum	d44cad3-current' \
  '2	7	CCX	src/point_add/trailmix_ludicrous/codec.rs	561	unclassified	d44cad3-current' \
  '3	5	CCX	src/point_add/trailmix_ludicrous/fused.rs	987	unclassified	d44cad3-current' \
  > "$tmpdir/source-summary-artifacts.tsv"
if ! python3 scripts/storm-exact-miner.py trace-facts \
  --input "$tmpdir/source-summary-artifacts.tsv" \
  --frontier fixture-frontier/demo-source \
  --source-base public-demo-source \
  --stream-hash source-summary-artifacts-demo \
  --out "$tmpdir/source-summary-artifacts-facts.jsonl" >"$tmpdir/source-summary-artifacts-trace.out" 2>"$tmpdir/source-summary-artifacts-trace.err"; then
  printf 'public_harness_check=fail exact_miner_source_summary_artifacts_trace_failed\n' >&2
  cat "$tmpdir/source-summary-artifacts-trace.err" >&2
  fail=1
elif ! grep -q '"trace_context_family":"gidney_thread_sum"' "$tmpdir/source-summary-artifacts-facts.jsonl"; then
  printf 'public_harness_check=fail exact_miner_source_summary_family_lost\n' >&2
  cat "$tmpdir/source-summary-artifacts-facts.jsonl" >&2
  fail=1
elif ! python3 scripts/storm-exact-miner.py support-check \
  --facts "$tmpdir/source-summary-artifacts-facts.jsonl" \
  --out "$tmpdir/source-summary-artifacts-support.jsonl" >"$tmpdir/source-summary-artifacts-support.out" 2>"$tmpdir/source-summary-artifacts-support.err"; then
  printf 'public_harness_check=fail exact_miner_source_summary_artifacts_support_failed\n' >&2
  cat "$tmpdir/source-summary-artifacts-support.err" >&2
  fail=1
elif ! grep -q 'certified=0 unknown=0 counterexample=3' "$tmpdir/source-summary-artifacts-support.out" \
  || ! grep -q 'codec_step0_source_map_mismatch' "$tmpdir/source-summary-artifacts-support.jsonl" \
  || ! grep -q 'source_context_not_op_site' "$tmpdir/source-summary-artifacts-support.jsonl"; then
  printf 'public_harness_check=fail exact_miner_source_summary_artifacts_counts\n' >&2
  cat "$tmpdir/source-summary-artifacts-support.out" >&2
  cat "$tmpdir/source-summary-artifacts-support.jsonl" >&2
  fail=1
elif ! python3 scripts/storm-exact-miner.py mine \
  --facts "$tmpdir/source-summary-artifacts-support.jsonl" \
  --include-unknown-sites \
  --max-unknown-sites 0 \
  --out "$tmpdir/source-summary-artifacts-candidates.jsonl" >"$tmpdir/source-summary-artifacts-mine.out" 2>"$tmpdir/source-summary-artifacts-mine.err"; then
  printf 'public_harness_check=fail exact_miner_source_summary_artifacts_mine_failed\n' >&2
  cat "$tmpdir/source-summary-artifacts-mine.err" >&2
  fail=1
elif ! python3 scripts/storm-exact-miner.py prove \
  --candidates "$tmpdir/source-summary-artifacts-candidates.jsonl" \
  --out "$tmpdir/source-summary-artifacts-proofs.jsonl" >"$tmpdir/source-summary-artifacts-prove.out" 2>"$tmpdir/source-summary-artifacts-prove.err"; then
  printf 'public_harness_check=fail exact_miner_source_summary_artifacts_prove_failed\n' >&2
  cat "$tmpdir/source-summary-artifacts-prove.err" >&2
  fail=1
elif [ "$(grep -c '"proof_status":"COUNTEREXAMPLE"' "$tmpdir/source-summary-artifacts-proofs.jsonl")" -ne 3 ] \
  || grep -q '"proof_status":"UNKNOWN"' "$tmpdir/source-summary-artifacts-proofs.jsonl"; then
  printf 'public_harness_check=fail exact_miner_source_summary_artifacts_proof_status\n' >&2
  cat "$tmpdir/source-summary-artifacts-proofs.jsonl" >&2
  fail=1
fi

printf '%s\n' \
  'rank	count	kind	file	line	family	source_hash' \
  '1	7	CCX	src/point_add/trailmix_ludicrous/codec.rs	561	unclassified	future-source' \
  > "$tmpdir/source-summary-future.tsv"
if ! python3 scripts/storm-exact-miner.py trace-facts \
  --input "$tmpdir/source-summary-future.tsv" \
  --frontier fixture-frontier/future-source \
  --source-base future-source \
  --stream-hash source-summary-future-demo \
  --out "$tmpdir/source-summary-future-facts.jsonl" >"$tmpdir/source-summary-future-trace.out" 2>"$tmpdir/source-summary-future-trace.err"; then
  printf 'public_harness_check=fail exact_miner_source_summary_future_trace_failed\n' >&2
  cat "$tmpdir/source-summary-future-trace.err" >&2
  fail=1
elif ! python3 scripts/storm-exact-miner.py support-check \
  --facts "$tmpdir/source-summary-future-facts.jsonl" \
  --out "$tmpdir/source-summary-future-support.jsonl" >"$tmpdir/source-summary-future-support.out" 2>"$tmpdir/source-summary-future-support.err"; then
  printf 'public_harness_check=fail exact_miner_source_summary_future_support_failed\n' >&2
  cat "$tmpdir/source-summary-future-support.err" >&2
  fail=1
elif ! grep -q 'certified=0 unknown=1 counterexample=0' "$tmpdir/source-summary-future-support.out"; then
  printf 'public_harness_check=fail exact_miner_source_summary_future_overclosed\n' >&2
  cat "$tmpdir/source-summary-future-support.out" >&2
  cat "$tmpdir/source-summary-future-support.jsonl" >&2
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

cat >"$tmpdir/q1152-binder-trace.raw" <<'EOF'
TLM_GIDNEY_THREAD call=5 phase=tlm_apply_inverse_mod_sub_register width=8 cin=1 cout=1 vents=0 ops_start=100 ops_end=180
ALLOC_NEAR active=1152 next_idx=1151 phase='tlm_apply_inverse_mod_sub_register' ops_idx=100 free_pool=0 caller=src/point_add/trailmix_ludicrous/gidney.rs:1217
TLM_GIDNEY_THREAD call=9 phase=tlm_apply_forward_mod_add_register width=8 cin=1 cout=1 vents=0 ops_start=200 ops_end=280
ALLOC_NEAR active=1152 next_idx=1151 phase='tlm_apply_forward_mod_add_register' ops_idx=200 free_pool=0 caller=src/point_add/trailmix_ludicrous/gidney.rs:1217
TLM_MCX_INC call=170 phase=tlm_apply_forward_mod_add_fold n=12 skip_lsb_x=true anc=3 ops_start=300 ops_end=330
ALLOC_NEAR active=1152 next_idx=1151 phase='tlm_apply_forward_mod_add_fold' ops_idx=300 free_pool=0 caller=src/point_add/trailmix_ludicrous/mcx.rs:318
EOF
cat >"$tmpdir/q1152-binder-gidney.rs" <<'EOF'
const GIDNEY_THREAD_FWD_DEAD_RANGES: &[(usize, usize, usize)] = &[
    (5, 0, 3),
    (9, 2, 4),
];
EOF
if ! python3 scripts/storm-q1152-binder-ledger.py \
  --trace "$tmpdir/q1152-binder-trace.raw" \
  --gidney-source "$tmpdir/q1152-binder-gidney.rs" \
  --summary-out "$tmpdir/q1152-binder-summary.tsv" \
  --peak 1152 >"$tmpdir/q1152-binder.out" 2>"$tmpdir/q1152-binder.err"; then
  printf 'public_harness_check=fail q1152_binder_ledger_failed\n' >&2
  cat "$tmpdir/q1152-binder.err" >&2
  fail=1
elif ! grep -q 'q1152_binder_ledger=pass' "$tmpdir/q1152-binder.out" ||
     ! grep -q 'gidney_binding_calls=2' "$tmpdir/q1152-binder.out" ||
     ! grep -q 'gidney_prefix_dead_binding_calls=1' "$tmpdir/q1152-binder.out" ||
     ! grep -q 'mcx_peak_ops=1' "$tmpdir/q1152-binder.out" ||
     ! grep -q 'mcx_binding_calls=1' "$tmpdir/q1152-binder.out" ||
     ! grep -q 'mcx_n_values=12' "$tmpdir/q1152-binder.out" ||
     ! grep -q 'decision=coordinated-cut-requires-mcx-replacement' "$tmpdir/q1152-binder.out" ||
     ! grep -q $'gidney.rs:1217\t2\t2\t2\t2\t1152\t1152\ttlm_apply_inverse_mod_sub_register\ttlm_apply_inverse_mod_sub_register\t5,9\t5\t4\t\t\t\tgidney_thread_forward_prefix' "$tmpdir/q1152-binder-summary.tsv" ||
     ! grep -q $'mcx.rs:318\t1\t1\t1\t1\t1152\t1152\ttlm_apply_forward_mod_add_fold\ttlm_apply_forward_mod_add_fold\t170\t\t0\t12\t3\ttrue\tnone_kg_prefix_ancilla' "$tmpdir/q1152-binder-summary.tsv"; then
  printf 'public_harness_check=fail q1152_binder_ledger_output\n' >&2
  cat "$tmpdir/q1152-binder.out" >&2
  cat "$tmpdir/q1152-binder-summary.tsv" >&2
  fail=1
fi

cat >"$tmpdir/mcx-incrementer.trace" <<'EOF'
TLM_MCX_INC call=170 phase=tlm_apply_forward_mod_add_fold n=10 skip_lsb_x=true anc=3 ops_start=300 ops_end=330
TLM_MCX_INC call=171 phase=tlm_apply_forward_mod_add_fold n=11 skip_lsb_x=true anc=3 ops_start=400 ops_end=430
TLM_MCX_INC call=172 phase=tlm_apply_forward_mod_add_fold n=12 skip_lsb_x=true anc=3 ops_start=500 ops_end=530
EOF
if ! python3 scripts/storm-mcx-incrementer-budget.py \
  --trace "$tmpdir/mcx-incrementer.trace" \
  --break-even-delta 75 \
  --candidate-extra-per-call 24 \
  --summary-out "$tmpdir/mcx-incrementer-budget.tsv" >"$tmpdir/mcx-incrementer-budget.out" 2>"$tmpdir/mcx-incrementer-budget.err"; then
  printf 'public_harness_check=fail mcx_incrementer_budget_failed\n' >&2
  cat "$tmpdir/mcx-incrementer-budget.err" >&2
  fail=1
elif ! grep -q 'mcx_incrementer_budget=pass' "$tmpdir/mcx-incrementer-budget.out" ||
     ! grep -q 'trace_rows=3' "$tmpdir/mcx-incrementer-budget.out" ||
     ! grep -q 'total_calls=3' "$tmpdir/mcx-incrementer-budget.out" ||
     ! grep -q 'current_total_ccx=74' "$tmpdir/mcx-incrementer-budget.out" ||
     ! grep -q 'candidate_extra_total=72.0' "$tmpdir/mcx-incrementer-budget.out" ||
     ! grep -q 'decision=candidate-budget-pass' "$tmpdir/mcx-incrementer-budget.out" ||
     ! grep -q $'10\t1\t3\t21\t21\t7\t7\t2\t11' "$tmpdir/mcx-incrementer-budget.tsv" ||
     ! grep -q $'12\t1\t3\t29\t29\t10\t9\t2\t13' "$tmpdir/mcx-incrementer-budget.tsv"; then
  printf 'public_harness_check=fail mcx_incrementer_budget_output\n' >&2
  cat "$tmpdir/mcx-incrementer-budget.out" >&2
  cat "$tmpdir/mcx-incrementer-budget.tsv" >&2
  fail=1
fi
if ! python3 scripts/storm-mcx-incrementer-budget.py \
  --trace "$tmpdir/mcx-incrementer.trace" \
  --break-even-delta 75 \
  --candidate-extra-per-call 26 >"$tmpdir/mcx-incrementer-budget-fail.out" 2>"$tmpdir/mcx-incrementer-budget-fail.err"; then
  printf 'public_harness_check=fail mcx_incrementer_budget_failcase_failed\n' >&2
  cat "$tmpdir/mcx-incrementer-budget-fail.err" >&2
  fail=1
elif ! grep -q 'candidate_extra_total=78.0' "$tmpdir/mcx-incrementer-budget-fail.out" ||
     ! grep -q 'decision=candidate-budget-fail' "$tmpdir/mcx-incrementer-budget-fail.out"; then
  printf 'public_harness_check=fail mcx_incrementer_budget_failcase_output\n' >&2
  cat "$tmpdir/mcx-incrementer-budget-fail.out" >&2
  fail=1
fi

if ! python3 scripts/storm-construction-package-gate.py \
  --target-qubits 1151 \
  --extra-per-site 1 \
  --charged-sites 2617 \
  --required-binders gidney,mcx,gcd,fold,register \
  --covered-binders gidney >"$tmpdir/construction-package-windowed.out" 2>"$tmpdir/construction-package-windowed.err"; then
  printf 'public_harness_check=fail construction_package_windowed_failed\n' >&2
  cat "$tmpdir/construction-package-windowed.err" >&2
  fail=1
elif ! grep -q 'construction_package_gate=pass' "$tmpdir/construction-package-windowed.out" ||
     ! grep -q 'coverage_ok=0' "$tmpdir/construction-package-windowed.out" ||
     ! grep -q 'count_ok=0' "$tmpdir/construction-package-windowed.out" ||
     ! grep -q 'decision=package-nack' "$tmpdir/construction-package-windowed.out" ||
     ! grep -q 'reasons=missing_coverage,score_no_edge' "$tmpdir/construction-package-windowed.out"; then
  printf 'public_harness_check=fail construction_package_windowed_output\n' >&2
  cat "$tmpdir/construction-package-windowed.out" >&2
  fail=1
fi
if ! python3 scripts/storm-construction-package-gate.py \
  --target-qubits 1151 \
  --extra-avg-tof 1185 \
  --required-binders gidney,mcx \
  --covered-binders gidney,mcx >"$tmpdir/construction-package-prefilter.out" 2>"$tmpdir/construction-package-prefilter.err"; then
  printf 'public_harness_check=fail construction_package_prefilter_failed\n' >&2
  cat "$tmpdir/construction-package-prefilter.err" >&2
  fail=1
elif ! grep -q 'coverage_ok=1' "$tmpdir/construction-package-prefilter.out" ||
     ! grep -q 'count_ok=1' "$tmpdir/construction-package-prefilter.out" ||
     ! grep -q 'decision=count-prefilter-only' "$tmpdir/construction-package-prefilter.out"; then
  printf 'public_harness_check=fail construction_package_prefilter_output\n' >&2
  cat "$tmpdir/construction-package-prefilter.out" >&2
  fail=1
fi
if ! python3 scripts/storm-construction-package-gate.py \
  --target-qubits 1151 \
  --extra-avg-tof 1185 \
  --required-binders gidney,mcx \
  --covered-binders gidney,mcx \
  --candidate-clean pass >"$tmpdir/construction-package-ready.out" 2>"$tmpdir/construction-package-ready.err"; then
  printf 'public_harness_check=fail construction_package_ready_failed\n' >&2
  cat "$tmpdir/construction-package-ready.err" >&2
  fail=1
elif ! grep -q 'candidate_clean=pass' "$tmpdir/construction-package-ready.out" ||
     ! grep -q 'decision=ready-for-validation' "$tmpdir/construction-package-ready.out"; then
  printf 'public_harness_check=fail construction_package_ready_output\n' >&2
  cat "$tmpdir/construction-package-ready.out" >&2
  fail=1
fi

if ! python3 scripts/storm-frontier-escape-gate.py \
  --escape-class current-corpus-knob \
  --local-optimum measured >"$tmpdir/frontier-escape-current.out" 2>"$tmpdir/frontier-escape-current.err"; then
  printf 'public_harness_check=fail frontier_escape_current_failed\n' >&2
  cat "$tmpdir/frontier-escape-current.err" >&2
  fail=1
elif ! grep -q 'frontier_escape_gate=pass' "$tmpdir/frontier-escape-current.out" ||
     ! grep -q 'escape_class=current-corpus-knob' "$tmpdir/frontier-escape-current.out" ||
     ! grep -q 'decision=escape-nack' "$tmpdir/frontier-escape-current.out" ||
     ! grep -q 'reasons=current_corpus_closed,score_no_edge' "$tmpdir/frontier-escape-current.out"; then
  printf 'public_harness_check=fail frontier_escape_current_output\n' >&2
  cat "$tmpdir/frontier-escape-current.out" >&2
  fail=1
fi
if ! python3 scripts/storm-frontier-escape-gate.py \
  --escape-class construction-package \
  --coverage pass \
  --count pass \
  --score-edge 295 >"$tmpdir/frontier-escape-construction.out" 2>"$tmpdir/frontier-escape-construction.err"; then
  printf 'public_harness_check=fail frontier_escape_construction_failed\n' >&2
  cat "$tmpdir/frontier-escape-construction.err" >&2
  fail=1
elif ! grep -q 'escape_class=construction-package' "$tmpdir/frontier-escape-construction.out" ||
     ! grep -q 'decision=construction-prefilter-only' "$tmpdir/frontier-escape-construction.out"; then
  printf 'public_harness_check=fail frontier_escape_construction_output\n' >&2
  cat "$tmpdir/frontier-escape-construction.out" >&2
  fail=1
fi
if ! python3 scripts/storm-frontier-escape-gate.py \
  --escape-class source-theorem \
  --source-support certified \
  --expected-avg-saving 1 \
  --score-edge 1152 \
  --candidate-clean pass >"$tmpdir/frontier-escape-source-ready.out" 2>"$tmpdir/frontier-escape-source-ready.err"; then
  printf 'public_harness_check=fail frontier_escape_source_ready_failed\n' >&2
  cat "$tmpdir/frontier-escape-source-ready.err" >&2
  fail=1
elif ! grep -q 'escape_class=source-theorem' "$tmpdir/frontier-escape-source-ready.out" ||
     ! grep -q 'decision=ready-for-validation' "$tmpdir/frontier-escape-source-ready.out"; then
  printf 'public_harness_check=fail frontier_escape_source_ready_output\n' >&2
  cat "$tmpdir/frontier-escape-source-ready.out" >&2
  fail=1
fi
if ! python3 scripts/storm-frontier-escape-gate.py \
  --escape-class nonce-retune \
  --nonce-retune-status prefilter \
  --score-edge 1000 \
  --candidate-clean unknown >"$tmpdir/frontier-escape-nonce-prefilter.out" 2>"$tmpdir/frontier-escape-nonce-prefilter.err"; then
  printf 'public_harness_check=fail frontier_escape_nonce_prefilter_failed\n' >&2
  cat "$tmpdir/frontier-escape-nonce-prefilter.err" >&2
  fail=1
elif ! grep -q 'escape_class=nonce-retune' "$tmpdir/frontier-escape-nonce-prefilter.out" ||
     ! grep -q 'decision=escape-nack' "$tmpdir/frontier-escape-nonce-prefilter.out" ||
     ! grep -q 'reasons=prefilter_only,candidate_not_clean' "$tmpdir/frontier-escape-nonce-prefilter.out"; then
  printf 'public_harness_check=fail frontier_escape_nonce_prefilter_output\n' >&2
  cat "$tmpdir/frontier-escape-nonce-prefilter.out" >&2
  fail=1
fi

if ! python3 scripts/storm-square-static-gap-audit.py \
  --min-width 1 \
  --max-width 6 \
  --summary-out "$tmpdir/square-static-gap.tsv" >"$tmpdir/square-static-gap.out" 2>"$tmpdir/square-static-gap.err"; then
  printf 'public_harness_check=fail square_static_gap_audit_failed\n' >&2
  cat "$tmpdir/square-static-gap.err" >&2
  fail=1
elif ! grep -q 'square_static_gap_audit=pass' "$tmpdir/square-static-gap.out" ||
     ! grep -q 'fixed_zero_pattern=bit1_only' "$tmpdir/square-static-gap.out" ||
     ! grep -q 'source_bit1_gap_has_executable_ccx=0' "$tmpdir/square-static-gap.out" ||
     ! grep -q 'cross_terms_checked=35' "$tmpdir/square-static-gap.out" ||
     ! grep -q 'cross_terms_live=35' "$tmpdir/square-static-gap.out" ||
     ! grep -q 'decision=no-executable-zero-bit-trim' "$tmpdir/square-static-gap.out" ||
     ! grep -q $'6\t1\t1\t0\t15\t15\t0:1:row2:prod2:x3' "$tmpdir/square-static-gap.tsv"; then
  printf 'public_harness_check=fail square_static_gap_audit_output\n' >&2
  cat "$tmpdir/square-static-gap.out" >&2
  cat "$tmpdir/square-static-gap.tsv" >&2
  fail=1
fi

cat >"$tmpdir/single-ccx-fanout-build.out" <<'EOF'
  emitted ops : 10221059
EOF
cat >"$tmpdir/single-ccx-fanout-build.err" <<'EOF'
SINGLE_CCX_FANOUT: STOP passes=318 input_ops=10221377 output_ops=10221059 reason=no target-fanout conjugation found
SINGLE_CCX_FANOUT: SUMMARY input_ops=10221377 output_ops=10221059 passes=318
EOF
cat >"$tmpdir/single-ccx-fanout-eval.out" <<'EOF'
  loaded ops  : 10221059
  qubits      : 1152
  classical mismatches    : 24
  phase-garbage batches   : 16
  ancilla-garbage batches : 0
EOF
if ! python3 scripts/storm-single-ccx-fanout-ledger.py \
  --build-stdout "$tmpdir/single-ccx-fanout-build.out" \
  --build-stderr "$tmpdir/single-ccx-fanout-build.err" \
  --eval-stdout "$tmpdir/single-ccx-fanout-eval.out" \
  >"$tmpdir/single-ccx-fanout-ledger.out" 2>"$tmpdir/single-ccx-fanout-ledger.err"; then
  printf 'public_harness_check=fail single_ccx_fanout_ledger_failed\n' >&2
  cat "$tmpdir/single-ccx-fanout-ledger.err" >&2
  fail=1
elif ! grep -q 'single_ccx_fanout_ledger=pass' "$tmpdir/single-ccx-fanout-ledger.out" ||
     ! grep -q 'delta_ops=-318' "$tmpdir/single-ccx-fanout-ledger.out" ||
     ! grep -q 'passes=318' "$tmpdir/single-ccx-fanout-ledger.out" ||
     ! grep -q 'classical=24' "$tmpdir/single-ccx-fanout-ledger.out" ||
     ! grep -q 'phase=16' "$tmpdir/single-ccx-fanout-ledger.out" ||
     ! grep -q 'decision=trusted-eval-nack' "$tmpdir/single-ccx-fanout-ledger.out"; then
  printf 'public_harness_check=fail single_ccx_fanout_ledger_output\n' >&2
  cat "$tmpdir/single-ccx-fanout-ledger.out" >&2
  fail=1
fi

if ! python3 scripts/storm-fanout-survivor-phase-gate.py \
  examples/fanout-survivor-phase-gate.example.txt \
  >"$tmpdir/fanout-survivor-phase-gate-hold.out" \
  2>"$tmpdir/fanout-survivor-phase-gate-hold.err"; then
  printf 'public_harness_check=fail fanout_survivor_phase_gate_hold_failed\n' >&2
  cat "$tmpdir/fanout-survivor-phase-gate-hold.err" >&2
  fail=1
elif ! grep -q 'fanout_survivor_phase_gate=hold' "$tmpdir/fanout-survivor-phase-gate-hold.out" ||
     ! grep -q 'official_dirty=1' "$tmpdir/fanout-survivor-phase-gate-hold.out" ||
     ! grep -q 'missing_official=1' "$tmpdir/fanout-survivor-phase-gate-hold.out" ||
     ! grep -q 'phase_dirty=1' "$tmpdir/fanout-survivor-phase-gate-hold.out" ||
     ! grep -q 'decision=hold_for_official_eval' "$tmpdir/fanout-survivor-phase-gate-hold.out"; then
  printf 'public_harness_check=fail fanout_survivor_phase_gate_hold_output\n' >&2
  cat "$tmpdir/fanout-survivor-phase-gate-hold.out" >&2
  fail=1
fi

cat >"$tmpdir/fanout-survivor-phase-gate-ready.log" <<'EOF'
GPU prefilter CLEAN nonce=103
official eval CLEAN nonce=103 classical=0 phase=0 ancilla=0
EOF
if ! python3 scripts/storm-fanout-survivor-phase-gate.py \
  "$tmpdir/fanout-survivor-phase-gate-ready.log" \
  --require-ready \
  >"$tmpdir/fanout-survivor-phase-gate-ready.out" \
  2>"$tmpdir/fanout-survivor-phase-gate-ready.err"; then
  printf 'public_harness_check=fail fanout_survivor_phase_gate_ready_failed\n' >&2
  cat "$tmpdir/fanout-survivor-phase-gate-ready.err" >&2
  fail=1
elif ! grep -q 'fanout_survivor_phase_gate=ready' "$tmpdir/fanout-survivor-phase-gate-ready.out" ||
     ! grep -q 'official_clean=1' "$tmpdir/fanout-survivor-phase-gate-ready.out" ||
     ! grep -q 'phase_gap=false' "$tmpdir/fanout-survivor-phase-gate-ready.out" ||
     ! grep -q 'submit_authorized=false' "$tmpdir/fanout-survivor-phase-gate-ready.out" ||
     ! grep -q 'decision=validation_submit_gate_required' "$tmpdir/fanout-survivor-phase-gate-ready.out"; then
  printf 'public_harness_check=fail fanout_survivor_phase_gate_ready_output\n' >&2
  cat "$tmpdir/fanout-survivor-phase-gate-ready.out" >&2
  fail=1
fi

cat >"$tmpdir/fanout-survivor-phase-gate-raw-eval.out" <<'EOF'
=== quantum_ecc: eval_circuit (trusted stage) ===
  loaded ops  : 10221059
-- correctness tests (9024 shots) --
  fast exit              : enabled for dirty-candidate triage
  tested shots            : 64
  classical mismatches    : 0
  phase-garbage batches   : 1
  ancilla-garbage batches : 0
EOF
if ! python3 scripts/storm-fanout-survivor-phase-gate.py \
  "$tmpdir/fanout-survivor-phase-gate-raw-eval.out" \
  --nonce 104 \
  --mark-survivor \
  >"$tmpdir/fanout-survivor-phase-gate-raw-eval-gate.out" \
  2>"$tmpdir/fanout-survivor-phase-gate-raw-eval-gate.err"; then
  printf 'public_harness_check=fail fanout_survivor_phase_gate_raw_eval_failed\n' >&2
  cat "$tmpdir/fanout-survivor-phase-gate-raw-eval-gate.err" >&2
  fail=1
elif ! grep -q 'fanout_survivor_phase_gate=nack' "$tmpdir/fanout-survivor-phase-gate-raw-eval-gate.out" ||
     ! grep -q 'gpu_survivors=1' "$tmpdir/fanout-survivor-phase-gate-raw-eval-gate.out" ||
     ! grep -q 'official_dirty=1' "$tmpdir/fanout-survivor-phase-gate-raw-eval-gate.out" ||
     ! grep -q 'phase_dirty=1' "$tmpdir/fanout-survivor-phase-gate-raw-eval-gate.out"; then
  printf 'public_harness_check=fail fanout_survivor_phase_gate_raw_eval_output\n' >&2
  cat "$tmpdir/fanout-survivor-phase-gate-raw-eval-gate.out" >&2
  fail=1
fi

cat >"$tmpdir/fanout-survivor-phase-gate-double-nonce.log" <<'EOF'
STORM_RUNPOD_GPU_CLEAN_PREFILTER nonce=nonce=431 launching_eval=1
official eval NACK nonce=431 classical=1 phase=0 ancilla=0
EOF
if ! python3 scripts/storm-fanout-survivor-phase-gate.py \
  "$tmpdir/fanout-survivor-phase-gate-double-nonce.log" \
  >"$tmpdir/fanout-survivor-phase-gate-double-nonce.out" \
  2>"$tmpdir/fanout-survivor-phase-gate-double-nonce.err"; then
  printf 'public_harness_check=fail fanout_survivor_phase_gate_double_nonce_failed\n' >&2
  cat "$tmpdir/fanout-survivor-phase-gate-double-nonce.err" >&2
  fail=1
elif ! grep -q 'fanout_survivor_phase_gate=nack' "$tmpdir/fanout-survivor-phase-gate-double-nonce.out" ||
     ! grep -q 'gpu_survivors=1' "$tmpdir/fanout-survivor-phase-gate-double-nonce.out" ||
     ! grep -q 'official_dirty=1' "$tmpdir/fanout-survivor-phase-gate-double-nonce.out" ||
     ! grep -q 'classical_dirty=1' "$tmpdir/fanout-survivor-phase-gate-double-nonce.out"; then
  printf 'public_harness_check=fail fanout_survivor_phase_gate_double_nonce_output\n' >&2
  cat "$tmpdir/fanout-survivor-phase-gate-double-nonce.out" >&2
  fail=1
fi

if ! python3 scripts/storm-fanout-burst-triage-gate.py \
  examples/fanout-burst-triage-nack.example.txt \
  --require-no-candidate \
  >"$tmpdir/fanout-burst-triage-nack.out" \
  2>"$tmpdir/fanout-burst-triage-nack.err"; then
  printf 'public_harness_check=fail fanout_burst_triage_nack_failed\n' >&2
  cat "$tmpdir/fanout-burst-triage-nack.err" >&2
  fail=1
elif ! grep -q 'fanout_burst_triage_gate=nack' "$tmpdir/fanout-burst-triage-nack.out" ||
     ! grep -q 'clean_summary=0' "$tmpdir/fanout-burst-triage-nack.out" ||
     ! grep -q 'best_dirty=1' "$tmpdir/fanout-burst-triage-nack.out"; then
  printf 'public_harness_check=fail fanout_burst_triage_nack_output\n' >&2
  cat "$tmpdir/fanout-burst-triage-nack.out" >&2
  fail=1
fi

if ! python3 scripts/storm-fanout-burst-triage-gate.py \
  examples/fanout-burst-triage-candidate.example.txt \
  >"$tmpdir/fanout-burst-triage-candidate.out" \
  2>"$tmpdir/fanout-burst-triage-candidate.err"; then
  printf 'public_harness_check=fail fanout_burst_triage_candidate_failed\n' >&2
  cat "$tmpdir/fanout-burst-triage-candidate.err" >&2
  fail=1
elif ! grep -q 'fanout_burst_triage_gate=candidate' "$tmpdir/fanout-burst-triage-candidate.out" ||
     ! grep -q 'zero_rows=1' "$tmpdir/fanout-burst-triage-candidate.out" ||
     ! grep -q 'decision=full-local-validation-required' "$tmpdir/fanout-burst-triage-candidate.out"; then
  printf 'public_harness_check=fail fanout_burst_triage_candidate_output\n' >&2
  cat "$tmpdir/fanout-burst-triage-candidate.out" >&2
  fail=1
fi

cat >"$tmpdir/fanout-survivor-phase-gate-eval-header.log" <<'EOF'
STORM_RUNPOD_GPU_CLEAN_PREFILTER nonce=501 launching_eval=1
=== fanout/eval-501.log ===
-- correctness tests (9024 shots) --
  classical mismatches    : 0
  phase-garbage batches   : 1
  ancilla-garbage batches : 0
EOF
if ! python3 scripts/storm-fanout-survivor-phase-gate.py \
  "$tmpdir/fanout-survivor-phase-gate-eval-header.log" \
  >"$tmpdir/fanout-survivor-phase-gate-eval-header.out" \
  2>"$tmpdir/fanout-survivor-phase-gate-eval-header.err"; then
  printf 'public_harness_check=fail fanout_survivor_phase_gate_eval_header_failed\n' >&2
  cat "$tmpdir/fanout-survivor-phase-gate-eval-header.err" >&2
  fail=1
elif ! grep -q 'fanout_survivor_phase_gate=nack' "$tmpdir/fanout-survivor-phase-gate-eval-header.out" ||
     ! grep -q 'gpu_survivors=1' "$tmpdir/fanout-survivor-phase-gate-eval-header.out" ||
     ! grep -q 'official_dirty=1' "$tmpdir/fanout-survivor-phase-gate-eval-header.out" ||
     ! grep -q 'phase_dirty=1' "$tmpdir/fanout-survivor-phase-gate-eval-header.out"; then
  printf 'public_harness_check=fail fanout_survivor_phase_gate_eval_header_output\n' >&2
  cat "$tmpdir/fanout-survivor-phase-gate-eval-header.out" >&2
  fail=1
fi

if python3 scripts/storm-official-eval-isolation-gate.py \
  examples/official-eval-isolation-unsafe.example.sh \
  --require-pass \
  >"$tmpdir/official-eval-isolation-unsafe.out" \
  2>"$tmpdir/official-eval-isolation-unsafe.err"; then
  printf 'public_harness_check=fail official_eval_isolation_unsafe_unexpected_pass\n' >&2
  cat "$tmpdir/official-eval-isolation-unsafe.out" >&2
  fail=1
elif ! grep -q 'official_eval_isolation_gate=fail' "$tmpdir/official-eval-isolation-unsafe.out" ||
     ! grep -q 'shared_artifact_without_lock_or_isolation' "$tmpdir/official-eval-isolation-unsafe.out"; then
  printf 'public_harness_check=fail official_eval_isolation_unsafe_output\n' >&2
  cat "$tmpdir/official-eval-isolation-unsafe.out" >&2
  cat "$tmpdir/official-eval-isolation-unsafe.err" >&2
  fail=1
fi

if ! python3 scripts/storm-official-eval-isolation-gate.py \
  examples/official-eval-isolation-locked.example.sh \
  --require-pass \
  >"$tmpdir/official-eval-isolation-locked.out" \
  2>"$tmpdir/official-eval-isolation-locked.err"; then
  printf 'public_harness_check=fail official_eval_isolation_locked_failed\n' >&2
  cat "$tmpdir/official-eval-isolation-locked.err" >&2
  fail=1
elif ! grep -q 'official_eval_isolation_gate=pass' "$tmpdir/official-eval-isolation-locked.out" ||
     ! grep -q 'lock=true' "$tmpdir/official-eval-isolation-locked.out"; then
  printf 'public_harness_check=fail official_eval_isolation_locked_output\n' >&2
  cat "$tmpdir/official-eval-isolation-locked.out" >&2
  fail=1
fi

if ! python3 scripts/storm-official-eval-isolation-gate.py \
  examples/official-eval-isolation-workdir.example.sh \
  --require-pass \
  >"$tmpdir/official-eval-isolation-workdir.out" \
  2>"$tmpdir/official-eval-isolation-workdir.err"; then
  printf 'public_harness_check=fail official_eval_isolation_workdir_failed\n' >&2
  cat "$tmpdir/official-eval-isolation-workdir.err" >&2
  fail=1
elif ! grep -q 'official_eval_isolation_gate=pass' "$tmpdir/official-eval-isolation-workdir.out" ||
     ! grep -q 'isolated=true' "$tmpdir/official-eval-isolation-workdir.out"; then
  printf 'public_harness_check=fail official_eval_isolation_workdir_output\n' >&2
  cat "$tmpdir/official-eval-isolation-workdir.out" >&2
  fail=1
fi

if python3 scripts/storm-official-eval-isolation-gate.py \
  examples/official-eval-isolation-helper-storm.example.sh \
  >"$tmpdir/official-eval-isolation-helper-storm.out" \
  2>"$tmpdir/official-eval-isolation-helper-storm.err"; then
  printf 'public_harness_check=fail official_eval_isolation_helper_storm_should_fail\n' >&2
  cat "$tmpdir/official-eval-isolation-helper-storm.out" >&2
  fail=1
elif ! grep -q 'official_eval_isolation_gate=fail' "$tmpdir/official-eval-isolation-helper-storm.out" ||
     ! grep -q 'background_or_parallel_eval_helper' "$tmpdir/official-eval-isolation-helper-storm.out"; then
  printf 'public_harness_check=fail official_eval_isolation_helper_storm_output\n' >&2
  cat "$tmpdir/official-eval-isolation-helper-storm.out" >&2
  cat "$tmpdir/official-eval-isolation-helper-storm.err" >&2
  fail=1
fi

if ! python3 scripts/storm-fleet-owner-claim-gate.py \
  examples/fleet-owner-claim-pass.example.txt \
  --require-pass \
  >"$tmpdir/fleet-owner-claim-pass.out" \
  2>"$tmpdir/fleet-owner-claim-pass.err"; then
  printf 'public_harness_check=fail fleet_owner_claim_pass_failed\n' >&2
  cat "$tmpdir/fleet-owner-claim-pass.err" >&2
  fail=1
elif ! grep -q 'fleet_owner_claim_gate=pass' "$tmpdir/fleet-owner-claim-pass.out" ||
     ! grep -q 'no_submit_ack=true' "$tmpdir/fleet-owner-claim-pass.out" ||
     ! grep -q 'active_process_or_log=true' "$tmpdir/fleet-owner-claim-pass.out"; then
  printf 'public_harness_check=fail fleet_owner_claim_pass_output\n' >&2
  cat "$tmpdir/fleet-owner-claim-pass.out" >&2
  fail=1
fi

if python3 scripts/storm-fleet-owner-claim-gate.py \
  examples/fleet-owner-claim-missing.example.txt \
  --require-pass \
  >"$tmpdir/fleet-owner-claim-missing.out" \
  2>"$tmpdir/fleet-owner-claim-missing.err"; then
  printf 'public_harness_check=fail fleet_owner_claim_missing_unexpected_pass\n' >&2
  cat "$tmpdir/fleet-owner-claim-missing.out" >&2
  fail=1
elif ! grep -q 'fleet_owner_claim_gate=fail' "$tmpdir/fleet-owner-claim-missing.out" ||
     ! grep -q 'route_or_range' "$tmpdir/fleet-owner-claim-missing.out" ||
     ! grep -q 'no_submit_ack' "$tmpdir/fleet-owner-claim-missing.out"; then
  printf 'public_harness_check=fail fleet_owner_claim_missing_output\n' >&2
  cat "$tmpdir/fleet-owner-claim-missing.out" >&2
  cat "$tmpdir/fleet-owner-claim-missing.err" >&2
  fail=1
fi

if python3 scripts/storm-fleet-owner-claim-gate.py \
  examples/fleet-owner-claim-vague-token.example.txt \
  >"$tmpdir/fleet-owner-claim-vague-token.out" \
  2>"$tmpdir/fleet-owner-claim-vague-token.err"; then
  printf 'public_harness_check=fail fleet_owner_claim_vague_token_should_fail\n' >&2
  cat "$tmpdir/fleet-owner-claim-vague-token.out" >&2
  fail=1
elif ! grep -q 'fleet_owner_claim_gate=fail' "$tmpdir/fleet-owner-claim-vague-token.out" ||
     ! grep -q 'pod_identity' "$tmpdir/fleet-owner-claim-vague-token.out"; then
  printf 'public_harness_check=fail fleet_owner_claim_vague_token_output\n' >&2
  cat "$tmpdir/fleet-owner-claim-vague-token.out" >&2
  cat "$tmpdir/fleet-owner-claim-vague-token.err" >&2
  fail=1
fi

if python3 scripts/storm-fleet-owner-claim-gate.py \
  examples/fleet-owner-claim-combined-tail.example.txt \
  --strict-single-packet \
  --require-pass \
  >"$tmpdir/fleet-owner-claim-combined-tail.out" \
  2>"$tmpdir/fleet-owner-claim-combined-tail.err"; then
  printf 'public_harness_check=fail fleet_owner_claim_combined_tail_should_fail\n' >&2
  cat "$tmpdir/fleet-owner-claim-combined-tail.out" >&2
  fail=1
elif ! grep -q 'fleet_owner_claim_gate=fail' "$tmpdir/fleet-owner-claim-combined-tail.out" ||
     ! grep -q 'multiple_owner_packets' "$tmpdir/fleet-owner-claim-combined-tail.out"; then
  printf 'public_harness_check=fail fleet_owner_claim_combined_tail_output\n' >&2
  cat "$tmpdir/fleet-owner-claim-combined-tail.out" >&2
  cat "$tmpdir/fleet-owner-claim-combined-tail.err" >&2
  fail=1
fi

if ! python3 scripts/storm-pod-wrapper-dup-gate.py \
  examples/pod-wrapper-dup-pass.example.txt \
  --require-pass \
  >"$tmpdir/pod-wrapper-dup-pass.out" \
  2>"$tmpdir/pod-wrapper-dup-pass.err"; then
  printf 'public_harness_check=fail pod_wrapper_dup_pass_failed\n' >&2
  cat "$tmpdir/pod-wrapper-dup-pass.err" >&2
  fail=1
elif ! grep -q 'pod_wrapper_dup_gate=pass' "$tmpdir/pod-wrapper-dup-pass.out" ||
     ! grep -q 'queued_marker=true' "$tmpdir/pod-wrapper-dup-pass.out" ||
     ! grep -q 'lock=true' "$tmpdir/pod-wrapper-dup-pass.out"; then
  printf 'public_harness_check=fail pod_wrapper_dup_pass_output\n' >&2
  cat "$tmpdir/pod-wrapper-dup-pass.out" >&2
  fail=1
fi

if python3 scripts/storm-pod-wrapper-dup-gate.py \
  examples/pod-wrapper-dup-fail.example.txt \
  --require-pass \
  >"$tmpdir/pod-wrapper-dup-fail.out" \
  2>"$tmpdir/pod-wrapper-dup-fail.err"; then
  printf 'public_harness_check=fail pod_wrapper_dup_fail_unexpected_pass\n' >&2
  cat "$tmpdir/pod-wrapper-dup-fail.out" >&2
  fail=1
elif ! grep -q 'pod_wrapper_dup_gate=fail' "$tmpdir/pod-wrapper-dup-fail.out" ||
     ! grep -q 'duplicate_gpu_route_wrapper' "$tmpdir/pod-wrapper-dup-fail.out" ||
     ! grep -q 'duplicate_eval_nonce_wrapper' "$tmpdir/pod-wrapper-dup-fail.out"; then
  printf 'public_harness_check=fail pod_wrapper_dup_fail_output\n' >&2
  cat "$tmpdir/pod-wrapper-dup-fail.out" >&2
  cat "$tmpdir/pod-wrapper-dup-fail.err" >&2
  fail=1
fi

if ! python3 scripts/storm-compute-restart-gate.py \
  examples/compute-restart-pass.example.txt \
  --require-pass \
  >"$tmpdir/compute-restart-pass.out" \
  2>"$tmpdir/compute-restart-pass.err"; then
  printf 'public_harness_check=fail compute_restart_pass_failed\n' >&2
  cat "$tmpdir/compute-restart-pass.err" >&2
  fail=1
elif ! grep -q 'compute_restart_gate=pass' "$tmpdir/compute-restart-pass.out" ||
     ! grep -q 'scanner=true' "$tmpdir/compute-restart-pass.out" ||
     ! grep -q 'certified_evidence=true' "$tmpdir/compute-restart-pass.out" ||
     ! grep -q 'source_base=d44cad3' "$tmpdir/compute-restart-pass.out" ||
     ! grep -q 'validation_owner=Storm-Codex' "$tmpdir/compute-restart-pass.out" ||
     ! grep -q 'budget=true' "$tmpdir/compute-restart-pass.out" ||
     ! grep -q 'stop_condition=true' "$tmpdir/compute-restart-pass.out" ||
     ! grep -q 'negative_edge=true' "$tmpdir/compute-restart-pass.out" ||
     ! grep -q 'scanner-restart-gate-cleared' "$tmpdir/compute-restart-pass.out"; then
  printf 'public_harness_check=fail compute_restart_pass_output\n' >&2
  cat "$tmpdir/compute-restart-pass.out" >&2
  fail=1
fi

if python3 scripts/storm-compute-restart-gate.py \
  examples/compute-restart-fail.example.txt \
  --require-pass \
  >"$tmpdir/compute-restart-fail.out" \
  2>"$tmpdir/compute-restart-fail.err"; then
  printf 'public_harness_check=fail compute_restart_fail_unexpected_pass\n' >&2
  cat "$tmpdir/compute-restart-fail.out" >&2
  fail=1
elif ! grep -q 'compute_restart_gate=fail' "$tmpdir/compute-restart-fail.out" ||
     ! grep -q 'scanner_restart_under_closed_compute_gate' "$tmpdir/compute-restart-fail.out" ||
     ! grep -q 'stale_or_manual_scanner_route' "$tmpdir/compute-restart-fail.out" ||
     ! grep -q 'scanner_without_route_ack_and_certified_evidence' "$tmpdir/compute-restart-fail.out"; then
  printf 'public_harness_check=fail compute_restart_fail_output\n' >&2
  cat "$tmpdir/compute-restart-fail.out" >&2
  cat "$tmpdir/compute-restart-fail.err" >&2
  fail=1
fi

if python3 scripts/storm-compute-restart-gate.py \
  examples/compute-restart-hold.example.txt \
  --require-pass \
  >"$tmpdir/compute-restart-hold.out" \
  2>"$tmpdir/compute-restart-hold.err"; then
  printf 'public_harness_check=fail compute_restart_hold_unexpected_pass\n' >&2
  cat "$tmpdir/compute-restart-hold.out" >&2
  fail=1
elif ! grep -q 'compute_restart_gate=hold' "$tmpdir/compute-restart-hold.out" ||
     ! grep -q 'missing_owner' "$tmpdir/compute-restart-hold.out" ||
     ! grep -q 'missing_route_or_range' "$tmpdir/compute-restart-hold.out" ||
     ! grep -q 'missing_budget' "$tmpdir/compute-restart-hold.out" ||
     ! grep -q 'missing_stop_condition' "$tmpdir/compute-restart-hold.out" ||
     ! grep -q 'complete-route-owner-and-gate-evidence' "$tmpdir/compute-restart-hold.out"; then
  printf 'public_harness_check=fail compute_restart_hold_output\n' >&2
  cat "$tmpdir/compute-restart-hold.out" >&2
  cat "$tmpdir/compute-restart-hold.err" >&2
  fail=1
fi

if ! python3 scripts/storm-compute-restart-gate.py \
  examples/compute-restart-eval-pass.example.txt \
  --require-pass \
  >"$tmpdir/compute-restart-eval-pass.out" \
  2>"$tmpdir/compute-restart-eval-pass.err"; then
  printf 'public_harness_check=fail compute_restart_eval_pass_failed\n' >&2
  cat "$tmpdir/compute-restart-eval-pass.err" >&2
  fail=1
elif ! grep -q 'compute_restart_gate=pass' "$tmpdir/compute-restart-eval-pass.out" ||
     ! grep -q 'scanner=false' "$tmpdir/compute-restart-eval-pass.out" ||
     ! grep -q 'official_eval=true' "$tmpdir/compute-restart-eval-pass.out" ||
     ! grep -q 'no-scanner-restart' "$tmpdir/compute-restart-eval-pass.out"; then
  printf 'public_harness_check=fail compute_restart_eval_pass_output\n' >&2
  cat "$tmpdir/compute-restart-eval-pass.out" >&2
  fail=1
fi

if ! python3 scripts/storm-local-heavy-compute-gate.py \
  examples/local-heavy-compute-pass.example.txt \
  --require-pass \
  >"$tmpdir/local-heavy-compute-pass.out" \
  2>"$tmpdir/local-heavy-compute-pass.err"; then
  printf 'public_harness_check=fail local_heavy_compute_pass_failed\n' >&2
  cat "$tmpdir/local-heavy-compute-pass.err" >&2
  fail=1
elif ! grep -q 'local_heavy_compute_gate=pass' "$tmpdir/local-heavy-compute-pass.out" ||
     ! grep -q 'remote_heavy=2' "$tmpdir/local-heavy-compute-pass.out" ||
     ! grep -q 'allowed_lightweight=true' "$tmpdir/local-heavy-compute-pass.out"; then
  printf 'public_harness_check=fail local_heavy_compute_pass_output\n' >&2
  cat "$tmpdir/local-heavy-compute-pass.out" >&2
  fail=1
fi

if python3 scripts/storm-local-heavy-compute-gate.py \
  examples/local-heavy-compute-fail.example.txt \
  --require-pass \
  >"$tmpdir/local-heavy-compute-fail.out" \
  2>"$tmpdir/local-heavy-compute-fail.err"; then
  printf 'public_harness_check=fail local_heavy_compute_fail_unexpected_pass\n' >&2
  cat "$tmpdir/local-heavy-compute-fail.out" >&2
  fail=1
elif ! grep -q 'local_heavy_compute_gate=fail' "$tmpdir/local-heavy-compute-fail.out" ||
     ! grep -q 'local_heavy=7' "$tmpdir/local-heavy-compute-fail.out" ||
     ! grep -q 'local_recurring=1' "$tmpdir/local-heavy-compute-fail.out" ||
     ! grep -q 'storm-exact-miner.py' "$tmpdir/local-heavy-compute-fail.out" ||
     ! grep -q 'route_compare' "$tmpdir/local-heavy-compute-fail.out" ||
     ! grep -q 'stop-mac-local-heavy-compute' "$tmpdir/local-heavy-compute-fail.out"; then
  printf 'public_harness_check=fail local_heavy_compute_fail_output\n' >&2
  cat "$tmpdir/local-heavy-compute-fail.out" >&2
  cat "$tmpdir/local-heavy-compute-fail.err" >&2
  fail=1
fi

if python3 scripts/storm-local-heavy-compute-gate.py \
  examples/local-heavy-compute-hold.example.txt \
  --require-pass \
  >"$tmpdir/local-heavy-compute-hold.out" \
  2>"$tmpdir/local-heavy-compute-hold.err"; then
  printf 'public_harness_check=fail local_heavy_compute_hold_unexpected_pass\n' >&2
  cat "$tmpdir/local-heavy-compute-hold.out" >&2
  fail=1
elif ! grep -q 'local_heavy_compute_gate=hold' "$tmpdir/local-heavy-compute-hold.out" ||
     ! grep -q 'unknown_heavy=2' "$tmpdir/local-heavy-compute-hold.out" ||
     ! grep -q 'unknown_recurring=1' "$tmpdir/local-heavy-compute-hold.out" ||
     ! grep -q 'require-host-and-owner-evidence' "$tmpdir/local-heavy-compute-hold.out"; then
  printf 'public_harness_check=fail local_heavy_compute_hold_output\n' >&2
  cat "$tmpdir/local-heavy-compute-hold.out" >&2
  cat "$tmpdir/local-heavy-compute-hold.err" >&2
  fail=1
fi

if ! python3 scripts/storm-pod-inventory-ack-gate.py \
  examples/pod-inventory-ack-pass.example.txt \
  --require-pass \
  >"$tmpdir/pod-inventory-ack-pass.out" \
  2>"$tmpdir/pod-inventory-ack-pass.err"; then
  printf 'public_harness_check=fail pod_inventory_ack_pass_failed\n' >&2
  cat "$tmpdir/pod-inventory-ack-pass.err" >&2
  fail=1
elif ! grep -q 'pod_inventory_ack_gate=pass' "$tmpdir/pod-inventory-ack-pass.out" ||
     ! grep -q 'status=stopped' "$tmpdir/pod-inventory-ack-pass.out" ||
     ! grep -q 'no_start_ack=true' "$tmpdir/pod-inventory-ack-pass.out" ||
     ! grep -q 'decision=inventory-ack-accepted-no-compute' "$tmpdir/pod-inventory-ack-pass.out"; then
  printf 'public_harness_check=fail pod_inventory_ack_pass_output\n' >&2
  cat "$tmpdir/pod-inventory-ack-pass.out" >&2
  fail=1
fi

if python3 scripts/storm-pod-inventory-ack-gate.py \
  examples/pod-inventory-ack-hold.example.txt \
  --require-pass \
  >"$tmpdir/pod-inventory-ack-hold.out" \
  2>"$tmpdir/pod-inventory-ack-hold.err"; then
  printf 'public_harness_check=fail pod_inventory_ack_hold_unexpected_pass\n' >&2
  cat "$tmpdir/pod-inventory-ack-hold.out" >&2
  fail=1
elif ! grep -q 'pod_inventory_ack_gate=hold' "$tmpdir/pod-inventory-ack-hold.out" ||
     ! grep -q 'owner_unknown' "$tmpdir/pod-inventory-ack-hold.out" ||
     ! grep -q 'provider_inventory_not_verified' "$tmpdir/pod-inventory-ack-hold.out"; then
  printf 'public_harness_check=fail pod_inventory_ack_hold_output\n' >&2
  cat "$tmpdir/pod-inventory-ack-hold.out" >&2
  cat "$tmpdir/pod-inventory-ack-hold.err" >&2
  fail=1
fi

if python3 scripts/storm-pod-inventory-ack-gate.py \
  examples/pod-inventory-ack-fail.example.txt \
  --require-pass \
  >"$tmpdir/pod-inventory-ack-fail.out" \
  2>"$tmpdir/pod-inventory-ack-fail.err"; then
  printf 'public_harness_check=fail pod_inventory_ack_fail_unexpected_pass\n' >&2
  cat "$tmpdir/pod-inventory-ack-fail.out" >&2
  fail=1
elif ! grep -q 'pod_inventory_ack_gate=fail' "$tmpdir/pod-inventory-ack-fail.out" ||
     ! grep -q 'ownerless_running_pod' "$tmpdir/pod-inventory-ack-fail.out" ||
     ! grep -q 'premature_compute_or_start_request' "$tmpdir/pod-inventory-ack-fail.out" ||
     ! grep -q 'missing_no_start_or_compute_closed_ack' "$tmpdir/pod-inventory-ack-fail.out"; then
  printf 'public_harness_check=fail pod_inventory_ack_fail_output\n' >&2
  cat "$tmpdir/pod-inventory-ack-fail.out" >&2
  cat "$tmpdir/pod-inventory-ack-fail.err" >&2
  fail=1
fi

if ! python3 scripts/storm-pod-inventory-ack-gate.py \
  examples/pod-inventory-ack-account-empty-pass.example.txt \
  --require-pass \
  >"$tmpdir/pod-inventory-ack-account-empty-pass.out" \
  2>"$tmpdir/pod-inventory-ack-account-empty-pass.err"; then
  printf 'public_harness_check=fail pod_inventory_ack_account_empty_pass_failed\n' >&2
  cat "$tmpdir/pod-inventory-ack-account-empty-pass.err" >&2
  fail=1
elif ! grep -q 'pod_inventory_ack_gate=pass' "$tmpdir/pod-inventory-ack-account-empty-pass.out" ||
     ! grep -q 'account_empty=true' "$tmpdir/pod-inventory-ack-account-empty-pass.out" ||
     ! grep -q 'spend_zero=true' "$tmpdir/pod-inventory-ack-account-empty-pass.out" ||
     ! grep -q 'double_read_verified=true' "$tmpdir/pod-inventory-ack-account-empty-pass.out" ||
     ! grep -q 'decision=inventory-ack-accepted-no-compute' "$tmpdir/pod-inventory-ack-account-empty-pass.out"; then
  printf 'public_harness_check=fail pod_inventory_ack_account_empty_pass_output\n' >&2
  cat "$tmpdir/pod-inventory-ack-account-empty-pass.out" >&2
  fail=1
fi

if python3 scripts/storm-pod-inventory-ack-gate.py \
  examples/pod-inventory-ack-account-empty-hold.example.txt \
  --require-pass \
  >"$tmpdir/pod-inventory-ack-account-empty-hold.out" \
  2>"$tmpdir/pod-inventory-ack-account-empty-hold.err"; then
  printf 'public_harness_check=fail pod_inventory_ack_account_empty_hold_unexpected_pass\n' >&2
  cat "$tmpdir/pod-inventory-ack-account-empty-hold.out" >&2
  fail=1
elif ! grep -q 'pod_inventory_ack_gate=hold' "$tmpdir/pod-inventory-ack-account-empty-hold.out" ||
     ! grep -q 'missing_zero_spend_evidence' "$tmpdir/pod-inventory-ack-account-empty-hold.out" ||
     ! grep -q 'missing_double_read_verification' "$tmpdir/pod-inventory-ack-account-empty-hold.out"; then
  printf 'public_harness_check=fail pod_inventory_ack_account_empty_hold_output\n' >&2
  cat "$tmpdir/pod-inventory-ack-account-empty-hold.out" >&2
  cat "$tmpdir/pod-inventory-ack-account-empty-hold.err" >&2
  fail=1
fi

if python3 scripts/storm-pod-inventory-ack-gate.py \
  examples/pod-inventory-ack-account-empty-fail.example.txt \
  --require-pass \
  >"$tmpdir/pod-inventory-ack-account-empty-fail.out" \
  2>"$tmpdir/pod-inventory-ack-account-empty-fail.err"; then
  printf 'public_harness_check=fail pod_inventory_ack_account_empty_fail_unexpected_pass\n' >&2
  cat "$tmpdir/pod-inventory-ack-account-empty-fail.out" >&2
  fail=1
elif ! grep -q 'pod_inventory_ack_gate=fail' "$tmpdir/pod-inventory-ack-account-empty-fail.out" ||
     ! grep -q 'account_empty_nonzero_spend' "$tmpdir/pod-inventory-ack-account-empty-fail.out"; then
  printf 'public_harness_check=fail pod_inventory_ack_account_empty_fail_output\n' >&2
  cat "$tmpdir/pod-inventory-ack-account-empty-fail.out" >&2
  cat "$tmpdir/pod-inventory-ack-account-empty-fail.err" >&2
  fail=1
fi

if ! python3 scripts/storm-candidate-validation-packet-gate.py \
  examples/candidate-validation-packet-pass.example.txt \
  --require-pass \
  >"$tmpdir/candidate-validation-packet-pass.out" \
  2>"$tmpdir/candidate-validation-packet-pass.err"; then
  printf 'public_harness_check=fail candidate_validation_packet_pass_failed\n' >&2
  cat "$tmpdir/candidate-validation-packet-pass.err" >&2
  fail=1
elif ! grep -q 'candidate_validation_packet_gate=pass' "$tmpdir/candidate-validation-packet-pass.out" ||
     ! grep -q 'decision=candidate-for-akash-handoff-no-submit' "$tmpdir/candidate-validation-packet-pass.out" ||
     ! grep -q 'source_base=d44cad3' "$tmpdir/candidate-validation-packet-pass.out" ||
     ! grep -q 'no_submit_ack=true' "$tmpdir/candidate-validation-packet-pass.out"; then
  printf 'public_harness_check=fail candidate_validation_packet_pass_output\n' >&2
  cat "$tmpdir/candidate-validation-packet-pass.out" >&2
  fail=1
fi

if python3 scripts/storm-candidate-validation-packet-gate.py \
  examples/candidate-validation-packet-hold.example.txt \
  --require-pass \
  >"$tmpdir/candidate-validation-packet-hold.out" \
  2>"$tmpdir/candidate-validation-packet-hold.err"; then
  printf 'public_harness_check=fail candidate_validation_packet_hold_unexpected_pass\n' >&2
  cat "$tmpdir/candidate-validation-packet-hold.out" >&2
  fail=1
elif ! grep -q 'candidate_validation_packet_gate=hold' "$tmpdir/candidate-validation-packet-hold.out" ||
     ! grep -q 'missing_remote_host' "$tmpdir/candidate-validation-packet-hold.out" ||
     ! grep -q 'missing_source_base' "$tmpdir/candidate-validation-packet-hold.out" ||
     ! grep -q 'missing_artifact_evidence' "$tmpdir/candidate-validation-packet-hold.out"; then
  printf 'public_harness_check=fail candidate_validation_packet_hold_output\n' >&2
  cat "$tmpdir/candidate-validation-packet-hold.out" >&2
  cat "$tmpdir/candidate-validation-packet-hold.err" >&2
  fail=1
fi

if python3 scripts/storm-candidate-validation-packet-gate.py \
  examples/candidate-validation-packet-fail.example.txt \
  --require-pass \
  >"$tmpdir/candidate-validation-packet-fail.out" \
  2>"$tmpdir/candidate-validation-packet-fail.err"; then
  printf 'public_harness_check=fail candidate_validation_packet_fail_unexpected_pass\n' >&2
  cat "$tmpdir/candidate-validation-packet-fail.out" >&2
  fail=1
elif ! grep -q 'candidate_validation_packet_gate=fail' "$tmpdir/candidate-validation-packet-fail.out" ||
     ! grep -q 'local_validation_packet' "$tmpdir/candidate-validation-packet-fail.out" ||
     ! grep -q 'dirty_cpa_counts' "$tmpdir/candidate-validation-packet-fail.out" ||
     ! grep -q 'missing_no_submit_ack' "$tmpdir/candidate-validation-packet-fail.out"; then
  printf 'public_harness_check=fail candidate_validation_packet_fail_output\n' >&2
  cat "$tmpdir/candidate-validation-packet-fail.out" >&2
  cat "$tmpdir/candidate-validation-packet-fail.err" >&2
  fail=1
fi

if python3 scripts/storm-candidate-validation-packet-gate.py \
  examples/candidate-validation-packet-stale.example.txt \
  --require-pass \
  >"$tmpdir/candidate-validation-packet-stale.out" \
  2>"$tmpdir/candidate-validation-packet-stale.err"; then
  printf 'public_harness_check=fail candidate_validation_packet_stale_unexpected_pass\n' >&2
  cat "$tmpdir/candidate-validation-packet-stale.out" >&2
  fail=1
elif ! grep -q 'candidate_validation_packet_gate=fail' "$tmpdir/candidate-validation-packet-stale.out" ||
     ! grep -q 'stale_source_base' "$tmpdir/candidate-validation-packet-stale.out" ||
     ! grep -q 'source_base=58866a2' "$tmpdir/candidate-validation-packet-stale.out"; then
  printf 'public_harness_check=fail candidate_validation_packet_stale_output\n' >&2
  cat "$tmpdir/candidate-validation-packet-stale.out" >&2
  cat "$tmpdir/candidate-validation-packet-stale.err" >&2
  fail=1
fi

if ! python3 scripts/storm-apply-cswap-support-gate.py \
  examples/apply-cswap-support-pass.example.txt \
  --require-pass \
  >"$tmpdir/apply-cswap-support-pass.out" \
  2>"$tmpdir/apply-cswap-support-pass.err"; then
  printf 'public_harness_check=fail apply_cswap_support_pass_failed\n' >&2
  cat "$tmpdir/apply-cswap-support-pass.err" >&2
  fail=1
elif ! grep -q 'apply_cswap_support_gate=pass' "$tmpdir/apply-cswap-support-pass.out" ||
     ! grep -q 'exact_scope=true' "$tmpdir/apply-cswap-support-pass.out" ||
     ! grep -q 'route_id=apply-cswap-step-bit-proof' "$tmpdir/apply-cswap-support-pass.out" ||
     ! grep -q 'frontier_score=1571592960.0' "$tmpdir/apply-cswap-support-pass.out" ||
     ! grep -q 'qubits=1152' "$tmpdir/apply-cswap-support-pass.out" ||
     ! grep -q 'evidence_label=Partial' "$tmpdir/apply-cswap-support-pass.out" ||
     ! grep -q 'invariants=swp_zero' "$tmpdir/apply-cswap-support-pass.out" ||
     ! grep -q 'ready-for-source-proof-review-no-submit' "$tmpdir/apply-cswap-support-pass.out"; then
  printf 'public_harness_check=fail apply_cswap_support_pass_output\n' >&2
  cat "$tmpdir/apply-cswap-support-pass.out" >&2
  fail=1
fi

if python3 scripts/storm-apply-cswap-support-gate.py \
  examples/apply-cswap-support-hold.example.txt \
  --require-pass \
  >"$tmpdir/apply-cswap-support-hold.out" \
  2>"$tmpdir/apply-cswap-support-hold.err"; then
  printf 'public_harness_check=fail apply_cswap_support_hold_unexpected_pass\n' >&2
  cat "$tmpdir/apply-cswap-support-hold.out" >&2
  fail=1
elif ! grep -q 'apply_cswap_support_gate=hold' "$tmpdir/apply-cswap-support-hold.out" ||
     ! grep -q 'missing_per_step_per_bit_scope' "$tmpdir/apply-cswap-support-hold.out" ||
     ! grep -q 'missing_source_hash_bound_certificate' "$tmpdir/apply-cswap-support-hold.out" ||
     ! grep -q 'support_unknown' "$tmpdir/apply-cswap-support-hold.out"; then
  printf 'public_harness_check=fail apply_cswap_support_hold_output\n' >&2
  cat "$tmpdir/apply-cswap-support-hold.out" >&2
  cat "$tmpdir/apply-cswap-support-hold.err" >&2
  fail=1
fi

if python3 scripts/storm-apply-cswap-support-gate.py \
  examples/apply-cswap-support-fail.example.txt \
  --require-pass \
  >"$tmpdir/apply-cswap-support-fail.out" \
  2>"$tmpdir/apply-cswap-support-fail.err"; then
  printf 'public_harness_check=fail apply_cswap_support_fail_unexpected_pass\n' >&2
  cat "$tmpdir/apply-cswap-support-fail.out" >&2
  fail=1
elif ! grep -q 'apply_cswap_support_gate=fail' "$tmpdir/apply-cswap-support-fail.out" ||
     ! grep -q 'broad_cswap_delete_scope' "$tmpdir/apply-cswap-support-fail.out" ||
     ! grep -q 'support_counterexample' "$tmpdir/apply-cswap-support-fail.out" ||
     ! grep -q 'premature_compute_request' "$tmpdir/apply-cswap-support-fail.out" ||
     ! grep -q 'support_packet_overclaims_full_run' "$tmpdir/apply-cswap-support-fail.out" ||
     ! grep -q 'premature_submit_or_akash_language' "$tmpdir/apply-cswap-support-fail.out"; then
  printf 'public_harness_check=fail apply_cswap_support_fail_output\n' >&2
  cat "$tmpdir/apply-cswap-support-fail.out" >&2
  cat "$tmpdir/apply-cswap-support-fail.err" >&2
  fail=1
fi

if python3 scripts/storm-apply-cswap-support-gate.py \
  examples/apply-cswap-support-stale.example.txt \
  --require-pass \
  >"$tmpdir/apply-cswap-support-stale.out" \
  2>"$tmpdir/apply-cswap-support-stale.err"; then
  printf 'public_harness_check=fail apply_cswap_support_stale_unexpected_pass\n' >&2
  cat "$tmpdir/apply-cswap-support-stale.out" >&2
  fail=1
elif ! grep -q 'apply_cswap_support_gate=fail' "$tmpdir/apply-cswap-support-stale.out" ||
     ! grep -q 'stale_source_base' "$tmpdir/apply-cswap-support-stale.out" ||
     ! grep -q 'source_base=deadbee' "$tmpdir/apply-cswap-support-stale.out"; then
  printf 'public_harness_check=fail apply_cswap_support_stale_output\n' >&2
  cat "$tmpdir/apply-cswap-support-stale.out" >&2
  cat "$tmpdir/apply-cswap-support-stale.err" >&2
  fail=1
fi

if ! python3 scripts/storm-source-packet-novelty-gate.py \
  examples/source-packet-novelty-pass.example.txt \
  --require-pass \
  >"$tmpdir/source-packet-novelty-pass.out" \
  2>"$tmpdir/source-packet-novelty-pass.err"; then
  printf 'public_harness_check=fail source_packet_novelty_pass_failed\n' >&2
  cat "$tmpdir/source-packet-novelty-pass.err" >&2
  fail=1
elif ! grep -q 'source_packet_novelty_gate=pass' "$tmpdir/source-packet-novelty-pass.out" ||
     ! grep -q 'outside_closed_ledger=true' "$tmpdir/source-packet-novelty-pass.out" ||
     ! grep -q 'support_status=UNKNOWN' "$tmpdir/source-packet-novelty-pass.out" ||
     ! grep -q 'decision=admit-one-bounded-source-proof-no-compute' "$tmpdir/source-packet-novelty-pass.out"; then
  printf 'public_harness_check=fail source_packet_novelty_pass_output\n' >&2
  cat "$tmpdir/source-packet-novelty-pass.out" >&2
  fail=1
fi

if ! python3 scripts/storm-source-packet-novelty-gate.py \
  examples/source-packet-novelty-arith-pass.example.txt \
  --require-pass \
  >"$tmpdir/source-packet-novelty-arith-pass.out" \
  2>"$tmpdir/source-packet-novelty-arith-pass.err"; then
  printf 'public_harness_check=fail source_packet_novelty_arith_pass_failed\n' >&2
  cat "$tmpdir/source-packet-novelty-arith-pass.err" >&2
  fail=1
elif ! grep -q 'source_packet_novelty_gate=pass' "$tmpdir/source-packet-novelty-arith-pass.out" ||
     ! grep -q 'source_location=src/point_add/arith.rs:1322' "$tmpdir/source-packet-novelty-arith-pass.out" ||
     ! grep -q 'decision=admit-one-bounded-source-proof-no-compute' "$tmpdir/source-packet-novelty-arith-pass.out"; then
  printf 'public_harness_check=fail source_packet_novelty_arith_pass_output\n' >&2
  cat "$tmpdir/source-packet-novelty-arith-pass.out" >&2
  fail=1
fi

if python3 scripts/storm-source-packet-novelty-gate.py \
  examples/source-packet-novelty-hold.example.txt \
  --require-pass \
  >"$tmpdir/source-packet-novelty-hold.out" \
  2>"$tmpdir/source-packet-novelty-hold.err"; then
  printf 'public_harness_check=fail source_packet_novelty_hold_unexpected_pass\n' >&2
  cat "$tmpdir/source-packet-novelty-hold.out" >&2
  fail=1
elif ! grep -q 'source_packet_novelty_gate=hold' "$tmpdir/source-packet-novelty-hold.out" ||
     ! grep -q 'missing_source_hash_bound_context' "$tmpdir/source-packet-novelty-hold.out" ||
     ! grep -q 'missing_novelty_status_new_or_outside_closed_ledger' "$tmpdir/source-packet-novelty-hold.out" ||
     ! grep -q 'novelty_unknown' "$tmpdir/source-packet-novelty-hold.out"; then
  printf 'public_harness_check=fail source_packet_novelty_hold_output\n' >&2
  cat "$tmpdir/source-packet-novelty-hold.out" >&2
  cat "$tmpdir/source-packet-novelty-hold.err" >&2
  fail=1
fi

if python3 scripts/storm-source-packet-novelty-gate.py \
  examples/source-packet-novelty-fail.example.txt \
  --require-pass \
  >"$tmpdir/source-packet-novelty-fail.out" \
  2>"$tmpdir/source-packet-novelty-fail.err"; then
  printf 'public_harness_check=fail source_packet_novelty_fail_unexpected_pass\n' >&2
  cat "$tmpdir/source-packet-novelty-fail.out" >&2
  fail=1
elif ! grep -q 'source_packet_novelty_gate=fail' "$tmpdir/source-packet-novelty-fail.out" ||
     ! grep -q 'source_counterexample_or_ledger_hit' "$tmpdir/source-packet-novelty-fail.out" ||
     ! grep -q 'all_current_unknowns_closed' "$tmpdir/source-packet-novelty-fail.out" ||
     ! grep -q 'next_unclosed_empty_without_new_packet' "$tmpdir/source-packet-novelty-fail.out" ||
     ! grep -q 'premature_compute_request' "$tmpdir/source-packet-novelty-fail.out"; then
  printf 'public_harness_check=fail source_packet_novelty_fail_output\n' >&2
  cat "$tmpdir/source-packet-novelty-fail.out" >&2
  cat "$tmpdir/source-packet-novelty-fail.err" >&2
  fail=1
fi

if python3 scripts/storm-source-packet-novelty-gate.py \
  examples/source-packet-novelty-family-exhausted.example.txt \
  --require-pass \
  >"$tmpdir/source-packet-novelty-family-exhausted.out" \
  2>"$tmpdir/source-packet-novelty-family-exhausted.err"; then
  printf 'public_harness_check=fail source_packet_novelty_family_exhausted_unexpected_pass\n' >&2
  cat "$tmpdir/source-packet-novelty-family-exhausted.out" >&2
  fail=1
elif ! grep -q 'source_packet_novelty_gate=fail' "$tmpdir/source-packet-novelty-family-exhausted.out" ||
     ! grep -q 'source_family_exhausted=true' "$tmpdir/source-packet-novelty-family-exhausted.out" ||
     ! grep -q 'source_family_exhausted' "$tmpdir/source-packet-novelty-family-exhausted.out" ||
     ! grep -q 'summary_total=71' "$tmpdir/source-packet-novelty-family-exhausted.out" ||
     ! grep -q 'open_after=0' "$tmpdir/source-packet-novelty-family-exhausted.out" ||
     ! grep -q 'open_digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' "$tmpdir/source-packet-novelty-family-exhausted.out"; then
  printf 'public_harness_check=fail source_packet_novelty_family_exhausted_output\n' >&2
  cat "$tmpdir/source-packet-novelty-family-exhausted.out" >&2
  cat "$tmpdir/source-packet-novelty-family-exhausted.err" >&2
  fail=1
fi

if python3 scripts/storm-source-packet-novelty-gate.py \
  examples/source-packet-novelty-stale.example.txt \
  --require-pass \
  >"$tmpdir/source-packet-novelty-stale.out" \
  2>"$tmpdir/source-packet-novelty-stale.err"; then
  printf 'public_harness_check=fail source_packet_novelty_stale_unexpected_pass\n' >&2
  cat "$tmpdir/source-packet-novelty-stale.out" >&2
  fail=1
elif ! grep -q 'source_packet_novelty_gate=fail' "$tmpdir/source-packet-novelty-stale.out" ||
     ! grep -q 'stale_source_base' "$tmpdir/source-packet-novelty-stale.out" ||
     ! grep -q 'source_base=58866a2' "$tmpdir/source-packet-novelty-stale.out"; then
  printf 'public_harness_check=fail source_packet_novelty_stale_output\n' >&2
  cat "$tmpdir/source-packet-novelty-stale.out" >&2
  cat "$tmpdir/source-packet-novelty-stale.err" >&2
  fail=1
fi

if ! python3 scripts/storm-source-row-routing-gate.py \
  examples/source-row-routing-packet.example.txt \
  --require-pass \
  >"$tmpdir/source-row-routing-packet.out" \
  2>"$tmpdir/source-row-routing-packet.err"; then
  printf 'public_harness_check=fail source_row_routing_packet_failed\n' >&2
  cat "$tmpdir/source-row-routing-packet.err" >&2
  fail=1
elif ! grep -q 'source_row_routing_gate=pass' "$tmpdir/source-row-routing-packet.out" ||
     ! grep -q 'packet=true' "$tmpdir/source-row-routing-packet.out" ||
     ! grep -q 'closure=false' "$tmpdir/source-row-routing-packet.out" ||
     ! grep -q 'decision=source-row-packet-ready-no-compute' "$tmpdir/source-row-routing-packet.out"; then
  printf 'public_harness_check=fail source_row_routing_packet_output\n' >&2
  cat "$tmpdir/source-row-routing-packet.out" >&2
  fail=1
fi

if ! python3 scripts/storm-source-row-routing-gate.py \
  examples/source-row-routing-closure.example.txt \
  --require-pass \
  >"$tmpdir/source-row-routing-closure.out" \
  2>"$tmpdir/source-row-routing-closure.err"; then
  printf 'public_harness_check=fail source_row_routing_closure_failed\n' >&2
  cat "$tmpdir/source-row-routing-closure.err" >&2
  fail=1
elif ! grep -q 'source_row_routing_gate=pass' "$tmpdir/source-row-routing-closure.out" ||
     ! grep -q 'packet=false' "$tmpdir/source-row-routing-closure.out" ||
     ! grep -q 'closure=true' "$tmpdir/source-row-routing-closure.out" ||
     ! grep -q 'decision=source-row-closed-advance-next-no-compute' "$tmpdir/source-row-routing-closure.out"; then
  printf 'public_harness_check=fail source_row_routing_closure_output\n' >&2
  cat "$tmpdir/source-row-routing-closure.out" >&2
  fail=1
fi

if python3 scripts/storm-source-row-routing-gate.py \
  examples/source-row-routing-hold.example.txt \
  --require-pass \
  >"$tmpdir/source-row-routing-hold.out" \
  2>"$tmpdir/source-row-routing-hold.err"; then
  printf 'public_harness_check=fail source_row_routing_hold_unexpected_pass\n' >&2
  cat "$tmpdir/source-row-routing-hold.out" >&2
  fail=1
elif ! grep -q 'source_row_routing_gate=hold' "$tmpdir/source-row-routing-hold.out" ||
     ! grep -q 'closure_missing_proof_counterexample' "$tmpdir/source-row-routing-hold.out" ||
     ! grep -q 'missing_closure_reason_or_artifact' "$tmpdir/source-row-routing-hold.out" ||
     ! grep -q 'missing_next_source_row' "$tmpdir/source-row-routing-hold.out"; then
  printf 'public_harness_check=fail source_row_routing_hold_output\n' >&2
  cat "$tmpdir/source-row-routing-hold.out" >&2
  cat "$tmpdir/source-row-routing-hold.err" >&2
  fail=1
fi

if python3 scripts/storm-source-row-routing-gate.py \
  examples/source-row-routing-fail.example.txt \
  --require-pass \
  >"$tmpdir/source-row-routing-fail.out" \
  2>"$tmpdir/source-row-routing-fail.err"; then
  printf 'public_harness_check=fail source_row_routing_fail_unexpected_pass\n' >&2
  cat "$tmpdir/source-row-routing-fail.out" >&2
  fail=1
elif ! grep -q 'source_row_routing_gate=fail' "$tmpdir/source-row-routing-fail.out" ||
     ! grep -q 'premature_compute_request' "$tmpdir/source-row-routing-fail.out"; then
  printf 'public_harness_check=fail source_row_routing_fail_output\n' >&2
  cat "$tmpdir/source-row-routing-fail.out" >&2
  cat "$tmpdir/source-row-routing-fail.err" >&2
  fail=1
fi

if ! python3 scripts/storm-transcript-overlap-gate.py \
  examples/transcript-overlap-pass.example.txt \
  --require-pass \
  >"$tmpdir/transcript-overlap-pass.out" \
  2>"$tmpdir/transcript-overlap-pass.err"; then
  printf 'public_harness_check=fail transcript_overlap_pass_failed\n' >&2
  cat "$tmpdir/transcript-overlap-pass.err" >&2
  fail=1
elif ! grep -q 'transcript_overlap_gate=pass' "$tmpdir/transcript-overlap-pass.out" ||
     ! grep -q 'score_edge_ok=true' "$tmpdir/transcript-overlap-pass.out" ||
     ! grep -q 'source_hash_bound=true' "$tmpdir/transcript-overlap-pass.out" ||
     ! grep -q 'exact_support=true' "$tmpdir/transcript-overlap-pass.out" ||
     ! grep -q 'decision=source-theorem-review-no-compute' "$tmpdir/transcript-overlap-pass.out"; then
  printf 'public_harness_check=fail transcript_overlap_pass_output\n' >&2
  cat "$tmpdir/transcript-overlap-pass.out" >&2
  fail=1
fi

if python3 scripts/storm-transcript-overlap-gate.py \
  examples/transcript-overlap-hold.example.txt \
  --require-pass \
  >"$tmpdir/transcript-overlap-hold.out" \
  2>"$tmpdir/transcript-overlap-hold.err"; then
  printf 'public_harness_check=fail transcript_overlap_hold_unexpected_pass\n' >&2
  cat "$tmpdir/transcript-overlap-hold.out" >&2
  fail=1
elif ! grep -q 'transcript_overlap_gate=hold' "$tmpdir/transcript-overlap-hold.out" ||
     ! grep -q 'missing_source_hash_bound_context' "$tmpdir/transcript-overlap-hold.out" ||
     ! grep -q 'missing_exact_support_certified' "$tmpdir/transcript-overlap-hold.out" ||
     ! grep -q 'missing_score_edge' "$tmpdir/transcript-overlap-hold.out"; then
  printf 'public_harness_check=fail transcript_overlap_hold_output\n' >&2
  cat "$tmpdir/transcript-overlap-hold.out" >&2
  cat "$tmpdir/transcript-overlap-hold.err" >&2
  fail=1
fi

if python3 scripts/storm-transcript-overlap-gate.py \
  examples/transcript-overlap-fail.example.txt \
  --require-pass \
  >"$tmpdir/transcript-overlap-fail.out" \
  2>"$tmpdir/transcript-overlap-fail.err"; then
  printf 'public_harness_check=fail transcript_overlap_fail_unexpected_pass\n' >&2
  cat "$tmpdir/transcript-overlap-fail.out" >&2
  fail=1
elif ! grep -q 'transcript_overlap_gate=fail' "$tmpdir/transcript-overlap-fail.out" ||
     ! grep -q 'dirty_bounded_probe' "$tmpdir/transcript-overlap-fail.out" ||
     ! grep -q 'stale_index_warnings' "$tmpdir/transcript-overlap-fail.out" ||
     ! grep -q 'active_only_origin_map' "$tmpdir/transcript-overlap-fail.out" ||
     ! grep -q 'score_no_edge' "$tmpdir/transcript-overlap-fail.out" ||
     ! grep -q 'missing_required_peak_calls' "$tmpdir/transcript-overlap-fail.out"; then
  printf 'public_harness_check=fail transcript_overlap_fail_output\n' >&2
  cat "$tmpdir/transcript-overlap-fail.out" >&2
  cat "$tmpdir/transcript-overlap-fail.err" >&2
  fail=1
fi

if python3 scripts/storm-transcript-overlap-gate.py \
  examples/transcript-overlap-stale.example.txt \
  --require-pass \
  >"$tmpdir/transcript-overlap-stale.out" \
  2>"$tmpdir/transcript-overlap-stale.err"; then
  printf 'public_harness_check=fail transcript_overlap_stale_unexpected_pass\n' >&2
  cat "$tmpdir/transcript-overlap-stale.out" >&2
  fail=1
elif ! grep -q 'transcript_overlap_gate=fail' "$tmpdir/transcript-overlap-stale.out" ||
     ! grep -q 'stale_source_base' "$tmpdir/transcript-overlap-stale.out" ||
     ! grep -q 'source_base=58866a2' "$tmpdir/transcript-overlap-stale.out"; then
  printf 'public_harness_check=fail transcript_overlap_stale_output\n' >&2
  cat "$tmpdir/transcript-overlap-stale.out" >&2
  cat "$tmpdir/transcript-overlap-stale.err" >&2
  fail=1
fi

if ! python3 scripts/storm-ffg-pair-proof-gate.py \
  examples/ffg-pair-proof-pass.example.txt \
  --require-pass \
  >"$tmpdir/ffg-pair-proof-pass.out" \
  2>"$tmpdir/ffg-pair-proof-pass.err"; then
  printf 'public_harness_check=fail ffg_pair_proof_pass_failed\n' >&2
  cat "$tmpdir/ffg-pair-proof-pass.err" >&2
  fail=1
elif ! grep -q 'ffg_pair_proof_gate=pass' "$tmpdir/ffg-pair-proof-pass.out" ||
     ! grep -q 'pair_complete=true' "$tmpdir/ffg-pair-proof-pass.out" ||
     ! grep -q 'source_hash_bound=true' "$tmpdir/ffg-pair-proof-pass.out" ||
     ! grep -q 'candidate_hash_bound=true' "$tmpdir/ffg-pair-proof-pass.out" ||
     ! grep -q 'route_compare_admission=pass' "$tmpdir/ffg-pair-proof-pass.out" ||
     ! grep -q 'admitted=1' "$tmpdir/ffg-pair-proof-pass.out" ||
     ! grep -q 'decision=source-bound-ffg-proof-review-no-compute' "$tmpdir/ffg-pair-proof-pass.out"; then
  printf 'public_harness_check=fail ffg_pair_proof_pass_output\n' >&2
  cat "$tmpdir/ffg-pair-proof-pass.out" >&2
  fail=1
fi

if python3 scripts/storm-ffg-pair-proof-gate.py \
  examples/ffg-pair-proof-hold.example.txt \
  --require-pass \
  >"$tmpdir/ffg-pair-proof-hold.out" \
  2>"$tmpdir/ffg-pair-proof-hold.err"; then
  printf 'public_harness_check=fail ffg_pair_proof_hold_unexpected_pass\n' >&2
  cat "$tmpdir/ffg-pair-proof-hold.out" >&2
  fail=1
elif ! grep -q 'ffg_pair_proof_gate=hold' "$tmpdir/ffg-pair-proof-hold.out" ||
     ! grep -q 'missing_candidate_hash' "$tmpdir/ffg-pair-proof-hold.out" ||
     ! grep -q 'candidate_hash_bound=false' "$tmpdir/ffg-pair-proof-hold.out"; then
  printf 'public_harness_check=fail ffg_pair_proof_hold_output\n' >&2
  cat "$tmpdir/ffg-pair-proof-hold.out" >&2
  cat "$tmpdir/ffg-pair-proof-hold.err" >&2
  fail=1
fi

if python3 scripts/storm-ffg-pair-proof-gate.py \
  examples/ffg-pair-proof-fail.example.txt \
  --require-pass \
  >"$tmpdir/ffg-pair-proof-fail.out" \
  2>"$tmpdir/ffg-pair-proof-fail.err"; then
  printf 'public_harness_check=fail ffg_pair_proof_fail_unexpected_pass\n' >&2
  cat "$tmpdir/ffg-pair-proof-fail.out" >&2
  fail=1
elif ! grep -q 'ffg_pair_proof_gate=fail' "$tmpdir/ffg-pair-proof-fail.out" ||
     ! grep -q 'missing_required_ffg_calls' "$tmpdir/ffg-pair-proof-fail.out" ||
     ! grep -q 'route_compare_not_pass' "$tmpdir/ffg-pair-proof-fail.out" ||
     ! grep -q 'route_compare_shots_below_min' "$tmpdir/ffg-pair-proof-fail.out" ||
     ! grep -q 'wrong_qubit_tier' "$tmpdir/ffg-pair-proof-fail.out" ||
     ! grep -q 'score_no_edge' "$tmpdir/ffg-pair-proof-fail.out"; then
  printf 'public_harness_check=fail ffg_pair_proof_fail_output\n' >&2
  cat "$tmpdir/ffg-pair-proof-fail.out" >&2
  cat "$tmpdir/ffg-pair-proof-fail.err" >&2
  fail=1
fi

if ! python3 scripts/storm-compute-unlock-gate.py \
  examples/compute-unlock-pass.example.txt \
  --require-pass \
  >"$tmpdir/compute-unlock-pass.out" \
  2>"$tmpdir/compute-unlock-pass.err"; then
  printf 'public_harness_check=fail compute_unlock_pass_failed\n' >&2
  cat "$tmpdir/compute-unlock-pass.err" >&2
  fail=1
elif ! grep -q 'compute_unlock_gate=pass' "$tmpdir/compute-unlock-pass.out" ||
     ! grep -q 'storm_route_ack=true' "$tmpdir/compute-unlock-pass.out" ||
     ! grep -q 'source_hash_bound=true' "$tmpdir/compute-unlock-pass.out" ||
     ! grep -q 'value_exact=true' "$tmpdir/compute-unlock-pass.out" ||
     ! grep -q 'certified=true' "$tmpdir/compute-unlock-pass.out" ||
     ! grep -q 'decision=compute-unlock-ready-for-storm-dispatch-no-submit' "$tmpdir/compute-unlock-pass.out"; then
  printf 'public_harness_check=fail compute_unlock_pass_output\n' >&2
  cat "$tmpdir/compute-unlock-pass.out" >&2
  fail=1
fi

if python3 scripts/storm-compute-unlock-gate.py \
  examples/compute-unlock-hold.example.txt \
  --require-pass \
  >"$tmpdir/compute-unlock-hold.out" \
  2>"$tmpdir/compute-unlock-hold.err"; then
  printf 'public_harness_check=fail compute_unlock_hold_unexpected_pass\n' >&2
  cat "$tmpdir/compute-unlock-hold.out" >&2
  fail=1
elif ! grep -q 'compute_unlock_gate=hold' "$tmpdir/compute-unlock-hold.out" ||
     ! grep -q 'missing_compute_request' "$tmpdir/compute-unlock-hold.out" ||
     ! grep -q 'missing_storm_route_ack' "$tmpdir/compute-unlock-hold.out" ||
     ! grep -q 'missing_budget' "$tmpdir/compute-unlock-hold.out" ||
     ! grep -q 'missing_stop_condition' "$tmpdir/compute-unlock-hold.out"; then
  printf 'public_harness_check=fail compute_unlock_hold_output\n' >&2
  cat "$tmpdir/compute-unlock-hold.out" >&2
  cat "$tmpdir/compute-unlock-hold.err" >&2
  fail=1
fi

if python3 scripts/storm-compute-unlock-gate.py \
  examples/compute-unlock-fail.example.txt \
  --require-pass \
  >"$tmpdir/compute-unlock-fail.out" \
  2>"$tmpdir/compute-unlock-fail.err"; then
  printf 'public_harness_check=fail compute_unlock_fail_unexpected_pass\n' >&2
  cat "$tmpdir/compute-unlock-fail.out" >&2
  fail=1
elif ! grep -q 'compute_unlock_gate=fail' "$tmpdir/compute-unlock-fail.out" ||
     ! grep -q 'compute_closed_without_unlock_packet' "$tmpdir/compute-unlock-fail.out" ||
     ! grep -q 'prefilter_is_not_compute_unlock' "$tmpdir/compute-unlock-fail.out" ||
     ! grep -q 'dirty_or_failed_validation_evidence' "$tmpdir/compute-unlock-fail.out" ||
     ! grep -q 'missing_storm_route_ack' "$tmpdir/compute-unlock-fail.out"; then
  printf 'public_harness_check=fail compute_unlock_fail_output\n' >&2
  cat "$tmpdir/compute-unlock-fail.out" >&2
  cat "$tmpdir/compute-unlock-fail.err" >&2
  fail=1
fi

if python3 scripts/storm-compute-unlock-gate.py \
  examples/compute-unlock-stale.example.txt \
  --require-pass \
  >"$tmpdir/compute-unlock-stale.out" \
  2>"$tmpdir/compute-unlock-stale.err"; then
  printf 'public_harness_check=fail compute_unlock_stale_unexpected_pass\n' >&2
  cat "$tmpdir/compute-unlock-stale.out" >&2
  fail=1
elif ! grep -q 'compute_unlock_gate=fail' "$tmpdir/compute-unlock-stale.out" ||
     ! grep -q 'stale_source_base' "$tmpdir/compute-unlock-stale.out" ||
     ! grep -q 'source_base=58866a2' "$tmpdir/compute-unlock-stale.out"; then
  printf 'public_harness_check=fail compute_unlock_stale_output\n' >&2
  cat "$tmpdir/compute-unlock-stale.out" >&2
  cat "$tmpdir/compute-unlock-stale.err" >&2
  fail=1
fi

python3 scripts/storm-claim-ledger.py append \
  --ledger "$tmpdir/claim-ledger.jsonl" \
  --agent Storm-Codex \
  --kind NACK \
  --lane q1152-fanout \
  --skill redsky \
  --file coord.md \
  --next keep-validating \
  --evidence-label Prefilter \
  --proof-status N/A \
  --frontier d44cad3/q1152/1571592960 >"$tmpdir/claim-ledger-append.out" 2>"$tmpdir/claim-ledger-append.err" || {
    printf 'public_harness_check=fail claim_ledger_append_failed\n' >&2
    cat "$tmpdir/claim-ledger-append.err" >&2
    fail=1
  }
if ! python3 scripts/storm-claim-ledger.py validate \
  --ledger "$tmpdir/claim-ledger.jsonl" >"$tmpdir/claim-ledger-validate.out" 2>"$tmpdir/claim-ledger-validate.err"; then
  printf 'public_harness_check=fail claim_ledger_validate_failed\n' >&2
  cat "$tmpdir/claim-ledger-validate.err" >&2
  fail=1
elif ! grep -q 'claim_ledger=pass rows=1' "$tmpdir/claim-ledger-validate.out"; then
  printf 'public_harness_check=fail claim_ledger_validate_output\n' >&2
  cat "$tmpdir/claim-ledger-validate.out" >&2
  fail=1
fi
cat >"$tmpdir/claim-ledger-missing-frontier.jsonl" <<'EOF'
{"agent":"Storm-Codex","evidence_label":"Local full run","file":"coord.md","frontier":"","kind":"CLAIM","lane":"candidate","next":"fresh-frontier","no_submit_ack":"yes","proof_status":"CERTIFIED","skill":"validation-submit-gate","timestamp":"2026-06-28T00:00:00Z"}
EOF
if python3 scripts/storm-claim-ledger.py validate \
  --ledger "$tmpdir/claim-ledger-missing-frontier.jsonl" >"$tmpdir/claim-ledger-missing-frontier.out" 2>"$tmpdir/claim-ledger-missing-frontier.err"; then
  printf 'public_harness_check=fail claim_ledger_missing_frontier_should_fail\n' >&2
  cat "$tmpdir/claim-ledger-missing-frontier.out" >&2
  fail=1
elif ! grep -q 'Local full run requires frontier' "$tmpdir/claim-ledger-missing-frontier.err" ||
     ! grep -q 'CERTIFIED proof_status requires frontier' "$tmpdir/claim-ledger-missing-frontier.err"; then
  printf 'public_harness_check=fail claim_ledger_missing_frontier_output\n' >&2
  cat "$tmpdir/claim-ledger-missing-frontier.out" >&2
  cat "$tmpdir/claim-ledger-missing-frontier.err" >&2
  fail=1
fi

cat >"$tmpdir/claim-ledger-local-full-ready.jsonl" <<'EOF'
{"agent":"Storm-Codex","ancilla":0,"avg_toffoli":"1364228.0","candidate_score":1571590656,"classical":0,"evidence_label":"Local full run","file":"score.json","frontier":"d44cad3/q1152/1571592960","frontier_score":1571592960,"kind":"CLAIM","lane":"candidate","next":"fresh-frontier","no_submit_ack":"yes","phase":0,"proof_status":"CERTIFIED","qubits":1152,"skill":"validation-submit-gate","timestamp":"2026-06-28T00:00:00Z"}
EOF
if ! python3 scripts/storm-claim-ledger.py validate \
  --ledger "$tmpdir/claim-ledger-local-full-ready.jsonl" >"$tmpdir/claim-ledger-local-full-ready.out" 2>"$tmpdir/claim-ledger-local-full-ready.err"; then
  printf 'public_harness_check=fail claim_ledger_local_full_ready_failed\n' >&2
  cat "$tmpdir/claim-ledger-local-full-ready.err" >&2
  fail=1
fi
if ! python3 scripts/storm-claim-ledger.py summary \
  --ledger "$tmpdir/claim-ledger-local-full-ready.jsonl" >"$tmpdir/claim-ledger-local-full-ready-summary.out" 2>"$tmpdir/claim-ledger-local-full-ready-summary.err"; then
  printf 'public_harness_check=fail claim_ledger_local_full_ready_summary_failed\n' >&2
  cat "$tmpdir/claim-ledger-local-full-ready-summary.err" >&2
  fail=1
elif ! grep -q 'local_full_submit_ready=1' "$tmpdir/claim-ledger-local-full-ready-summary.out"; then
  printf 'public_harness_check=fail claim_ledger_local_full_ready_summary_output\n' >&2
  cat "$tmpdir/claim-ledger-local-full-ready-summary.out" >&2
  fail=1
fi

cat >"$tmpdir/claim-ledger-local-full-dirty.jsonl" <<'EOF'
{"agent":"Storm-Codex","ancilla":0,"avg_toffoli":"1364228.0","candidate_score":1571590656,"classical":0,"evidence_label":"Local full run","file":"score.json","frontier":"d44cad3/q1152/1571592960","frontier_score":1571592960,"kind":"CLAIM","lane":"candidate","next":"fresh-frontier","no_submit_ack":"yes","phase":1,"proof_status":"CERTIFIED","qubits":1152,"skill":"validation-submit-gate","timestamp":"2026-06-28T00:00:00Z"}
EOF
if python3 scripts/storm-claim-ledger.py validate \
  --ledger "$tmpdir/claim-ledger-local-full-dirty.jsonl" >"$tmpdir/claim-ledger-local-full-dirty.out" 2>"$tmpdir/claim-ledger-local-full-dirty.err"; then
  printf 'public_harness_check=fail claim_ledger_local_full_dirty_should_fail\n' >&2
  cat "$tmpdir/claim-ledger-local-full-dirty.out" >&2
  fail=1
elif ! grep -q 'Local full run requires classical/phase/ancilla all zero' "$tmpdir/claim-ledger-local-full-dirty.err"; then
  printf 'public_harness_check=fail claim_ledger_local_full_dirty_output\n' >&2
  cat "$tmpdir/claim-ledger-local-full-dirty.out" >&2
  cat "$tmpdir/claim-ledger-local-full-dirty.err" >&2
  fail=1
fi

if ! python3 scripts/storm-bluesky-redsky-loop-gate.py \
  examples/bluesky-redsky-loop-pass.example.json \
  --require-implemented >"$tmpdir/bluesky-redsky-loop-pass.out" 2>"$tmpdir/bluesky-redsky-loop-pass.err"; then
  printf 'public_harness_check=fail bluesky_redsky_loop_pass_failed\n' >&2
  cat "$tmpdir/bluesky-redsky-loop-pass.out" >&2
  cat "$tmpdir/bluesky-redsky-loop-pass.err" >&2
  fail=1
elif ! grep -q 'bluesky_redsky_loop_gate=pass' "$tmpdir/bluesky-redsky-loop-pass.out" ||
     ! grep -q 'loops=5' "$tmpdir/bluesky-redsky-loop-pass.out" ||
     ! grep -q 'implemented=5' "$tmpdir/bluesky-redsky-loop-pass.out" ||
     ! grep -q 'verified=5' "$tmpdir/bluesky-redsky-loop-pass.out" ||
     ! grep -q 'compute_dispatch_allowed=0' "$tmpdir/bluesky-redsky-loop-pass.out" ||
     ! grep -q 'submit_language_allowed=0' "$tmpdir/bluesky-redsky-loop-pass.out"; then
  printf 'public_harness_check=fail bluesky_redsky_loop_pass_output\n' >&2
  cat "$tmpdir/bluesky-redsky-loop-pass.out" >&2
  fail=1
fi

if python3 scripts/storm-bluesky-redsky-loop-gate.py \
  examples/bluesky-redsky-loop-overclaim.example.json \
  --exact-loops 1 \
  --require-implemented >"$tmpdir/bluesky-redsky-loop-overclaim.out" 2>"$tmpdir/bluesky-redsky-loop-overclaim.err"; then
  printf 'public_harness_check=fail bluesky_redsky_loop_overclaim_should_fail\n' >&2
  cat "$tmpdir/bluesky-redsky-loop-overclaim.out" >&2
  fail=1
elif ! grep -q 'bluesky_redsky_loop_gate=fail' "$tmpdir/bluesky-redsky-loop-overclaim.out" ||
     ! grep -q 'submit language requires Local full run evidence' "$tmpdir/bluesky-redsky-loop-overclaim.err" ||
     ! grep -q 'submit language missing true fresh_frontier_recheck' "$tmpdir/bluesky-redsky-loop-overclaim.err"; then
  printf 'public_harness_check=fail bluesky_redsky_loop_overclaim_output\n' >&2
  cat "$tmpdir/bluesky-redsky-loop-overclaim.out" >&2
  cat "$tmpdir/bluesky-redsky-loop-overclaim.err" >&2
  fail=1
fi

cat >"$tmpdir/q1152-avgt-sim.rs" <<'EOF'
match op.kind {
    OperationType::CCZ | OperationType::CCX => {
        self.stats.toffoli_gates += executed_shots;
    }
    _ => {}
}
let mut current_base_condition = u64::MAX;
if op.c_condition != NO_BIT {
    cond &= self.bit(op.c_condition);
}
let executed_shots = cond.count_ones();
EOF
cat >"$tmpdir/q1152-avgt-eval.rs" <<'EOF'
fn write_score(avg_tof: f64, qubits: u64) {
    let toffoli = avg_tof.round() as u64;
    let score = toffoli.saturating_mul(qubits);
}
EOF
cat >"$tmpdir/q1152-avgt-circuit.rs" <<'EOF'
pub enum OperationType {
    CCX = 13,
    CCZ = 14,
    PushCondition = 15,
    PopCondition = 16,
}
match self.kind {
    OperationType::CCX | OperationType::CCZ => {
        c_condition_flag = ALLOWED;
    }
    OperationType::PushCondition => {
        c_condition_flag = REQUIRED;
    }
    _ => {}
}
EOF
cat >"$tmpdir/q1152-avgt-mod.rs" <<'EOF'
fn push_condition(&mut self, cond: BitId) {}
fn pop_condition(&mut self) {}
EOF
cat >"$tmpdir/q1152-avgt-paper.md" <<'EOF'
- 2020-10-01 Efficient Construction of a Control Modular Adder on a Carry-Lookahead Adder Using Relative-phase Toffoli Gates
- 2024-01-31 Optimizing T and CNOT Gates in Quantum Ripple-Carry Adders and Comparators
EOF
python3 - "$tmpdir/q1152-avgt-ops.bin" <<'PY'
import struct
import sys
NO = (1 << 64) - 1
ops = [
    (13, NO),
    (15, 0),
    (14, NO),
    (16, NO),
    (13, 1),
]
with open(sys.argv[1], "wb") as f:
    f.write(b"QECCOPS1")
    f.write(struct.pack("<Q", len(ops)))
    for kind, c_condition in ops:
        f.write(struct.pack("<IIQQQQQQ", kind, 0, NO, NO, NO, NO, c_condition, NO))
PY
if ! python3 scripts/storm-q1152-avgt-theorem.py \
  --sim-rs "$tmpdir/q1152-avgt-sim.rs" \
  --eval-circuit-rs "$tmpdir/q1152-avgt-eval.rs" \
  --circuit-rs "$tmpdir/q1152-avgt-circuit.rs" \
  --point-add-mod-rs "$tmpdir/q1152-avgt-mod.rs" \
  --ops-bin "$tmpdir/q1152-avgt-ops.bin" \
  --paper-summary "$tmpdir/q1152-avgt-paper.md" \
  --summary-out "$tmpdir/q1152-avgt-summary.tsv" \
  --report-out "$tmpdir/q1152-avgt-report.md" \
  >"$tmpdir/q1152-avgt-theorem.out" 2>"$tmpdir/q1152-avgt-theorem.err"; then
  printf 'public_harness_check=fail q1152_avgt_theorem_failed\n' >&2
  cat "$tmpdir/q1152-avgt-theorem.err" >&2
  fail=1
elif ! grep -q 'q1152_avgt_theorem=pass' "$tmpdir/q1152-avgt-theorem.out" ||
     ! grep -q 'paper_toffoli_hits=2' "$tmpdir/q1152-avgt-theorem.out" ||
     ! grep -q 'toy_quantum_sparse_ccx=64' "$tmpdir/q1152-avgt-theorem.out" ||
     ! grep -q 'toy_classical_conditioned_ccx=32' "$tmpdir/q1152-avgt-theorem.out" ||
     ! grep -q 'discount_bearing_toffoli=2' "$tmpdir/q1152-avgt-theorem.out" ||
     ! grep -q 'decision=source-theorem-packet' "$tmpdir/q1152-avgt-theorem.out"; then
  printf 'public_harness_check=fail q1152_avgt_theorem_output\n' >&2
  cat "$tmpdir/q1152-avgt-theorem.out" >&2
  fail=1
fi

if ! python3 scripts/storm-bluesky-redsky-loop-gate.py \
  docs/bluesky-redsky-pod-inventory-ack-2026-06-28.json \
  --require-implemented >"$tmpdir/bluesky-redsky-pod-inventory.out" 2>"$tmpdir/bluesky-redsky-pod-inventory.err"; then
  printf 'public_harness_check=fail bluesky_redsky_pod_inventory_failed\n' >&2
  cat "$tmpdir/bluesky-redsky-pod-inventory.out" >&2
  cat "$tmpdir/bluesky-redsky-pod-inventory.err" >&2
  fail=1
elif ! grep -q 'bluesky_redsky_loop_gate=pass' "$tmpdir/bluesky-redsky-pod-inventory.out" ||
     ! grep -q 'route_id=process-pod-inventory-ack-five-loop' "$tmpdir/bluesky-redsky-pod-inventory.out" ||
     ! grep -q 'loops=5' "$tmpdir/bluesky-redsky-pod-inventory.out" ||
     ! grep -q 'implemented=5' "$tmpdir/bluesky-redsky-pod-inventory.out" ||
     ! grep -q 'verified=5' "$tmpdir/bluesky-redsky-pod-inventory.out" ||
     ! grep -q 'compute_dispatch_allowed=0' "$tmpdir/bluesky-redsky-pod-inventory.out" ||
     ! grep -q 'submit_language_allowed=0' "$tmpdir/bluesky-redsky-pod-inventory.out"; then
  printf 'public_harness_check=fail bluesky_redsky_pod_inventory_output\n' >&2
  cat "$tmpdir/bluesky-redsky-pod-inventory.out" >&2
  fail=1
fi

if ! python3 scripts/storm-paper-invariant-intake-gate.py \
  examples/paper-invariant-intake-pass.example.txt \
  --require-pass \
  >"$tmpdir/paper-invariant-intake-pass.out" \
  2>"$tmpdir/paper-invariant-intake-pass.err"; then
  printf 'public_harness_check=fail paper_invariant_intake_pass_failed\n' >&2
  cat "$tmpdir/paper-invariant-intake-pass.err" >&2
  fail=1
elif ! grep -q 'paper_invariant_intake_gate=pass' "$tmpdir/paper-invariant-intake-pass.out" ||
     ! grep -q 'source_hash_bound=true' "$tmpdir/paper-invariant-intake-pass.out" ||
     ! grep -q 'candidate_hash_bound=true' "$tmpdir/paper-invariant-intake-pass.out" ||
     ! grep -q 'source_backed=true' "$tmpdir/paper-invariant-intake-pass.out" ||
     ! grep -q 'score_visible_effect=true' "$tmpdir/paper-invariant-intake-pass.out" ||
     ! grep -q 'certified=true' "$tmpdir/paper-invariant-intake-pass.out" ||
     ! grep -q 'decision=source-backed-skill-review-no-compute' "$tmpdir/paper-invariant-intake-pass.out"; then
  printf 'public_harness_check=fail paper_invariant_intake_pass_output\n' >&2
  cat "$tmpdir/paper-invariant-intake-pass.out" >&2
  fail=1
fi

if python3 scripts/storm-paper-invariant-intake-gate.py \
  examples/paper-invariant-intake-hold.example.txt \
  --require-pass \
  >"$tmpdir/paper-invariant-intake-hold.out" \
  2>"$tmpdir/paper-invariant-intake-hold.err"; then
  printf 'public_harness_check=fail paper_invariant_intake_hold_unexpected_pass\n' >&2
  cat "$tmpdir/paper-invariant-intake-hold.out" >&2
  fail=1
elif ! grep -q 'paper_invariant_intake_gate=hold' "$tmpdir/paper-invariant-intake-hold.out" ||
     ! grep -q 'missing_source_hash' "$tmpdir/paper-invariant-intake-hold.out" ||
     ! grep -q 'missing_candidate_hash' "$tmpdir/paper-invariant-intake-hold.out"; then
  printf 'public_harness_check=fail paper_invariant_intake_hold_output\n' >&2
  cat "$tmpdir/paper-invariant-intake-hold.out" >&2
  cat "$tmpdir/paper-invariant-intake-hold.err" >&2
  fail=1
fi

if python3 scripts/storm-paper-invariant-intake-gate.py \
  examples/paper-invariant-intake-fail.example.txt \
  --require-pass \
  >"$tmpdir/paper-invariant-intake-fail.out" \
  2>"$tmpdir/paper-invariant-intake-fail.err"; then
  printf 'public_harness_check=fail paper_invariant_intake_fail_unexpected_pass\n' >&2
  cat "$tmpdir/paper-invariant-intake-fail.out" >&2
  fail=1
elif ! grep -q 'paper_invariant_intake_gate=fail' "$tmpdir/paper-invariant-intake-fail.out" ||
     ! grep -q 'paper_only_scout' "$tmpdir/paper-invariant-intake-fail.out" ||
     ! grep -q 'no_score_visible_ir_effect' "$tmpdir/paper-invariant-intake-fail.out" ||
     ! grep -q 'support_or_proof_counterexample' "$tmpdir/paper-invariant-intake-fail.out" ||
     ! grep -q 'premature_compute_or_residual_request' "$tmpdir/paper-invariant-intake-fail.out"; then
  printf 'public_harness_check=fail paper_invariant_intake_fail_output\n' >&2
  cat "$tmpdir/paper-invariant-intake-fail.out" >&2
  cat "$tmpdir/paper-invariant-intake-fail.err" >&2
  fail=1
fi

cat >"$tmpdir/cout-host-row-safe.json" <<'EOF'
{
  "host_qid": 9001,
  "owner_family": "gidney",
  "owner_call": 5,
  "owner_bit": 7,
  "alloc_op": 100,
  "zero_free_op": 500,
  "last_write_before_borrow": 180,
  "borrow_start_op": 200,
  "borrow_end_op": 260,
  "owner_reads_or_writes_during_borrow": "no",
  "owner_touch_ops": "120,180",
  "disjoint_from_operands": "yes",
  "operand_qids": "1,2,3,4,5",
  "chunk_width": 40,
  "cin_present": "true",
  "erase_is_inverse": "true"
}
EOF
if ! python3 scripts/storm-cout-host-row-gate.py \
  --input "$tmpdir/cout-host-row-safe.json" \
  --summary-out "$tmpdir/cout-host-row-safe.tsv" >"$tmpdir/cout-host-row-safe.out" 2>"$tmpdir/cout-host-row-safe.err"; then
  printf 'public_harness_check=fail cout_host_row_safe_failed\n' >&2
  cat "$tmpdir/cout-host-row-safe.err" >&2
  fail=1
elif ! grep -q 'safe=1' "$tmpdir/cout-host-row-safe.out" ||
     ! grep -q 'validator_ready=1' "$tmpdir/cout-host-row-safe.out" ||
     ! grep -q 'first_result=SAFE_HOST_ROW' "$tmpdir/cout-host-row-safe.out" ||
     ! grep -q $'1\t9001\tgidney\t5\t7\tSAFE_HOST_ROW\tqid_live_idle_disjoint\t1' "$tmpdir/cout-host-row-safe.tsv"; then
  printf 'public_harness_check=fail cout_host_row_safe_output\n' >&2
  cat "$tmpdir/cout-host-row-safe.out" >&2
  cat "$tmpdir/cout-host-row-safe.tsv" >&2
  fail=1
fi

cat >"$tmpdir/cout-host-row-alias.json" <<'EOF'
{
  "host_qid": 9001,
  "owner_family": "gidney",
  "owner_call": 5,
  "owner_bit": 7,
  "alloc_op": 100,
  "zero_free_op": 500,
  "last_write_before_borrow": 180,
  "borrow_start_op": 200,
  "borrow_end_op": 260,
  "owner_reads_or_writes_during_borrow": "no",
  "owner_touch_ops": "120,220",
  "disjoint_from_operands": "yes",
  "operand_qids": "1,2,3,4,5",
  "chunk_width": 40,
  "cin_present": "true",
  "erase_is_inverse": "true"
}
EOF
if ! python3 scripts/storm-cout-host-row-gate.py \
  --input "$tmpdir/cout-host-row-alias.json" >"$tmpdir/cout-host-row-alias.out" 2>"$tmpdir/cout-host-row-alias.err"; then
  printf 'public_harness_check=fail cout_host_row_alias_failed\n' >&2
  cat "$tmpdir/cout-host-row-alias.err" >&2
  fail=1
elif ! grep -q 'hard_nack_alias=1' "$tmpdir/cout-host-row-alias.out" ||
     ! grep -q 'first_result=HARD_NACK_ALIAS' "$tmpdir/cout-host-row-alias.out" ||
     ! grep -q 'first_reason=owner_touch_inside_borrow:220' "$tmpdir/cout-host-row-alias.out"; then
  printf 'public_harness_check=fail cout_host_row_alias_output\n' >&2
  cat "$tmpdir/cout-host-row-alias.out" >&2
  fail=1
fi

cat >"$tmpdir/cout-host-row-double-free.json" <<'EOF'
{
  "host_qid": 9001,
  "owner_family": "gidney",
  "owner_call": 5,
  "owner_bit": 7,
  "alloc_op": 100,
  "zero_free_op": 230,
  "last_write_before_borrow": 180,
  "borrow_start_op": 200,
  "borrow_end_op": 260,
  "owner_reads_or_writes_during_borrow": "no",
  "owner_touch_ops": "120,180",
  "disjoint_from_operands": "yes",
  "operand_qids": "1,2,3,4,5",
  "chunk_width": 40,
  "cin_present": "true",
  "erase_is_inverse": "true"
}
EOF
if ! python3 scripts/storm-cout-host-row-gate.py \
  --input "$tmpdir/cout-host-row-double-free.json" >"$tmpdir/cout-host-row-double-free.out" 2>"$tmpdir/cout-host-row-double-free.err"; then
  printf 'public_harness_check=fail cout_host_row_double_free_failed\n' >&2
  cat "$tmpdir/cout-host-row-double-free.err" >&2
  fail=1
elif ! grep -q 'double_free=1' "$tmpdir/cout-host-row-double-free.out" ||
     ! grep -q 'first_result=DOUBLE_FREE' "$tmpdir/cout-host-row-double-free.out"; then
  printf 'public_harness_check=fail cout_host_row_double_free_output\n' >&2
  cat "$tmpdir/cout-host-row-double-free.out" >&2
  fail=1
fi

cat >"$tmpdir/zero-host-point-add.rs" <<'EOF'
impl Builder {
    fn alloc_qubit(&mut self) -> QubitId {
        self.active_qubits += 1;
        if let Some(q) = self.free_qubits.pop() {
            QubitId(q.into())
        } else {
            QubitId(0)
        }
    }
    fn free(&mut self, q: QubitId) {
        self.r(q);
        self.free_qubits.push(q.0.try_into().unwrap());
        if self.active_qubits > 0 {
            self.active_qubits -= 1;
        }
    }
    fn reacquire(&mut self, q: QubitId) {
        let pos = self.free_qubits.iter().position(|&free_q| u64::from(free_q) == q.0).unwrap();
        self.free_qubits.swap_remove(pos);
        self.active_qubits += 1;
    }
}
EOF
cat >"$tmpdir/zero-host-trailmix-mod.rs" <<'EOF'
impl BExt for B {
    fn loan_zero_qubit(&mut self, q: QubitId) {
        self.free_qubits.push(q.0.try_into().unwrap());
        if self.active_qubits > 0 {
            self.active_qubits -= 1;
        }
    }
}
fn target_qubit_headroom(circ: &B) -> Option<usize> {
    std::env::var("TLM_TARGET_Q")
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .map(|target| target.saturating_sub(circ.active_qubits as usize))
}
EOF
cat >"$tmpdir/zero-host-gidney.rs" <<'EOF'
pub fn controlled_hybrid_add_cout_refs(circ: &mut B, ctrl: &QubitId, a: &[&QubitId], b: &[&QubitId], cout: &QubitId, k: usize) {
    let fit = take_cout_fit(k);
    let effective = target_qubit_headroom(circ)
        .map_or(fit.selected, |headroom| fit.selected.min(headroom));
    controlled_hybrid_add_cout_refs_impl(circ, ctrl, a, b, cout, effective);
}
fn controlled_hybrid_add_cout_refs_impl(circ: &mut B, ctrl: &QubitId, a: &[&QubitId], b: &[&QubitId], cout: &QubitId, k: usize) {
    let cy = circ.alloc_qubit();
    controlled_clean_add_threaded(circ, ctrl, a, b, None, Some(&cy), k);
}
EOF
cat >"$tmpdir/zero-host-families.tsv" <<'EOF'
host_family	counted_active	known_zero	idle	owner_touches_during_borrow	disjoint_from_operands	delta_active
free_pool	no	yes	yes	no	yes	1
dead_carrier	yes	yes	no	yes	no	0
live_data	yes	no	yes	no	yes	0
EOF
if ! python3 scripts/storm-zero-host-accounting-gate.py \
  --point-add-rs "$tmpdir/zero-host-point-add.rs" \
  --trailmix-mod-rs "$tmpdir/zero-host-trailmix-mod.rs" \
  --gidney-rs "$tmpdir/zero-host-gidney.rs" \
  --host-families "$tmpdir/zero-host-families.tsv" \
  --summary-out "$tmpdir/zero-host-summary.tsv" >"$tmpdir/zero-host.out" 2>"$tmpdir/zero-host.err"; then
  printf 'public_harness_check=fail zero_host_accounting_failed\n' >&2
  cat "$tmpdir/zero-host.err" >&2
  fail=1
elif ! grep -q 'zero_host_accounting_gate=pass' "$tmpdir/zero-host.out" ||
     ! grep -q 'source_ok=1' "$tmpdir/zero-host.out" ||
     ! grep -q 'no_relief=1' "$tmpdir/zero-host.out" ||
     ! grep -q 'hard_nack_alias=1' "$tmpdir/zero-host.out" ||
     ! grep -q 'no_host=1' "$tmpdir/zero-host.out" ||
     ! grep -q 'decision=source-accounting-nack' "$tmpdir/zero-host.out" ||
     ! grep -q $'host_family\tfree_pool\tNO_THROTTLE_RELIEF\tfree_or_loaned_zero_is_not_counted_active' "$tmpdir/zero-host-summary.tsv" ||
     ! grep -q $'host_family\tdead_carrier\tHARD_NACK_ALIAS\towner_touches_during_borrow' "$tmpdir/zero-host-summary.tsv"; then
  printf 'public_harness_check=fail zero_host_accounting_output\n' >&2
  cat "$tmpdir/zero-host.out" >&2
  cat "$tmpdir/zero-host-summary.tsv" >&2
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
44	512	CCX	src/point_add/trailmix_ludicrous/gidney.rs	186	none	5890f18abd5d147c
45	502	CCX	src/point_add/trailmix_ludicrous/gidney.rs	179	none	3c978d43c3f08159
46	502	CCX	src/point_add/trailmix_ludicrous/gidney.rs	203	none	3c978d43c3f08159
47	10	CCX	src/point_add/trailmix_ludicrous/gidney.rs	174	none	388916ff50ef6e31
48	2	CCX	src/point_add/trailmix_ludicrous/gidney.rs	211	none	ed611a6fdf670876
49	8307	Z	src/point_add/trailmix_ludicrous/mod.rs	73	none	d44cad3-current
50	1568	Other	src/point_add/trailmix_ludicrous/mod.rs	87	none	d44cad3-current
51	360	CCX	src/point_add/trailmix_ludicrous/fused.rs	131	none	be2dffe287a5dfa3
52	360	CCX	src/point_add/trailmix_ludicrous/fused.rs	267	none	1d624234070becf3
53	292	CCX	src/point_add/trailmix_ludicrous/fused.rs	721	none	346e8758b72fdb65
54	216	CCX	src/point_add/trailmix_ludicrous/fused.rs	377	none	0ed7a7200421f913
55	180	CCX	src/point_add/trailmix_ludicrous/fused.rs	174	none	049c84b7e77e10d5
56	146	CCX	src/point_add/trailmix_ludicrous/fused.rs	728	none	9e9abb2b0080fbe6
57	146	CCX	src/point_add/trailmix_ludicrous/fused.rs	731	none	55504b11b40ccbbd
58	262	CCX	src/point_add/trailmix_ludicrous/arith.rs	1026	none	e70d0e40e1654d5f
59	256	CCX	src/point_add/trailmix_ludicrous/fused.rs	1271	none	4687a22ce2228f11
60	250	CCX	src/point_add/trailmix_ludicrous/arith.rs	2949	none	ebc3d55796151155
61	100	CCX	src/point_add/trailmix_ludicrous/fused.rs	471	none	1c6dc8a1b9f162e9
62	72	CCX	src/point_add/trailmix_ludicrous/arith.rs	262	none	5885ef471d3da0d9
63	27	CCX	src/point_add/trailmix_ludicrous/fused.rs	987	none	79102dddd2f8cab2
64	2	CCX	src/point_add/trailmix_ludicrous/codec.rs	546	none	b416ac85b613263a
65	2	CCX	src/point_add/trailmix_ludicrous/codec.rs	561	none	89ff43160a3a5b7b
66	2	CCX	src/point_add/trailmix_ludicrous/gcd.rs	750	none	d541def583011a3e
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
elif ! grep -q 'counterexample=66' "$tmpdir/source-hash-bound-scout-supported.out" ||
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

cat >"$tmpdir/const-chunk-demo-arith.rs" <<'EOF'
const CONST_CHUNK_DEAD_RANGES: &[(usize, usize, usize)] = &[
    (10, 0, 2),
    (11, 3, 5),
    (12, 0, 0),
];
EOF
cat >"$tmpdir/const-chunk-demo-contexts.tsv" <<'EOF'
file	line	context_hex	family	call	bit	kind	count
src/point_add/trailmix_ludicrous/arith.rs	1090	0x08000a00	const_chunk_carry	10	0	CCX	1
src/point_add/trailmix_ludicrous/arith.rs	1090	0x08000a01	const_chunk_carry	10	1	CCX	1
src/point_add/trailmix_ludicrous/arith.rs	1090	0x08000a02	const_chunk_carry	10	2	CCX	1
src/point_add/trailmix_ludicrous/arith.rs	1090	0x08000b03	const_chunk_carry	11	3	CCX	1
src/point_add/trailmix_ludicrous/arith.rs	1090	0x08000c00	const_chunk_carry	12	0	CCX	1
EOF
if ! python3 scripts/storm-const-chunk-prefix-ledger.py \
  --arith-source "$tmpdir/const-chunk-demo-arith.rs" \
  --contexts "$tmpdir/const-chunk-demo-contexts.tsv" \
  --summary-out "$tmpdir/const-chunk-prefix-none.tsv" >"$tmpdir/const-chunk-prefix-none.out" 2>"$tmpdir/const-chunk-prefix-none.err"; then
  printf 'public_harness_check=fail const_chunk_prefix_no_binding_failed\n' >&2
  cat "$tmpdir/const-chunk-prefix-none.err" >&2
  fail=1
elif ! grep -q 'decision=need-binding-call-trace' "$tmpdir/const-chunk-prefix-none.out" ||
     ! grep -q 'traced_prefix_calls=2' "$tmpdir/const-chunk-prefix-none.out"; then
  printf 'public_harness_check=fail const_chunk_prefix_no_binding_decision\n' >&2
  cat "$tmpdir/const-chunk-prefix-none.out" >&2
  fail=1
fi
if ! python3 scripts/storm-const-chunk-prefix-ledger.py \
  --arith-source "$tmpdir/const-chunk-demo-arith.rs" \
  --contexts "$tmpdir/const-chunk-demo-contexts.tsv" \
  --binding-calls 10,12 \
  --summary-out "$tmpdir/const-chunk-prefix-binding.tsv" >"$tmpdir/const-chunk-prefix-binding.out" 2>"$tmpdir/const-chunk-prefix-binding.err"; then
  printf 'public_harness_check=fail const_chunk_prefix_binding_failed\n' >&2
  cat "$tmpdir/const-chunk-prefix-binding.err" >&2
  fail=1
elif ! grep -q 'decision=prefix-binding-candidate' "$tmpdir/const-chunk-prefix-binding.out" ||
     ! grep -q 'binding_prefix_calls=2' "$tmpdir/const-chunk-prefix-binding.out" ||
     ! grep -q 'estimated_saved_allocs=4' "$tmpdir/const-chunk-prefix-binding.out" ||
     ! grep -q 'estimated_delta_toffoli=-4' "$tmpdir/const-chunk-prefix-binding.out"; then
  printf 'public_harness_check=fail const_chunk_prefix_binding_decision\n' >&2
  cat "$tmpdir/const-chunk-prefix-binding.out" >&2
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

if python3 scripts/storm-windowed-carry-toy.py \
  --max-width 2 \
  --window 0 \
  --count-width 16 \
  --count-window 15 >"$tmpdir/windowed-carry-zero-window.out" 2>"$tmpdir/windowed-carry-zero-window.err"; then
  printf 'public_harness_check=fail windowed_carry_zero_window_unexpected_pass\n' >&2
  fail=1
elif ! grep -q -- '--window and --count-window must be >=1' "$tmpdir/windowed-carry-zero-window.err"; then
  printf 'public_harness_check=fail windowed_carry_zero_window_error\n' >&2
  cat "$tmpdir/windowed-carry-zero-window.err" >&2
  fail=1
fi

if ! python3 scripts/storm-ffg-pair-complete-toy.py \
  --max-width 5 \
  --chunks 4 >"$tmpdir/ffg-pair-complete-no-recompute.out" 2>"$tmpdir/ffg-pair-complete-no-recompute.err"; then
  printf 'public_harness_check=fail ffg_pair_complete_no_recompute_failed\n' >&2
  cat "$tmpdir/ffg-pair-complete-no-recompute.err" >&2
  fail=1
elif ! grep -q 'ffg_pair_complete_toy=fail' "$tmpdir/ffg-pair-complete-no-recompute.out" ||
     ! grep -q 'carry_predictor_mismatches=0' "$tmpdir/ffg-pair-complete-no-recompute.out" ||
     ! grep -q 'no_recompute_dependency_violations=3' "$tmpdir/ffg-pair-complete-no-recompute.out" ||
     ! grep -q 'recompute_required=1' "$tmpdir/ffg-pair-complete-no-recompute.out" ||
     ! grep -q 'decision=no-recompute-pair-complete-nack' "$tmpdir/ffg-pair-complete-no-recompute.out" ||
     ! grep -q 'witness=erase_carry_1_needs_freed_carry_0' "$tmpdir/ffg-pair-complete-no-recompute.out" ||
     ! grep -q 'source_edit_ready=0' "$tmpdir/ffg-pair-complete-no-recompute.out"; then
  printf 'public_harness_check=fail ffg_pair_complete_no_recompute_output\n' >&2
  cat "$tmpdir/ffg-pair-complete-no-recompute.out" >&2
  fail=1
fi

if ! python3 scripts/storm-ffg-pair-complete-toy.py \
  --max-width 5 \
  --chunks 4 \
  --allow-recompute >"$tmpdir/ffg-pair-complete-recompute.out" 2>"$tmpdir/ffg-pair-complete-recompute.err"; then
  printf 'public_harness_check=fail ffg_pair_complete_recompute_failed\n' >&2
  cat "$tmpdir/ffg-pair-complete-recompute.err" >&2
  fail=1
elif ! grep -q 'ffg_pair_complete_toy=hold' "$tmpdir/ffg-pair-complete-recompute.out" ||
     ! grep -q 'carry_predictor_mismatches=0' "$tmpdir/ffg-pair-complete-recompute.out" ||
     ! grep -q 'recompute_predicates_lower_bound=6' "$tmpdir/ffg-pair-complete-recompute.out" ||
     ! grep -q 'decision=recompute-plan-needs-source-phase-score-proof' "$tmpdir/ffg-pair-complete-recompute.out" ||
     ! grep -q 'required_next=source-hash-bound-recompute-certificate' "$tmpdir/ffg-pair-complete-recompute.out"; then
  printf 'public_harness_check=fail ffg_pair_complete_recompute_output\n' >&2
  cat "$tmpdir/ffg-pair-complete-recompute.out" >&2
  fail=1
fi

cat >"$tmpdir/route-compare-dirty.out" <<'EOF'
BASE_SUMMARY shots=256 ops=10228095 qubits=1147 bits=613101 classical=1 phase_batches=1 ancilla_batches=0 avg_tof=1396798.035 avg_cliff=5632151.273
CAND_SUMMARY shots=256 ops=10228101 qubits=1147 bits=613101 classical=1 phase_batches=0 ancilla_batches=0 avg_tof=1396718.473 avg_cliff=5631466.793
COMPARE_SUMMARY shots=256 output_diff=0 phase_diff_batches=1
EOF
if ! python3 scripts/storm-route-compare-admission.py \
  --route-compare "$tmpdir/route-compare-dirty.out" \
  --frontier-score 1571592960 >"$tmpdir/route-compare-dirty-admit.out" 2>"$tmpdir/route-compare-dirty-admit.err"; then
  printf 'public_harness_check=fail route_compare_dirty_failed\n' >&2
  cat "$tmpdir/route-compare-dirty-admit.err" >&2
  fail=1
elif ! grep -q 'route_compare_admission=fail' "$tmpdir/route-compare-dirty-admit.out" ||
     ! grep -q 'admitted=0' "$tmpdir/route-compare-dirty-admit.out" ||
     ! grep -q 'baseline_clean=0' "$tmpdir/route-compare-dirty-admit.out" ||
     ! grep -q 'candidate_clean=0' "$tmpdir/route-compare-dirty-admit.out" ||
     ! grep -q 'compare_clean=0' "$tmpdir/route-compare-dirty-admit.out" ||
     ! grep -q 'score_edge=0' "$tmpdir/route-compare-dirty-admit.out" ||
     ! grep -q 'decision=dirty-baseline-no-admission' "$tmpdir/route-compare-dirty-admit.out"; then
  printf 'public_harness_check=fail route_compare_dirty_decision\n' >&2
  cat "$tmpdir/route-compare-dirty-admit.out" >&2
  fail=1
fi

cat >"$tmpdir/route-compare-no-edge.out" <<'EOF'
BASE_SUMMARY shots=9024 ops=10228095 qubits=1152 bits=613101 classical=0 phase_batches=0 ancilla_batches=0 avg_tof=1364230.000 avg_cliff=5632151.273
CAND_SUMMARY shots=9024 ops=10228101 qubits=1152 bits=613101 classical=0 phase_batches=0 ancilla_batches=0 avg_tof=1364230.000 avg_cliff=5631466.793
COMPARE_SUMMARY shots=9024 output_diff=0 phase_diff_batches=0
EOF
if ! python3 scripts/storm-route-compare-admission.py \
  --route-compare "$tmpdir/route-compare-no-edge.out" \
  --frontier-score 1571592960 >"$tmpdir/route-compare-no-edge-admit.out" 2>"$tmpdir/route-compare-no-edge-admit.err"; then
  printf 'public_harness_check=fail route_compare_no_edge_failed\n' >&2
  cat "$tmpdir/route-compare-no-edge-admit.err" >&2
  fail=1
elif ! grep -q 'route_compare_admission=fail' "$tmpdir/route-compare-no-edge-admit.out" ||
     ! grep -q 'admitted=0' "$tmpdir/route-compare-no-edge-admit.out" ||
     ! grep -q 'baseline_clean=1' "$tmpdir/route-compare-no-edge-admit.out" ||
     ! grep -q 'candidate_clean=1' "$tmpdir/route-compare-no-edge-admit.out" ||
     ! grep -q 'compare_clean=1' "$tmpdir/route-compare-no-edge-admit.out" ||
     ! grep -q 'score_edge=0' "$tmpdir/route-compare-no-edge-admit.out" ||
     ! grep -q 'decision=score-no-edge' "$tmpdir/route-compare-no-edge-admit.out"; then
  printf 'public_harness_check=fail route_compare_no_edge_decision\n' >&2
  cat "$tmpdir/route-compare-no-edge-admit.out" >&2
  fail=1
fi

cat >"$tmpdir/route-compare-incomplete.out" <<'EOF'
BASE_SUMMARY shots=9024 ops=10228095 qubits=1152 bits=613101 classical=0 phase_batches=0 ancilla_batches=0 avg_tof=1364230.000 avg_cliff=5632151.273
CAND_SUMMARY shots=9024 ops=10228101 qubits=1152 bits=613101 phase_batches=0 ancilla_batches=0 avg_tof=1364228.000 avg_cliff=5631466.793
COMPARE_SUMMARY shots=9024 output_diff=0 phase_diff_batches=0
EOF
if ! python3 scripts/storm-route-compare-admission.py \
  --route-compare "$tmpdir/route-compare-incomplete.out" \
  --frontier-score 1571592960 >"$tmpdir/route-compare-incomplete-admit.out" 2>"$tmpdir/route-compare-incomplete-admit.err"; then
  printf 'public_harness_check=fail route_compare_incomplete_failed\n' >&2
  cat "$tmpdir/route-compare-incomplete-admit.err" >&2
  fail=1
elif ! grep -q 'route_compare_admission=hold' "$tmpdir/route-compare-incomplete-admit.out" ||
     ! grep -q 'admitted=0' "$tmpdir/route-compare-incomplete-admit.out" ||
     ! grep -q 'candidate_clean=0' "$tmpdir/route-compare-incomplete-admit.out" ||
     ! grep -q 'decision=incomplete-summary-no-admission' "$tmpdir/route-compare-incomplete-admit.out" ||
     ! grep -q 'candidate_classical_missing' "$tmpdir/route-compare-incomplete-admit.out"; then
  printf 'public_harness_check=fail route_compare_incomplete_decision\n' >&2
  cat "$tmpdir/route-compare-incomplete-admit.out" >&2
  fail=1
fi

cat >"$tmpdir/route-compare-malformed.out" <<'EOF'
BASE_SUMMARY shots=9024 ops=10228095 qubits=1152 bits=613101 classical=0 phase_batches=0 ancilla_batches=0 avg_tof=1364230.000 avg_cliff=5632151.273
CAND_SUMMARY shots=9024 ops=10228101 qubits=1152 bits=613101 classical=not-a-number phase_batches=0 ancilla_batches=0 avg_tof=1364228.000 avg_cliff=5631466.793
COMPARE_SUMMARY shots=9024 output_diff=0 phase_diff_batches=0
EOF
if ! python3 scripts/storm-route-compare-admission.py \
  --route-compare "$tmpdir/route-compare-malformed.out" \
  --frontier-score 1571592960 >"$tmpdir/route-compare-malformed-admit.out" 2>"$tmpdir/route-compare-malformed-admit.err"; then
  printf 'public_harness_check=fail route_compare_malformed_failed\n' >&2
  cat "$tmpdir/route-compare-malformed-admit.err" >&2
  fail=1
elif ! grep -q 'route_compare_admission=hold' "$tmpdir/route-compare-malformed-admit.out" ||
     ! grep -q 'admitted=0' "$tmpdir/route-compare-malformed-admit.out" ||
     ! grep -q 'candidate_clean=0' "$tmpdir/route-compare-malformed-admit.out" ||
     ! grep -q 'decision=incomplete-summary-no-admission' "$tmpdir/route-compare-malformed-admit.out" ||
     ! grep -q 'candidate_classical_malformed' "$tmpdir/route-compare-malformed-admit.out"; then
  printf 'public_harness_check=fail route_compare_malformed_decision\n' >&2
  cat "$tmpdir/route-compare-malformed-admit.out" >&2
  fail=1
fi

cat >"$tmpdir/route-compare-shot-mismatch.out" <<'EOF'
BASE_SUMMARY shots=9024 ops=10228095 qubits=1152 bits=613101 classical=0 phase_batches=0 ancilla_batches=0 avg_tof=1364230.000 avg_cliff=5630100.000
CAND_SUMMARY shots=9024 ops=10221377 qubits=1152 bits=613101 classical=0 phase_batches=0 ancilla_batches=0 avg_tof=1364228.000 avg_cliff=5630000.000
COMPARE_SUMMARY shots=256 output_diff=0 phase_diff_batches=0
EOF
if ! python3 scripts/storm-route-compare-admission.py \
  --route-compare "$tmpdir/route-compare-shot-mismatch.out" \
  --frontier-score 1571592960 >"$tmpdir/route-compare-shot-mismatch-admit.out" 2>"$tmpdir/route-compare-shot-mismatch-admit.err"; then
  printf 'public_harness_check=fail route_compare_shot_mismatch_failed\n' >&2
  cat "$tmpdir/route-compare-shot-mismatch-admit.err" >&2
  fail=1
elif ! grep -q 'route_compare_admission=fail' "$tmpdir/route-compare-shot-mismatch-admit.out" ||
     ! grep -q 'admitted=0' "$tmpdir/route-compare-shot-mismatch-admit.out" ||
     ! grep -q 'score_edge=1' "$tmpdir/route-compare-shot-mismatch-admit.out" ||
     ! grep -q 'decision=shot-mismatch-no-admission' "$tmpdir/route-compare-shot-mismatch-admit.out"; then
  printf 'public_harness_check=fail route_compare_shot_mismatch_decision\n' >&2
  cat "$tmpdir/route-compare-shot-mismatch-admit.out" >&2
  fail=1
fi

cat >"$tmpdir/route-compare-short-edge.out" <<'EOF'
BASE_SUMMARY shots=256 ops=10228095 qubits=1152 bits=613101 classical=0 phase_batches=0 ancilla_batches=0 avg_tof=1364230.000 avg_cliff=5630100.000
CAND_SUMMARY shots=256 ops=10221377 qubits=1152 bits=613101 classical=0 phase_batches=0 ancilla_batches=0 avg_tof=1364228.000 avg_cliff=5630000.000
COMPARE_SUMMARY shots=256 output_diff=0 phase_diff_batches=0
EOF
if ! python3 scripts/storm-route-compare-admission.py \
  --route-compare "$tmpdir/route-compare-short-edge.out" \
  --frontier-score 1571592960 >"$tmpdir/route-compare-short-edge-admit.out" 2>"$tmpdir/route-compare-short-edge-admit.err"; then
  printf 'public_harness_check=fail route_compare_short_edge_failed\n' >&2
  cat "$tmpdir/route-compare-short-edge-admit.err" >&2
  fail=1
elif ! grep -q 'route_compare_admission=hold' "$tmpdir/route-compare-short-edge-admit.out" ||
     ! grep -q 'admitted=0' "$tmpdir/route-compare-short-edge-admit.out" ||
     ! grep -q 'score_edge=1' "$tmpdir/route-compare-short-edge-admit.out" ||
     ! grep -q 'shots=256' "$tmpdir/route-compare-short-edge-admit.out" ||
     ! grep -q 'min_shots=9024' "$tmpdir/route-compare-short-edge-admit.out" ||
     ! grep -q 'decision=insufficient-shots-no-admission' "$tmpdir/route-compare-short-edge-admit.out"; then
  printf 'public_harness_check=fail route_compare_short_edge_decision\n' >&2
  cat "$tmpdir/route-compare-short-edge-admit.out" >&2
  fail=1
fi

cat >"$tmpdir/route-compare-round-tie.out" <<'EOF'
BASE_SUMMARY shots=9024 ops=10228095 qubits=1152 bits=613101 classical=0 phase_batches=0 ancilla_batches=0 avg_tof=1364230.000 avg_cliff=5630100.000
CAND_SUMMARY shots=9024 ops=10221377 qubits=1152 bits=613101 classical=0 phase_batches=0 ancilla_batches=0 avg_tof=1364229.999 avg_cliff=5630000.000
COMPARE_SUMMARY shots=9024 output_diff=0 phase_diff_batches=0
EOF
if ! python3 scripts/storm-route-compare-admission.py \
  --route-compare "$tmpdir/route-compare-round-tie.out" \
  --frontier-score 1571592960 >"$tmpdir/route-compare-round-tie-admit.out" 2>"$tmpdir/route-compare-round-tie-admit.err"; then
  printf 'public_harness_check=fail route_compare_round_tie_failed\n' >&2
  cat "$tmpdir/route-compare-round-tie-admit.err" >&2
  fail=1
elif ! grep -q 'route_compare_admission=fail' "$tmpdir/route-compare-round-tie-admit.out" ||
     ! grep -q 'admitted=0' "$tmpdir/route-compare-round-tie-admit.out" ||
     ! grep -q 'score_edge=0' "$tmpdir/route-compare-round-tie-admit.out" ||
     ! grep -q 'score=1571592960.000000' "$tmpdir/route-compare-round-tie-admit.out" ||
     ! grep -q 'avg_tof_rounded=1364230' "$tmpdir/route-compare-round-tie-admit.out" ||
     ! grep -q 'decision=score-no-edge' "$tmpdir/route-compare-round-tie-admit.out"; then
  printf 'public_harness_check=fail route_compare_round_tie_decision\n' >&2
  cat "$tmpdir/route-compare-round-tie-admit.out" >&2
  fail=1
fi

cat >"$tmpdir/route-compare-edge.out" <<'EOF'
BASE_SUMMARY shots=9024 ops=10228095 qubits=1152 bits=613101 classical=0 phase_batches=0 ancilla_batches=0 avg_tof=1364230.000 avg_cliff=5630100.000
CAND_SUMMARY shots=9024 ops=10221377 qubits=1152 bits=613101 classical=0 phase_batches=0 ancilla_batches=0 avg_tof=1364228.000 avg_cliff=5630000.000
COMPARE_SUMMARY shots=9024 output_diff=0 phase_diff_batches=0
EOF
if ! python3 scripts/storm-route-compare-admission.py \
  --route-compare "$tmpdir/route-compare-edge.out" \
  --frontier-score 1571592960 >"$tmpdir/route-compare-edge-admit.out" 2>"$tmpdir/route-compare-edge-admit.err"; then
  printf 'public_harness_check=fail route_compare_edge_failed\n' >&2
  cat "$tmpdir/route-compare-edge-admit.err" >&2
  fail=1
elif ! grep -q 'route_compare_admission=pass' "$tmpdir/route-compare-edge-admit.out" ||
     ! grep -q 'admitted=1' "$tmpdir/route-compare-edge-admit.out" ||
     ! grep -q 'baseline_clean=1' "$tmpdir/route-compare-edge-admit.out" ||
     ! grep -q 'candidate_clean=1' "$tmpdir/route-compare-edge-admit.out" ||
     ! grep -q 'compare_clean=1' "$tmpdir/route-compare-edge-admit.out" ||
     ! grep -q 'score_edge=1' "$tmpdir/route-compare-edge-admit.out" ||
     ! grep -q 'decision=route-clean-score-edge' "$tmpdir/route-compare-edge-admit.out"; then
  printf 'public_harness_check=fail route_compare_edge_decision\n' >&2
  cat "$tmpdir/route-compare-edge-admit.out" >&2
  fail=1
fi

if python3 scripts/storm-route-compare-admission.py \
  --route-compare "$tmpdir/route-compare-dirty.out" \
  --frontier-score 1571592960 \
  --require-admission >"$tmpdir/route-compare-dirty-strict.out" 2>"$tmpdir/route-compare-dirty-strict.err"; then
  printf 'public_harness_check=fail route_compare_dirty_strict_unexpected_pass\n' >&2
  cat "$tmpdir/route-compare-dirty-strict.out" >&2
  fail=1
fi

if ! python3 scripts/storm-route-compare-admission.py \
  --route-compare "$tmpdir/route-compare-edge.out" \
  --frontier-score 1571592960 \
  --require-admission >"$tmpdir/route-compare-edge-strict.out" 2>"$tmpdir/route-compare-edge-strict.err"; then
  printf 'public_harness_check=fail route_compare_edge_strict_failed\n' >&2
  cat "$tmpdir/route-compare-edge-strict.err" >&2
  fail=1
elif ! grep -q 'admitted=1' "$tmpdir/route-compare-edge-strict.out"; then
  printf 'public_harness_check=fail route_compare_edge_strict_output\n' >&2
  cat "$tmpdir/route-compare-edge-strict.out" >&2
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
