#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
usage: scripts/pebble-memory-ledger.sh --frontier SCORE --q Q --build-log FILE --eval-log FILE [options]

Options:
  --route NAME             Route or checkout label.
  --candidate NAME         Candidate label.
  --drop-state STATE       none, historical, regenerated, fixed-point, or mixed.
  --move TEXT              Pebbling move being tested.
  --removed-value TEXT     Value removed, delayed, or recomputed.
  --producer TEXT          Producer node or callsite.
  --consumers TEXT         Consumer nodes or callsites.
  --trace-log FILE         Optional TLM_TAPE/TLM_FFG trace for plateau analysis.
  --trace-target-q Q       Peak target for FFG rows in the trace.
  --trace-active-floor Q   Optional active-qubit floor for neighboring TLM_TAPE rows.
  --notes TEXT             Extra one-line notes.

The script emits the paper-reversible-pebbling-memory-management output shape.
EOF
}

frontier=""
q=""
build_log=""
eval_log=""
route="unknown"
candidate="unknown"
drop_state="unknown"
move="unknown"
removed_value="unknown"
producer="unknown"
consumers="unknown"
trace_log=""
trace_target_q=""
trace_active_floor=""
notes=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --frontier) frontier="${2:?missing frontier}"; shift 2 ;;
    --q) q="${2:?missing q}"; shift 2 ;;
    --build-log) build_log="${2:?missing build log}"; shift 2 ;;
    --eval-log) eval_log="${2:?missing eval log}"; shift 2 ;;
    --route) route="${2:?missing route}"; shift 2 ;;
    --candidate) candidate="${2:?missing candidate}"; shift 2 ;;
    --drop-state) drop_state="${2:?missing drop state}"; shift 2 ;;
    --move) move="${2:?missing move}"; shift 2 ;;
    --removed-value) removed_value="${2:?missing removed value}"; shift 2 ;;
    --producer) producer="${2:?missing producer}"; shift 2 ;;
    --consumers) consumers="${2:?missing consumers}"; shift 2 ;;
    --trace-log) trace_log="${2:?missing trace log}"; shift 2 ;;
    --trace-target-q) trace_target_q="${2:?missing trace target q}"; shift 2 ;;
    --trace-active-floor) trace_active_floor="${2:?missing trace active floor}"; shift 2 ;;
    --notes) notes="${2:?missing notes}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$frontier" ] || [ -z "$q" ] || [ -z "$build_log" ] || [ -z "$eval_log" ]; then
  usage >&2
  exit 2
fi

if [ ! -f "$build_log" ]; then
  printf 'missing build log: %s\n' "$build_log" >&2
  exit 1
fi
if [ ! -f "$eval_log" ]; then
  printf 'missing eval log: %s\n' "$eval_log" >&2
  exit 1
fi
if [ -n "$trace_log" ] && [ ! -f "$trace_log" ]; then
  printf 'missing trace log: %s\n' "$trace_log" >&2
  exit 1
fi

max_avg_t=$(( (frontier - 1) / q ))

profile_line="$(grep 'TLM_PROFILE peak_qubits=' "$build_log" | tail -n 1 || true)"
peak_qubits="$(printf '%s\n' "$profile_line" | sed -n 's/.*peak_qubits=\([0-9][0-9]*\).*/\1/p')"
peak_phase="$(printf '%s\n' "$profile_line" | sed -n 's/.*peak_phase=\([^ ]*\).*/\1/p')"
peak_ops_idx="$(printf '%s\n' "$profile_line" | sed -n 's/.*peak_ops_idx=\([0-9][0-9]*\).*/\1/p')"
profile_emitted="$(printf '%s\n' "$profile_line" | sed -n 's/.*emitted_ops=\([0-9][0-9]*\).*/\1/p')"

loaded_ops="$(sed -n 's/^  loaded ops  : *//p' "$eval_log" | tail -n 1)"
eval_qubits="$(sed -n 's/^  qubits      : *//p' "$eval_log" | tail -n 1)"
eval_bits="$(sed -n 's/^  bits        : *//p' "$eval_log" | tail -n 1)"
shots="$(sed -n 's/^  tested shots            : *//p' "$eval_log" | tail -n 1)"
classical="$(sed -n 's/^  classical mismatches    : *//p' "$eval_log" | tail -n 1)"
phase="$(sed -n 's/^  phase-garbage batches   : *//p' "$eval_log" | tail -n 1)"
ancilla="$(sed -n 's/^  ancilla-garbage batches : *//p' "$eval_log" | tail -n 1)"
avg_t="$(sed -n 's/^  avg executed Toffoli  : *//p' "$eval_log" | tail -n 1)"

