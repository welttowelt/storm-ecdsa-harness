#!/usr/bin/env bash
# qcut-candidate-prefilter.sh — implements the 3-gate q-cut prefilter (skill q1153-peak-structural-map.md).
#
# Kill a qubit-width-cut candidate on paper BEFORE any build/island compute. Pass the candidate's
# restore mechanism, the peak chunk's stage-width s, and a Toffoli-factor estimate; the tool applies
# the 3 gates (restore safety, dependency-floor, product-test) and verdicts CHASE / KILL-<gate>.
#
# Usage:
#   qcut-candidate-prefilter.sh <restore_mech> <peak_chunk_s> <toffoli_factor_vs_ripple>
#   restore_mech ∈ {exact-unitary, cond-clean-dagger, bennett, dirty-borrow, mbu-live-control, ghosting, prob-trunc}
#   peak_chunk_s = the stage-width of the chunk that sets the global peak (our peak is s=2)
#   toffoli_factor_vs_ripple = ratio of the candidate's Toffoli count to the ~8-CCX/chunk ripple
#                              (e.g. 1.0 ≈ same, 4.0 ≈ O(n log n) asymptotic adder at narrow n)
# Example:
#   qcut-candidate-prefilter.sh dirty-borrow 2 4.0   # → KILL (g1 dirty + g2 width-1 + g3 product)
#   qcut-candidate-prefilter.sh exact-unitary 6 1.0    # → CHASE (if a staircase-reshape made the peak s=6)

set -euo pipefail
rm="${1:?usage: $0 <restore_mech> <peak_chunk_s> <toffoli_factor_vs_ripple>}"
s="${2:?need peak chunk stage-width s}"
tf="${3:?need toffoli_factor_vs_ripple (candidate Toffoli / ~8-CCX-chunk ripple)}"

# Gate 1: restore-mechanism safety
safe="exact-unitary cond-clean-dagger bennett"
if echo " $safe " | grep -q " $rm "; then g1="SAFE (unitary-invertible by construction — cannot hit the 9024/141/141 wall)"
else g1="KILL-g1: inexact restore ($rm) → structural palindrome violation → 9024cls/141pha/141anc nonce-independent. Switch route."; fi

# Gate 2: dependency-floor (width-1 s=2 peak is unresolvable by any adder substitution)
if [ "$s" -le 2 ] 2>/dev/null; then g2="KILL-g2: peak chunk is width-1 (s=$s). Any adder needs >=2 carries for s=2 (c_1 feeds c_2=cout); NO adder substitution reduces it. Only a staircase-reshape (move peak to s>=4) escapes.";
else g2="PASS-g2: peak chunk s=$s (wide) — adder tricks applicable / below-peak-irrelevant."; fi

# Gate 3: product-test (Toffoli factor must not eat the qubit win)
g3="$(
awk -v tf="$tf" 'BEGIN{
  # rough: a width-1 cut (peak 1153->1152) buys ~0.087% (1/1153); the Toffoli factor must stay under ~1.0009 to net win
  cut_frac = 1.0/1153.0
  if (tf > 1.0 + cut_frac) print "KILL-g3: Toffoli factor " tf " > width win " cut_frac " → round(new_avgT)x1152 >= old_score (asymptotic adder loses the product at narrow n)."
  else print "PASS-g3: Toffoli factor " tf " within the width-win budget — run the build, then CONFIRM round(new_avgT)x1152 < old_score."
}'
)"
echo "$g3"

echo ""
echo "=== VERDICT for restore=$rm peak_s=$s toffoli_factor=$tf ==="
echo "g1 [restore]: $g1"
echo "g2 [floor]:   $g2"
echo "g3 [product]: $g3"
if [[ "$g1" == KILL* ]]; then
  echo "→ KILL (gate 1). Do not build."
elif [[ "$g2" == KILL* ]]; then
  echo "→ KILL (gate 2). Do not build."
elif [[ "$g3" == KILL* ]]; then
  echo "→ KILL (gate 3). Do not build."
else
  echo "→ CHASE only after build confirms score and restore/phase/ancilla checks."
fi
