#!/usr/bin/env bash
set -euo pipefail

trace=""
frontier=""
q=""
target_q=""
route="unknown"
candidate="unknown"
top="12"

usage() {
  cat <<'USAGE'
usage: active-volume-ledger.sh --trace PATH --frontier SCORE --q Q [options]

Options:
  --target-q Q       target peak qubit tier; defaults to Q-1
  --route NAME       route label
  --candidate NAME   candidate label
  --top N            number of pressure rows to print; default 12
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
    --top) top="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'unknown_arg=%s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$trace" ] || [ -z "$frontier" ] || [ -z "$q" ]; then
  usage >&2
  exit 2
fi
if [ ! -f "$trace" ]; then
  printf 'active_volume_gate=fail missing_trace=%s\n' "$trace" >&2
  exit 1
fi
case "$frontier" in ''|*[!0-9]*) printf 'invalid_frontier=%s\n' "$frontier" >&2; exit 2 ;; esac
case "$q" in ''|*[!0-9]*) printf 'invalid_q=%s\n' "$q" >&2; exit 2 ;; esac
case "$top" in ''|*[!0-9]*) printf 'invalid_top=%s\n' "$top" >&2; exit 2 ;; esac

if [ -z "$target_q" ]; then
  target_q=$((q - 1))
fi
case "$target_q" in ''|*[!0-9]*) printf 'invalid_target_q=%s\n' "$target_q" >&2; exit 2 ;; esac

max_avg=$(( (frontier - 1) / q ))
target_max_avg=$(( (frontier - 1) / target_q ))

awk -v route="$route" \
    -v candidate="$candidate" \
    -v frontier="$frontier" \
    -v q="$q" \
    -v target_q="$target_q" \
    -v max_avg="$max_avg" \
    -v target_max_avg="$target_max_avg" \
    -v top="$top" '
  function field(name,    i, a) {
    for (i = 1; i <= NF; i++) {
      if ($i ~ ("^" name "=")) {
        split($i, a, "=");
        return a[2];
      }
    }
    return "";
  }
  function append(list, item) {
    if (item == "") return list;
    if (list == "") return item;
    return list "," item;
  }
  /^TLM_FFG / {
    n++;
    call[n] = field("call");
    phase[n] = field("phase");
    g[n] = field("g") + 0;
    entry[n] = field("entry_active") + 0;
    peak[n] = field("local_peak") + 0;
    ops[n] = field("ops") + 0;
    if (peak[n] > max_peak) {
      max_peak = peak[n];
      max_peak_call = call[n];
    }
  }
  /^TLM_TAPE / {
    tape_rows++;
    active = field("active") + 0;
    iter = field("i");
    tape = field("tape") + 0;
    pending = field("pending") + 0;
    codec = field("codec");
    if (active > max_tape_active) {
      max_tape_active = active;
      max_tape_line = sprintf("i=%s active=%d tape=%d pending=%d codec=%s",
        iter, active, tape, pending, codec);
    }
    if (active > target_q) {
      tape_above++;
      if (iter != "") tape_iters[iter] = 1;
    }
  }
  END {
    for (i = 1; i <= n; i++) {
      span = 1;
      if (i < n && ops[i + 1] > ops[i]) span = ops[i + 1] - ops[i];
      over = peak[i] - target_q;
      if (over > 0) {
        above++;
        weighted = over * span;
        total_weighted += weighted;
        row_call[above] = call[i];
        row_phase[above] = phase[i];
        row_g[above] = g[i];
        row_entry[above] = entry[i];
        row_peak[above] = peak[i];
        row_over[above] = over;
        row_span[above] = span;
        row_weighted[above] = weighted;
        calls = append(calls, call[i]);
        if (over > max_over) max_over = over;
      }
    }

    for (iter in tape_iters) {
      tape_iter_count++;
      tape_iter_list = append(tape_iter_list, iter);
    }

    decision = above == 0 ? "target-already-satisfied" : "rank-first";
    max_peak_text = max_peak ? max_peak : "unknown";
    calls_text = calls == "" ? "none" : calls;
    max_tape_line_text = max_tape_line == "" ? "none" : max_tape_line;

    printf "SQUARE active-volume gate:\n";
    printf "- Route: %s\n", route;
    printf "- Candidate: %s\n", candidate;
    printf "- Frontier/q/max avgT: %s/%s/%s\n", frontier, q, max_avg;
    printf "- Target q/max avgT: %s/%s\n", target_q, target_max_avg;
    printf "- Max FFG peak: %s call=%s\n", max_peak_text, max_peak_call;
    printf "- FFG rows above target: %d calls=%s\n", above, calls_text;
    printf "- Uniform peak reduction needed: %d\n", max_over;
    printf "- Weighted pressure proxy: %d\n", total_weighted;
    printf "- Tape rows above target: %d iter_count=%d max_tape_row={%s}\n",
      tape_above, tape_iter_count, max_tape_line_text;
    printf "- Decision: %s\n", decision;

    if (above > 0) {
      printf "- Top pressure rows:\n";
      for (rank = 1; rank <= top && rank <= above; rank++) {
        best = 0;
        for (i = 1; i <= above; i++) {
          if (!used[i] && (best == 0 || row_weighted[i] > row_weighted[best])) {
            best = i;
          }
        }
        if (best == 0) break;
        used[best] = 1;
        printf "  rank=%d call=%s phase=%s g=%d entry=%d peak=%d over=%d span_ops=%d pressure=%d\n",
          rank, row_call[best], row_phase[best], row_g[best], row_entry[best],
          row_peak[best], row_over[best], row_span[best], row_weighted[best];
      }
    }
  }
' "$trace"
