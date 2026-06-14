#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail=0

print_fail() {
  printf 'redaction_check=fail reason=%s\n' "$1" >&2
  fail=1
}

for forbidden in runs logs state tmp output exports private mailbox chat_exports attachments; do
  if [ -e "$forbidden" ]; then
    print_fail "forbidden_path_present:$forbidden"
  fi
done

scan_files() {
  find . \
    -path './.git' -prune -o \
    -path './scripts/redaction-check.sh' -prune -o \
    -type f -print
}

check_pattern() {
  local name="$1"
  local pattern="$2"
  local matches
  matches="$(scan_files | xargs grep -nE "$pattern" 2>/dev/null || true)"
  if [ "$matches" != "" ]; then
    printf 'redaction_check=match pattern=%s\n%s\n' "$name" "$matches" >&2
    fail=1
  fi
}

check_pattern "runpod_api_key" 'rpa_[[:alnum:]]{16,}'
check_pattern "generic_secret_key" '(^|[^[:alnum:]_])sk-[[:alnum:]]{16,}'
check_pattern "remote_command" 'ssh[[:space:]]+[^[:space:]]+@'
check_pattern "root_remote" 'root@'
check_pattern "host_port" '([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{2,5})?'
check_pattern "private_key_name" 'id_ed25519|BEGIN OPENSSH PRIVATE KEY|BEGIN RSA PRIVATE KEY'
check_pattern "url_token" 'token='
check_pattern "private_home_path" '/Users/[A-Za-z0-9._-]+'
check_pattern "live_mailbox_name" 'ECDSA_FAIL_AGENT_HANDOFF'
check_pattern "raw_nonce_assignment" '(^|[^[:alpha:]])(nonce|TAIL_NONCE|DIALOG_TAIL_NONCE)[_A-Za-z0-9-]*[=:][[:space:]]*[0-9]{4,}'

if [ "$fail" -ne 0 ]; then
  exit 1
fi

printf 'redaction_check=pass\n'

