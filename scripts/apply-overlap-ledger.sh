#!/usr/bin/env bash
set -euo pipefail

trace=""
frontier=""
q=""
target_q=""
route="unknown"
candidate="pending_symbols"
target_phase="tlm_apply_inverse_mod_sub_fold"
target_i="255"

usage() {
  cat <<'USAGE'
usage: apply-overlap-ledger.sh --trace PATH --frontier SCORE --q Q [options]

Options:
  --target-q Q       target peak qubit tier; defaults to Q-1
  --route NAME       route or checkout label
  --candidate NAME   overlap candidate; default pending_symbols
  --target-phase P   fold/apply phase; default tlm_apply_inverse_mod_sub_fold
  --target-i I       fold iteration; default 255, or "any"

The script emits a public proof ledger for apply/codec/fold overlap claims.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --trace) trace="${2:?missing trace}"; shift 2 ;;
    --frontier) frontier="${2:?missing frontier}"; shift 2 ;;
    --q) q="${2:?missing q}"; shift 2 ;;
    --target-q) target_q="${2:?missing target q}"; shift 2 ;;
    --route) route="${2:?missing route}"; shift 2 ;;
    --candidate) candidate="${2:?missing candidate}"; shift 2 ;;
    --target-phase) target_phase="${2:?missing target phase}"; shift 2 ;;
    --target-i) target_i="${2:?missing target i}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'unknown_arg=%s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$trace" ] || [ -z "$frontier" ] || [ -z "$q" ]; then
  usage >&2
  exit 2
fi
if [ ! -f "$trace" ]; then
  printf 'apply_overlap_gate=fail missing_trace=%s\n' "$trace" >&2
  exit 1
fi
case "$frontier" in ''|*[!0-9]*) printf 'invalid_frontier=%s\n' "$frontier" >&2; exit 2 ;; esac
case "$q" in ''|*[!0-9]*) printf 'invalid_q=%s\n' "$q" >&2; exit 2 ;; esac
if [ "$q" -le 1 ]; then
  printf 'invalid_q=%s\n' "$q" >&2
  exit 2
fi

if [ -z "$target_q" ]; then
  target_q=$((q - 1))
fi
case "$target_q" in ''|*[!0-9]*) printf 'invalid_target_q=%s\n' "$target_q" >&2; exit 2 ;; esac
if [ "$target_q" -le 0 ]; then
  printf 'invalid_target_q=%s\n' "$target_q" >&2
  exit 2
fi
if [ "$target_i" != "any" ]; then
  case "$target_i" in ''|*[!0-9]*) printf 'invalid_target_i=%s\n' "$target_i" >&2; exit 2 ;; esac
fi

max_avg=$(( (frontier - 1) / q ))
target_max_avg=$(( (frontier - 1) / target_q ))
requested_cut=$((q - target_q))

