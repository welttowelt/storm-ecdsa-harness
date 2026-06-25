#!/usr/bin/env bash
set -euo pipefail

trace=""
frontier=""
q=""
target_q=""
route=""
candidate="unknown"
covered_calls=""
all_consumers="unknown"
cut_bits="1"
hidden_scratch="0"
extra_toffoli="unknown"

usage() {
  cat <<'USAGE'
usage: uncompute-window-ledger.sh --trace PATH --frontier SCORE --q Q [options]

Options:
  --target-q Q          target peak qubit tier; defaults to Q-1
  --route NAME          route label for the ledger
  --candidate NAME      proposed uncompute/recompute candidate
  --covered-calls CSV   FFG call ids covered by the candidate
  --all-consumers yes|no|unknown
  --cut-bits N          resident bits removed inside the peak; default 1
  --hidden-scratch N    scratch bits reintroduced inside the peak; default 0
  --extra-toffoli N     estimated added Toffoli count, if known
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --trace) trace="${2:-}"; shift 2 ;;
    --frontier) frontier="${2:-}"; shift 2 ;;
    --q) q="${2:-}"; shift 2 ;;
    --target-q) target_q="${2:-}"; shift 2 ;;
    --route) route="${2:-}"; shift 2 ;;
    --candidate) candidate="${2:-}"; shift 2 ;;
    --covered-calls) covered_calls="${2:-}"; shift 2 ;;
    --all-consumers) all_consumers="${2:-}"; shift 2 ;;
    --cut-bits) cut_bits="${2:-}"; shift 2 ;;
    --hidden-scratch) hidden_scratch="${2:-}"; shift 2 ;;
    --extra-toffoli) extra_toffoli="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'unknown_arg=%s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$trace" ] || [ -z "$frontier" ] || [ -z "$q" ]; then
  usage >&2
  exit 2
fi
if [ ! -f "$trace" ]; then
  printf 'reqomp_uncompute_gate=fail missing_trace=%s\n' "$trace" >&2
  exit 1
fi
case "$cut_bits" in ''|*[!0-9]*) printf 'invalid_cut_bits=%s\n' "$cut_bits" >&2; exit 2 ;; esac
case "$hidden_scratch" in ''|*[!0-9]*) printf 'invalid_hidden_scratch=%s\n' "$hidden_scratch" >&2; exit 2 ;; esac

if [ -z "$target_q" ]; then
  target_q=$((q - 1))
fi

max_avg=$(( (frontier - 1) / q ))
target_max_avg=$(( (frontier - 1) / target_q ))

above_calls="$(
  awk -v target_q="$target_q" '
    /^TLM_FFG / {
      call = peak = "";
      for (i = 1; i <= NF; i++) {
        if ($i ~ /^call=/) { split($i, a, "="); call = a[2]; }
        if ($i ~ /^local_peak=/) { split($i, a, "="); peak = a[2] + 0; }
      }
      if (call != "" && peak > target_q) seen[call] = 1;
    }
    END {
      first = 1;
      for (c in seen) {
        if (!first) printf ",";
        printf "%s", c;
        first = 0;
      }
      printf "\n";
    }
  ' "$trace" | tr ',' '\n' | sed '/^$/d' | sort -n | paste -sd, -
)"

missing_calls="$(
  awk -v need="$above_calls" -v have="$covered_calls" '
    BEGIN {
      split(need, n, ",");
      split(have, h, ",");
      for (i in h) if (h[i] != "") covered[h[i]] = 1;
      first = 1;
      for (i = 1; i <= length(n); i++) {
        if (n[i] != "" && !(n[i] in covered)) {
          if (!first) printf ",";
          printf "%s", n[i];
          first = 0;
        }
      }
      printf "\n";
    }
  '
)"

if [ -z "$above_calls" ]; then
  decision="target-already-satisfied"
elif [ -n "$missing_calls" ]; then
  decision="incomplete-window"
elif [ "$all_consumers" != "yes" ]; then
  decision="missing-consumer-audit"
elif [ "$hidden_scratch" -ge "$cut_bits" ]; then
  decision="scratch-erases-cut"
else
  decision="prototype-required"
fi

printf 'Reqomp uncompute window gate:\n'
printf -- '- Route: %s\n' "${route:-unknown}"
printf -- '- Frontier/q/max avgT: %s/%s/%s\n' "$frontier" "$q" "$max_avg"
printf -- '- Target q/max avgT: %s/%s\n' "$target_q" "$target_max_avg"
printf -- '- Candidate: %s\n' "$candidate"
printf -- '- Above-target calls: %s\n' "${above_calls:-none}"
printf -- '- Covered calls: %s\n' "${covered_calls:-none}"
printf -- '- Missing calls: %s\n' "${missing_calls:-none}"
printf -- '- Cut bits: %s\n' "$cut_bits"
printf -- '- Hidden scratch bits: %s\n' "$hidden_scratch"
printf -- '- Extra Toffoli estimate: %s\n' "$extra_toffoli"
printf -- '- All consumers accounted: %s\n' "$all_consumers"
printf -- '- Decision: %s\n' "$decision"
