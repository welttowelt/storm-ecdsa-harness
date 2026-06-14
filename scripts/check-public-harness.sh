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
  templates/mailbox-entry.md \
  templates/route-packet.md \
  templates/compute-request.md \
  templates/public-note.md \
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
need_text templates/route-packet.md "evidence label" "Evidence label"
need_text templates/route-packet.md "submit gate" "Submit gate"
need_text templates/compute-request.md "validator" "Validator"
need_text templates/compute-request.md "kill condition" "Kill condition"
need_text templates/mailbox-entry.md "purpose limits" "Purpose/limits"
need_text templates/mailbox-entry.md "read receipt requested" "Read receipt requested"
need_text templates/public-note.md "purpose and limits" "Purpose And Limits"
need_text templates/public-note.md "evidence label" "Evidence label"

need_text examples/operator-card.example.md "falsifiable decision" "Falsifiable decision"
need_text examples/mailbox-entry.example.md "read receipt requested" "Read receipt requested"
need_text examples/route-packet.example.md "stop condition" "Stop condition"
need_text examples/compute-request.example.md "zero paid compute" "zero"
need_text examples/public-note.example.md "not a candidate" "not a candidate"
need_text dashboard/fixtures/status.json "demo fixture" "demo fixture|fixture data"

if [ "$fail" -ne 0 ]; then
  exit 1
fi

printf 'public_harness_check=pass\n'
