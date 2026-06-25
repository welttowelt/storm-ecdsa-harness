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
  examples/audit-card.example.md \
  examples/operator-card.example.md \
  examples/mailbox-entry.example.md \
  examples/route-packet.example.md \
  examples/compute-request.example.md \
  examples/public-note.example.md \
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

need_text examples/operator-card.example.md "falsifiable decision" "Falsifiable decision"
need_text examples/audit-card.example.md "rci tony" "RCI/Tony"
need_text examples/audit-card.example.md "redsky" "Redsky Pass"
need_text examples/audit-card.example.md "bluesky" "Bluesky Pass"
need_text examples/mailbox-entry.example.md "read receipt requested" "Read receipt requested"
need_text examples/route-packet.example.md "stop condition" "Stop condition"
need_text examples/compute-request.example.md "zero paid compute" "zero"
need_text examples/public-note.example.md "not a candidate" "not a candidate"
need_text dashboard/fixtures/status.json "public fixture" "public fixture|fixture data"

if [ "$fail" -ne 0 ]; then
  exit 1
fi

printf 'public_harness_check=pass\n'