awk -v route="$route" \
    -v candidate="$candidate" \
    -v frontier="$frontier" \
    -v q="$q" \
    -v target_q="$target_q" \
    -v max_avg="$max_avg" \
    -v target_max_avg="$target_max_avg" \
    -v requested_cut="$requested_cut" \
    -v target_phase="$target_phase" \
    -v target_i="$target_i" '
  function field(name,    i, a) {
    for (i = 1; i <= NF; i++) {
      if ($i ~ ("^" name "=")) {
        split($i, a, "=");
        return a[2];
      }
    }
    return "";
  }
  function truthy(v, low) {
    low = tolower(v);
    return low == "1" || low == "true" || low == "yes" || low == "ok" || low == "clean" || low == "certified";
  }
  function append(list, item) {
    if (item == "") return list;
    if (list == "") return item;
    return list "," item;
  }
  /^TLM_PROFILE / {
    profile_rows++;
    phase = field("peak_phase");
    peak = field("peak_qubits") + 0;
    ops_idx = field("peak_ops_idx");
    emitted = field("emitted_ops");
    if (peak > profile_peak) {
      profile_peak = peak;
      profile_phase = phase;
      profile_ops_idx = ops_idx;
      profile_emitted = emitted;
    }
    if (phase == target_phase) profile_phase_seen = 1;
  }
  /^TLM_TAPE / {
    phase = field("phase");
    iter = field("i");
    if ((target_phase == "any" || phase == "" || phase == target_phase) &&
        (target_i == "any" || iter == target_i)) {
      tape_matches++;
      active = field("active") + 0;
      tape = field("tape") + 0;
      pending = field("pending") + 0;
      codec = field("codec");
      if (active > max_tape_active) {
        max_tape_active = active;
        max_tape_line = sprintf("i=%s active=%d tape=%d pending=%d codec=%s phase=%s",
          iter, active, tape, pending, codec, phase);
      }
      if (tape > max_tape) max_tape = tape;
      if (pending > max_pending) max_pending = pending;
      if (active > target_q) tape_above++;
      tape_iters = append(tape_iters, iter);
    }
  }
  /^TLM_OVERLAP_CHECK / {
    cand = field("candidate");
    iter = field("i");
    phase = field("target_phase");
    if (phase == "") phase = field("phase");
    if ((candidate == "any" || cand == candidate) &&
        (target_i == "any" || iter == target_i) &&
        (target_phase == "any" || phase == target_phase)) {
      evidence++;
      reads = field("reads_during_fold");
      if (reads == "") reads = field("read_count");
      if (reads == "") reads = field("reads");
      if (reads == "") reads = "unknown";
      restore = field("restore_proof");
      if (restore == "") restore = field("restore");
      phase_proof = field("phase_proof");
      if (phase_proof == "") phase_proof = field("phase_clean");
      cert = field("support_certificate");
      if (cert == "") cert = field("certificate");
      status = field("support_status");

      if (reads == "unknown" || reads + 0 > 0) {
        read_block = 1;
      }
      if (!truthy(restore)) {
        restore_missing = 1;
      }
      if (!truthy(phase_proof)) {
        phase_missing = 1;
      }
      if (cert != "" || truthy(status)) {
        cert_count++;
      }
      evidence_lines = append(evidence_lines,
        sprintf("candidate=%s i=%s reads=%s restore=%s phase=%s cert=%s status=%s",
          cand, iter, reads, restore, phase_proof, cert, status));
    }
  }
  END {
    if (tape_matches == 0) {
      decision = "missing-tape-overlap-trace";
      next_step = "capture TLM_TAPE rows around the fold before editing solver code";
    } else if (evidence == 0) {
      decision = "measure-read-restore-phase";
      next_step = "add TLM_OVERLAP_CHECK with reads_during_fold, restore_proof, phase_proof, and certificate";
    } else if (read_block) {
      decision = "overlap-nacked-read-during-fold";
      next_step = "abandon this overlap or move decode after the last fold read";
    } else if (restore_missing) {
      decision = "overlap-restore-proof-missing";
      next_step = "prove the delayed or streamed wires restore exactly before uncompute";
    } else if (phase_missing) {
      decision = "overlap-phase-proof-missing";
      next_step = "prove the phase channel is unchanged by the delayed wires";
    } else if (cert_count == 0) {
      decision = "certificate-ready";
      next_step = "attach a public route-specific support certificate before compute";
    } else {
      decision = "support-certified-binder-fact";
      next_step = "promote to a bounded local solver patch with toy/read/restore/phase tests";
    }

    profile_text = profile_rows ? sprintf("peak=%d phase=%s ops_idx=%s emitted_ops=%s",
      profile_peak, profile_phase, profile_ops_idx, profile_emitted) : "none";
    max_tape_text = max_tape_line == "" ? "none" : max_tape_line;
    evidence_text = evidence_lines == "" ? "none" : evidence_lines;
    tape_iters_text = tape_iters == "" ? "none" : tape_iters;

    printf "Apply overlap ledger:\n";
    printf "- Route: %s\n", route;
    printf "- Candidate: %s\n", candidate;
    printf "- Frontier/q/max avgT: %s/%s/%s\n", frontier, q, max_avg;
    printf "- Target q/max avgT: %s/%s\n", target_q, target_max_avg;
    printf "- Requested width cut: %d\n", requested_cut;
    printf "- Target phase: %s\n", target_phase;
    printf "- Target iter: %s\n", target_i;
    printf "- Peak profile: %s\n", profile_text;
    printf "- Tape overlap: rows=%d above_target=%d max={%s} max_tape=%d max_pending=%d iters=%s\n",
      tape_matches, tape_above, max_tape_text, max_tape, max_pending, tape_iters_text;
    printf "- Evidence rows: %d details=%s\n", evidence, evidence_text;
    printf "- Decision: %s\n", decision;
    printf "- Next: %s\n", next_step;
  }
' "$trace"
