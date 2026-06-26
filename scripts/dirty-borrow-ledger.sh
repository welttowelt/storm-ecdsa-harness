#!/usr/bin/env bash
set -euo pipefail

frontier=""
q=""
target_q=""
route="unknown"
candidate="unknown"
source_lane="unknown"
borrow_window="unknown"
source_idle="unknown"
restores_original_state="unknown"
identity_proof="unknown"
old_consumers_before_borrow="unknown"
raw_result="unknown"

usage() {
  cat <<'USAGE'
usage: dirty-borrow-ledger.sh --frontier SCORE --q Q [options]

Options:
  --target-q Q                     target peak qubit tier; defaults to Q
  --route NAME                     route label
  --candidate NAME                 borrowed-lane candidate
  --source-lane LABEL              source/host lane label
  --borrow-window START..END       window where source is borrowed
  --source-idle yes|no|unknown
  --restores-original-state yes|no|unknown
  --identity-proof yes|no|unknown
  --old-consumers-before-borrow yes|no|unknown
  --raw-result SHOTS:C/P/A         trusted raw/no-drop result
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --frontier) frontier="${2:-}"; shift 2 ;;
    --q) q="${2:-}"; shift 2 ;;
    --target-q) target_q="${2:-}"; shift 2 ;;
    --route) route="${2:-}"; shift 2 ;;
    --candidate) candidate="${2:-}"; shift 2 ;;
    --source-lane) source_lane="${2:-}"; shift 2 ;;
    --borrow-window) borrow_window="${2:-}"; shift 2 ;;
    --source-idle) source_idle="${2:-}"; shift 2 ;;
    --restores-original-state) restores_original_state="${2:-}"; shift 2 ;;
    --identity-proof) identity_proof="${2:-}"; shift 2 ;;
    --old-consumers-before-borrow) old_consumers_before_borrow="${2:-}"; shift 2 ;;
    --raw-result) raw_result="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'unknown_arg=%s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$frontier" ] || [ -z "$q" ]; then
  usage >&2
  exit 2
fi
case "$frontier" in ''|*[!0-9]*) printf 'invalid_frontier=%s\n' "$frontier" >&2; exit 2 ;; esac
case "$q" in ''|*[!0-9]*) printf 'invalid_q=%s\n' "$q" >&2; exit 2 ;; esac

if [ -z "$target_q" ]; then
  target_q="$q"
fi
case "$target_q" in ''|*[!0-9]*) printf 'invalid_target_q=%s\n' "$target_q" >&2; exit 2 ;; esac

max_avg=$(( (frontier - 1) / q ))
target_max_avg=$(( (frontier - 1) / target_q ))

raw_clean="no"
case "$raw_result" in
  *:0/0/0|0/0/0) raw_clean="yes" ;;
esac

if [ "$source_idle" = "no" ]; then
  decision="reject-source-active"
elif [ "$old_consumers_before_borrow" = "no" ]; then
  decision="reject-old-owner-live"
elif [ "$restores_original_state" = "no" ]; then
  decision="reject-not-restored"
elif [ "$raw_clean" != "yes" ]; then
  decision="dirty-borrow-invalid"
elif [ "$identity_proof" = "no" ]; then
  decision="proof-required"
elif [ "$source_idle" != "yes" ] || [ "$restores_original_state" != "yes" ] || [ "$identity_proof" != "yes" ] || [ "$old_consumers_before_borrow" != "yes" ]; then
  decision="proof-required"
else
  decision="prototype-eligible"
fi

printf 'Dirty borrow entanglement gate:\n'
printf -- '- Route: %s\n' "$route"
printf -- '- Candidate: %s\n' "$candidate"
printf -- '- Frontier/q/max avgT: %s/%s/%s\n' "$frontier" "$q" "$max_avg"
printf -- '- Target q/max avgT: %s/%s\n' "$target_q" "$target_max_avg"
printf -- '- Source lane: %s\n' "$source_lane"
printf -- '- Borrow window: %s\n' "$borrow_window"
printf -- '- Source idle: %s\n' "$source_idle"
printf -- '- Old-owner consumers before borrow: %s\n' "$old_consumers_before_borrow"
printf -- '- Restores original source state: %s\n' "$restores_original_state"
printf -- '- Identity-on-entanglement proof: %s\n' "$identity_proof"
printf -- '- Raw/no-drop result: %s\n' "$raw_result"
printf -- '- Decision: %s\n' "$decision"