drop_summary="$((grep -E 'DROP_DEAD_ROBUST(:|_SECOND:)' "$build_log" || true) | tail -n 4 | tr '\n' '; ' | sed 's/[; ]*$//')"
if [ -z "$drop_summary" ]; then
  drop_summary="not observed"
fi

score_state="unknown"
if [ -n "$avg_t" ]; then
  score_state="$(awk -v avg="$avg_t" -v max="$max_avg_t" 'BEGIN {
    gap = avg - max;
    printf "avgT=%0.3f max_avgT=%d gap=%0.3f", avg, max, gap
  }')"
fi

clean_state="unknown"
if [ -n "$classical" ] && [ -n "$phase" ] && [ -n "$ancilla" ]; then
  if [ "$classical" = "0" ] && [ "$phase" = "0" ] && [ "$ancilla" = "0" ]; then
    clean_state="0/0/0 clean"
  else
    clean_state="${classical}/${phase}/${ancilla} dirty"
  fi
fi

trace_summary="not provided"
if [ -n "$trace_log" ]; then
  trace_target_q="${trace_target_q:-$q}"
  trace_active_floor="${trace_active_floor:-$trace_target_q}"
  trace_summary="$(awk -v target="$trace_target_q" -v floor="$trace_active_floor" '
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
    $1 == "TLM_TAPE" {
      tape_rows++;
      active = field("active") + 0;
      tape = field("tape") + 0;
      pending = field("pending") + 0;
      iter = field("i");
      direction = field("direction");
      stage = field("stage");
      codec = field("codec");
      if (active > max_active) {
        max_active = active;
        max_line = sprintf("direction=%s stage=%s i=%s active=%d tape=%d pending=%d codec=%s",
          direction, stage, iter, active, tape, pending, codec);
      }
      if (active >= floor) {
        plateau_rows++;
        if (first_plateau_i == "" || iter + 0 < first_plateau_i + 0) first_plateau_i = iter;
        if (last_plateau_i == "" || iter + 0 > last_plateau_i + 0) last_plateau_i = iter;
        if (tape > max_plateau_tape) max_plateau_tape = tape;
        if (pending > max_plateau_pending) max_plateau_pending = pending;
        if (codec != "") plateau_codec[codec]++;
      }
    }
    $1 == "TLM_FFG" {
      ffg_rows++;
      call = field("call");
      entry = field("entry_active") + 0;
      peak = field("local_peak") + 0;
      if (entry >= target || peak >= target) {
        ffg_plateau++;
        ffg_calls = append(ffg_calls, call);
      }
    }
    END {
      codec_summary = "";
      for (codec in plateau_codec) {
        if (codec_summary == "") codec_summary = codec ":" plateau_codec[codec];
        else codec_summary = codec_summary "," codec ":" plateau_codec[codec];
      }
      if (tape_rows == 0 && ffg_rows == 0) {
        print "TLM_TAPE/TLM_FFG rows not observed";
      } else {
        printf "target_q=%s active_floor=%s tape_rows=%d max_tape_row={%s}; tape_floor_rows=%d i_range=%s..%s max_tape=%d max_pending=%d codecs=%s; ffg_plateau=%d calls=%s",
          target, floor, tape_rows, max_line, plateau_rows,
          (first_plateau_i == "" ? "none" : first_plateau_i),
          (last_plateau_i == "" ? "none" : last_plateau_i),
          max_plateau_tape, max_plateau_pending,
          (codec_summary == "" ? "none" : codec_summary),
          ffg_plateau, (ffg_calls == "" ? "none" : ffg_calls);
      }
    }
  ' "$trace_log")"
fi

cat <<EOF
Reversible pebbling memory gate:
- Frontier: ${frontier}
- Route: ${route}
- Candidate: ${candidate}
- q target / max avgT: q=${q} max_avgT=${max_avg_t}
- Peak node: phase=${peak_phase:-unknown} q=${peak_qubits:-unknown} ops_idx=${peak_ops_idx:-unknown} emitted=${profile_emitted:-unknown}
- Removed or delayed value: ${removed_value}
- Producer / consumers: producer=${producer}; consumers=${consumers}
- Pebbling move: ${move}
- Trace ledger: ${trace_summary}
- Extra ops estimate: ${score_state}
- Dead-drop state: ${drop_state}; ${drop_summary}
- Residual evidence: shots=${shots:-unknown} eval_q=${eval_qubits:-unknown} bits=${eval_bits:-unknown} loaded_ops=${loaded_ops:-unknown} result=${clean_state}
- Decision: continue only if current-stream drops and 0/0/0; otherwise regenerate or park
EOF

if [ -n "$notes" ]; then
  printf '%s\n' "- Notes: ${notes}"
fi
