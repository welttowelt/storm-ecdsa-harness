#!/usr/bin/env bash
# circuit-edit-desync-diagnostic.sh — implements the `circuit-edit-integration-safety` skill as software.
#
# Use after wiring ANY op-stream edit (a new adder, a vent, a borrowed ancilla, an env override that
# changes the op stream) into an ecdsa.fail reversible circuit. Runs the skill's step-1 falsifier
# (DROP_DEAD_ROBUST disabled = the "stale dead-gate index" kill-test from Dead Gate Elimination,
# arXiv:2504.12729) and tells you whether nonce-independent full-circuit dirt is a STALE-INDEX
# artifact (cheap fix: regen the .idx) or a deeper defect (free-pool aliasing / adder math).
#
# Usage:
#   circuit-edit-desync-diagnostic.sh <checkout> <nonce> [EDIT_ENV ...]
# Example:
#   circuit-edit-desync-diagnostic.sh ~/ecdsafail-challenge 10058189779 TLM_GIDNEY_3CLEAN_SUFFIX=1
#
# Output: a one-line verdict (STALE-INDEX | NOT-STALE | CLEAN) + the cls/pha/anc for drops-on vs
# drops-off, + the recommended next step per the skill's ladder.

set -euo pipefail

ck="${1:?usage: $0 <checkout> <nonce> [EDIT_ENV...]}"
nonce="${2:?need a nonce}"
shift 2 || true
edit_env=("$@")

cd "$ck"
BIN="./target/release"

eval_one() {  # $1 = extra env string (e.g. "DROP_DEAD_ROBUST_DISABLE=1"); prints "cls pha anc"
  local extra="$1"
  # shellcheck disable=SC2086
  env DIALOG_TAIL_NONCE="$nonce" $extra "${edit_env[@]}" "$BIN/build_circuit" >/dev/null 2>&1
  env DIALOG_TAIL_NONCE="$nonce" $extra "${edit_env[@]}" "$BIN/eval_circuit" 2>&1 \
    | awk '/classical mismatches/   {c=$NF}
           /phase-garbage batches/   {p=$NF}
           /ancilla-garbage batches/ {a=$NF}
           END{printf "%s %s %s\n", c+0, p+0, a+0}'
}

echo "=== desync diagnostic: checkout=$ck nonce=$nonce edit=[${edit_env[*]}] ==="

# Reference: drops ON (the dirty baseline you're debugging)
read -r c_on p_on a_on < <(eval_one "")
echo "drops-ON  (production): cls=$c_on pha=$p_on anc=$a_on"

# Step 1 of the ladder: drops OFF (raw stream, no dead-gate index)
read -r c_off p_off a_off < <(eval_one "DROP_DEAD_ROBUST_DISABLE=1 DROP_DEAD_ROBUST_SECOND=0")
echo "drops-OFF (raw):       cls=$c_off pha=$p_off anc=$a_off"

echo ""
if [ "$a_off" = "0" ] && { [ "$a_on" -gt 0 ] 2>/dev/null || [ "$c_on" -gt 0 ] 2>/dev/null; }; then
  echo "VERDICT: STALE-INDEX (Dead-Gate-Elimination scope violation). The edit changed the op stream;"
  echo "  the baseline .idx dropped the WRONG ops. anc=0 raw = your primitive is value-exact."
  echo "  FIX: regen the drop-dead .idx for the edited stream (dead_ccx_scan / find_dead_ccx with"
  echo "  DEAD_SCAN_REAL_SEED=1, or per-nonce). See regen-drop-dead-idx.sh. Residual cls/pha (nonce-"
  echo "  dependent) = a findable island, not structural death."
elif [ "$a_off" -gt 0 ] 2>/dev/null; then
  echo "VERDICT: NOT-STALE-INDEX. anc>0 even raw => free-pool ID-reuse aliasing or adder math (palindrome"
  echo "  violation). Proceed to skill step 2 (disable free pool: fresh high IDs for transient ancilla)"
  echo "  then step 3 (vent discharge target). Emit first-divergence shot + first nonzero ancilla bit."
elif [ "$c_off" = "0" ] && [ "$p_off" = "0" ]; then
  echo "VERDICT: CLEAN raw. The edit is value-exact; any drops-on dirt was stale-index. Ship the regen'd .idx."
else
  echo "VERDICT: ambiguous (cls/pha raw but anc=0) — likely a findable island (nonce-dependent). Hunt a"
  echo "  clean nonce; if found, measure avgT x peak."
fi
echo ""
echo "Refs: skill circuit-edit-integration-safety.md; Dead Gate Elimination arXiv:2504.12729;"
echo "Qubit Recycling Revisited PLDI 2024; Gidney Spooky Pebble 2019."
