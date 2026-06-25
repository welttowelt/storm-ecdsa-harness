#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail=0
mode="tree"

if [ "${1:-}" = "--history" ]; then
  mode="history"
elif [ "${1:-}" != "" ]; then
  printf 'usage: %s [--history]\n' "$0" >&2
  exit 2
fi

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
    -path './.github/workflows/redaction.yml' -prune -o \
    -path './scripts/redaction-check.sh' -prune -o \
    -type f -print
}

scan_tree_pattern() {
  local pattern="$1"
  scan_files | xargs grep -nE "$pattern" 2>/dev/null || true
}

scan_history_pattern() {
  local pattern="$1"
  git grep -nE "$pattern" "$(git rev-list --all)" -- . \
    ':(exclude)scripts/redaction-check.sh' \
    ':(exclude).github/workflows/redaction.yml' \
    2>/dev/null || true
}

check_pattern() {
  local name="$1"
  local pattern="$2"
  local matches
  if [ "$mode" = "history" ]; then
    matches="$(scan_history_pattern "$pattern")"
  else
    matches="$(scan_tree_pattern "$pattern")"
  fi
  if [ "$matches" != "" ]; then
    printf 'redaction_check=match pattern=%s\n%s\n' "$name" "$matches" >&2
    fail=1
  fi
}

check_pattern "runpod_api_key" 'rpa_[[:alnum:]]{16,}'
check_pattern "generic_secret_key" '(^|[^[:alnum:]_])sk-[[:alnum:]]{16,}'
check_pattern "github_token" '(gh[pousr]_[[:alnum:]]{20,}|github_pat_[[:alnum:]_]{20,})'
check_pattern "aws_access_key" '(AKIA|ASIA)[A-Z0-9]{16}'
check_pattern "google_api_key" 'AIza[[:alnum:]_-]{20,}'
check_pattern "slack_token" 'xox[baprs]-[[:alnum:]-]{20,}'
check_pattern "bearer_token" '(^|[^[:alpha:]])[Bb]earer[[:space:]]+[[:alnum:]_.~+/-]{20,}'
check_pattern "remote_command" 'ssh[[:space:]]+[^[:space:]]+@'
check_pattern "root_remote" 'root@'
check_pattern "host_port" '([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{2,5})?'
check_pattern "runpod_endpoint" 'runpod\.io|proxy\.runpod\.net'
check_pattern "private_key_name" 'id_ed25519|BEGIN (OPENSSH|RSA|DSA|EC|PRIVATE) PRIVATE KEY'
check_pattern "url_token" 'token='
check_pattern "private_home_path" '/Users/[A-Za-z0-9._-]+'
check_pattern "private_linux_home_path" '(/home/[A-Za-z0-9._-]+|/root(/|$))'
check_pattern "private_windows_home_path" '[A-Za-z]:\\Users\\[A-Za-z0-9._-]+'
check_pattern "live_mailbox_name" 'ECDSA_FAIL_AGENT_HANDOFF'
check_pattern "raw_nonce_assignment" '(^|[^[:alpha:]])(nonce|TAIL_NONCE|DIALOG_TAIL_NONCE)[_A-Za-z0-9-]*[=:][[:space:]]*[0-9]{4,}'
check_pattern "raw_hex_nonce_assignment" '(^|[^[:alpha:]])(nonce|TAIL_NONCE|DIALOG_TAIL_NONCE)[_A-Za-z0-9-]*[=:][[:space:]]*0x[0-9A-Fa-f]{8,}'

if [ "$fail" -ne 0 ]; then
  exit 1
fi

printf 'redaction_check=pass mode=%s\n' "$mode"
