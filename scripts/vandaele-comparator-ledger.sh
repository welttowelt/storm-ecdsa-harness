#!/usr/bin/env bash
set -euo pipefail

trace=""
frontier=""
q=""
route=""
candidate=""
dirty_host="unknown"
middle_callback="unknown"

usage() {
  cat <<'USAGE'
usage: vandaele-comparator-ledger.sh --trace PATH --frontier SCORE --q Q [options]

Options:
  --route NAME              route label for the ledger
  --candidate NAME          candidate label
  --dirty-host STATE        yes/no/unknown plus note
  --middle-callback STATE   preserved/unknown/not-needed plus note
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --trace) trace="${2:-}"; shift 2 ;;
    --frontier) frontier="${2:-}"; shift 2 ;;
    --q) q="${2:-}"; shift 2 ;;
    --route) route="${2:-}"; shift 2 ;;
    --candidate) candidate="${2:-}"; shift 2 ;;
    --dirty-host) dirty_host="${2:-}"; shift 2 ;;
    --middle-callback) middle_callback="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'unknown_arg=%s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$trace" ] || [ -z "$frontier" ] || [ -z "$q" ]; then
  usage >&2
  exit 2
fi
if [ ! -f "$trace" ]; then
  printf 'vandaele_comparator_gate=fail missing_trace=%s\n' "$trace" >&2
  exit 1
fi

max_avg=$(( (frontier - 1) / q ))
peak_qubits="$(grep -Eo 'peak_qubits=[0-9]+' "$trace" | tail -n 1 | cut -d= -f2 || true)"
if [ -z "$peak_qubits" ]; then
  peak_qubits="$(awk '
    /ALLOC_NEAR/ {
      for (i = 1; i <= NF; i++) {
        if ($i ~ /^active=[0-9]+$/) {
          split($i, a, "=");
          if (a[2] + 0 > max) max = a[2] + 0;
        }
      }
    }
    END { if (max > 0) print max; }
  ' "$trace")"
fi
peak_qubits="${peak_qubits:-unknown}"

alloc_total="$(grep -c 'ALLOC_NEAR' "$trace" || true)"
comparator_hits="$(grep 'ALLOC_NEAR' "$trace" | grep -Eci 'compare|comparator|arith.rs:769' || true)"
co_peak_carry_hits="$(
  grep 'ALLOC_NEAR' "$trace" \
    | grep -Evi 'compare|comparator|arith.rs:769' \
    | grep -Eci 'gidney.rs:1217|arith.rs:1077|arith.rs:1194|fused.rs:1621|fused.rs:1622|mcx.rs:318|arith.rs:1859|const_chunk_add_clean|carry' \
    || true
)"

exclusion_stats="$(
  awk '
    /ALLOC_NEAR/ {
      active = 0;
      caller = "";
      for (i = 1; i <= NF; i++) {
        if ($i ~ /^active=[0-9]+$/) {
          split($i, a, "=");
          active = a[2] + 0;
        }
        if ($i ~ /^caller=/) {
          split($i, c, "=");
          caller = c[2];
        }
      }
      if (caller !~ /arith.rs:769|comparator/) {
        if (active > no_comp) no_comp = active;
      }
      if (caller !~ /arith.rs:769|comparator|gidney.rs:1217|arith.rs:1077|arith.rs:1194|fused.rs:1621|fused.rs:1622|mcx.rs:318|arith.rs:1859/) {
        if (active > no_pair) no_pair = active;
      }
    }
    END {
      printf "max_without_comparator=%s\n", (no_comp ? no_comp : "unknown");
      printf "max_without_main_pair=%s\n", (no_pair ? no_pair : "unknown");
    }
  ' "$trace"
)"
max_without_comparator="$(printf '%s\n' "$exclusion_stats" | awk -F= '/max_without_comparator/ { print $2 }')"
max_without_main_pair="$(printf '%s\n' "$exclusion_stats" | awk -F= '/max_without_main_pair/ { print $2 }')"

top_callers="$(
  grep 'ALLOC_NEAR' "$trace" \
    | sed -E 's/.*caller=//' \
    | sort \
    | uniq -c \
    | sort -nr \
    | head -n 8 \
    || true
)"

first_peak="$(
  grep -E 'TLM_FFG|TLM_PROFILE|ALLOC_NEAR' "$trace" \
    | head -n 8 \
    || true
)"

decision="park"
if [ "${comparator_hits:-0}" -gt 0 ]; then
  if [ "$max_without_comparator" = "$peak_qubits" ] && [ "$peak_qubits" != "unknown" ]; then
    decision="plateau-cut-required"
  elif [ "${co_peak_carry_hits:-0}" -gt 0 ]; then
    decision="paired-cut-required"
    if [ "$max_without_main_pair" = "$peak_qubits" ] && [ "$peak_qubits" != "unknown" ]; then
      decision="plateau-cut-required"
    fi
  else
    decision="toy-port"
  fi
fi

cat <<EOF
Vandaele comparator gate:
- Route: ${route:-unknown}
- Candidate: ${candidate:-unknown}
- Frontier/q/max avgT: ${frontier}/${q}/${max_avg}
- Peak evidence: peak_qubits=${peak_qubits} alloc_near=${alloc_total}
- Comparator peak hits: ${comparator_hits}
- Co-peak carry/fold wall hits: ${co_peak_carry_hits}
- Max without comparator: ${max_without_comparator:-unknown}
- Max without main comparator/add pair: ${max_without_main_pair:-unknown}
- Dirty host: ${dirty_host}
- Middle callback preserved: ${middle_callback}
- Decision: ${decision}
EOF

if [ -n "$top_callers" ]; then
  printf -- '- Top peak callers:\n'
  printf '%s\n' "$top_callers" | sed 's/^/  /'
fi
if [ -n "$first_peak" ]; then
  printf -- '- First trace rows:\n'
  printf '%s\n' "$first_peak" | sed 's/^/  /'
fi

if [ "$decision" = "park" ]; then
  exit 3
fi
